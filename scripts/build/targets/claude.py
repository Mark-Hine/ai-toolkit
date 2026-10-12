"""Claude Code: plugins under claude/plugins, path-scoped rules linked from claude/home/rules."""
from engine import render
from targets.base import Output, Target

RULE_PLATFORMS = ('android', 'ios', 'web')


class Claude(Target):
    name = 'claude'

    def skill_ref(self, kit, skill):
        return f'{kit}:{skill}'

    def invoke(self, kit, skill):
        return f'/{kit}:{skill}'

    def owned_roots(self):
        return [f'claude/home/rules/{p}' for p in RULE_PLATFORMS]

    def outputs(self, project):
        out = []
        for rel, text in project.rules.items():
            platform, name = rel.split('/')[-2:]
            out.append(Output(f'claude/home/rules/{platform}/{name}', render(text, self, rel).encode()))
        return out
