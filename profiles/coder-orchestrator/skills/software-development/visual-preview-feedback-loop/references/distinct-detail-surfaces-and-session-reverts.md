# Distinct detail surfaces and session-scoped reverts

## Surface disambiguation checklist

Before changing a UI described as “job detail” or similar:

1. Record the exact reported URL, including pathname and query string.
2. Trace route parsing to the mounted component.
3. Identify the exact JSX/content renderer for the reported field.
4. Inventory sibling surfaces displaying the same entity: full page, modal/inspector, drawer, timeline, conversation view.
5. State each surface’s purpose and invariants. Shared data does not imply shared UX.
6. Test and publicly verify the exact route and state from the report.

A URL link rendered correctly in a timeline does not prove it renders correctly in an agent-reply bubble. A modal fix does not prove or authorize a full-page redesign.

## Correcting work on the wrong surface

When feedback says the wrong surface was changed:

- Stop feature expansion.
- Audit the exact commits and file hunks produced during the session.
- Propose a narrow revert of session-owned deltas.
- Preserve both surfaces; do not merge or delete either unless requested.
- Preserve unrelated concurrent commits and untracked files.
- Use revert commits in shared history; avoid reset/history rewriting.
- Verify route parsing, component opening behavior, focused tests, full suite/build, and final diff.

## Approval semantics

If the current user message says “do not implement,” treat short approval-like feedback as plan feedback only and revise the artifact. Execute only when the user later explicitly authorizes implementation. Once execution is explicitly authorized, do not return another proposal-only response.
