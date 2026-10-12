"""The adapter interface every target implements. A new agent subclasses Target in its own module."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Output:
    """One generated file. `mode` is set for verbatim copies, which keep the source file's mode."""
    path: str
    content: bytes
    mode: int | None = None


class Target:
    name = ''

    def __init__(self, config):
        self.config = config
        self.tokens = config.get('tokens', {})
        self.capabilities = config.get('capabilities', {})
        self.models = config.get('models', {})

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

    # Layout.
    def owned_roots(self):
        """Directories whose every file is build output for this target."""
        return []

    def outputs(self, project):
        """Every generated file for this target except verbatim copies, as Output objects."""
        return []
