"""The adapter interface every target implements. A new agent subclasses Target in its own module."""
import json
from dataclasses import dataclass

from engine import RenderError, apply_tokens, parse_frontmatter, render, scalar, split_frontmatter, string_list

# Neutral skill frontmatter keys. Each target maps them to its own keys or drops them.
SKILL_KEYS = {'name', 'description', 'description_short', 'argument_hint', 'invocation', 'allowed_tools',
              'when_to_use', 'preamble', 'metadata'}
AGENT_KEYS = {'name', 'description', 'role', 'skills'}
PLATFORM_TITLES = {'android': 'Android', 'ios': 'iOS', 'web': 'web'}


@dataclass(frozen=True)
class Output:
    """One generated file. `mode` is set for verbatim copies, which keep the source file's mode."""
    path: str
    content: bytes
    mode: int | None = None


def emit(key, raw):
    """A frontmatter line, keeping a raw value that starts on the next line (a block or a nested map)."""
    return f'{key}:{raw}' if raw.startswith('\n') or not raw else f'{key}: {raw}'


class Target:
    name = ''

    def __init__(self, config):
        self.config = config
        self.tokens = config.get('tokens', {})
        self.capabilities = config.get('capabilities', {})
        self.models = config.get('models', {})
        self.file_names = config.get('file_names', {})
        self.preambles = config.get('preambles', {})
        self.roles = config.get('roles', {})
        self.agent_overrides = config.get('agents', {})
        self.formats = config.get('formats', {})

    # Template hooks used by engine.render.
    def flag(self, name):
        if name not in self.capabilities:
            raise KeyError(name)
        return bool(self.capabilities[name])

    def value(self, key):
        if key == 'target':
            return self.name
        if key not in self.capabilities:
            raise KeyError(key)
        return self.capabilities[key]

    def token(self, name, arg):
        if name == 'model':
            return self.models[arg]
        if name == 'skill':
            return self.skill_ref(*self.kit_skill(arg))
        if name == 'invoke':
            return self.invoke(*self.kit_skill(arg))
        if name == 'skill_named':
            return self.formats[name].format(id=self.skill_ref(*self.kit_skill(arg)))
        if name == 'sibling':
            return '../' + self.skill_dir(*self.kit_skill(arg)).rsplit('/', 1)[1]
        if name == 'skill_dir':
            return self.skill_dir_ref(*self.kit_skill(arg))
        if name in self.formats:
            if not arg:
                raise KeyError(name)
            platform, _, rest = arg.partition('/')
            return self.formats[name].format(arg=arg, platform=platform, name=rest,
                                             title=PLATFORM_TITLES.get(platform, platform))
        if arg is not None:
            raise KeyError(name)
        return self.tokens[name]

    @staticmethod
    def kit_skill(arg):
        if not arg or '/' not in arg:
            raise KeyError(arg)
        kit, skill = arg.split('/', 1)
        return kit, skill

    # Naming. Codex and Antigravity flatten kit and skill into one name.
    @staticmethod
    def flat_name(kit, skill):
        if skill == kit:
            return skill
        return f'{kit.removesuffix("-kit")}-{skill}'

    def skill_ref(self, kit, skill):
        raise NotImplementedError

    def invoke(self, kit, skill):
        raise NotImplementedError

    def skill_dir(self, kit, skill):
        raise NotImplementedError

    def agent_path(self, kit, agent):
        raise NotImplementedError

    def skill_dir_ref(self, kit, skill):
        """How one skill's text points at another skill's folder."""
        return '../' + self.skill_dir(kit, skill).rsplit('/', 1)[1]

    def file_name(self, rel):
        head, _, base = rel.rpartition('/')
        base = self.file_names.get(base, base)
        return f'{head}/{base}' if head else base

    # Layout.
    def owned_roots(self, project):
        """Directories whose every file is build output for this target."""
        return [self.skill_dir(s.kit, s.name) for s in project.skills]

    def outputs(self, project):
        """Every generated file for this target except the shared verbatim copies."""
        out = []
        for skill in project.skills:
            out += self.skill_outputs(skill)
        for agent in project.agents:
            out.append(self.agent_output(agent))
        return out

    # Skills.
    def skill_outputs(self, skill):
        base = self.skill_dir(skill.kit, skill.name)
        out = []
        for rel, (data, mode) in skill.files.items():
            source = f'{skill.source}/{rel}'
            dest = f'{base}/{self.file_name(rel)}'
            if rel == 'SKILL.md':
                out.append(Output(dest, self.render_skill(skill, data.decode(), source).encode()))
            elif rel.endswith('.md'):
                out.append(Output(dest, render(data.decode(), self, source).encode()))
            else:
                out.append(Output(dest, data, mode))
        return out + self.skill_extras(skill, base)

    def skill_extras(self, skill, base):
        return []

    def render_skill(self, skill, text, source):
        block, body = split_frontmatter(text)
        entries = parse_frontmatter(block)
        unknown = {key for key, _ in entries} - SKILL_KEYS
        if unknown:
            raise RenderError(f'{source}: unknown skill frontmatter keys {sorted(unknown)}')
        fields = {key: apply_tokens(raw, self, source) for key, raw in entries}
        if scalar(fields.get('name', '')) != skill.name:
            raise RenderError(f'{source}: name must be {skill.name}')
        lines = self.skill_frontmatter(skill, entries, fields)
        preamble = self.preambles.get(fields['preamble']) if 'preamble' in fields else None
        head = '---\n' + '\n'.join(lines) + '\n---\n'
        if preamble:
            head += '\n' + preamble + '\n'
        return head + render(body, self, source)

    def skill_frontmatter(self, skill, entries, fields):
        raise NotImplementedError

    def flat_skill_frontmatter(self, skill, entries, fields):
        """Codex and Antigravity read only a flattened name, a quoted description and metadata."""
        if 'description_short' in fields:
            description = scalar(fields['description_short'])
        else:
            description = scalar(fields['description'])
            if 'when_to_use' in fields:
                description += ' - ' + scalar(fields['when_to_use'])
        lines = [f'name: {self.flat_name(skill.kit, skill.name)}',
                 f'description: {json.dumps(description, ensure_ascii=False)}']
        if 'metadata' in fields:
            lines.append(emit('metadata', fields['metadata']))
        return lines

    # Agents.
    def role_fields(self, agent):
        fields = dict(self.roles[agent.role])
        fields.update(self.agent_overrides.get(agent.name, {}))
        return fields

    def agent_frontmatter(self, agent, entries):
        unknown = {key for key, _ in entries} - AGENT_KEYS
        if unknown:
            raise RenderError(f'{agent.source}: unknown agent frontmatter keys {sorted(unknown)}')
        fields = dict(entries)
        skills = [self.kit_skill(s) for s in string_list(fields.get('skills', '[]'))]
        return fields, skills

    def agent_body(self, agent, body):
        """The rendered instructions, plus the target's closing paragraph when it has one."""
        text = render(body, self, agent.source)
        footer = self.formats.get('agent_footer')
        # The footer names the platform's guidance folder, which only the platform kits have.
        if footer and agent.kit.removesuffix('-kit') in PLATFORM_TITLES:
            text = text.rstrip('\n') + '\n\n' + footer.format(platform=agent.kit.removesuffix('-kit')) + '\n'
        return text

    def agent_output(self, agent):
        raise NotImplementedError
