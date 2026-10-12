"""Install helpers shared by the Codex and Antigravity installers. Standard library only, Python 3.11.

Both installers merge a managed block into the agent's AGENTS.md, link the shared guidance, create
machine.md once, and back up anything they replace under <config home>/backups/ai-toolkit-<timestamp>/
with a manifest.json that records each original location.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import tempfile

REPO = Path(__file__).resolve().parents[1]
MARKERS = ('<!-- ai-toolkit:start -->', '<!-- ai-toolkit:end -->')
# Installed name under <config home>/guidance/ -> source under shared/guidance/.
SHARED_GUIDANCE = {
    'common.md': 'common.md',
    'kotlin.md': 'kotlin.md',
    'design-standards.md': 'design-standards.md',
    'design-assets.md': 'design-assets.md',
    'writing-style.md': 'writing-style-brief.md',
}


def merged_guidance(existing, guidance):
    """Replace or append the managed ai-toolkit instruction block."""
    start, end = MARKERS
    block = start + '\n' + guidance.rstrip() + '\n' + end
    if start in existing or end in existing:
        if existing.count(start) != 1 or existing.count(end) != 1 or existing.index(start) > existing.index(end):
            raise ValueError('Malformed ai-toolkit instruction markers')
        return existing[:existing.index(start)] + block + existing[existing.index(end) + len(end):]
    return (existing.rstrip() + '\n\n' if existing.strip() else '') + block + '\n'


class Installer:
    """File operations with dry-run, atomic writes and backups. Subclasses implement run()."""

    def __init__(self, config_home, dry_run=False):
        self.config_home = Path(config_home)
        self.dry_run = dry_run
        self.stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        self.backup_root = self.config_home / 'backups' / ('ai-toolkit-' + self.stamp)
        self.backups = []
        self.notes = []

    def say(self, verb, path):
        print(('Would ' + verb.lower() if self.dry_run else verb) + ' ' + str(path))

    def backup(self, path):
        if not os.path.lexists(path):
            return
        destination = self.backup_root / str(len(self.backups)) / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            destination.symlink_to(os.readlink(path), target_is_directory=path.is_dir())
        elif path.is_dir():
            shutil.copytree(path, destination)
        else:
            shutil.copy2(path, destination)
        self.backups.append({'original': str(path), 'backup': str(destination)})
        (self.backup_root / 'manifest.json').write_text(json.dumps(self.backups, indent=2) + '\n')

    def write(self, path, content, mode=0o600):
        path = Path(path)
        if path.is_file() and not path.is_symlink() and path.read_text() == content:
            return
        self.say('Write', path)
        if self.dry_run:
            return
        self.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
            stream.write(content)
            temp = Path(stream.name)
        temp.chmod(mode)
        os.replace(temp, path)

    def link(self, source, target):
        source, target = Path(source), Path(target)
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        self.say('Link', target)
        if self.dry_run:
            return
        self.backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_dir() and not target.is_symlink():
            # Preserve the complete displaced directory in the backup before replacing it.
            target.rename(self.backup_root / ('displaced-' + target.name))
        elif os.path.lexists(target):
            target.unlink()
        target.symlink_to(source, target_is_directory=source.is_dir())

    def remove(self, path, reason):
        path = Path(path)
        if not os.path.lexists(path):
            return
        self.say('Remove', path)
        self.notes.append(f'removed {path} ({reason})')
        if self.dry_run:
            return
        self.backup(path)
        path.unlink()

    def merge_instructions(self, agents_file, guidance_source):
        """The merged AGENTS.md text. Computed before any write, so malformed markers change nothing."""
        existing = agents_file.read_text() if agents_file.exists() else ''
        return merged_guidance(existing, Path(guidance_source).read_text())

    def create_machine_file(self, example):
        machine = self.config_home / 'machine.md'
        if not machine.exists():
            self.write(machine, Path(example).read_text())

    def link_shared_guidance(self):
        for installed, source in SHARED_GUIDANCE.items():
            self.link(REPO / 'shared/guidance' / source, self.config_home / 'guidance' / installed)

    def report(self):
        if self.backups:
            print('Backups: ' + str(self.backup_root))
        for note in self.notes:
            print('Note: ' + note)
