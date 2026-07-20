# Discovery redesign: merchandising and deployment

Use when promoting an approved Discovery prototype into the live React + Go/SQLite app.

## Merchandising semantics

Build all sections from one consistent candidate set and enforce cross-section uniqueness with a shared ID set.

- **Most Popular:** active membership count DESC, completed-join count DESC, `created_at` DESC, name, ID.
- Active means `program_members.status='active'` only.
- Completed joins include `active`, `inactive`, and `banned`; exclude `pending` and `left`.
- **New Programs:** exclude Popular IDs, then `created_at` DESC with stable name/ID tie-breaks.
- **Open to Join:** exclude used IDs; retain only `visibility='public'` (approval-free); Fisher–Yates shuffle a copy using injectable RNG; sample once after successful fetch, not during render.
- Never classify `need_approval` as Open to Join and never use ratings as a substitute for membership popularity.
- Do not silently merchandise from a truncated page. Verify the list endpoint’s maximum and catalog size, or add a narrow complete-candidate contract.

## Category deep links

The Discovery category link and Programs filter must share one allowlist of exact category IDs. Use `/programs?category=<id>`, initialize filter state from `useSearchParams`, synchronize selection back to the URL, remove the parameter for All, and fall back safely on unknown values.

## Prototype-to-live guard

Reuse `TopNav`, `Footer`, DTOs, image fallback, i18next, theme state, and Router links. Keep prototype HTML as reference only. Verify carousel lifecycle, one footer landmark, compact whole-card links, mobile rail boundaries, and unrelated routes.

## Deployment verification

1. Build from `apps/web`; deploy `apps/web/dist/` to the configured nginx root.
2. Inspect `systemctl status`/unit details before installing an API binary. The active Komuna unit executes `/home/ubuntu/projects/komuna/api/server`; installing another binary path does not deploy it.
3. Build Go from `api/v1`, install to the unit’s actual `ExecStart`, restart, then verify the listening port and `/api/v1/programs` DTO fields.
4. Verify the public HTML references the new hashed JS/CSS, category URLs return 200, and the live API exposes `memberCount`, `joinedMemberCount`, `lowestPrice`, and `visibility`.
5. If broad suites fail, isolate feature regressions from unrelated environment-backed tests. For example, checkout tests may require payment configuration; report that blocker but do not treat it as a Discovery failure. Never claim screenshot QA when browser automation was unavailable.
