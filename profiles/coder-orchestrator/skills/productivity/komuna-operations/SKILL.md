---
name: komuna-operations
description: "Safe operational tasks for the Komuna Go+SQLite API: database state management, seeding, user recovery, service lifecycle, and deployment. Use when modifying Komuna's live database, seeding data, recovering lost accounts, or managing the Go API service."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [komuna, database, seeding, operations, go-api]
    related_skills: [komuna-daily-report]
---

# Komuna Operations

## Overview

Safe operations for Komuna's Go/SQLite API.

## Reference playbooks

- `references/slug-link-audit.md` — slug route audit.
- `references/product-route-slug-resolution-and-manager-scope.md` — safe ID/slug resolution, tenant scope, manager authorization, and regression matrix.
- `references/wallet-package-name-display.md` — wallet package/display names: live Go API joins, frontend DTO fallback, tests, deploy pitfalls.
- `references/admin-products-metric-and-cancellation-policy.md` — Admin Products tab pitfall: ambiguous products/sessions metric and session cancellation policy visibility.
- `references/product-slug-create-backfill.md` — Product slug creation/backfill pitfall: nullable product slugs can hide activated sessions from program-wide upcoming-session lists.





- `references/slug-link-audit.md` — use when canonical program/product slugs exist in the API but the website still shows old UUID routes; covers frontend DTO/route-builder/cache/deploy checks.
- `references/product-custom-fields.md` — spec/schema mapping for product custom field definitions and voucher-claim custom field answers.

## Service Management

```bash
# Restart the API service (ports :8095 internally, :443 via nginx)
sudo systemctl restart komuna-api.service

# Check status
sudo systemctl status komuna-api.service

# Build and deploy
cd /home/ubuntu/projects/komuna/api/v1
go test ./... && go build -o ../server .
sudo systemctl restart komuna-api.service
```

Public URL: `https://komuna.ahsanworks.com/`

### Mechanical Go API Refactors

When implementing an approved no-behavior-change split of `api/v1/main.go`:
1. Keep every new file in `api/v1/` as `package main`; do not create subdirectories or new packages.
2. Baseline first: `go test ./...` and `go build -o /tmp/komuna-refactor-check .` before moving code.
3. Move top-level declarations by responsibility only; preserve handler/function names and route registrations.
4. Use `goimports` after the split to assign imports per file (`go install golang.org/x/tools/cmd/goimports@latest` if missing).
5. Build the real deployed binary with `go build -o ../server .`, restart `komuna-api.service`, then verify local and public health plus a real data endpoint (for example `/api/v1/programs`).
6. Commit/push only the refactor files; leave unrelated untracked docs/uploads alone.


## CRITICAL: Database Safety Rules

**NEVER delete `sqlite.db` to re-seed.** This wipes all auth_users, auth_sessions, members, vouchers, claims, purchases, and any runtime data. The user WILL lose accounts they created and will be unable to log in. Instead, always **merge data into the live database** using Python/SQLite DELETE+INSERT patterns, never `rm`.

### Schema Versions

The API has two schema generations. Know which one you're working with before touching the DB:

**V2 (current — relational schema):** `main.go` is ~2240 lines. Separate tables for every entity:
- `programs`, `products`, `users`, `auth_users`, `program_members`, `program_member_roles`, `product_managers`
- `purchase_packages`, `package_entries`, `sessions`, `vouchers`, `voucher_claims`, `subscriptions`
- `purchases`, `purchase_items`, `session_templates`, `session_managers`
- `requests`, `audit_logs`, `notifications`, `platform_settings`, `platform_admins`
- `custom_fields`, `custom_field_answers`, `program_invitations`

**V1 (legacy — `app_state` JSON blob):** `main.go` is ~1700 lines. A single `app_state` table with one row containing the entire state as JSON.

To determine the version: check if `app_state` table exists:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='app_state';
```
If it returns a row → V1. If not (and there are 25+ tables instead) → V2.

### V2 Safe Pattern: DELETE + INSERT in relational tables

```python
# Disable FK during bulk seed to avoid cascade issues
con.execute("PRAGMA foreign_keys=OFF")

# Delete seed data in dependency order (children first)
for t in ["voucher_claims","custom_field_answers","subscriptions","vouchers",
           "purchases","purchase_items","session_managers","session_templates",
           "sessions","package_entries","purchase_packages",
           "product_managers","custom_fields","products",
           "program_member_roles","program_members","program_invitations",
           "requests","audit_logs","notifications","programs"]:
    con.execute(f"DELETE FROM {t}")

# Insert programs (use INSERT, not INSERT OR REPLACE)
for p in all_progs:
    con.execute("INSERT INTO programs(id,name,description,...) VALUES(?,?,?,...)",
                (p["id"], p["name"], p["desc"], ...))

# Insert products (each references a program_id)
for p in all_products:
    con.execute("INSERT INTO products(id,program_id,name,...) VALUES(?,?,?,...)",
                (p["id"], p["pid"], p["name"], ...))

# Insert users + auth_users (both tables must have matching IDs)
for email, name in user_names.items():
    uid = f"user-{hash(email) & mask:016x}"
    con.execute("INSERT OR IGNORE INTO users(id,email,name,created_at) VALUES(?,?,?,?)", ...)
    con.execute("INSERT OR IGNORE INTO auth_users(id,email,name,password_hash,created_at) VALUES(?,?,?,?,?)", ...)

# Insert program_members + roles + product_managers
for prog_id, roles, status in member_spec:
    pmid = gen_id("pm")
    con.execute("INSERT INTO program_members(id,user_id,program_id,status,joined_at) VALUES(...)", ...)
    for role in roles:
        con.execute("INSERT INTO program_member_roles(id,program_member_id,role) VALUES(...)", ...)
    # Manager roles get product_managers entries too
    if "manager" in roles:
        for prod_id in manager_products[email][prog_id]:
            con.execute("INSERT INTO product_managers(id,program_member_id,product_id) VALUES(...)", ...)

con.commit()
```

Then restart the service: `sudo systemctl restart komuna-api.service`

### V1 (Legacy) Safe Pattern: Read-Modify-Write app_state via Python

```python
import sqlite3, json
from datetime import datetime, timezone

con = sqlite3.connect('sqlite.db')

# OPTIONAL: Force WAL checkpoint to merge pending writes into main DB
con.execute('PRAGMA wal_checkpoint(TRUNCATE)')

# Read current state
row = con.execute("SELECT payload FROM app_state WHERE id=1").fetchone()
state = json.loads(row[0])

# Modify (e.g., add programs)
state['Programs'].append({...})

# Write back — use compact JSON to match Go output
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
con.execute("UPDATE app_state SET payload=?, updated_at=? WHERE id=1",
            (json.dumps(state, separators=(',', ':')), now))
con.commit()
con.close()
```

Then restart the service: `sudo systemctl restart komuna-api.service`

### Adding Seed Programs Without Damage (V1 Legacy)

**This applies only to the V1 `app_state` JSON blob API.** For V2 relational, use the DELETE+INSERT pattern in the V2 section above.

1. Read current programs from live DB via `curl http://127.0.0.1:8095/api/v1/programs`
2. Identify which programs need adding (check by ID)
3. Use the Python read-modify-write pattern above to insert only missing programs
4. Restart service
5. Verify via `curl http://127.0.0.1:8095/api/v1/programs | python3 -c "import json,sys; print(len(json.load(sys.stdin)['data']))"`

### WAL Checkpointing (V1 Legacy)

**V1 only.** When the Go service was running the V1 `app_state` API, SQLite WAL mode meant recent writes lived in `sqlite.db-wal`, not the main file. Always run `PRAGMA wal_checkpoint(TRUNCATE)` before reading from Python to get the full current state. V2's relational schema with multiple tables doesn't typically need this for reads.

## Auth System

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/auth/sign-up` | Register |
| POST | `/api/v1/auth/sign-in` | Login |
| GET | `/api/v1/auth/session` | Check session (now includes `profile_picture`) |
| POST | `/api/v1/auth/sign-out` | Logout |
| PUT | `/api/v1/profile/name` | Change display name |
| PUT | `/api/v1/profile/email` | Change email (requires password) |
| PUT | `/api/v1/profile/password` | Change password (requires current password, min 8 chars) |
| POST | `/api/v1/profile/picture` | Upload profile picture (multipart, 5MB max) |
| DELETE | `/api/v1/profile/picture` | Remove profile picture |

### Password Hashing (Go implementation reproduced in Python)

The Go API uses a custom salted SHA256 hash with 120,000 iterations:

```python
import hashlib, secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)  # 32 hex chars
    buf = (salt + ":" + password).encode()
    for _ in range(120000):
        buf = hashlib.sha256(buf).digest()
    return f"{salt}:{buf.hex()}"
```

Format stored in `auth_users.password_hash`: `hex_salt:hex_digest`

### Recovering a Lost User Account

When the DB was accidentally wiped and a user can't log in:
1. Hash a temporary password using the Python function above
2. Insert into `auth_users`:
   ```sql
   INSERT INTO auth_users(id, email, name, password_hash, created_at)
   VALUES (?, ?, ?, ?, ?)
   ```
3. Add a member record in `app_state.payload["Members"]` for their programs
4. Tell the user their temp password and instruct them to change it immediately

## Project Structure

```
/home/ubuntu/projects/komuna/
├── api/v1/main.go       # Go API — single-file, ~2240 lines (V2 relational schema)
├── api/v1/main_test.go  # Tests
├── api/server           # Compiled binary
├── sqlite.db            # Live database (DO NOT DELETE, DO NOT rm -f)
├── sqlite.db.bak-*      # Backups created before seed operations
├── apps/api/            # Cloudflare Worker (TypeScript, separate deployment)
├── apps/web/            # React SPA (Vite)
│   ├── .env             # Build-time env vars (VITE_ prefixed — see pitfall below)
│   ├── dist/            # Production build output
│   └── .env.example     # Template (does NOT include VITE_USD_TO_IDR_RATE)
└── docs/                # Project documentation
```

## Frontend Build & Deploy

```bash
cd /home/ubuntu/projects/komuna/apps/web

# Build (tsc + vite build)
npm run build

