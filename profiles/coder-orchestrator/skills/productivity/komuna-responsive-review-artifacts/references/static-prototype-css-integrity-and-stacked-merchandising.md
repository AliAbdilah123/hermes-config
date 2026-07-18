# Static prototype CSS integrity and stacked merchandising

## Product correction

For Komuna Discovery/landing redesign prototypes:

- When the user rejects filtering pills/tabs, render each category as a real, vertically stacked section—not a control that swaps one shared grid.
- Keep the approved centered max-width shell consistently across hero and all program sections.
- Populate implementation sections from database/API semantics. Typical factual groupings are:
  - **Most Popular:** participation/member count, then rating.
  - **New Programs:** creation timestamp descending.
  - **Open to Join:** actual public or approval-based joining policy.
- Do not imply Free Trial unless the data model/API exposes a truthful free-trial signal.
- A static prototype may use representative records, but label them clearly and specify database-backed implementation behavior.

## Artifact corruption failure mode

Hermes `read_file` output is display-oriented and prefixes lines with `LINE_NUM|`. It may also visually truncate long lines. Never take the displayed `content` from a prior read and write it back wholesale as the artifact source. Doing so can persist prefixes such as `1|`, inject truncation markers, and break CSS parsing midway through `<style>`.

The characteristic symptom is partial styling: early global/header/hero rules still apply, while later card/grid rules vanish and program content collapses into plain text. A stray `1|` at the page’s top-left is a strong indicator.

## Safe update pattern

1. Use targeted `patch` replacements against the source file whenever possible.
2. If a full rewrite is necessary, write from an independently held complete source string—not `read_file`’s rendered output.
3. Keep CSS readable enough that missing tails and malformed boundaries are detectable.
4. After publishing, fetch the public cache-busted HTML and assert:
   - Starts with `<!doctype` and has no `\nN|` line prefixes.
   - Contains no truncation marker such as `... [truncated]`.
   - Contains critical late stylesheet rules (for example grid and card selectors).
   - Ends with closing HTML markup and returns HTTP 200.
5. Perform visual verification. Confirm cards render as cards/grids, status and category labels do not concatenate, links use intended styling, and the page does not leave unexplained empty width.

## Minimal deterministic probe

```python
from pathlib import Path

s = Path("prototype.html").read_text()
checks = {
    "doctype": s.startswith("<!doctype"),
    "no_line_prefixes": not any(f"\n{i}|" in s for i in range(1, 200)),
    "no_truncation": "... [truncated]" not in s,
    "grid_css": ".grid" in s and "display:grid" in s,
    "card_css": ".card" in s,
    "closed": s.rstrip().endswith("</html>"),
}
assert all(checks.values()), checks
```

This source probe complements—not replaces—browser/screenshot QA.