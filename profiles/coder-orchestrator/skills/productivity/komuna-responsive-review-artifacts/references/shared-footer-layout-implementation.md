# Shared footer layout implementation note

Session learning from the Komuna footer design/implementation flow.

## User workflow signal

When the user approves a static design but asks for a small design edit in the same sentence as implementation (for example: “remove the Explore navigations, after that implement it”), treat the edit as part of the approved scope and implement the edited version. Do not re-open approval unless the edit changes the core layout/IA materially.

## Footer-specific Komuna pattern

- The public Discovery page already rendered `components/layout/Footer`; the old component was only a single copyright line.
- Dashboard pages are wrapped by `components/dashboard/DashboardShell.tsx`.
- `DashboardShell.css` hides child page headers/footers inside `.dashboard-content`:
  - `.dashboard-content > header:first-child, .dashboard-content > footer:last-child { display: none !important; }`
- Therefore the dashboard footer must be rendered by `DashboardShell` **outside** `.dashboard-content`, not by individual dashboard pages.
- Use one shared `Footer` component with variants, e.g. `variant="public" | "dashboard"`, to keep public and dashboard footers consistent without duplicating markup.
- For this approved footer design, omit the “Explore” navigation group. Keep member/support/legal/copyright/trust-note content instead.

## Testing/verification pattern

- Add a Discovery/page-level test asserting the footer copyright appears and “Explore” does not.
- Add a DashboardShell-level test asserting the compact dashboard footer appears and contains the workspace trust note.
- If broader route-guard/sidebar tests in the same file are already failing for unrelated routing/auth reasons, report that separately; still run the narrow footer assertions and `npm run build`.
- Verify the built CSS/asset was deployed by grepping the deployed local asset for the new footer class before final public-link reporting.
