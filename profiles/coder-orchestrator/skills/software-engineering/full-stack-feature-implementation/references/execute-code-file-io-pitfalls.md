# execute_code File I/O Pitfalls

When doing mass string replacements or file rewrites via `execute_code`, NEVER use
the `hermes_tools` `read_file` / `write_file` for the read-modify-write cycle.
These tools are designed for agent-level use, not programmatic use inside
`execute_code`.

## Rule: Always use Python's native `open()` for file I/O in execute_code

```python
# ✅ CORRECT — use native Python open()
with open('/path/to/file.go', 'r') as f:
    content = f.read()
# ... modify content ...
with open('/path/to/file.go', 'w') as f:
    f.write(content)
```

```python
# ❌ WRONG — read_file embeds line numbers in content
from hermes_tools import read_file, write_file
content = read_file('/path/to/file.go', limit=2000)['content']
# content is now "1|package main\n2|\n3|import (\n..." — the "N|" prefix
# will be written back, corrupting the file
write_file('/path/to/file.go', content)
```

## Why this happens

`hermes_tools.read_file` returns content formatted for agent display:
```
1|package main
2|
3|import (
...
```

Writing this back embeds literal `1|`, `2|`, `3|` prefixes into the file,
making it invalid (Go: `expected 'package', found 1`).

## Secondary pitfall: substring replacement can break identifiers

When doing string-based find-and-replace for i18n/localization, short English
words like "approved" can match field names (`approved_count`), breaking code.
Always use the full context string (e.g., `"Proposal approved"` not `"approved"`)
and verify with a build after replacement.

If a partial match corrupts identifiers, restore from git and start fresh with
the file content read via native `open()`.
