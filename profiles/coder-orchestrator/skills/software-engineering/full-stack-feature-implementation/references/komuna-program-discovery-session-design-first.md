# Komuna program discovery/session changes: design-first workflow

Use when the user asks for changes around Komuna public program pages, upcoming sessions, discovery filters/location, program slugs, or program categories — especially when they ask to see the design before implementation.

## Workflow

1. **Do not implement first.** Inspect the relevant files and publish a styled HTML review artifact under `/prd/<slug>.html` before code changes.
2. **Split investigation with subagents when the request spans areas.** Good scopes:
   - Program detail/session UX (`ProgramDetailPage`, `HeroRightSessions`, `SessionCardCompact`, `AllSessionsPage`, i18n/tests).
   - API/data model (`programs` schema, migrations, DTOs, services/controllers, seeds, slugs/categories).
   - Discovery/location UX (`DiscoveryPage`, `CategorySidebar`, `filterPrograms`, geolocation behavior/tests).
3. **Make the proposal concrete.** Include visual states, exact file map, validation commands, and clarifying questions. Publish and verify public HTML contains newly requested phrases before asking for approval.
4. **Wait for approval/answers** when the user explicitly requested proposal before implementation.

## Komuna file map observed

- Upcoming sessions hero:
  - `apps/web/src/pages/ProgramDetailPage.tsx` fetches upcoming sessions and passes them to `HeroRightSessions`.
  - `apps/web/src/pages/program-detail/HeroRightSessions.tsx` slices visible sessions and renders `SessionCardCompact`.
  - `apps/web/src/pages/all-sessions/SessionCardCompact.tsx` owns compact card time/details styling.
  - `apps/web/src/pages/AllSessionsPage.tsx` owns full sessions page header/title/description.
  - i18n labels live in `apps/web/src/i18n/en.json` and `id.json`.
- Program slugs/categories:
  - Current routes/API are UUID/id-based (`/programs/:id`) unless changed.
  - Program schema/DTO/service/controller/seed files are under `apps/api/src/db/schema.ts`, `apps/api/src/dto/programs.ts`, `apps/api/src/services/programs.ts`, `apps/api/src/controllers/programs.ts`, and seeds.
  - Frontend API mirror is `apps/web/src/lib/api-types.ts`; cards route in `apps/web/src/components/discovery/ProgramCard.tsx`.
- Discovery location:
  - `apps/web/src/pages/DiscoveryPage.tsx` owns `locationFilter` and list fetching/filtering.
  - `apps/web/src/components/discovery/CategorySidebar.tsx` owns location filter UI.
  - `apps/web/src/lib/filterPrograms.ts` contains current placeholder location logic.

## Design defaults

- Session urgency: bigger schedule time; if starts in <1 hour, warm yellow glow + countdown; strongest emphasis on the first upcoming hero session. Keep glow subtle, not harsh neon.
- Rename public sessions copy to **Upcoming sessions** and remove unnecessary description copy when requested.
- Program slugs: generate from program name, expose as public link, and keep UUID fallback so existing links do not break.
- Categories: prefer multi-category data model if discovery should reflect what programs offer; single-select UI can ship first if simpler.
- GPS discovery: use native `navigator.geolocation`; do not add dependencies. If permission denied/unsupported, keep all programs visible. Do not claim “Closest first” unless real distance sorting exists.

## Verification

- Publish proposal via the PRD route and verify HTTP 200 plus exact phrases.
- After implementation: run relevant web tests/build and API tests, then verify the deployed public Komuna URL and fresh assets/bundle markers.
