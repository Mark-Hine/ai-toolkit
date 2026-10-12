"""Tests for the agent-neutral build: template engine, target naming and the committed outputs."""
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import build  # noqa: E402
import engine  # noqa: E402
from targets import TARGETS  # noqa: E402

CONFIG = tomllib.loads((HERE / 'agents.toml').read_text())


def target(name):
    return TARGETS[name](CONFIG['targets'][name])


class EngineTests(unittest.TestCase):
    def test_tokens_render_per_target(self):
        text = 'Read {@project_file_full}, then run {@invoke web-kit/run-app} with {@skill web-kit/standards}.'
        self.assertEqual(engine.render(text, target('claude')),
                         'Read `CLAUDE.md`, then run /web-kit:run-app with web-kit:standards.')
        self.assertEqual(engine.render(text, target('codex')),
                         'Read `AGENTS.md`, then run $web-run-app with web-standards.')
        self.assertEqual(engine.render(text, target('antigravity')),
                         'Read `AGENTS.md` (or `GEMINI.md`), then run /web-run-app with web-standards.')

    def test_skill_named_like_its_kit_keeps_its_name(self):
        self.assertEqual(engine.render('{@invoke pr-review/pr-review}', target('codex')), '$pr-review')
        self.assertEqual(engine.render('{@invoke toolkit/audit}', target('antigravity')), '/toolkit-audit')
        self.assertEqual(engine.render('{@invoke design-kit/iterate}', target('claude')), '/design-kit:iterate')

    def test_model_token(self):
        self.assertEqual(engine.render('{@model review}', target('antigravity')), 'pro')
        self.assertEqual(engine.render('{@model research}', target('codex')), 'gpt-6-sol')

    def test_unknown_token_fails(self):
        with self.assertRaises(engine.RenderError):
            engine.render('{@no_such_token}', target('claude'))
        with self.assertRaises(engine.RenderError):
            engine.render('{@model nonsense}', target('claude'))

    def test_double_braces_are_left_alone(self):
        text = 'token: ${{ secrets.TOKEN }}'
        self.assertEqual(engine.render(text, target('codex')), text)

    def test_blocks_keep_one_branch(self):
        text = 'a\n<!-- if: plan_mode -->\nplan\n<!-- else -->\nno plan\n<!-- end -->\nz'
        self.assertEqual(engine.render(text, target('claude')), 'a\nplan\nz')
        self.assertEqual(engine.render(text, target('codex')), 'a\nno plan\nz')

    def test_block_conditions(self):
        text = '<!-- if: target=codex, ci_cli=agy -->\nyes\n<!-- end -->'
        self.assertEqual(engine.render(text, target('claude')), '')
        self.assertEqual(engine.render(text, target('codex')), 'yes')
        self.assertEqual(engine.render(text, target('antigravity')), 'yes')
        self.assertEqual(engine.render('<!-- if: !plan_mode -->\nx\n<!-- end -->', target('claude')), '')

    def test_unknown_capability_fails(self):
        with self.assertRaises(KeyError):
            engine.render('<!-- if: no_such_flag -->\nx\n<!-- end -->', target('claude'))

    def test_malformed_blocks_fail(self):
        for text in ('<!-- if: plan_mode -->\nx', '<!-- else -->', '<!-- end -->',
                     '<!-- if: plan_mode -->\n<!-- if: plan_mode -->\n<!-- end -->\n<!-- end -->'):
            with self.assertRaises(engine.RenderError, msg=text):
                engine.render(text, target('claude'))

    def test_lint_flags_literals_outside_blocks_only(self):
        text = 'See ~/.claude/rules.\n<!-- if: target=claude -->\nSee ~/.claude/rules.\n<!-- end -->\nRun $android-feature.'
        self.assertEqual([n for n, _ in engine.lint(text)], [1, 5])
        self.assertEqual(engine.lint('Read {@project_file} and DESIGN.md.'), [])


class RepositoryTests(unittest.TestCase):
    def test_sources_pass_the_lint(self):
        self.assertEqual(build.lint_sources(build.Project()), [])

    def test_committed_outputs_are_current(self):
        self.assertEqual(build.run(check=True), 0)

    def test_every_target_has_settings_and_an_adapter(self):
        self.assertEqual(set(CONFIG['targets']), set(TARGETS))
        flags = {name: set(settings['capabilities']) for name, settings in CONFIG['targets'].items()}
        self.assertEqual(len({frozenset(f) for f in flags.values()}), 1, flags)

    def test_orphans_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src/rules/web').mkdir(parents=True)
            (root / 'src/rules/web/a.md').write_text('# A\n')
            stray = root / 'claude/home/rules/web/old.md'
            stray.parent.mkdir(parents=True)
            stray.write_text('old')
            config = {'targets': {'claude': CONFIG['targets']['claude']}}
            project = build.Project(root)
            outputs = build.all_outputs(project, config)
            self.assertEqual([o.path for o in outputs], ['claude/home/rules/web/a.md'])
            self.assertEqual(build.orphans(project, config, outputs), ['claude/home/rules/web/old.md'])


if __name__ == '__main__':
    unittest.main()
