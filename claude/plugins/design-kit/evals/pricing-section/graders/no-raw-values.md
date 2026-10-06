---
type: regex
target: { source: file, path: index.html }
pattern: '(?<![&\w])#[0-9a-fA-F]{3,8}\b|font-family|fonts\.(?:googleapis|gstatic)\.com'
flags: i
match: not_contains
---
