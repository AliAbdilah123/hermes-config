# shadcn Card padding in legacy panel UIs

When migrating an existing React/Vite dashboard from custom `.panel` cards to shadcn `Card`, watch for padding/layout regressions rather than assuming the primitive swap is visually neutral.

## Pattern observed

Legacy panels often already have:
- `.panel-title` with fixed height, horizontal padding, and a border-bottom.
- content wrappers such as `.opportunity-list`, `.kanban-full`, `.script-controls`, `.generator-grid`, `.member-list`, etc. with their own padding/margins.
- CSS grid placement tied to legacy classes (for example multiple cards sharing `.opportunity-panel`).

shadcn `CardHeader`/`CardContent` add default `p-6` / `pt-0`. If the old title/content spacing remains, the result is bulky or uneven card padding. If two cards keep the same legacy grid-area class, they can overlap or place awkwardly.

## Fix approach

1. For shadcn-wrapped legacy sections, add a scoped class such as `shadcn-section-card`.
2. Reset direct `CardHeader`/`CardContent` padding in that scope, then re-apply one deliberate inset:
   - header wrapper: `padding: 0` so existing `.panel-title` owns title spacing.
   - content wrapper: compact app-specific padding such as `14px 16px 16px`.
3. Remove duplicate padding from nested lists inside the card (for example `.opportunity-list { padding: 0 }`).
4. For legacy panels not yet converted to `Card`, normalize direct child sections explicitly:
   - `.fullscreen-panel .kanban-full`
   - `.script-panel > .script-controls`, `.script-panel > .table-wrap`, `.script-panel > label`, `.script-panel > .script-actions`
   - `.generator-panel > .generator-grid`, `.generator-panel > .page-primary`
   - `.settings-panel > .inline-form`, `.settings-panel > .tenant-meta`
   - `.settings-members-panel > .member-list`
5. If a dashboard grid uses named areas, ensure newly split cards have unique classes and grid areas, e.g. `segment-panel` and `best-opportunity-panel` instead of both using `opportunity-panel`.
6. Rebuild, deploy, and verify the deployed CSS/JS includes the new padding classes and hashes. Use a screenshot after auth/navigation when possible to visually confirm no overlap and balanced spacing.

## Pitfalls

- Do not globally edit shadcn `CardHeader`/`CardContent` defaults unless the whole app wants that. Scope resets to migrated legacy panels.
- Do not rely only on build success for visual spacing changes. Use a browser/screenshot check on the public page.
- Comments may be stripped from production CSS; verify selectors/rules, not comment text.
