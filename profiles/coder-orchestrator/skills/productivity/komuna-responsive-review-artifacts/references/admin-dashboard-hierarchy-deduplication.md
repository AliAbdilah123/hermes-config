# Admin Dashboard Hierarchy Deduplication

Use this pattern when a dashboard screenshot shows repeated workspace/program identity and nested card-within-card framing.

## Diagnose by information level

Map each label and container to one level before proposing changes:

1. **Global topbar** — brand, role, global controls. Do not repeat the active program name when the page already has a program header.
2. **Program header** — the single canonical program name, visibility, timezone, and program-level navigation.
3. **Feature page** — feature title only, such as `Sessions`.
4. **Feature controls/content** — tabs, counts, product groups, rows, and actions.

A program name appearing in the topbar, program header, and feature header is hierarchy duplication, not useful context.

## Flattening rule

When the feature page is already inside the dashboard content region, remove decorative outer shells that only add another border/background/padding layer. Keep semantic and interactive boundaries:

- Keep the page heading and view tabs.
- Keep product-group boundaries and session-row dividers.
- Remove breadcrumb/eyebrow copy that merely restates role + feature.
- Remove guidance text when the controls and labels already make the workflow clear.
- Preserve live status/error messages, tab semantics, and all behavior.

## Review artifact requirements

Show the full dashboard context so reviewers can see where the one remaining program name lives. Include three explicit change callouts:

- topbar identity removal,
- feature heading simplification,
- redundant container removal.

State implementation scope as markup/CSS-only when behavior is intentionally unchanged. On mobile, flattening should remain intact rather than replacing the removed desktop shell with another stacked card.

## Acceptance checks after approval

- Program name appears once in the dashboard hierarchy.
- Feature heading is the feature name only.
- Removed breadcrumb and descriptive copy are absent.
- No redundant outer feature card remains.
- Tabs, product groups, session actions, accessibility roles, and status messaging still work.