# Deploy to nginx static dir
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/
sudo chown -R www-data:www-data /var/www/html/projects/komuna/
```

The frontend is served by nginx from `/var/www/html/projects/komuna/` at the path prefix `/projects/komuna/`. The Vite build reads env vars from `apps/web/.env`, NOT from the root `/home/ubuntu/projects/komuna/.env`.

### Admin Management Route Layout Consistency

When fixing or adding program admin management pages (overview, members, products, packages, vouchers, analytics, audit log), use the canonical tabbed dashboard route family: `/dashboard/programs/:id/<section>` wrapped by `ProgramDetailLayout`. The older `/programs/:id/admin/<section>` routes are workspace-shell legacy routes and will not show the tab strip unless explicitly redirected. If a user reports an admin page "doesn't look like the other dashboard pages" or lacks management tabs, check `apps/web/src/App.tsx` and `apps/web/src/components/dashboard/workspaceNavigation.tsx` first:
- Admin side-nav links for management sections should point to `/dashboard/programs/${programId}/...`.
- Legacy `/programs/:id/admin` routes should redirect to the matching dashboard section (`audit` → `audit-log`).
- Keep routes that are not in the tab strip (for example approvals) on their existing workspace route unless adding them to `ProgramDetailLayout` intentionally.
- Add/adjust `workspaceNavigation.test.tsx` so it asserts canonical dashboard hrefs, then verify with `npm run test -- workspaceNavigation && npm run build`, deploy `apps/web/dist/`, and confirm the public HTML serves the new bundle.

### Session Template / Activation UI Placement

When implementing or adjusting session template generation/activation in Komuna, put admin-facing template and activation controls inside the existing program detail **Sessions** tab (`apps/web/src/pages/dashboard/SessionsTab.tsx`) rather than standalone pages or the admin dashboard overview. Keep separate route components embeddable (`embedded` prop) if useful, but render the primary UI inside Sessions so it follows the dashboard information architecture.

Before coding, actually read the approved review artifacts under `docs/*session*` / the public `/prd/...` links the user references. Do not implement from memory or from a nearby standalone page if the artifact says a different page; this user treats that as a serious workflow failure.

Current intended admin Sessions-tab behavior:
- The template schedule is UI-only until activation. Build the visible rows from `session_templates.weekly_slots` by finding upcoming calendar dates whose weekday matches `day_of_week`.
- Show **only upcoming** rows; do not show ended sessions in this admin UI.
- Always show the closest 5 upcoming template dates per session product, sorted nearest-to-latest.
- Activating one template row should create/save the real `sessions` row for that date/time (if missing), then mark it active so members in the program can see/join it.
- Existing saved sessions should be matched back to the same template date/time so booked counts, active state, QR, and attendance detail attach to the right row.
- Deactivation still needs the warning CTA and cancellation/refund/notification behavior for booked members.

Theme pitfall: do not introduce dark custom cards or one-off visual language. Use existing dashboard tokens and structure: `var(--paper-1)`, `var(--ink-1)`, `var(--ink-3)`, `var(--rule)`, serif headings, mono eyebrow labels, rounded `10px` cards, and mobile stacked cards/full-width actions. Verify with `npm run build`, `go build -o ../server .`, restart `komuna-api.service`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, and confirm the public JS bundle contains stable markers for the intended Sessions-tab behavior.tion architecture.

Before coding, actually read the approved review artifacts under `docs/*session*` / the public `/prd/...` links the user references. Do not implement from memory or from a nearby standalone page if the artifact says a different page; this user treats that as a serious workflow failure.

Current intended admin Sessions-tab behavior:
- The template schedule is UI-only until activation. Build the visible rows from `session_templates.weekly_slots` by finding upcoming calendar dates whose weekday matches `day_of_week`.
- Show **only upcoming** rows; do not show ended sessions in this admin UI.
- Always show the closest 5 upcoming template dates per session product, sorted nearest-to-latest.
- Activating one template row should create/save the real `sessions` row for that date/time (if missing), then mark it active so members in the program can see/join it.
- Existing saved sessions should be matched back to the same template date/time so booked counts, active state, QR, and attendance detail attach to the right row.
- Deactivation still needs the warning CTA and cancellation/refund/notification behavior for booked members.

Theme pitfall: do not introduce dark custom cards or one-off visual language. Use existing dashboard tokens and structure: `var(--paper-1)`, `var(--ink-1)`, `var(--ink-3)`, `var(--rule)`, serif headings, mono eyebrow labels, rounded `10px` cards, and mobile stacked cards/full-width actions. Verify with `npm run build`, `go build -o ../server .`, restart `komuna-api.service`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, and confirm the public JS bundle contains stable markers for the intended Sessions-tab behavior.

### Public Sessions Page Layout Corrections

When adjusting the public all-sessions page (`apps/web/src/pages/AllSessionsPage.tsx`):
- If the user asks for the sessions to match the program-detail session-card layout, use the compact horizontal card component (`SessionCardCompact`) for every tab/status instead of mixing one large hero card with smaller cards.
- If the user asks for sessions to be “listed and scrolled horizontally,” render the cards in a single horizontal rail (`display:flex`, `overflow-x:auto`, equal `flex-basis`, optional `scroll-snap`) rather than a vertical stack or masonry/grid. Keep card widths equal so no session is visually prioritized.
- Keep the scrollbar minimal and theme-aligned: thin, transparent track, subtle `var(--rule-2)` rounded thumb. Avoid a loud native scrollbar that distracts from the cards.
- Verification pattern: `npm run test -- AllSessionsPage && npm run build`, deploy `apps/web/dist/`, then confirm the live bundle contains the rail/scrollbar selectors.
- Final-report pitfall: do not send a seed/test route like `/programs/p1/sessions` as the review link unless that is the actual program the user provided. Use the project root `https://komuna.ahsanworks.com/` or the exact real URL under discussion.

### Program/Product/Package Seed Images: Local Assets via `image_url`

When planning or implementing Komuna seed repairs that involve program/product/package imagery:
- `image_url` is the canonical field for seeded visuals. Do **not** replace it with a new public field such as `image_asset`; the user explicitly expects `image_url` to fetch local generated assets.
- `image_url` values should point to app-served local assets, not remote URLs. Use paths like `/program-images/<id>.svg`, `/product-images/<id>.svg`, and `/package-images/<id>.svg` under `apps/web/public/`.
- If package images are needed, add `purchase_packages.image_url` safely. Make every `ALTER TABLE` idempotent: tolerate duplicate-column errors in the Go schema loop and/or check `PRAGMA table_info` in backfill scripts before altering.
- Seed/backfill every program, product, and purchase package with a contextual local image asset. Keep `image_tone` / `image_label` only as deterministic fallback when an item unexpectedly has no `image_url`; normal seeded data should never hit the fallback.
- Add a deterministic backfill/validation script when changing live data. The script should back up `sqlite.db`, add missing columns, fill empty `image_url`/slug values, and fail on counts for missing program/product/package images, missing product slugs, or non-positive package prices.
- Deploy both the Vite `dist/` and the public image folders to nginx. Because Komuna runs at root behind nginx runtime basename rewrites, root-relative asset URLs (`/package-images/...`) are safest on `https://komuna.ahsanworks.com/`.
- Smoke-check after deployment with local and public curls: API health, a package/product endpoint returning non-empty `imageUrl`, and `HEAD https://komuna.ahsanworks.com/package-images/<file>.svg` returning 200.

### Discovery Program Card CTA Changes

When the user asks to remove repetitive Join/Joined CTAs from discovery cards, make the smallest frontend-only change in `apps/web/src/components/discovery/ProgramCard.tsx`: remove the card-level join action/button and its now-unused imports/state, but keep the whole card clickable via `navigate(detailPath)` so joining still happens from the program detail page. Verify with `npm run test -- ProgramCard && npm run build`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, then commit/push.

### All Sessions Page Card Layout Consistency

When the user asks for the sessions page tabs (Upcoming/Ongoing/Past) to match the program-detail session card layout, target `apps/web/src/pages/AllSessionsPage.tsx` and prefer reusing `SessionCardCompact` from `apps/web/src/pages/all-sessions/SessionCardCompact.tsx`. Remove the special upcoming-only hero/featured split (`SessionCard` + `selectHeroAndNextThree`) so every tab maps `sessionsData.items` through the same compact horizontal card component; this keeps all cards equal height/structure and avoids one oversized first card. Verify with `npm run test -- AllSessionsPage && npm run build`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, then confirm the public JS no longer contains `all-sessions-featured` and does contain `all-sessions-grid` before commit/push.

### All Sessions Page Card Layout Consistency

When the user asks for the sessions page tabs (`/programs/:id/sessions` — Upcoming/Ongoing/Past) to match the program detail session-card layout, update `apps/web/src/pages/AllSessionsPage.tsx` to use `SessionCardCompact` consistently for every status. Do not keep the special Upcoming hero/featured card (`SessionCard` + `selectHeroAndNextThree`) if the request says no card should be bigger than the others.

If the user asks for the sessions to be “listed and scrolled horizontally,” render the `SessionCardCompact` items as a horizontal rail: parent `display: flex`, `overflowX: auto`, `scrollSnapType: 'x mandatory'`, and wrap each card in an equal-width flex item such as `flex: '0 0 clamp(280px, calc(100vw - 160px), 760px)'` with `scrollSnapAlign: 'start'`. Verify with `npm run test -- AllSessionsPage && npm run build`, deploy `apps/web/dist/`, confirm the public bundle contains `scrollSnapType`, then commit and push.

### Sessions Page Horizontal Rails

When adjusting the public sessions page (`apps/web/src/pages/AllSessionsPage.tsx`) to match program-detail compact session cards:
- Use `SessionCardCompact` for all status tabs (`upcoming`, `ongoing`, `past`) when the user asks for equal horizontal cards; avoid reintroducing a hero/featured card that makes one session larger than the others.
- For a horizontally scrolling rail, wrap each compact card in an equal-width flex child (for example `flex: '0 0 clamp(280px, calc(100vw - 160px), 760px)'`) and set the rail to `display:flex`, `overflowX:auto`, and `scrollSnapType:'x mandatory'`.
- Desktop mouse wheels normally require Shift to scroll horizontal overflow. If the user expects hover + normal wheel scrolling, add an `onWheel` handler on the rail that maps vertical `deltaY` into `currentTarget.scrollLeft` and `preventDefault()` when vertical delta dominates; add a focused test that dispatches a `WheelEvent` and asserts `scrollLeft` changes.
- Keep the rail scrollbar subtle and theme-aligned (`scrollbar-width: thin`, transparent track, `var(--rule-2)` rounded thumb) instead of a loud default bar.
- After deploying, verify the public bundle contains the relevant scroll/scrollbar marker. In final reports, do not invent a sample program URL such as `/programs/p1/sessions`; use the exact user-provided page when available or the root project link `https://komuna.ahsanworks.com/`.

### Sessions Page Layout Consistency

When adjusting member-facing sessions list layouts (`apps/web/src/pages/AllSessionsPage.tsx`), match the program detail upcoming-session implementation unless the user explicitly asks for a different interaction model:
- Reuse `SessionCardCompact` from `apps/web/src/pages/all-sessions/SessionCardCompact.tsx`.
- Prefer the same `hero-sessions__list` flex-column structure used by `HeroRightSessions` (`display:flex`, `flexDirection:'column'`, `gap:12`, `flex:1`, `minHeight:0`) so every card has the same compact horizontal-card shape and no card is featured/larger.
- Do **not** add custom scrollbar CSS, wheel-event handlers, scroll hijacking, or visual overlays to solve perceived scrollbar minimalism unless the user explicitly requests that behavior. These can make mouse/trackpad scrolling feel broken.
- If experimenting with horizontal rails, confirm the desired native scroll behavior first; browser horizontal rails usually require Shift+wheel or trackpad horizontal gestures, so don't assume vertical wheel should be remapped.
- Verify with `npm run test -- AllSessionsPage && npm run build`, deploy `apps/web/dist/`, and check the public bundle for the intended class/handler presence or absence.

### Mobile UI Fix Pattern: Program Detail / Responsive Pages

When fixing Komuna mobile layout issues after an approved review artifact, prefer the smallest CSS-led patch:
1. Add stable class hooks to existing inline-styled React elements instead of rewriting components.
2. Import one small page-scoped stylesheet from the page entry (`apps/web/src/pages/ProgramDetailPage.tsx` for program detail fixes).
3. Use media-query overrides to neutralize desktop inline styles (`grid-template-columns`, large `padding`, `min-height`, image `aspect-ratio`, large typography); `!important` is acceptable here because many current components use inline style props.
4. For guest-only sign-in prompts, keep desktop spacing as the base and compact through classes such as `guest-banner`, `guest-banner__content`, `guest-banner__icon`, `guest-banner__text`, and `guest-banner__button`. On narrow screens: reduce padding/icon/text, allow wrapping, and make the button full-width only around ≤420px.
5. For the program-detail "Upcoming sessions" column, desktop `SessionCardCompact` uses a 3-column grid (`148px` image + text + action). On mobile this can make titles/times wrap vertically. Fix in `apps/web/src/pages/program-detail/mobile.css` by overriding `.hero-sessions .session-card` to a compact 2-column grid (small image + text) and move the action/spots column to a full-width bottom row via `> :last-child { grid-column: 1 / -1; flex-direction: row !important; }`. This is smaller than rewriting the component.
6. When the user asks another page to match the program-detail upcoming-sessions rail, do not invent new scroll handlers, fade overlays, or custom scrollbar styling. First inspect the real program-detail page implementation: `ProgramDetailPage.tsx` wraps `HeroRightSessions` in `section.detail-upcoming`, and `apps/web/src/pages/program-detail/mobile.css` makes `.detail-upcoming .hero-sessions__list` a horizontal native-scroll rail (`flex-direction: row`, `overflow-x: auto`, `scroll-snap-type`/flex sizing via the existing `SessionCardCompact` rules). Reuse that exact class structure/CSS import where appropriate so the browser keeps native shift-wheel/trackpad behavior.
7. Verify with the specific page test plus build (`npm run test -- ProgramDetailPage && npm run build`, or the matching page test), deploy with rsync, then confirm the live CSS/JS asset contains the expected selectors/classes and the public route returns 200.

This avoids over-refactoring while making oversized hero/session/guest-banner sections fit mobile screens.

### Sessions Page Horizontal Rail UX

When adjusting the member-facing all-sessions page (`apps/web/src/pages/AllSessionsPage.tsx`):
- If the user asks for sessions to be horizontal like program-detail session cards, reuse `SessionCardCompact` for all status tabs (`upcoming`, `ongoing`, `past`) and render one equal-width native horizontal rail (`display:flex; overflow-x:auto; scroll-snap-type:x mandatory`). Do not keep a large featured/hero card in one tab if the requested goal is equal card structure.
- Do not hijack `wheel` events to translate vertical scrolling into horizontal scrolling unless the user explicitly requests non-native wheel behavior; it can make desktop scrolling feel broken. Keep browser-native horizontal scroll behavior.
- If the native scrollbar feels visually heavy, prefer non-interactive affordances such as subtle left/right edge fades with `pointer-events:none`. Avoid custom `::-webkit-scrollbar` / `scrollbar-width` styling when the user reports scroll behavior issues; scrollbar CSS can make debugging input behavior harder and may vary by OS/browser.
- Add or update the focused all-sessions test, run `npm run test -- AllSessionsPage && npm run build`, deploy `apps/web/dist/`, then verify the public bundle contains the intended layout markers and does not contain removed scroll hooks/styles.

### Public Link Reporting Pitfall

After deploying Komuna frontend changes, do not send placeholder/test routes such as `/programs/p1/...` as the review link unless the user specifically provided that route. Use the real route the user gave, or otherwise send only the domain root (`https://komuna.ahsanworks.com/`) and state the change applies globally to that page class.

### ERD Maintenance Requirement

Whenever a Komuna task changes the database structure, schema migration, table list, columns, foreign keys, or relationship semantics, update the ERD review page in the same change:
- Source artifact: `/home/ubuntu/projects/komuna/docs/komuna-erd.html`
- Public deployment target: `/usr/share/nginx/html/prds/komuna-erd.html`
- Public URL: `https://komuna.ahsanworks.com/prd/komuna-erd.html`

Keep the ERD dark-theme-first and preserve the light/dark toggle. After editing, deploy the HTML, verify the public page returns 200 and contains the changed table/column/relationship text, then commit/push the ERD update together with the schema change.

### Spec/PRD/ERD HTML Review Artifact Pattern

When the user asks to make a Komuna spec/PRD/diagram easier to read as HTML with the website's theme:
1. Use the authoritative source in the repo when available (for the main product spec, `komuna-community-session-bookings.md`). For ERD/database-map requests, inspect the live V2 SQLite schema (`sqlite.db` via `PRAGMA table_info` / `PRAGMA foreign_key_list`) and cross-check `references/v2-schema.md`; do not hand-draw relationships from memory.
2. Generate a standalone HTML file under `docs/`.
3. Match Komuna's dashboard theme tokens from `apps/web/src/globals.css`: `--paper-1`, `--paper-2`, `--paper-3`, `--ink-1`, `--ink-2`, `--ink-3`, `--rule`, `--rule-2`, `--accent`, `--accent-soft`, `--accent-ink`; keep serif large headings, mono eyebrow labels, rounded cards, and responsive/mobile layout.
4. For ERD pages, prefer a readable one-page artifact over a tiny dense graph: group tables by domain (Core, Membership/Roles, Commerce, Sessions/Ops), mark PK/FK columns, include the main business flow, and add a relationship table with source column → target table meanings. Avoid external JS/CDN dependencies when simple HTML/CSS cards and tables are enough.
5. Include a sticky/table-of-contents sidebar on desktop and a stacked layout on mobile for long specs; for diagrams, ensure cards collapse to one column on mobile.
6. Deploy review artifacts to `/usr/share/nginx/html/prds/` and verify with `curl -sI http://localhost/prd/<file>.html` returning 200. The public review link is `https://komuna.ahsanworks.com/prd/<file>.html`.
7. Commit and push the `docs/*.html` artifact after verification.

### Vite Env Var Pitfall

**CRITICAL:** Vite only exposes env vars prefixed with `VITE_` to client code (`import.meta.env`). The root `.env` has variables like `USD_TO_IDR_RATE=16000` — these are for the Go API, NOT accessible to the frontend. If a frontend feature depends on a build-time value:

1. The var MUST be in `apps/web/.env` (not root `.env`)
2. The var MUST be prefixed with `VITE_` (e.g., `VITE_USD_TO_IDR_RATE=16000`)
3. Rebuild and redeploy after adding/changing

**Symptom of this bug:** Currency conversion (IDR → USD) silently does nothing — `getUsdToIdrRate()` returns 0, the `if (rate)` guard skips conversion, prices display in IDR amounts with USD currency symbols (e.g., "$425,000" instead of "$26.56").

### Checkout Redirect Base URL Pitfall

**Symptom:** After checkout/payment, the user is sent to the old public IP such as `http://168.110.213.104/projects/komuna/auth/sign-in` instead of `https://komuna.ahsanworks.com/...`.

**Root cause:** The Go checkout path creates Xendit invoice redirect URLs from the root `.env` value `PUBLIC_BASE_URL` in `api/v1/commerce_handlers.go::createXenditInvoice()`. If `PUBLIC_BASE_URL` still points at the old IP, Xendit stores that stale URL when the invoice is created; frontend basename fixes cannot correct it after payment.

**Fix pattern:** Update the live root `/home/ubuntu/projects/komuna/.env` values and restart the Go API:
```env
PUBLIC_BASE_URL=https://komuna.ahsanworks.com
WEB_APP_URL=https://komuna.ahsanworks.com
AUTH_ISSUER=https://komuna.ahsanworks.com
```
Then:
```bash
sudo systemctl restart komuna-api.service
curl -sS http://127.0.0.1:8095/api/v1/health
curl -sS https://komuna.ahsanworks.com/api/v1/health
```
Do not read or print the full `.env`; patch only known keys and verify only non-secret relevant values.

### Wallet Route Canonicalization

Komuna should have a single member wallet page at `/wallet`. Avoid reintroducing a second page at `/programs/:id/member/wallet` or `/members/wallet`.

If duplicate wallet pages appear:
- Keep `apps/web/src/App.tsx` canonical route `/wallet` wrapped in `RequireAuth`.
- Make legacy/member workspace wallet routes redirect to `/wallet`, not render `<WalletPage />` again.
- Remove member workspace navigation entries with IDs like `member-wallet` that point to program-scoped wallet URLs.
- Update member dashboard and payment-return links to navigate to `/wallet`.
- Verify with focused tests (`workspaceNavigation`, `PaymentReturnPage`, `MemberDashboardPage`) and `npm run build`, deploy `apps/web/dist/`, then confirm the deployed JS no longer contains `/member/wallet`.

### Build-Time vs Runtime Basename Pitfall

**CRITICAL:** The nginx config for `komuna.ahsanworks.com` injects two runtime overrides via `sub_filter` before `</head>`:

```
sub_filter '</head>' '<script>window.__BASENAME__="/";window.__API_BASE__="/api/v1"</script></head>';
```

This means:

| Value | Build-time (`import.meta.env`) | Runtime (nginx injection) |
|-------|-------------------------------|--------------------------|
| `BASE_URL` / `__BASENAME__` | `/projects/komuna/` | `/` |
| API base | `/projects/komuna/api/v1` | `/api/v1` |

The domain serves the SPA at the **root** (`/`), NOT under `/projects/komuna/`. The `sub_filter` also rewrites asset paths: `src="/projects/komuna/assets/..."` → `src="/assets/..."`.

**ANY frontend code that constructs absolute URLs using `import.meta.env.BASE_URL` will produce wrong paths on the production domain.** Always check `window.__BASENAME__` at runtime first:

```ts
function getRuntimeBase(): string {
  if (typeof window !== 'undefined' && (window as any).__BASENAME__) {
    return (window as any).__BASENAME__ as string
  }
  return import.meta.env.BASE_URL || '/'
}
```

**Known casualty:** `resolveSignedOutRoute()` in `apps/web/src/lib/logout.ts` used the build-time base to construct the post-logout redirect URL. It produced `/projects/komuna/auth/sign-in` on a domain where React Router has basename `/`, so the remaining path `projects/komuna/auth/sign-in` matched no route → NotFoundPage with "Page not found."

**Verification after fix:**
```bash
# Confirm the deployed JS reads runtime __BASENAME__
curl -s "https://komuna.ahsanworks.com/assets/$(curl -s https://komuna.ahsanworks.com/ | grep -oP 'assets/index-[^\"]+\.js')" | grep -o '__BASENAME__'
# Must return matches (shows the runtime check is present)

# Confirm the domain HTML injects __BASENAME__
curl -s "https://komuna.ahsanworks.com/" | grep -o 'BASENAME__=\"/\"'
# Must return BASENAME__="/" (nginx sub_filter injection is active)
```

### Linked Files

- `scripts/hash_password.py` — standalone script to hash a password matching Go API's algorithm. Run directly: `python3 scripts/hash_password.py somepassword`
- `references/v2-schema.md` — complete V2 relational schema reference (tables, columns, FK relationships, seeding pattern, role assignment)
- `references/session-booking-flow.md` — pre-filling sessions with bookings: voucher → claim → sessions.taken data flow and SQL patterns
- `references/session-template-generation-design.md` — confirmed design rules for weekly templates, manager generation, inactive generated sessions, required template times, activation page, and mobile UX
- `references/manager-dashboard.md` — Go API manager dashboard implementation: route handler, data flow, timezone handling, response shape, and `countAttendance` helper
- `references/frontend-auth-guards.md` — React SPA auth architecture: session store, sign-out flow, protected route pattern, route audit of missing guards, and the "??"/"User" stale-render bug
- `references/restricted-route-auth-guards.md` — backend + frontend restricted-route auth guard pattern; avoid `currentUser()` fallback on account/dashboard APIs and add unauth 401 regression tests
- `references/session-template-generation-activation-design.md` — confirmed design decisions for session templates, generation permissions, generation range, one-off sessions, and separate per-date activation UX
- `references/program-product-package-seed-quality-audit.md` — audit and fix pattern for blank/internal slugs, missing package coverage, product/package image support, free packages, session-card route split, and currency/money overflow issues.

### External Seed Scripts

- `/tmp/komuna-reseed-v2.py` — full 40-user, 25-program seed script for the V2 relational schema. Run with: `sudo systemctl stop komuna-api.service && python3 /tmp/komuna-reseed-v2.py && sudo systemctl start komuna-api.service`

## Full-State Reseeding (Complete DB Replacement)

When the user provides a full spec (users + programs + memberships + roles), write a Python script that populates all relevant tables. The approach differs by schema version.

### V2 Relational Schema Seed Script

For the current V2 relational schema, always:
1. `PRAGMA foreign_keys=OFF` before DELETE operations
2. Delete seed data in dependency order (children before parents)
3. Insert programs, products, users, auth_users, program_members, roles, product_managers
4. Insert packages, sessions, vouchers, requests as needed
5. Restart the service: `sudo systemctl restart komuna-api.service`
6. Verify with curl health check + programs endpoint + login test + workspace test

See `scripts/komuna-reseed-v2.py` for a working 40-user, 25-program seed script with the full relational schema pattern.

### V1 (Legacy) app_state JSON Seed Script

For the V1 `app_state` JSON blob API: build the entire `app_state` payload and populate `auth_users`. The script must produce JSON that Go's `json.Unmarshal` can deserialize into the `State` struct.

### JSON Type Pitfalls (V1 Legacy — Go `app_state` JSON → Python)

These Go struct fields will cause silent `load_failed` 500 errors if the JSON types don't match:

| Go Type | Go JSON Key | Correct Python | WRONG Python |
|---------|------------|----------------|-------------|
| `*int` | `ValidityValue` | `30` (integer) | `"30"` (string) |
| `Role` struct | `"role"`, `"product_id"` | lowercase keys | `"Role"`, `"ScopedProductID"` |
| `Package.SupersedesID` | `SupersedesID` | `""` (empty string) | missing key |
| `[]Purchase` | `Purchases` | `[]` or `"Purchases":[]` | missing key entirely |

### Full Seed Script Template

See `scripts/komuna-reseed.py` for a working 40-user, 25-program seed script. **Always stop the service first and back up the DB before running.** Key patterns:
- Password hashing: use `scripts/hash_password.py` or inline the algorithm
- Always include all state keys even if empty: `Purchases: []`
- Use `json.dumps(state, separators=(',', ':'))` for compact output matching Go
- Build `auth_users` and `app_state` in the same script, then restart the service

### Debugging `load_failed` Errors

When the Go API returns 500 with `{"error":"load_failed"}` after a manual DB update:

1. **Test with minimal state first**: Replace the payload with an empty state (`all lists empty, Settings with required fields`). If that loads, the schema is fine — the problem is a specific field.
2. **Incrementally add complexity**: Add programs, then members, then products — test after each step to isolate the offending JSON.
3. **Check Go struct tags**: Compare your JSON keys against Go struct field names and explicit `json:"..."` tags. Go's default serialization uses TitleCase; only structs with explicit tags diverge.
4. **Temporary debug logging**: Add `log.Printf` to the `load()` function (line ~230 in `main.go`) to see the unmarshal error, then `go build`, redeploy, test, and remove the debug logging.

### Python Date Helpers

```python
from datetime import datetime, timezone, timedelta
t = datetime.now(timezone.utc)
ts = lambda h_offset=0: (t + timedelta(hours=h_offset)).strftime('%Y-%m-%dT%H:%M:%SZ')
# NEVER: t.replace(hour=t.hour+h_offset) — fails when offset crosses midnight
now_str = lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
```

## Common Issues & Troubleshooting

### ⚠️ Dual-Stack Architecture (Go + Cloudflare Workers)

The Komuna project has **two API stacks**:

| Stack | Location | Status | API Prefix |
|-------|----------|--------|------------|
| **Go+SQLite** | `api/v1/main.go`, port 8095 | **Production** (served by nginx) | `/api/v1/`, `/projects/komuna/api/v1/` |
| **Cloudflare Workers** | `apps/api/src/` (Hono+Drizzle+NeonDB) | NOT deployed here (Cloudflare-hosted) | Depends on `VITE_API_BASE_URL` |

The frontend (`apps/web/`) hits whichever API `VITE_API_BASE_URL` points to. When debugging API issues:
- Check `apps/web/.env` for the active `VITE_API_BASE_URL`
- The Go API uses custom auth (salted SHA256), the Worker API uses Neon Auth
- DB state lives in different places (local `sqlite.db` vs NeonDB Postgres)
- **Before touching the Go DB, verify which stack the frontend is configured to hit**

**🚨 CRITICAL PITFALL — Feature implementation MUST target the Go API first.** This server runs the Go API on port 8095, nginx proxies `/api/v1/` to it. The Cloudflare Worker at `apps/api/src/` is a separate deployment that is NOT running on this machine. When asked to implement a backend feature, always modify `api/v1/main.go` (the Go API), NOT `apps/api/src/` (the Worker). Modifying the Worker code has zero effect on production — the Go API is the one serving real traffic. The Worker API is a future migration target, not the current live backend.

**Double-check:** If you catch yourself editing TypeScript files in `apps/api/src/` for a feature that should go live, stop — you need to edit `api/v1/main.go` instead. The frontend at `apps/web/` connects to the Go API via nginx; the Worker is not in the request path for this deployment.

### Attendance CRUD Buttons Not Working

**Symptom:** Attended/No-show toggle buttons on the manager dashboard flash a loading spinner briefly but don't persist. Alias edit works fine. No console errors.

#### Production Stack (Go API — `api/v1/main.go`)

This is the **more common scenario** since the production nginx proxies `/api/v1/` to the Go API on port 8095.

**Root cause:** The Go API's `sessionTree` function at line 1599 was a **stub**: it returned a fake response without ever touching the database:
```go
// STUB — returned fake success without writing to DB
jsonOut(w, map[string]any{"claim_id": "", "session_id": sid, "attendance_status": "present", "marked_at": now(), "method": "manual"})
```
The frontend sends `POST /sessions/:id/attendance/override` → stub returns HTTP 200 with fake data → frontend calls `fetchData()` to refresh → DB was never updated → old status reappears.

**Fix:** Implement real body parsing and DB update in `sessionTree`:
```go
if len(parts) >= 2 && parts[1] == "attendance" {
    // /override sub-path for manual status changes
    if len(parts) >= 3 && parts[2] == "override" {
        var in struct {
            ClaimID   string `json:"claim_id"`
            NewStatus string `json:"new_status"`
        }
        json.NewDecoder(r.Body).Decode(&in)
        a.db.Exec("UPDATE voucher_claims SET attendance_status=? WHERE id=? AND session_id=?", in.NewStatus, in.ClaimID, sid)
        jsonOut(w, map[string]any{"claim_id": in.ClaimID, "session_id": sid, "attendance_status": in.NewStatus})
        return
    }
    // Base /attendance — marks present (QR/manual flow)
    var in struct { ClaimID string `json:"claim_id"`; Method string `json:"method"` }
    json.NewDecoder(r.Body).Decode(&in)
    a.db.Exec("UPDATE voucher_claims SET attendance_status='present' WHERE id=? AND session_id=?", in.ClaimID, sid)
    jsonOut(w, map[string]any{"claim_id": in.ClaimID, "session_id": sid, "attendance_status": "present"})
    return
}
```

**Pitfall — `claimByID` returns nil:** The `claimByID` helper function uses `rows.Scan` into plain `string` fields, which fails silently when `cancelled_at` is NULL (see "Go `rows.Scan` Silent Failure" below). Do NOT call `claimByID` in attendance responses — return a synthetic JSON response instead (the frontend doesn't use the claim detail, it calls `fetchData()` separately).

**Test:** `curl -X POST http://127.0.0.1:8095/api/v1/sessions/<sid>/attendance/override -H 'Content-Type: application/json' -d '{"claim_id":"clm-xxx","new_status":"present"}'` → verify DB updated: `sqlite3 sqlite.db "SELECT attendance_status FROM voucher_claims WHERE id='clm-xxx'"`.

#### Worker API Stack (`apps/api/src/`)

**Root cause (different):** Frontend `apiClient.markAttendance()` sends `{ claim_id, status }` to `POST /sessions/:id/attendance`, but the Worker API Zod validator expects `{ claim_id, method: 'qr_scan' | 'manual' }`. Zod strips unknown fields silently — no error, no network failure, just no data change.

Additionally, the `markAttendance` service always sets status to `'present'` (for QR/mobile flow), so `'absent'` would be wrong even if the payload matched.

**Fix:** Route to `POST /sessions/:id/attendance/override` with `{ claim_id, new_status }` instead. This endpoint accepts both `'present'` and `'absent'` and has no `already_marked` guard.

**Files (Worker stack):**
- Frontend: `apps/web/src/lib/api.ts` — `markAttendance` method (change endpoint path + payload)
- Backend validator: `apps/api/src/validators/attendance.ts` — `markAttendanceBodySchema` vs `overrideAttendanceBodySchema`
- Backend service: `apps/api/src/services/attendance.ts` — `markAttendance` vs `overrideAttendance`

### Program Cards/Detail Show Joined or Rejoin for Guests/New Users

**Symptom:** A guest or newly signed-up user sees discovery/program cards as “Joined”, or the program detail CTA says “Rejoin program” even though they have never joined. This may appear on discovery, search, and detail pages. It is usually an API DTO bug, not localStorage.

**Root causes:**
1. `api/v1/dto.go::programDTO()` hardcoded `membershipStatus: "active"` for every program instead of checking `program_members` for the current signed-in user.
2. Detail DTOs may hardcode `userRoles` (for example `[]string{"admin", "member"}`) even when `membershipStatus` is `null`. The frontend `HeroSection` treats `membershipStatus === null && userRoles.length > 0` as “previous member” and shows **Rejoin program**.
3. Program cards use the DTO `slug`. `programDTO()` can generate a slug from the program name when `programs.slug` is empty, but `programTree()` previously resolved only `id` or stored `slug`, so generated slugs 404.
4. The React session can consider the visitor a guest while the browser still has an old `komuna_session` cookie. If normal `apiClient` requests use browser credentials, the API can return joined/member data for what the UI treats as a guest, causing **Joined**, **Rejoin program**, **Book**, or **Leave Program** to appear incorrectly.

**Fix pattern:**
- Pass the real per-request membership status into `programDTO()` from list and detail handlers:
  ```go
  a.programDTO(p, cats, mc, rating, spw, feat != 0, true, a.programMembershipStatus(r, p.ID), nil)
  ```
- For detail responses, also pass real roles for the current authenticated user; guests and non-members must get `userRoles: []`:
  ```go
  a.programDTO(p, cats, mc, rating, spw, feat != 0, false, a.programMembershipStatus(r, p.ID), a.programUserRoles(r, p.ID))
  ```
- Implement `programMembershipStatus(r, pid)` and `programUserRoles(r, pid)` using `X-Komuna-User` or `userFromRequest(r)`; return `nil`/`[]` when unauthenticated or no membership row exists. Do **not** use `currentUser()` here because it falls back to the demo user and can leak demo membership/roles into anonymous/new-user responses.
- Make `programTree()` resolve ID, stored slug, and generated slug (`slugify(name)`) so any slug emitted by the list DTO can be fetched by detail routes.
- In `apps/web/src/lib/api.ts`, normal `ApiClient` requests should set `credentials: 'omit'`. Auth endpoints can still use `credentials: 'include'` when intentionally setting/clearing cookies, but public data fetches must not silently authenticate via stale cookies.
- Defensively gate membership UI by frontend auth state too: program cards should ignore `p.membershipStatus` unless `authClient.useSession()` has a real user, and `HeroSection`/CTA should ignore `membershipStatus`/`userRoles` when `isAuthenticated` is false. This prevents **Book/Leave/Rejoin** showing for guests even if bad/stale API data arrives.

**Regression checks:**
- Extend the signup workspace regression test to call `GET /api/v1/programs` with the new token and assert every `membershipStatus` is `null` before joining.
- Also fetch `GET /api/v1/programs/<id-or-slug>` with that token and assert `membershipStatus == null` and `len(userRoles) == 0`; this catches the detail-page “Rejoin program” bug.
- Add a route test that gets a slug from `GET /api/v1/programs`, then verifies `GET /api/v1/programs/<slug>` returns 200.
- Add a frontend `ApiClient` test asserting request init has `credentials: 'omit'`.
- Add a frontend program-detail regression where `authClient.useSession()` returns guest/null but the mocked program has `membershipStatus: 'active'` and roles; assert the page shows **Sign in to join** and not **Member**/**Leave Program**.
- Manual public probe: as a guest and as a fresh temporary user, fetch a detail endpoint and confirm `membershipStatus: null` and `userRoles: []`. Then join a public program and confirm detail returns `membershipStatus: active`. For UI regressions, also verify the deployed JS asset contains `credentials:\`omit\`` and the visible guest CTA is not **Book/Leave/Rejoin**.

