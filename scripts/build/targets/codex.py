"""OpenAI Codex: skills under codex/skills, agents as TOML under codex/agents, guidance under codex/home/guidance.

Codex agents carry their instructions in a TOML string. The installer appends the per-agent guard hooks at
install time, so the generated file holds only the agent definition.
"""
import json
import tomllib

from engine import RenderError, apply_tokens, parse_frontmatter, render, scalar, split_frontmatter
from targets.base import Output, Target

RULE_PLATFORMS = ('android', 'ios', 'web')
MANUAL_POLICY = 'policy:\n  allow_implicit_invocation: false\n'


class Codex(Target):
    name = 'codex'

    def skill_ref(self, kit, skill):
        return self.flat_name(kit, skill)

    def invoke(self, kit, skill):
        return f'${self.flat_name(kit, skill)}'

    def skill_dir(self, kit, skill):
        return f'codex/skills/{self.flat_name(kit, skill)}'

    def agent_path(self, kit, agent):
        return f'codex/agents/{agent}.toml'

    def owned_roots(self, project):
        return [f'codex/home/guidance/{p}' for p in RULE_PLATFORMS] + super().owned_roots(project)

    def outputs(self, project):
        out = []
        for rel, text in project.rules.items():
            platform, name = rel.split('/')[-2:]
            out.append(Output(f'codex/home/guidance/{platform}/{name}', render(text, self, rel).encode()))
        return out + super().outputs(project)

    def skill_frontmatter(self, skill, entries, fields):
        return self.flat_skill_frontmatter(skill, entries, fields)

    def skill_extras(self, skill, base):
        block, _ = split_frontmatter(skill.files['SKILL.md'][0].decode())
        fields = dict(parse_frontmatter(block))
        if fields.get('invocation', '').strip() == 'manual':
            return [Output(f'{base}/agents/openai.yaml', MANUAL_POLICY.encode())]
        return []

    def agent_output(self, agent):
        block, body = split_frontmatter(agent.text)
        fields, _ = self.agent_frontmatter(agent, parse_frontmatter(block))
        description = scalar(apply_tokens(fields['description'], self, agent.source))
        lines = [f'name = {json.dumps(scalar(fields["name"]))}',
                 f'description = {json.dumps(description, ensure_ascii=False)}']
        for key, value in self.role_fields(agent).items():
            value = apply_tokens(value, self, agent.source) if isinstance(value, str) else value
            lines.append(f'{key} = {json.dumps(value, ensure_ascii=False)}')
        instructions = self.agent_body(agent, body).lstrip('\n')
        lines.append(f'developer_instructions = {json.dumps(instructions, ensure_ascii=False)}')
        text = '\n'.join(lines) + '\n'
        try:
            tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise RenderError(f'{agent.source}: generated Codex TOML does not parse: {error}') from None
        return Output(self.agent_path(agent.kit, agent.name), text.encode())
