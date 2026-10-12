"""OpenAI Codex: skills under codex/skills, guidance files read on instruction from codex/home/guidance."""
from engine import render
from targets.base import Output, Target

RULE_PLATFORMS = ('android', 'ios', 'web')


class Codex(Target):
    name = 'codex'

    def skill_ref(self, kit, skill):
        return self.flat_name(kit, skill)

    def invoke(self, kit, skill):
        return f'${self.flat_name(kit, skill)}'

    def owned_roots(self):
        return [f'codex/home/guidance/{p}' for p in RULE_PLATFORMS]

    def outputs(self, project):
        out = []
        for rel, text in project.rules.items():
            platform, name = rel.split('/')[-2:]
            out.append(Output(f'codex/home/guidance/{platform}/{name}', render(text, self, rel).encode()))
        return out
