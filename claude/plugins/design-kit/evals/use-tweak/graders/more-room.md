---
type: regex
target: { source: file, path: components.css }
pattern: '\.card\s*\{[^}]*padding:\s*var\(--space-(?:6|8|12)\)|\.features\s*\{[^}]*gap:\s*var\(--space-(?:6|8|12)\)'
---
