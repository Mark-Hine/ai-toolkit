"""Vote and thread reconciliation rules of the pr-review Azure DevOps poster, run against a fake host."""
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'post_azdo', REPO_ROOT / 'claude/plugins/pr-review/skills/pr-review/scripts/post_azdo.py')
post_azdo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(post_azdo)


class FakeAdo:
    def __init__(self):
        self.calls = []

    def create_thread(self, content, path=None, line=None, status='active'):
        self.calls.append(('create', content.split('\n', 1)[0], path, line))

    def reply(self, thread_id, content):
        self.calls.append(('reply', thread_id, content.split(' at ')[0].split('. ')[0]))

    def set_status(self, thread_id, status):
        self.calls.append(('status', thread_id, status))

    def kinds(self):
        return [c[0] + (':' + c[2] if c[0] == 'status' else '') for c in self.calls]


def finding(fid, severity, status='open'):
    return {'id': fid, 'severity': severity, 'status': status, 'title': fid, 'pr_comment': 'x',
            'file': 'a.kt', 'line': 3}


def thread(tid, status, comments=()):
    return {'id': tid, 'status': status, 'comments': [{'content': c} for c in comments]}


def doc(*findings, verdict='request_changes'):
    return {'schema': 'pr-review/v1', 'verdict': verdict, 'findings': list(findings), 'scope': {'source_head': 'abc123'}}


class VoteTest(unittest.TestCase):
    def test_open_blocker_gates(self):
        self.assertEqual(post_azdo.VOTE['waiting_for_author'], post_azdo.compute_vote(doc(finding('B1', 'blocker')), {}, False))

    def test_regressed_and_partial_blockers_gate(self):
        for status in ('regressed', 'partial'):
            self.assertEqual(post_azdo.VOTE['waiting_for_author'],
                             post_azdo.compute_vote(doc(finding('B1', 'blocker', status)), {}, False), status)

    def test_wontfix_thread_does_not_lift_a_blocker(self):
        by_marker = {'B1': thread(1, 'wontFix')}
        self.assertEqual(post_azdo.VOTE['waiting_for_author'], post_azdo.compute_vote(doc(finding('B1', 'blocker')), by_marker, False))

    def test_fixed_blocker_with_open_nit_is_suggestions(self):
        d = doc(finding('B1', 'blocker', 'fixed'), finding('N1', 'nit'), verdict='approve_with_comments')
        self.assertEqual(post_azdo.VOTE['approve_with_suggestions'], post_azdo.compute_vote(d, {}, False))

    def test_all_fixed_is_approve(self):
        d = doc(finding('B1', 'blocker', 'fixed'), finding('M1', 'major', 'retracted'), verdict='approve')
        self.assertEqual(post_azdo.VOTE['approve'], post_azdo.compute_vote(d, {}, False))

    def test_question_gates_until_a_human_resolves_it(self):
        d = doc(finding('Q1', 'question'), verdict='request_changes')
        self.assertEqual(post_azdo.VOTE['waiting_for_author'], post_azdo.compute_vote(d, {}, False))
        self.assertEqual(post_azdo.VOTE['approve'], post_azdo.compute_vote(d, {'Q1': thread(1, 'byDesign')}, False))

    def test_reject_flag(self):
        self.assertEqual(post_azdo.VOTE['reject'], post_azdo.compute_vote(doc(finding('B1', 'blocker')), {}, True))


class ValidateTest(unittest.TestCase):
    def test_unknown_severity_and_status(self):
        problems = post_azdo.validate(doc(finding('X1', 'minor'), finding('X2', 'nit', 'untouched')))
        self.assertEqual(2, len(problems))

    def test_gating_blocker_needs_request_changes(self):
        self.assertTrue(post_azdo.validate(doc(finding('B1', 'blocker', 'regressed'), verdict='approve')))
        self.assertEqual([], post_azdo.validate(doc(finding('B1', 'blocker', 'regressed'))))


class ReconcileTest(unittest.TestCase):
    def run_case(self, f, t):
        ado = FakeAdo()
        post_azdo.reconcile(ado, doc(f), {} if t is None else {f['id']: t})
        return ado.kinds()

    def test_missing_thread(self):
        for status in ('open', 'regressed', 'partial'):
            self.assertEqual(['create'], self.run_case(finding('B1', 'blocker', status), None), status)
        for status in ('fixed', 'retracted'):
            self.assertEqual([], self.run_case(finding('B1', 'blocker', status), None), status)

    def test_active_thread(self):
        self.assertEqual([], self.run_case(finding('B1', 'blocker', 'open'), thread(1, 'active')))
        self.assertEqual([], self.run_case(finding('B1', 'blocker', 'regressed'), thread(1, 'active')))
        self.assertEqual(['reply', 'status:fixed'], self.run_case(finding('B1', 'blocker', 'fixed'), thread(1, 'active')))
        self.assertEqual(['reply', 'status:closed'], self.run_case(finding('B1', 'blocker', 'retracted'), thread(1, 'active')))

    def test_bot_resolved_thread(self):
        self.assertEqual(['reply', 'status:active'], self.run_case(finding('M1', 'major', 'open'), thread(1, 'fixed')))
        self.assertEqual([], self.run_case(finding('Q1', 'question', 'open'), thread(1, 'closed')))
        self.assertEqual(['reply', 'status:active'], self.run_case(finding('B1', 'blocker', 'regressed'), thread(1, 'fixed')))
        self.assertEqual(['reply', 'status:active'], self.run_case(finding('B1', 'blocker', 'partial'), thread(1, 'fixed')))
        self.assertEqual([], self.run_case(finding('B1', 'blocker', 'fixed'), thread(1, 'fixed')))

    def test_human_disposition_is_never_reopened(self):
        for tstatus in ('wontFix', 'byDesign'):
            self.assertEqual([], self.run_case(finding('M1', 'major', 'open'), thread(1, tstatus)), tstatus)
            self.assertEqual(['reply'], self.run_case(finding('M1', 'major', 'regressed'), thread(1, tstatus)), tstatus)
            already = thread(1, tstatus, comments=['Marked regressed at `abc` [pr-review:M1]'])
            self.assertEqual([], self.run_case(finding('M1', 'major', 'regressed'), already), tstatus)
            self.assertEqual([], self.run_case(finding('M1', 'major', 'fixed'), thread(1, tstatus)), tstatus)

    def test_summary_lists_gating_blockers(self):
        body = post_azdo.summary_body(doc(finding('B1', 'blocker', 'regressed'), finding('B2', 'blocker', 'fixed')))
        self.assertIn('1 blocker(s)', body)
        self.assertIn('[regressed]', body)


if __name__ == '__main__':
    unittest.main()