### Guests Can Join Programs Instead of Being Sent to Login

**Symptom:** An anonymous visitor clicks **Join**, sees “You joined the program,” and is redirected to the program sessions/page instead of the login/signup page.

**Root cause:** `joinProgram()` used `currentUser(r)`. In Komuna, `currentUser()` intentionally falls back to the demo/dev user when no authenticated session exists. That is unsafe for mutating user actions: it can create `program_members` rows for the demo user and return success to guests.

**Fix pattern:**
- For mutating user-specific endpoints, authenticate explicitly with `X-Komuna-User` or `userFromRequest(r)`; do **not** call `currentUser()` unless demo fallback is intentionally allowed.
- Return `401 auth_required` when no real session exists. The frontend already routes `ApiError(401)` through `redirectToSignInForUnauthorized(...)`, so the smallest backend fix restores the UI redirect behavior.
- Keep `currentUser()` use limited to read/demo-compatible paths, or audit every caller before using it in new code.

**Regression check:** Add a test that posts to `/api/v1/programs/<id>/join` without auth, expects `401`, and verifies no membership was inserted for `app.userID`/demo user.

**Manual probes:**
```bash
curl -i -X POST http://127.0.0.1:8095/api/v1/programs/prog-box/join
curl -i -X POST https://komuna.ahsanworks.com/api/v1/programs/prog-box/join
# Both must return 401 {"error":"auth_required"}
```

