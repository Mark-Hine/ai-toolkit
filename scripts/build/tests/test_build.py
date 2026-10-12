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


SKILL = '''---
name: feature
description: "Do the thing."
argument_hint: "[ticket]"
invocation: manual
preamble: playbook
metadata:
  verified: 2026-10-01
---

# Feature: {@args}
'''

AGENT = '''---
name: web-researcher
description: Looks things up.
role: researcher
skills: [web-kit/standards]
---

# Researcher
<!-- if: skills_preload -->
Preloaded.
<!-- else -->
Read it.
<!-- end -->
'''


def skill_project(root):
    skill_dir = root / 'src/skills/web-kit/feature'
    skill_dir.mkdir(parents=True)
    (skill_dir / 'SKILL.md').write_text(SKILL)
    (skill_dir / 'scripts').mkdir()
    (skill_dir / 'scripts/run.sh').write_text('echo hi\n')
    (skill_dir / 'scripts/run.sh').chmod(0o755)
    agents = root / 'src/agents/web-kit'
    agents.mkdir(parents=True)
    (agents / 'web-researcher.md').write_text(AGENT)
    return build.Project(root)


class SkillAndAgentTests(unittest.TestCase):
    def outputs(self, name):
        with tempfile.TemporaryDirectory() as temp:
            project = skill_project(Path(temp))
            settings = {k: v for k, v in CONFIG['targets'][name].items() if k != 'rule_files'}
            return {o.path: o for o in TARGETS[name](settings).outputs(project)}

    def test_claude_skill_maps_neutral_keys(self):
        out = self.outputs('claude')
        text = out['claude/plugins/web-kit/skills/feature/SKILL.md'].content.decode()
        self.assertTrue(text.startswith('---\nname: feature\ndescription: "Do the thing."\nargument-hint: "[ticket]"\n'
                                        'disable-model-invocation: true\nmetadata:\n  verified: 2026-10-01\n---\n'))
        self.assertIn('# Feature: $ARGUMENTS', text)
        self.assertEqual(out['claude/plugins/web-kit/skills/feature/scripts/run.sh'].mode, 0o755)

    def test_codex_skill_is_flat_with_preamble_and_policy(self):
        out = self.outputs('codex')
        text = out['codex/skills/web-feature/SKILL.md'].content.decode()
        self.assertTrue(text.startswith('---\nname: web-feature\ndescription: "Do the thing."\nmetadata:\n'))
        self.assertIn('---\n\nRead the project AGENTS.md', text)
        self.assertIn('# Feature: the user request', text)
        self.assertIn('codex/skills/web-feature/agents/openai.yaml', out)

    def test_agents_render_per_target(self):
        claude = self.outputs('claude')['claude/plugins/web-kit/agents/web-researcher.md'].content.decode()
        self.assertIn('model: sonnet\neffort: medium\nmaxTurns: 15\nskills:\n  - web-kit:standards\ncolor: blue\n', claude)
        self.assertIn('Preloaded.', claude)
        codex = tomllib.loads(self.outputs('codex')['codex/agents/web-researcher.toml'].content.decode())
        self.assertEqual((codex['model'], codex['sandbox_mode']), ('gpt-6-sol', 'read-only'))
        self.assertTrue(codex['developer_instructions'].startswith('# Researcher\nRead it.\n'))
        self.assertIn('~/.codex/guidance/web files', codex['developer_instructions'])
        agy = self.outputs('antigravity')['antigravity/plugins/web-kit/agents/web-researcher.md'].content.decode()
        self.assertIn('model: flash\n', agy)
        self.assertIn('skills: [skills/web-standards]\n', agy)
        self.assertIn('the web-kit rules, which load with this plugin', agy)

    def test_unknown_skill_key_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            project = skill_project(Path(temp))
            path = Path(temp) / 'src/skills/web-kit/feature/SKILL.md'
            path.write_text(SKILL.replace('preamble: playbook', 'colour: red'))
            project = build.Project(Path(temp))
            with self.assertRaises(engine.RenderError):
                target('claude').outputs(project)


class RepositoryTests(unittest.TestCase):
    def test_sources_pass_the_lint(self):
        self.assertEqual(build.lint_sources(build.Project(), CONFIG.get('lint', {}).get('allow', [])), [])

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
