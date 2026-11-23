"""The doctor collector counts workarounds, test runs and reply style from transcripts."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('doctor', REPO / 'tools/doctor.py')
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


def assistant(*blocks):
    return {'type': 'assistant', 'message': {'content': list(blocks)}}


def use(tool_id, name, **args):
    return {'type': 'tool_use', 'id': tool_id, 'name': name, 'input': args}


def result(tool_id, text, error=False):
    return {'type': 'user', 'message': {'content': [
        {'type': 'tool_result', 'tool_use_id': tool_id, 'content': text, 'is_error': error}]}}


def prompt(text):
    return {'type': 'user', 'message': {'content': text}}


class BashFactsTest(unittest.TestCase):
    def test_counts_shell_search_only_when_it_leads_the_command(self):
        self.assertEqual(doctor.bash_facts('grep -rn foo src')['shell_for_read_or_search'], 1)
        self.assertEqual(doctor.bash_facts('git log | grep foo')['shell_for_read_or_search'], 0)

    def test_separates_a_plain_sleep_from_a_polling_loop(self):
        self.assertEqual(doctor.bash_facts('sleep 5')['polling_loop'], 0)
        facts = doctor.bash_facts('until adb shell getprop sys.boot_completed; do sleep 2; done')
        self.assertEqual((facts['sleep'], facts['polling_loop']), (1, 1))

    def test_grades_gradle_test_runs_by_filter_and_module(self):
        filtered = doctor.bash_facts("./gradlew :app:testDebugUnitTest --tests 'a.B'")
        module = doctor.bash_facts('./gradlew :app:testDebugUnitTest')
        whole = doctor.bash_facts('./gradlew test')
        self.assertEqual((filtered['gradle_test_runs'], filtered['gradle_test_unfiltered']), (1, 0))
        self.assertEqual((module['gradle_test_unfiltered'], module['gradle_test_whole_project']), (1, 0))
        self.assertEqual(whole['gradle_test_whole_project'], 1)
        self.assertEqual(doctor.bash_facts('./gradlew assembleDebug')['gradle_test_runs'], 0)
        self.assertEqual(doctor.bash_facts('./gradlew :app:compileDebugUnitTestKotlin')['gradle_test_runs'], 0)


class ReplyFactsTest(unittest.TestCase):
    def test_ignores_code_when_counting_punctuation(self):
        facts = doctor.reply_facts('Done.\n```kotlin\nval a = 1; val b = 2\n```\nUse `a; b` here.')
        self.assertEqual(facts['semicolons'], 0)

    def test_detects_dash_bold_and_closing_offer(self):
        facts = doctor.reply_facts('It works \u2014 **mostly**. Want me to fix the rest?')
        self.assertEqual((facts['dashes'], facts['bold'], facts['offer']), (1, 1, 1))


class ClassifyErrorTest(unittest.TestCase):
    def test_names_the_common_failure_classes(self):
        self.assertEqual(doctor.classify_error('PreToolUse:Bash hook blocked this command'), 'hook_block')
        self.assertEqual(doctor.classify_error('File has not been read yet. Read it first.'), 'edit_before_read')
        self.assertEqual(doctor.classify_error('Exit code 1\nboom'), 'nonzero_exit')
        self.assertEqual(doctor.classify_error('something odd'), 'other')


class CollectTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        (self.home / 'rules').mkdir()
        (self.home / 'CLAUDE.md').write_text('x' * 100)
        (self.home / 'rules/common.md').write_text('y' * 50)
        (self.home / 'rules/scoped.md').write_text('---\npaths:\n  - "**/*.kt"\n---\n' + 'z' * 500)
        self.write('-work-app/s1.jsonl', [
            prompt('fix the bug'),
            assistant(use('t1', 'Bash', command='cat build.gradle'), use('t2', 'Bash', command='./gradlew test')),
            result('t1', 'ok'),
            result('t2', 'Exit code 1', error=True),
            assistant(use('t3', 'Write', file_path='/r/app/src/test/FooTest.kt', content='@Test fun a() {}\n@Test fun b() {}'),
                      use('t4', 'Write', file_path='/r/app/src/main/Foo.kt', content='class Foo\n' * 49),
                      use('t5', 'Agent', subagent_type='Explore', prompt='look')),
            assistant({'type': 'text', 'text': 'Fixed the bug in Foo.'}),
        ])
        self.write('-work-app/s1/subagents/a.jsonl', [assistant(use('u1', 'Read', file_path='/r/a'))])
        self.write('-tmp-trigger-eval-x/e.jsonl', [assistant(use('e1', 'Bash', command='sleep 1'))])

    def write(self, name, events):
        path = self.home / 'projects' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n')

    def test_counts_sessions_and_skips_eval_projects(self):
        report = doctor.collect(self.home, days=14)
        self.assertEqual((report['sessions'], report['subagent_transcripts'], report['eval_transcripts_skipped']), (1, 1, 1))
        self.assertEqual(report['tool_calls'], 6)
        self.assertEqual(report['workarounds']['sleep'], 0)

    def test_reports_errors_workarounds_and_test_ratios(self):
        report = doctor.collect(self.home, days=14)
        self.assertEqual(report['errors_by_category'], {'nonzero_exit': 1})
        self.assertEqual(report['workarounds']['shell_for_read_or_search'], 1)
        self.assertEqual(report['tests']['gradle_test_whole_project'], 1)
        self.assertEqual(report['tests']['tests_per_100_production_lines'], 4.0)
        self.assertEqual(report['subagents'], {'spawns': 1, 'spawns_without_model': 1})
        self.assertEqual(report['replies']['count'], 1)

    def test_measures_only_unscoped_rules_as_always_loaded(self):
        setup = doctor.collect(self.home, days=14)['setup']
        self.assertEqual(setup['always_loaded_chars'], 150)
        self.assertEqual(setup['eval_leftover_folders'], 1)

    def test_ignores_events_older_than_the_window(self):
        old = dict(assistant(use('o1', 'Bash', command='sleep 9')), timestamp='2020-01-01T00:00:00.000Z')
        self.write('-work-app/old.jsonl', [old])
        report = doctor.collect(self.home, days=14)
        self.assertEqual((report['sessions'], report['workarounds']['sleep']), (1, 0))

    def test_alias_hides_project_names(self):
        report = doctor.collect(self.home, days=14, use_alias=True)
        self.assertTrue(all(name.startswith('proj-') for name in report['sessions_by_project']))


if __name__ == '__main__':
    unittest.main()