### Superadmin Missing Dashboard Button

**Symptom:** A known superadmin logs in but the top-nav/profile Dashboard button is missing. They may only have member roles in programs.

**Root cause:** `apps/web/src/lib/useWorkspace.ts::canAccessDashboard()` grants access when `/api/v1/me/workspace` returns `isSuperAdmin: true`; the Go API sets that from `platform_admins` in `api/v1/main.go::workspace()`:

```go
a.db.QueryRow("SELECT COUNT(*) FROM platform_admins WHERE user_id=?", uid).Scan(&isSuperAdmin)
```

If `platform_admins` is empty or missing the user's exact `users.id`, `isSuperAdmin` is false and the frontend falls through to the admin/manager role check. A superadmin who is only a member will not see Dashboard.

**Check:**
```sql
SELECT id, user_id FROM platform_admins;
SELECT id, email, name FROM users WHERE email='USER_EMAIL';
SELECT id, email, name FROM auth_users WHERE email='USER_EMAIL';
```

**Fix:** Insert the user's `users.id` (which should match `auth_users.id`) into `platform_admins`; no service restart is needed because the handler reads the live DB.

```sql
INSERT INTO platform_admins(id, user_id)
VALUES ('pa-' || lower(hex(randomblob(4))), 'user-...');
```

