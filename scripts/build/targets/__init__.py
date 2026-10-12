"""Registry of build targets. Add a new agent's adapter here and give it a [targets.<name>] table."""
from targets.antigravity import Antigravity
from targets.claude import Claude
from targets.codex import Codex

TARGETS = {cls.name: cls for cls in (Claude, Codex, Antigravity)}
