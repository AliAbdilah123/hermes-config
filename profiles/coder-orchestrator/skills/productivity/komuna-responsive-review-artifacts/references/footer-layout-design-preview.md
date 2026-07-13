# Footer layout design preview pattern

Use when the user asks to add or change a Komuna footer but wants design approval before implementation.

## Pattern captured

- Treat the request as a static design proposal, not an implementation task.
- Publish a public review page under `/prd/<slug>.html` before touching live app behavior.
- Show both variants when the requirement spans public pages and dashboard pages:
  - **Public / Discovery-style footer:** roomy editorial footer, brand sentence, link groups, copyright/legal row.
  - **Dashboard footer:** compact shell-level footer below dashboard content, same legal/support links, workspace trust/context note.
- Make the implementation gate explicit: approval of the preview is not permission to deploy unless the user explicitly says to implement.

## Useful content architecture

- Brand: Komuna + short marketplace/community sentence.
- Explore/member/company link columns for public pages.
- Copyright row: `© 2026 Komuna. All rights reserved.`
- Dashboard variant: compact copyright + trust note such as “Workspace data stays scoped to your active program.”

## Implementation notes after approval

- Prefer extending `apps/web/src/components/layout/Footer.tsx` with a variant prop over creating one-off footers.
- Render the dashboard variant once in `apps/web/src/components/dashboard/DashboardShell.tsx`, below dashboard content.
- Add/update i18n keys in `apps/web/src/i18n/en.json` and `id.json`.
- Verify public pages and dashboard pages at mobile/tablet/desktop widths.