**Verify:** Login, then call `/api/v1/me/workspace` with the session token/cookie and confirm `isSuperAdmin: true`. The dashboard button comes from `TopNav`/`ProfileMenu` using `canAccessDashboard(workspace)`.

**Seed pitfall:** Full reseed scripts must also seed `platform_admins`; otherwise reseeding silently removes all superadmins.

**Debugging pitfall — silent `currentUser` fallback to `user-demo`:** `currentUser()` (main.go:460) falls back to `a.userID` (env `KOMUNA_DEV_USER_ID`, default `user-demo`) when `userBySession` fails. This masks auth failures — the workspace endpoint returns HTTP 200 with `uid: user-demo` and `isSuperAdmin: false` instead of 401. If you see `uid: user-demo` in a workspace response for a real authenticated user, the session token lookup is failing (check `auth_sessions` table for the token, verify expiry format matches `time.RFC3339`).

### Profile Purchases Tab / Checkout History UI

When implementing or fixing member purchase history in `/profile` (`apps/web/src/pages/ProfilePage.tsx`):
- Wait for explicit implementation approval if the user is still asking for a plan/review artifact. A request to add requirements to the plan is not approval to deploy live behavior.
- Use the website/dashboard theme, not a standalone PRD style: `var(--paper-*)`, `var(--ink-*)`, `var(--rule)`, serif headings, mono eyebrow labels, rounded `10px` cards.
- Reuse the admin dashboard table/card pattern rather than inventing a new visual system: desktop purchase history should be a real table; mobile should hide the table and show stacked cards only.
- Fetch the existing restricted `/purchases` API with `{ page: 1, limit: 100 }`, filter to paid/completed statuses, and show all item/package names plus the purchase/support reference ID.
- Currency pitfall: purchase `total_amount` values are stored as IDR-like numeric strings. Do **not** hardcode `toLocaleString('en-US', { currency: 'USD' })`; that displays IDR-sized numbers with a `$` prefix and ignores Indonesian. Use the shared `formatPriceLabel(amount, { locale })` without passing an explicit `currency`, so English converts via `VITE_USD_TO_IDR_RATE` and Indonesian renders `IDR`/`Rp`.
- Make the purchases component read the active locale from `useTranslation()` (`i18n.language === 'id' ? 'id' : 'en'`) so toggling ID/EN re-renders the amounts.
- Add a focused `ProfilePage` test that clicks the Purchases sidebar item and asserts the desktop table, mobile card marker, item names, reference ID, and that pending purchases are not shown. For currency fixes, also stub `VITE_USD_TO_IDR_RATE`, switch `i18n` from `en` to `id`, and assert `$...` becomes `Rp...`.
- Verify with `npm run test -- ProfilePage && npm run build`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, grep the public bundle for a stable marker such as `purchase-mobile-card`, then commit/push the frontend and matching plan artifact.

### Admin Members Page Profile Pictures + Manager Product Labels

When improving `/dashboard/programs/:id/members` / admin members UI:
- Backend member rows are returned from `api/v1/program_handlers.go::programMembers`. To show avatars, join `auth_users` on `pm.user_id` and return `profile_picture: a.profilePictureURL(uid, ext)`; the frontend `MemberDTO` should keep it optional for older responses.
- Frontend table/card UI is in `apps/web/src/pages/MembersPage.tsx`. Prefer CSS-only responsive changes in the inline `<style>` block: add stable classes such as `member-identity`, `member-avatar`, `members-toolbar-actions`, and override them under `@media (max-width: 760px)`.
- Mobile layout pattern: keep name/email as one block, set `.member-identity { justify-content: space-between; }`, and move the avatar block to the right with `order: 2; margin-left: auto;`.
- Keep the global `Add Manager` button and status/role control in one mobile row by wrapping them in `.members-toolbar-actions { display:flex; gap:8px; }` and giving children `flex:1; min-width:0`.
- Keep per-member role management controls in one `.member-role-actions` flex row: role badges, `Edit managed products` / `Add Manager`, and Add/Remove role buttons belong together. Do not leave `Add admin` in a separate block below products on mobile.
- For product managers, render a grey mono `Products` label as its own block above the product chips (`display:block; margin-bottom:6px`), then put chips in a separate flex wrapper such as `.member-products-chips`. Do not place the label inline beside the chips on mobile; it reads like an unexplained badge.
- Desktop recommendation: do **not** add a dedicated Products column unless admins need sorting/filtering by handled product; inline labeled chips under Roles avoid widening the table and keep mobile simpler.
- Regression test: extend `MembersPage.test.tsx` with a manager that has `profile_picture` and a `manager` role scoped to a product; assert the avatar `img`, `Products` label, and product name render.

### Admin/Manager CTA Changes Role in UI But Reverts After Refresh

**Symptom:** On the admin members dashboard, clicking Add/Remove admin or assigning manager products shows an optimistic UI update, but after refreshing the member is back to basic member / previous roles.

**Root cause:** The frontend calls `POST`/`DELETE /api/v1/programs/:programId/members/:userId/roles` from `apps/web/src/pages/MembersPage.tsx`. If `api/v1/program_handlers.go::programMembers` does not dispatch `action == "roles"`, the generic `len(parts) >= 4` branch can return `{"success":true}` without writing `program_member_roles`. This creates a silent success/no-op.

**Fix pattern:**
- In `programMembers`, dispatch `roles` before ban/unban success handling:
  ```go
  if action == "roles" {
      a.programMemberRole(w, r, pid, uid)
      return
  }
  ```
- Implement `programMemberRole` to decode `{ role, productId? }`, validate `admin|manager`, look up the member by `(program_id,user_id)`, and write/delete `program_member_roles`.
- For product-scoped manager roles, also keep `product_managers` in sync with `program_member_roles.product_id`; manager role without `product_id` will not show assigned products in workspace.
- For unscoped admin rows with nullable `product_id`, do not rely on `UNIQUE(program_member_id, role, product_id)` to dedupe NULLs in SQLite. Delete any existing `product_id IS NULL` row before inserting, or use a non-NULL sentinel/schema change deliberately.

**Regression check:** Add a Go test that posts `{"role":"admin"}` to `/api/v1/programs/prog-box/members/<userID>/roles`, asserts `program_member_roles` has the row, then fetches `/members` and checks `"role":"admin"` is returned. Also smoke a temporary live member and clean it up after verifying persisted count.

### Role Promotion Creates No Notification for the Promoted User

**Symptom:** Admin promotes a member to admin or manager. The role sticks in `program_member_roles` and the UI updates, but the promoted user receives no in-app notification or email about their new role.

**Root cause:** `api/v1/program_handlers.go::programMemberRole()` writes to `program_member_roles` (+ `product_managers` for managers) and immediately returns `{"success":true}`. It never inserts a row into the `notifications` table and never calls any email/enqueue path. The `notifications` table, read endpoints (`GET /notifications`, etc.), and schema exist, but they are write-only from the perspective of role changes — nothing ever populates them from the role-assignment handler.

**Spec expectation:** `komuna-community-session-bookings.md` §9 notification matrix specifies "Manager assigned to product → notify Admin and Manager (assignee)." This is documented in the spec but not implemented in the Go API.

**What this is NOT:** This is not a Gmail/stub-email problem. It's not that email is configured with example/stubbed credentials and silently failing. The notification is never created in the app's own `notifications` table, so it cannot reach Gmail, push, SMS, or any other channel. The Go API's notification infrastructure is read-only — it can list, mark-read, and count notifications that were already inserted, but no handler creates them.

**Verification (before any fix):**
```bash
# Confirm zero notification rows exist in total
sqlite3 sqlite.db "SELECT COUNT(*) FROM notifications;"
# → 0

# Confirm no role-related event types exist
sqlite3 sqlite.db "SELECT event_type, COUNT(*) FROM notifications GROUP BY event_type;"
# → (empty)
```

**Fix direction:** In `programMemberRole()`, after writing the role row, insert a `notifications` row with `event_type = 'role_assigned'` (or `manager_assigned`), `channel = 'push'` (always-on in-app), `recipient_id` set to the promoted user's id, and a descriptive title/body. For email delivery, also enqueue to a queue/email provider. The Worker API (`apps/api/src/`) has a `createNotification` pattern that can serve as a reference, but the fix must go into the Go API at `api/v1/program_handlers.go`.

### Checkout Redirects Use `PUBLIC_BASE_URL`

If checkout/payment success redirects users to the old IP or `/projects/komuna/...` instead of `https://komuna.ahsanworks.com`, check the root project `.env` loaded by the Go service. `api/v1/commerce_handlers.go::createXenditInvoice()` builds Xendit callback/success/failure URLs from:

