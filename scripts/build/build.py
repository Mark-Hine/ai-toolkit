#!/usr/bin/env python3
"""Generate the Claude Code, Codex and Antigravity layers from the agent-neutral sources.

Sources live under src/ (templates) and shared/ (files used as they are). Each target adapter in
scripts/build/targets/ decides where its files go and how they are worded, with settings from
scripts/build/agents.toml. Generated files are committed. Never edit them, edit the source and rerun.

  python3 scripts/build/build.py           write every output
  python3 scripts/build/build.py --check   exit 1 when an output is stale, missing or orphaned
Standard library only, Python 3.11 or later.
"""
import argparse
import os
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import engine  # noqa: E402
from targets import TARGETS  # noqa: E402
from targets.base import Output  # noqa: E402

ROOT = HERE.parents[1]
IGNORED_FILES = {'.DS_Store'}
CONFIG = HERE / 'agents.toml'


@dataclass
class Skill:
    kit: str
    name: str
    source: str
    files: dict = field(default_factory=dict)  # path inside the skill -> (bytes, mode)


@dataclass
class Agent:
    kit: str
    name: str
    role: str
    source: str
    text: str


class Project:
    """Read access to the sources, relative to the repo root."""

    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.rules = {self.rel(p): p.read_text() for p in sorted((self.root / 'src/rules').glob('*/*.md'))
                      if p.parent.name != 'delegation'}
        self.skills = [self.load_skill(d) for d in sorted((self.root / 'src/skills').glob('*/*/')) if d.is_dir()]
        self.agents = [self.load_agent(p) for p in sorted((self.root / 'src/agents').glob('*/*.md'))]
        self.agent_kits = sorted({a.kit for a in self.agents})
        self.skill_kits = sorted({s.kit for s in self.skills})

    def load_skill(self, directory):
        skill = Skill(directory.parent.name, directory.name, self.rel(directory))
        for path in sorted(directory.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.name not in IGNORED_FILES:
                skill.files[path.relative_to(directory).as_posix()] = (path.read_bytes(), path.stat().st_mode & 0o777)
        if 'SKILL.md' not in skill.files:
            raise ValueError(f'{skill.source} has no SKILL.md')
        return skill

    def load_agent(self, path):
        text = path.read_text()
        block, _ = engine.split_frontmatter(text)
        fields = dict(engine.parse_frontmatter(block))
        name = engine.scalar(fields.get('name', ''))
        if name != path.stem:
            raise ValueError(f'{self.rel(path)}: name must be {path.stem}')
        return Agent(path.parent.name, name, engine.scalar(fields.get('role', '')), self.rel(path), text)

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def read(self, rel):
        return (self.root / rel).read_text()

    def sources(self):
        """Every template under src/, for the lint."""
        return sorted(p for p in (self.root / 'src').rglob('*.md'))


def load_targets(config):
    targets = [TARGETS[name](settings) for name, settings in config['targets'].items()]
    # The values a `key=value` block condition may name, so a misspelling fails instead of rendering nothing.
    known = {'target': set(config['targets'])}
    for target in targets:
        for key, value in target.capabilities.items():
            known.setdefault(key, set()).add(str(value))
    for target in targets:
        target.known_values = known
    return targets


def copy_outputs(project, config):
    out = []
    for spec in config.get('copies', []):
        source = project.root / spec['src']
        data = source.read_bytes()
        mode = source.stat().st_mode & 0o777
        for name in TARGETS:
            for dest in spec.get(name, []):
                out.append(Output(dest, data, mode))
    return out


def all_outputs(project, config):
    outputs = copy_outputs(project, config)
    for target in load_targets(config):
        outputs += target.outputs(project)
    seen = {}
    for output in outputs:
        if output.path in seen:
            raise ValueError(f'{output.path} is produced twice')
        seen[output.path] = output
    return outputs


def owned_roots(project, config):
    roots = []
    for target in load_targets(config):
        roots += target.owned_roots(project)
    return roots


def lint_sources(project, allow=()):
    """Literal agent wording outside blocks. `allow` entries are a source path, or `path:text` for lines
    containing that text, for sources that name every agent on purpose."""
    problems = []
    for path in project.sources():
        rel = project.rel(path)
        if rel in allow or any(entry.endswith('/') and rel.startswith(entry) for entry in allow):
            continue
        texts = [entry.split(':', 1)[1] for entry in allow if entry.startswith(rel + ':')]
        for number, line in engine.lint(path.read_text(), rel):
            if not any(text in line for text in texts):
                problems.append(f'{rel}:{number}: literal agent wording outside a block: {line}')
    return problems


def orphans(project, config, outputs):
    produced = {o.path for o in outputs}
    found = set()
    for root in owned_roots(project, config):
        base = project.root / root
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if (path.is_file() and '__pycache__' not in path.parts and path.name not in IGNORED_FILES
                    and project.rel(path) not in produced):
                found.add(project.rel(path))
    return sorted(found)


def stale(project, output):
    path = project.root / output.path
    if not path.is_file() or path.read_bytes() != output.content:
        return True
    return output.mode is not None and (path.stat().st_mode & 0o777) != output.mode


def write(project, output):
    path = project.root / output.path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output.content)
    if output.mode is not None:
        os.chmod(path, output.mode)


def run(check, root=ROOT, config_path=CONFIG):
    project = Project(root)
    config = tomllib.loads(Path(config_path).read_text())
    errors = lint_sources(project, config.get('lint', {}).get('allow', []))
    if errors:
        for error in errors:
            print(f'::error::{error}')
        return 1
    outputs = all_outputs(project, config)
    changed = [o for o in outputs if stale(project, o)]
    extra = orphans(project, config, outputs)
    if check:
        for output in changed:
            print(f'::error::{output.path} is stale or missing, run python3 scripts/build/build.py')
        for rel in extra:
            print(f'::error::{rel} is not produced by the build, delete it or add a source')
        if changed or extra:
            return 1
        print(f'build: {len(outputs)} generated files are current')
        return 0
    for output in changed:
        write(project, output)
        print(f'wrote {output.path}')
    for rel in extra:
        (project.root / rel).unlink()
        print(f'removed {rel}')
    print(f'build: {len(outputs)} generated files, {len(changed)} written, {len(extra)} removed')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='report stale outputs instead of writing them')
    args = parser.parse_args(argv)
    return run(args.check)


if __name__ == '__main__':
    sys.exit(main())
