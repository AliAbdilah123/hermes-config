# Production-grade SaaS MVP: pages, real actions, and disabled states

Use this reference when a working dashboard still feels like a demo because navigation points to empty sections or buttons imply features that do not exist yet.

## Trigger

User says variants of:
- "Implement other pages and functionalities needed to make this production grade"
- "Disable / grey out navigation and buttons that don't contain anything yet"
- "This should not feel like a fake one-page demo"

## Pattern

1. **Inventory navigation first**
   - Classify every nav item and button as: implemented, implement-now, or future.
   - Do not leave dead links that navigate to blank sections.
   - Keep future features visible only if they help product positioning, but mark them `Soon` and disable interaction.

2. **Make implemented pages real**
   Minimum production-grade SaaS MVP pages for a BI/CRM dashboard:
   - Dashboard: KPI overview + highest-value actions.
   - Business database: searchable/filterable table, detail/select actions.
   - Opportunity engine: ranked opportunities, reasons, service recommendations.
   - CRM/prospects: pipeline/stages and add-lead flow.
   - Outreach scripts: copyable generated messages tied to selected business.
   - Website generator: select business, generate/deploy static preview.

3. **Grey out unfinished features clearly**
   - Use disabled `<button disabled>` for inactive actions, not clickable placeholders.
   - Apply visible grayscale/opacity styling and `cursor: not-allowed`.
   - Add concise labels like `Soon`, `Segera Hadir`, or a tooltip/message.
   - Typical future items to disable until implemented: AI chat, omnichannel inbox, training, billing, community, settings, upgrade, live city switcher.

4. **Restore real auth for production passes**
   - Visual-fidelity demos may temporarily skip login for screenshot comparison.
   - Production-grade passes should put login/session/CSRF back in front of data-mutating actions.
   - Store CSRF only as needed for the app session and handle expired-session/API errors with a visible banner.

5. **Back UI actions with actual APIs**
   - If a page has a primary action, it should call a real endpoint or be disabled.
   - Add API support + tests for missing high-value actions. Example: `POST /api/v1/leads` with CSRF protection so "Add to CRM" persists and appears in the pipeline.

6. **Verification checklist**
   - Run backend tests and frontend build.
   - Restart the supervised backend and redeploy built assets to nginx root.
   - Verify direct backend health, nginx app route, authenticated API flow, one mutating action, and a browser/headless screenshot.

## Pitfalls

- Do not keep a forced `authed = true` from visual demo work when moving to production hardening.
- Do not let inactive nav items use `<a href="#">`; this looks broken. Use disabled buttons.
- Do not claim production-grade if primary routes are just a dashboard with different headings.
- If public-IP curl times out from the same host, report hairpin/NAT caveat only after localhost/Tailscale/nginx checks pass.