```go
base := strings.TrimRight(env("PUBLIC_BASE_URL", "http://"+r.Host+"/projects/komuna"), "/")
```

Production values should be domain-root, not the old static path:

```env
PUBLIC_BASE_URL=https://komuna.ahsanworks.com
WEB_APP_URL=https://komuna.ahsanworks.com
```

Then restart `komuna-api.service` and verify local/public health. This is backend env configuration, not a Vite basename issue when the domain HTML already injects `window.__BASENAME__="/"`.

### Xendit Paid But No Voucher Issued / Missing Purchase History

**Symptom:** User completes Xendit checkout and lands on `/wallet?payment=success&purchaseId=...`, but the wallet shows no newly issued voucher, or the paid checkout is missing/stale in member purchase history. The DB purchase remains `pending` and `/checkout/confirm` returns `vouchers_issued: 0` even though money was transferred.

**Root cause:** Komuna purchase IDs are sent to Xendit as `external_id`; they are not Xendit's invoice IDs. Calling `GET https://api.xendit.co/v2/invoices/{purchaseID}` fails validation because Xendit invoice IDs are 24-char hex strings. If `finishPurchaseCore()` relies only on that lookup, it never sees `PAID`, leaves the purchase pending, and does not insert vouchers.

**Fix pattern:** Cover both return-page confirmation and provider webhook paths:

**Fix pattern:** In `defaultFetchXenditInvoiceStatus()`, first try direct invoice lookup only when appropriate, then fall back to querying by external ID:

```go
func defaultFetchXenditInvoiceStatus(purchaseID string) string {
    key := firstEnv("XENDIT_SECRET_KEY", "XENDIT_SECRET")
    if key == "" || purchaseID == "" { return "" }
    if status := fetchXenditInvoiceStatusURL("https://api.xendit.co/v2/invoices/"+purchaseID, key); status != "" {
        return status
    }
    return fetchXenditInvoiceStatusByExternalID(purchaseID, key)
}

func fetchXenditInvoiceStatusByExternalID(purchaseID, key string) string {
    reqURL := "https://api.xendit.co/v2/invoices?external_id=" + url.QueryEscape(purchaseID)
    // GET with Basic auth, decode []map[string]any, return lowercased out[0]["status"]
}
```

Also store Xendit's real invoice `id` from invoice creation in `purchases.xendit_invoice_id` (fall back to the purchase ID only if Xendit omits it). Webhook handling should resolve purchase ID in this order: `external_id`, legacy `purchaseId`, then `SELECT id FROM purchases WHERE xendit_invoice_id = webhook.id`. This covers provider payloads that include the invoice ID but omit the external ID, so paid checkouts still update the same purchase row and appear in `/purchases` history.

2. Store Xendit's real invoice `id` when creating checkout invoices. `createXenditInvoice()` should return both `invoice_url` and `id`, then `checkout()` should persist `xendit_invoice_id=<real Xendit id>` instead of writing the local `pur-...` purchase ID into that column.
3. Make `paymentWebhook()` robust to webhook payloads that include `id` but omit `external_id`: resolve the local purchase with `SELECT id FROM purchases WHERE xendit_invoice_id=?`, then call `finishPurchase()`. This keeps the member purchase history accurate even if Xendit sends only the provider invoice ID.

**Regression check:** Add a Go test that inserts a pending purchase with `xendit_invoice_id='xendit-invoice-1'`, posts `POST /api/v1/payments/xendit/webhook` with only `{ "id": "xendit-invoice-1", "status": "PAID" }`, then calls authenticated `GET /api/v1/purchases` and asserts the purchase appears with `status='paid'` and the correct `program_id`. This catches the provider-ID-only webhook path that normal `/checkout/confirm` tests miss.

**Recovery for affected users:** Re-run confirmation for the paid purchase after deploying the fix:

```bash
curl -sS -X POST http://127.0.0.1:8095/api/v1/checkout/confirm \
  -H 'Content-Type: application/json' \
  -d '{"purchaseId":"pur-..."}'
```

Then verify:

```sql
SELECT id,total_amount,status,created_at FROM purchases WHERE id='pur-...';
SELECT id,purchase_id,product_id,status,expired_at,created_at FROM vouchers WHERE purchase_id='pur-...';
```

Expected: purchase `status='paid'` and voucher rows with `source='purchase'` / `status='active'`.

### Checkout Role Eligibility: Admins Can Buy Their Own Program Packages

When asked whether an admin/manager can buy a package from their own program, the current Go checkout path allows it as long as the user has a `program_members` row for the package's program. `commerce_handlers.go::checkout()` authenticates via `requireUser`, loads the package's `program_id`, then checks only:

```sql
SELECT id FROM program_members WHERE program_id=? AND user_id=?
```

There is no role-based block for admins or product managers. Therefore:
- Program admin who is also a program member: can buy.
- Product manager who is also a program member: can buy.
- Regular member: can buy.
- Platform superadmin without program membership: cannot buy; checkout returns `not_a_member`.

If the business rule changes to prevent self-purchase by admins/managers, the fix belongs in the Go API checkout path before inserting `purchases`, not only in frontend button visibility.

### Wallet Route Canonicalization

The canonical member wallet page is `/wallet`. Do not create or keep program-scoped duplicate wallet pages such as `/programs/:id/member/wallet`; the wallet is user-wide, not program-scoped. If a legacy route exists, redirect it to `/wallet` and update member dashboard/payment-return links to `/wallet`. Remove wallet from program workspace navigation if it implies a separate program wallet.

### Member Dashboard Shows Program-Wide Active Voucher Count

**Symptom:** A newly signed-up member joins a program and the member dashboard shows active vouchers (for example `12`) while `/wallet` is empty.

**Root cause:** `memberDashboard()` counted all active vouchers for the program:
```sql
SELECT COUNT(*) FROM vouchers v
JOIN products p ON p.id=v.product_id
WHERE p.program_id=? AND v.status='active'
```
That is an admin/program inventory metric, not the member's wallet count. Wallet correctly filters through the current user's `program_members` row.

**Fix pattern:** Scope member dashboard voucher stats to the authenticated user and program membership:
```go
u, ok := a.requireUser(w, r)
if !ok { return }
a.db.QueryRow(`SELECT COUNT(*) FROM vouchers v
  JOIN program_members pm ON pm.id=v.program_member_id
  WHERE pm.program_id=? AND pm.user_id=? AND v.status='active'`, pid, u.ID).Scan(&vcount)
```
Do not join only through `products` for member-facing counts; that leaks other members' vouchers into the displayed total.

**Verification:** For the reported user, compare DB counts before/after:
```sql
-- expected wallet/dashboard count
SELECT COUNT(*) FROM vouchers WHERE program_member_id=? AND status='active';
-- buggy old dashboard count
SELECT COUNT(*) FROM vouchers v JOIN products p ON p.id=v.product_id WHERE p.program_id=? AND v.status='active';
```
Then call `/api/v1/programs/<program>/member/dashboard` and `/api/v1/wallet` with the same Bearer token; the dashboard `active_voucher_count` should match the user's wallet count, not the program total.

### Admin Packages Tab Blank Page / Missing Package Entries

**Symptom:** A program admin opens `/programs/:id/admin/packages` and the tab renders blank. Example: Lina Marlina as Balikpapan Coastal Yoga Studio admin.

**Root cause:** The Go API package list endpoint (`program_handlers.go::programPackages`, `GET /programs/:id/packages`) returns package rows from `scanPackage(rows)`, but `scanPackage` omits the `entries` array. The frontend `PackagesPage.tsx` treats `PackageDTO.entries` as required and calls `p.entries.length` and `pkg.entries.map(...)`, so `entries: undefined` causes an uncaught render error/blank page. The DB can still have valid `package_entries`; the list DTO is just incomplete. `packageByID()` already includes `entries`, so single-package/detail-style responses may look correct while the list crashes.

**Check:**
```bash
curl -sS http://127.0.0.1:8095/api/v1/programs/<program-id>/packages | python3 -m json.tool
sqlite3 sqlite.db "SELECT pp.id, pp.name, COUNT(pe.id) FROM purchase_packages pp LEFT JOIN package_entries pe ON pe.package_id=pp.id WHERE pp.program_id='<program-id>' GROUP BY pp.id"
```
If JSON rows lack `entries` but SQL shows rows in `package_entries`, this is the bug.

**Fix pattern:** Make the list endpoint return full `PackageDTO` rows with `entries: []` at minimum, preferably by reusing a helper that loads package entries for each package. Do not hide the frontend crash with optional chaining only; the API contract says `entries` is required. Add a regression test for `GET /programs/:id/packages` asserting every package has an array `entries` field, including programs/packages with zero entries.

### Admin Products Tab Edit CTA / Missing Edit Form

When the user reports the Products tab **Manage** CTA opens the public/showcase product page, or asks whether product editing already exists:
- First inspect `apps/web/src/pages/ProductsPage.tsx` before implementing. The page may already contain a full **create** form and unused i18n edit strings (`admin.products.editHeading`), but that is not evidence of a working edit flow.
- Current broken pattern to look for: a row action rendered as a React Router `Link` with `data-testid="manage-link"` pointing to `/programs/${programId}/products/${product.id}`. That route is the public product detail/showcase page, not an admin edit form.
- A functional fix is not label-only. Replace the CTA with an **Edit** button that stays on the admin Products tab, sets an explicit edit mode (`editingProductId` or equivalent), prefills the existing form state, uses the `editHeading`, and submits via an update endpoint.
- Check the production Go API (`api/v1/program_handlers.go::programProducts`) before promising persistence. If it only supports GET list/detail, POST create, archive/unarchive, sessions, and template routes, add a product update route such as `PUT /api/v1/programs/:programId/products/:productId` with validation and a response from `a.productByID(realProductID, true)`.
- Keep product edit schema-safe by default: for weekly schedules, reuse/upsert the existing `session_templates(product_id, weekly_slots)` row instead of adding product-table columns unless the plan explicitly requires a new column/table. Use `INSERT ... ON CONFLICT(product_id) DO UPDATE` after validating slots, and avoid any `DROP TABLE`, `DELETE FROM`, `TRUNCATE`, or DB-file replacement.
- Before deployment, run a destructive-SQL diff scan and a live DB shape/count check. The live DB is `/home/ubuntu/projects/komuna/sqlite.db`; `api/v1/sqlite.db` can be an empty/local artifact and may not contain production tables. Example checks: `git diff -- . ':(exclude).hermes/plans/*' ':(exclude)docs/*' | grep -Ei 'drop table|delete from|truncate|alter table|create table|sqlite.db|rm -rf' || true` and `sqlite3 /home/ubuntu/projects/komuna/sqlite.db "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('products','session_templates'); SELECT count(*) FROM products;"`.
- Regression tests should cover both layers: frontend test clicks the row Edit CTA, asserts no navigation to `/programs/:id/products/:productId`, sees a prefilled edit form, saves via `apiClient.put`, and updates the row; Go test sends PUT and verifies SQLite persistence after refresh. If only a frontend regression is added, still run `go test ./...`, `go build -o ../server .`, `npm run test -- ProductsPage`, and `env -u VITE_NEON_AUTH_URL npm run build`.
- If the user explicitly asks for a design/plan first when no working edit form exists, stop after publishing the plan/review artifact and wait for approval; do not implement/deploy from the investigation alone.
- For product time schedules, make the spec explicit that weekly schedule entries belong in the product create form and edit form, are persisted in the database (not just frontend state), and are validated on both frontend and backend. If the agreed UI uses schedule entries/rows, allow one row to select multiple weekdays when they share the same start/end time, then flatten that row to one `weekly_slots` item per weekday in the API payload. A weekday selected in any row must be disabled/blocked in every other row for the same product unless the user later approves multiple time slots per day. In edit mode, group persisted weekly slots with the same start/end time back into one multi-day row so the UI matches the plan. Validate weekly slots fully before updating the product row so duplicate/invalid schedules cannot leave a partial product edit behind. Prefer the existing `session_templates(product_id, weekly_slots)` upsert over new schema unless the plan explicitly approves a new table/column.
- Product create/edit manager assignment rule: every product must have at least one active program member manager selected in the form. Persist assignments in both `product_managers` and product-scoped `program_member_roles(role='manager', product_id=...)`; `/programs/:id/products` and product detail DTOs should return `manager_ids` so edit forms can preselect current managers. Backend create/update should reject empty `managerIds` with `manager_required` and validate each selected user has an active `program_members` row for that program before inserting the product or committing product edits. Use one transaction for product row + manager rows + weekly template upsert so validation failures do not leave partial products/templates. For existing live products without managers, back up `sqlite.db` and backfill only when a program has an active admin/member available; report any remaining products whose programs have no assignable member instead of inventing placeholder users.
- When the user approves spec answers or asks for implementation after a design-review loop, update only the implementation/spec files needed for that task. Do **not** redraw or republish design artifacts unless the user explicitly asks for design changes; this user treats unrequested design-page changes as regressions.

