# Komuna JSON-state seed updates: additive, not destructive

Use when the user asks to add/seed more Komuna programs or demo data in the local Go + SQLite JSON-state deployment.

## Lesson

If the user asks for “more data” or “programs outside X”, treat it as **additive** unless they explicitly say to remove existing locations. Preserve existing regional seed datasets (e.g. East Kalimantan/Kaltim programs) and append new global examples.

## Workflow

1. Inspect the active seed/data source:
   - Local deployed API usually serves from `/home/ubuntu/projects/komuna/sqlite.db` JSON `app_state`, not from the old Hono/Drizzle seeder.
   - Go seed lives in `api/v1/main.go` and only initializes `app_state` on a fresh DB (`INSERT OR IGNORE`).
   - Old detailed Kaltim source can live in `apps/api/src/db/seed-kaltim.ts`; use it as reference for names/locations if Go seed lost them.
2. Preserve, then append:
   - Keep existing Kaltim/East Kalimantan program names/locations.
   - Add new outside-region/global programs after the preserved set.
   - Keep required DTO-facing fields populated: `ID`, `Name`, `Description`, `Visibility`, `Timezone`, `Location`, `Category`, `Categories`, `ImageTone`, `ImageLabel`, `MemberCount`, `Rating`, `SessionsPerWeek`, and any current fields like `Featured` if present.
3. Build-time verification:
   - `cd api/v1 && gofmt -w main.go && go test ./... && go build -o ../server .`
4. Live-data update:
   - Rebuilding/restarting does **not** apply new `seed()` contents if `sqlite.db` already has `app_state`.
   - Do **not** delete `sqlite.db` unless the user explicitly approves losing runtime state.
   - Merge missing programs into the existing JSON `app_state` by ID, then restart the service.
5. Public verification:
   - Curl the public API and verify total count plus preserved location counts, e.g. `east_kalimantan == 14` and new global programs present.

## Pitfall

Do not interpret “make new programs outside Kalimantan Timur” as “remove Kalimantan Timur.” The user correction in this session was explicit: “I didn’t ask to remove it.” Future seed updates must be additive unless removal is requested.
