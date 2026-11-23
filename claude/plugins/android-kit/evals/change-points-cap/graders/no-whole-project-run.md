---
type: regex
target: { source: file, path: .gradle-calls.log }
pattern: '^(?!.*--tests)(?!.*:\w+:test)(?!.*:\w+:check).*\b(test\w*|check)\b'
flags: m
match: not_contains
---