### Package Edit/Create-Version Entry Persistence

When debugging or changing the packages admin form (`apps/web/src/pages/PackagesPage.tsx`) and Go package endpoint (`api/v1/program_handlers.go::programPackages`):
- Package edits are intentionally immutable/versioned: the frontend posts to `POST /programs/:id/packages` with `supersedesId`, then the new package should replace the old active version.
- The backend must persist both the package header and every submitted entry in `package_entries` inside one transaction. Do not insert only `purchase_packages`; that creates a visible new package with missing entries.
- Store `supersedes_id` and archive the superseded package server-side, not only by optimistic frontend state.
- Preserve entry fields from the form: `productId`, `quantity`, `benefitType`, `validityType`, and `validityValue`. Missing `benefitType` currently defaults to `voucher`, so frontend subscription work must explicitly send `benefitType: 'subscription'`.
- Regression test pattern: `POST /api/v1/programs/prog-box/packages` with `supersedesId` and one entry; assert response includes `supersedes_id`, non-empty `entries`, matching `package_id`, and old package `status='archived'`.

### Package Subscription / Entitlement Implementation

When implementing subscription package entries in Komuna:
- Keep `Package` and `Voucher` separate: packages are sellable containers, vouchers are one redeemable benefit type. A subscription entry should create a `subscriptions` row, not a special voucher row.
- Admin package UI should send explicit `benefitType: 'voucher' | 'subscription'`. Do not infer subscription from the old `UNLIMITED_QTY = 999` checkbox; hide/disable quantity for subscription entries and persist quantity as `1`.
- Paid checkout issuance belongs in `api/v1/commerce_handlers.go::finishPurchaseCore()`: for each paid `package_entries` row, create vouchers for `benefit_type='voucher'` and create one product-specific `subscriptions` entitlement for `benefit_type='subscription'`. Include `subscriptions_issued` in `/checkout/confirm` by counting `subscriptions.purchase_id`.
- Booking fallback belongs in `api/v1/booking_handlers.go::createClaim()`: try FIFO active vouchers first; if none match, find an active `subscriptions` row for the same `product_id` and current user, then insert `voucher_claims(subscription_id, session_id, claimant_id, created_at)` without consuming a voucher.
- SQLite live schema pitfall: current `voucher_claims.attendance_status` CHECK allows only `present`/`absent` (or NULL). For new subscription claims, omit `attendance_status` in the INSERT and return synthetic JSON with `attendance_status: 'pending'` to the frontend. Do not insert literal `'pending'` unless the live schema has been migrated.
- Wallet subscriptions should be returned from `/wallet` alongside voucher pockets. Keep cancellation on canonical `/wallet`, with a user-scoped endpoint like `POST /wallet/subscriptions/:id/cancel` that updates only subscriptions owned by the authenticated user's `program_members` rows.
- Regression test pattern: create a paid purchase containing a subscription package entry, assert `finishPurchaseCore()` creates one `subscriptions` row and zero vouchers, then POST `/claims` for a matching session and assert `voucher_claims.subscription_id` is populated; also test wallet cancellation changes status to `cancelled`.
- Review-plan artifacts for this class should include open approval questions about: cancel-at-period-end policy vs immediate cancellation, renewal/payment retry behavior, product-specific vs program-wide subscriptions, and immutable billing-type changes.

### Admin Packages Visibility / Archive Toggle

When changing admin package list visibility in `apps/web/src/pages/PackagesPage.tsx`:
- Archived packages should be hidden by default when the user asks for the package list to focus on current sellable packages.
- Use a simple boolean toggle such as **Show archived packages** instead of a three-state status filter unless the user explicitly asks for filtering by status.
- Keep active packages at the top by sorting visible rows with active rows before archived rows; preserve the rest of the existing order where possible.
- After archiving an active package, it should disappear from the default list immediately; when the toggle is on, archived rows remain visible with their archived badge/unarchive action.
- Update `apps/web/src/__tests__/PackagesPage.test.tsx` expectations: default row count excludes archived rows, toggling shows archived rows, archive action removes the row from default view, and edit/versioning tests should toggle archived visibility before asserting the superseded package row.
- Verify with `npm run test -- PackagesPage && npm run build`, deploy `apps/web/dist/`, then confirm the public bundle contains the toggle label before commit/push.

### Admin Packages Tab Mobile Layout / Summary Cards

When fixing the packages admin tab (`apps/web/src/pages/PackagesPage.tsx`) for mobile overflow or clipped form controls:
- Prefer the smallest CSS-led patch in the same component: add stable class hooks to existing inline-styled wrappers (`packages-page`, `packages-stats`, `packages-form-card`, `packages-form-grid`, `packages-entry-card`, `packages-entry-grid`, `packages-validity-row`) and override them in the component's existing `<style>` block.
- Desktop package statistic cards should stay in one row when there are four stats (`repeat(4, minmax(0, 1fr))`). Only override mobile to two columns per row (`repeat(2, minmax(0, 1fr))`) when requested.
- On narrow screens, keep each package entry as two rows: product + quantity on row 1, validity rule + numeric value/unit on row 2. Do not stack every control into one column unless the user explicitly asks; it feels messy and wastes vertical space.
- Add `box-sizing: border-box` scoped to `.packages-page` so `width: '100%'` inputs with padding do not create horizontal overflow.
- Verify with `npm run test -- PackagesPage && env -u VITE_NEON_AUTH_URL npm run build`, deploy `apps/web/dist/`, and grep the public bundle for the package layout class markers before commit/push.

### Admin Packages Tab Blank Page

**Symptom:** A program admin opens `/programs/:id/admin/packages` and the tab/page is blank. The API may still return `200 OK` for `/api/v1/programs/:id/packages`.

**Root cause:** The frontend `PackagesPage` treats `PackageDTO.entries` as required and renders `pkg.entries.length` / `pkg.entries.map(...)`. The Go list handler `programPackages()` can silently omit `entries` if it appends `scanPackage(rows)` directly. That creates a runtime render crash even though the package rows exist.

**Debug check:**
```bash
curl -sS https://komuna.ahsanworks.com/api/v1/programs/<program-id>/packages \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print([(p["id"], p.get("entries")) for p in d["data"]])'
```
If `entries` is missing or `null`, the frontend contract is broken. Compare with DB entries:
```sql
SELECT pp.id, pp.name, COUNT(pe.id)
FROM purchase_packages pp
LEFT JOIN package_entries pe ON pe.package_id=pp.id
WHERE pp.program_id='<program-id>'
GROUP BY pp.id;
```

**Fix pattern:** Make the list endpoint return the same full package DTO shape as `packageByID()` so every package has `entries: []` or populated entries. Also scan nullable `supersedes_id` with `sql.NullString`; scanning SQLite NULL into `*string`/plain string can make `packageByID()` return `nil` and hide entries. Add a Go regression test that GETs `/api/v1/programs/prog-box/packages` and asserts each item has non-nil `entries` with matching `package_id`.

### Package Edit Creates New Version But Drops Entries

**Symptom:** Editing an admin package creates a new package row, but the entry/product chips are empty on the new package.

**Root cause:** Package edits intentionally create a new version: `PackagesPage.tsx` posts to `POST /programs/:id/packages` with `supersedesId` and `entries`. If the Go API `programPackages()` POST handler only inserts `purchase_packages` and ignores `entries`, the returned DTO has `entries: []` because no `package_entries` rows were created. If the server also ignores `supersedesId`, archival/versioning happens only optimistically in frontend state and can drift after refresh.

**Fix pattern:** In the production Go API (`api/v1/program_handlers.go`), handle package creation/versioning in one DB transaction:
1. Decode `name`, `price`, optional `supersedesId`, and submitted `entries`.
2. Insert `purchase_packages` with `supersedes_id` set from `supersedesId`.
3. Insert one `package_entries` row per submitted entry (`productId`, `quantity`, optional `benefitType`, `validityType`, nullable `validityValue`).
4. If `supersedesId` is present, archive the old package server-side with `UPDATE purchase_packages SET status='archived' WHERE id=? AND program_id=?`.
5. Commit, then return `a.packageByID(pkgID)` so the frontend receives the persisted entries.

**Regression check:** Add a Go test that POSTs `/api/v1/programs/prog-box/packages` with `supersedesId` and an `entries` array, asserts the response has `supersedes_id`, one matching `entries[]` item, and that the old package is now `archived`. Run `go test ./... && go build -o ../server .`, restart `komuna-api.service`, and verify local/public health.

### Dashboard Shows "No assigned products" for Managers

**Symptom:** Manager logs in, navigates to a program, sees "No assigned products are available for this program."

**Root cause:** The workspace handler (`/me/workspace`) reads manager product assignments from `program_member_roles.product_id`, NOT from the `product_managers` table. If `program_member_roles` has `role='manager'` but `product_id IS NULL`, the workspace returns roles without `productId` → frontend shows empty state.

**Check:**
```sql
-- Manager roles with NULL product_id (these are broken)
SELECT pmr.id, pmr.program_member_id, pmr.product_id, u.email
FROM program_member_roles pmr
JOIN program_members pmm ON pmr.program_member_id = pmm.id
JOIN users u ON pmm.user_id = u.id
WHERE pmr.role = 'manager' AND (pmr.product_id IS NULL OR pmr.product_id = '');

-- Compare against product_managers (which has the real assignments)
SELECT pm.program_member_id, pm.product_id, u.email
FROM product_managers pm
JOIN program_members pmm ON pm.program_member_id = pmm.id
JOIN users u ON pmm.user_id = u.id;
```

**Fix:** Backfill `program_member_roles.product_id` from `product_managers` where the manager role's `product_id` is NULL. One `program_member` can manage multiple products — each gets its own `program_member_roles` row with the specific `product_id`.

**⚠ Multi-product pitfall:** If a manager has 1 row in `program_member_roles` (with NULL product_id) but 2 rows in `product_managers` (prod-A, prod-B), do NOT just UPDATE the single role row. That would only cover one product — the other stays invisible. Instead:

```sql
-- Step 1: UPDATE the existing NULL row for the first product
UPDATE program_member_roles
SET product_id = (SELECT product_id FROM product_managers WHERE program_member_id = ? LIMIT 1)
WHERE program_member_id = ? AND role = 'manager' AND product_id IS NULL;

-- Step 2: INSERT new rows for any additional products (skip the first)
INSERT INTO program_member_roles (id, program_member_id, role, product_id)
SELECT 'pmr-' || printf('%04x', abs(random()) % 65536),
       pm.program_member_id, 'manager', pm.product_id
FROM product_managers pm
WHERE pm.program_member_id = ?
  AND pm.product_id NOT IN (
    SELECT product_id FROM program_member_roles
    WHERE program_member_id = pm.program_member_id AND role = 'manager'
  );
```

