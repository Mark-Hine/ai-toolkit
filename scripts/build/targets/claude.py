"""Claude Code: plugins under claude/plugins, path-scoped rules linked from claude/home/rules."""
from engine import apply_tokens, parse_frontmatter, render, split_frontmatter
from targets.base import Output, Target, emit

RULE_PLATFORMS = ('android', 'ios', 'web')
# Neutral skill key to Claude key. `invocation` maps by value instead.
SKILL_KEY_NAMES = {'name': 'name', 'description': 'description', 'argument_hint': 'argument-hint',
                   'allowed_tools': 'allowed-tools', 'when_to_use': 'when_to_use', 'metadata': 'metadata'}
INVOCATION = {'manual': 'disable-model-invocation: true', 'reference': 'user-invocable: false'}


class Claude(Target):
    name = 'claude'

    def skill_ref(self, kit, skill):
        return f'{kit}:{skill}'

    def invoke(self, kit, skill):
        return f'/{kit}:{skill}'

    def skill_dir(self, kit, skill):
        return f'claude/plugins/{kit}/skills/{skill}'

    def agent_path(self, kit, agent):
        return f'claude/plugins/{kit}/agents/{agent}.md'

    def skill_dir_ref(self, kit, skill):
        # Plugin skills are not siblings on disk once installed, so name the plugin root.
        return f'${{CLAUDE_PLUGIN_ROOT}}/skills/{skill}'

    def owned_roots(self, project):
        roots = [f'claude/home/rules/{p}' for p in RULE_PLATFORMS]
        # Every plugin's skills and agents come from src/, so own them even when a kit has no sources left.
        return roots + self.plugin_roots(project, 'claude/plugins', ('skills', 'agents'))

    def outputs(self, project):
        out = []
        for rel, text in project.rules.items():
            platform, name = rel.split('/')[-2:]
            out.append(Output(f'claude/home/rules/{platform}/{name}', render(text, self, rel).encode()))
        return out + super().outputs(project)

    def skill_frontmatter(self, skill, entries, fields):
        lines = []
        for key, _ in entries:
            if key == 'invocation':
                lines.append(INVOCATION[fields[key].strip()])
            elif key in SKILL_KEY_NAMES:
                lines.append(emit(SKILL_KEY_NAMES[key], fields[key]))
        return lines

    def agent_output(self, agent):
        block, body = split_frontmatter(agent.text)
        fields, skills = self.agent_frontmatter(agent, parse_frontmatter(block))
        lines = [emit('name', fields['name']), emit('description', apply_tokens(fields['description'], self, agent.source))]
        for key, value in self.role_fields(agent).items():
            if key == 'skills':
                if value and skills:
                    lines.append('skills:' + ''.join(f'\n  - {self.skill_ref(*s)}' for s in skills))
                continue
            lines.append(f'{key}: {apply_tokens(str(value), self, agent.source)}')
        text = '---\n' + '\n'.join(lines) + '\n---\n' + self.agent_body(agent, body)
        return Output(self.agent_path(agent.kit, agent.name), text.encode())
