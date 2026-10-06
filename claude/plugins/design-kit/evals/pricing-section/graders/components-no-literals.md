---
type: regex
target: { source: file, path: components.css }
pattern: '\b\d+(?:\.\d+)?(?:px|rem|em)\b|(?<![&\w])#[0-9a-fA-F]{3,8}\b'
match: not_contains
---