Run the check query again after the fix — zero rows with NULL product_id means success.

### Pre-filling Sessions with Bookings

When testing requires booked members in a session, create voucher_claims directly. See `references/session-booking-flow.md` for the complete data flow and SQL patterns (vouchers → claims → sessions.taken).

Quick pattern:
1. Find or create giveaway vouchers for members scoped to the session's product
2. Create `voucher_claims` rows linking vouchers to the session
3. Mark vouchers `claimed`
4. Update `sessions.taken` to match claim count
5. Always stop service + backup DB first

### Go `http.ServeMux` Route Conflict — Same Path, Different Methods

**Symptom:** Service panics on startup with `pattern "/api/v1/profile/picture" conflicts with pattern "/api/v1/profile/picture"` even though the two registrations use different HTTP methods (e.g., one POST, one DELETE).

**Root cause:** Go's `http.NewServeMux` (pre-1.22) registers handlers by **path**, not by method. Registering `HandleFunc("/api/v1/profile/picture", wrap("POST", fn1))` and `HandleFunc("/api/v1/profile/picture", wrap("DELETE", fn2))` both register the same path pattern → panic at `mux.HandleFunc`. The method check inside `wrap` happens too late — the mux panics during registration.

**Fix:** Use a single `"*"` method handler and dispatch by `r.Method` internally:
```go
// Route — single registration
h("/profile/picture", "*", a.profilePicture)

// Handler — dispatch internally
func (a *App) profilePicture(w http.ResponseWriter, r *http.Request) {
    if r.Method == "DELETE" {
        a.profilePictureDelete(w, r)
        return
    }
    if r.Method != "POST" {
        errOut(w, 405, "method_not_allowed")
        return
    }
    // POST logic...
}
```

This follows the same pattern already used by `sessionTree`, `notificationTree`, and `claimTree` — a single `"*"` handler that parses URL sub-paths and dispatches.

### SQLite ALTER TABLE Idempotency

**Symptom:** After a mid-migration crash (e.g., the route-conflict panic above), the ALTER TABLE already ran but the service panicked before starting. On restart, the ALTER TABLE fails with `SQL logic error: duplicate column name` and the service won't boot.

**Root cause:** SQLite doesn't support `IF NOT EXISTS` for `ALTER TABLE ADD COLUMN`. The schema execution loop in `NewApp()` treats every error as fatal.

**Fix:** Make the schema loop tolerate "duplicate column name" errors from ALTER TABLE:
```go
for _, q := range schema() {
    if _, err = db.Exec(q); err != nil {
        // Ignore "duplicate column name" errors from ALTER TABLE (idempotent schema)
        if strings.Contains(q, "ALTER TABLE") && strings.Contains(err.Error(), "duplicate column") {
            continue
        }
        return nil, fmt.Errorf("schema: %w (sql: %s)", err, q[:min(80, len(q))])
    }
}
```

This lets the service restart cleanly after a mid-migration crash without manual DB intervention.

### Go `rows.Scan` Silent Failure with SQLite NULL Columns

## Go nil slice → JSON `null` pitfall

When building a JSON response with a slice that may be empty:

```go
// BROKEN — nil slice marshals to null, crashes frontend .length/.map calls
var cards []any
for rows.Next() { cards = append(cards, ...) }
jsonOut(w, map[string]any{"items": cards, ...})
// → "items": null  (if zero rows matched)

// FIXED — empty slice marshals to [] 
cards := []any{}
for rows.Next() { cards = append(cards, ...) }
// → "items": []
```

**Symptoms:** Frontend blank page on filtered views with zero results (e.g., "ongoing" tab with no sessions). Console: `TypeError: Cannot read properties of null (reading 'length')`. React unmounts after uncaught render error.

**Affected handlers:** `programSessions` (line 236) and any handler that conditionally appends to a nil-initialized slice. Always initialize with `:= []any{}` or `:= make([]any, 0)`.

### Go `rows.Scan` Silent Failure with SQLite NULL Columns

**Symptom:** API endpoint returns some fields populated (e.g., `id`, `voucher_id`) but ALL subsequent columns are empty/null (e.g., `member_name: null`, `member_email: ""`, `member_id: ""`). The DB query run directly in sqlite3 returns correct data, but the API response is empty.

**Root cause:** Scanning a SQLite NULL value into a plain Go `string` variable causes `rows.Scan` to fail silently **for all remaining columns**. If column 5 (`alias`) is NULL, columns 6–12 (`attendance_status`, `cancelled_at`, ..., `member_name`) all stay at their zero values (empty string). Because the Go code at `main.go:1162` ignores the `rows.Scan` error return, this failure is invisible — the row is still appended to the array with empty fields.

**Check:** Scan errors are silent when the error return is dropped:
```go
// BROKEN — ignores scan error, silent corruption
rows.Scan(&id, &vid, &subID, &sessionID, &alias, &att, &cancelled, ...)
```

**Fix:** Use `sql.NullString` for all nullable columns AND check the error:
```go
// FIXED — sql.NullString for nullable columns, error check
var subID, alias, att, cancelled sql.NullString
if err := rows.Scan(&id, &vid, &subID, &sessionID, &alias, &att, &cancelled, ...); err != nil {
    continue  // skip rows that fail scan
}
attendance := "pending"
if att.Valid && att.String != "" {
    attendance = att.String
}
```

**Affected columns** (any of these being NULL silently corrupts all columns scanned after them): `vc.alias`, `vc.attendance_status`, `vc.cancelled_at`, `vc.subscription_id`.

**Practical consequence:** `claimByID()` (line 1827) returns `nil` for most claims because `cancelled_at` is commonly NULL. When writing new endpoint code, avoid calling `claimByID` — construct a synthetic JSON response instead. Only use it for claims you know have non-NULL `cancelled_at`.

**Debugging approach:** Add a one-line `log.Printf` after the scan to see if values are populated, then rebuild + restart + curl. If the log shows empty strings but sqlite3 shows real data, the scan is failing on a nullable column earlier in the list.

### Restricted Route Auth Guards — Demo User Fallback Leaks

**Symptom:** Opening restricted pages as a guest returns `200 OK` data, empty account pages, platform metrics, or dashboard payloads instead of redirecting to login / returning `401`.

**Root cause:** The Go API's `currentUser()` helper falls back to the configured demo/default user when no real session exists. Restricted handlers must not call it directly.

**Fix:** Use a strict `requireUser(w, r)` helper in restricted handlers and return `401 auth_required` when no bearer/cookie session exists. Add a table-driven unauthenticated regression test for workspace, wallet, purchases, bookings, notifications, profile preferences, platform dashboard, and program admin/member/manage routes. Wrap direct frontend routes (`/wallet`, `/my/bookings`, `/notifications`, `/settings/notifications`, `/profile`) with an auth guard so guests redirect to sign-in instead of seeing page-level errors.

See `references/restricted-route-auth-guards.md` for the compact pattern and route checklist.

### Frontend Route Auth Guards — "??" and "User" After Sign-Out

**Symptom:** After signing out, pressing back in browser loads a dashboard URL. Top bar shows `'??'` avatar and `'User'` name instead of real user info. User can still access dashboard pages.

**Root cause:** `WorkspaceRoute` (the component wrapping all `/programs/:id/admin`, `/programs/:id/manage`, `/programs/:id/member` routes) had no auth check. It rendered `DashboardShell` unconditionally, and `ProfileMenu` fell back to `getInitials(null) = '??'` and `displayName = 'User'` when `authClient.useSession()` returned `{data: null}` (localStorage cleared by sign-out).

**Fix:** Add `authClient.useSession()` check with `<Navigate to="/auth/sign-in" replace />` when session is null. Same pattern applies to any protected route.

**Affected files:** `apps/web/src/components/routing/WorkspaceRoute.tsx` (fixed). Several standalone pages (`/wallet`, `/profile`, `/my/bookings`, `/notifications`) also lack auth guards — they show error states instead of redirecting.

#### Backend Auth Fallback Leak (`currentUser()`)

**Symptom:** An unauthenticated browser can open restricted pages or call restricted APIs and receive `200 OK` data instead of being redirected/signaled as unauthenticated. Examples to audit: `/me/workspace`, `/wallet`, `/purchases`, `/my/bookings`, `/notifications`, `/notifications/unread-count`, `/notifications/preferences`, `/profile/preferences`, `/platform/dashboard`, `/programs/:id/member/dashboard`, and mutating actions such as `/programs/:id/join`.

**Root cause:** Handlers call `currentUser(r)`, which falls back to `a.userID/a.userEmail/a.userName` (demo/default user) when no bearer token or `komuna_session` cookie exists. That helper is unsafe for production restricted routes; it masks missing auth and can leak demo/default-user data.

**Audit pattern:** Probe unauthenticated with a browser-like user agent so Cloudflare does not block the diagnostic request before it reaches the app:
```bash
curl -sS -H 'Accept: application/json' -H 'User-Agent: Mozilla/5.0' \
  -i https://komuna.ahsanworks.com/api/v1/wallet
```
Expected for restricted routes is `401` (or `403` for role-only platform/admin routes), not `200` with empty/demo data. Also probe `http://127.0.0.1:8095/api/v1/...` to distinguish app behavior from Cloudflare.

**Fix pattern:** For restricted handlers, use `userFromRequest(r)` directly and return `errOut(w, 401, "auth_required")` when it fails. Only use `currentUser(r)` for intentional dev/demo fallback paths. For public list/detail DTOs, keep using explicit membership helpers that return `nil` when unauthenticated.

See `references/frontend-auth-guards.md` for the full auth architecture, route audit, and verification commands.

### Spec Gap / "What's Not Done" Reviews

When the user asks what Komuna is missing against the spec, audit the **production Go API first** (`api/v1/`), not only `apps/api/` roadmap checkboxes. Use this compact sequence:
1. Read `komuna-community-session-bookings.md` for the authoritative product spec and `API.md` for explicit unchecked roadmap items.
2. Treat `API.md` Phase 10 unchecked items as high-confidence gaps: Xendit refunds, Xendit payouts, push dispatch, SMS dispatch, BetterStack logging, and R2 uploads unless production Go code proves otherwise.
3. Confirm against `api/v1/*.go` because production nginx serves the Go API. Look for stub/shallow handlers: `platform_handlers.go::voucherAction()` only marks vouchers refunded, `platformDashboard()` can return hardcoded `total_gmv` / `total_platform_fees`, `bookingRequestAction()` may return success without creating a claim, and join/booking approvals may omit notifications.
4. Include scheduled/async spec gaps that may not have routes: voucher-expiring reminders, 24h/1h session reminders, weekly schedule-change broadcasts, payment retry/backoff, manual payment reconciliation, and PPN invoice/receipt generation.
5. Report as a concise gap list with evidence from spec + file/function, and avoid implying Worker-only implementations are live unless they are deployed in the Go path.

### Verification Checklist

- [ ] `go test ./...` passes before deploying
- [ ] `go build -o ../server .` succeeds
- [ ] `sudo systemctl restart komuna-api.service` completes
- [ ] Internal health: `curl -sS http://127.0.0.1:8095/api/v1/health`
- [ ] Public programs: `curl -sS https://komuna.ahsanworks.com/api/v1/programs`
- [ ] Login test: sample user via `POST /api/v1/auth/sign-in`
- [ ] Workspace test: `GET /api/v1/me/workspace` with Bearer token for role verification
- [ ] Git committed and pushed after meaningful changes
- [ ] Database was NOT deleted — only modified via Python/SQLite if needed
