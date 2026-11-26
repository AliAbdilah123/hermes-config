---
name: open-design-design-systems
description: >-
  Author, extract, or update design-system packages in the self-hosted OpenDesign
  catalog behind designs.ahsanworks.com on this VPS. USE WHEN the user asks to
  "recreate <app>'s design in designs.ahsanworks.com / OpenDesign", add or extract
  a design system for the catalog, or otherwise author DESIGN.md + tokens.css +
  components.html + manifest.json packages. Covers repo location, the v1 package
  contract + manifest schema, the token-layer rules, and extracting a live app's
  real tokens from its shipped CSS.
---

# OpenDesign design-system packages

`designs.ahsanworks.com` is **not** a normal prod deploy target. It is the
self-hosted OpenDesign tool: nginx `basic_auth` + `proxy_pass` to
`127.0.0.1:7461`. The repo is `/home/ubuntu/projects/open-design` (git-clean,
`main`). An older copy also exists under `/home/ubuntu/videos/open-design`; the
live one serving port 7461 is `/home/ubuntu/projects/open-design`.

Catalog dirs inside the repo:
- `design-systems/<slug>/` — ~150 bundled design-system packages.
- `design-templates/` and `skills/` — templates and skills (sibling concerns).

## Package contract (v1)

Every `design-systems/<slug>/` package must ship, at minimum:

- `DESIGN.md` — canonical design prose (color, typography, spacing, components, anti-patterns).
- `tokens.css` — compiled `:root` token block.
- `components.html` — standalone component fixture.
- `manifest.json` — machine-readable discovery entry.

Optional: `USAGE.md`, `design-tokens.json`, `tailwind-v4.css`,
`components.manifest.json`, `preview/` (typically colors/typography/spacing
pages, indexed from `manifest.json` `preview.pages`), `assets/`, `fonts/`, `source/`.

`manifest.json` v1 fields (full schema: `design-systems/_schema/manifest.schema.ts`):
`schemaVersion:"od-design-system-project/v1"`, `id` (slug matching
`/^[a-z0-9-]+$/`), `name`, `category`, `description`, `source` (`bundled` |
`local` | `github` | `shadcn`), `files` (`design:"DESIGN.md"`,
`tokens:"tokens.css"`, optional `designTokens`/`tailwind`/`components`),
optional `usage`, `componentsManifest`, `craft`, `preview`, `sourceFiles`.
Unknown keys at any level fail validation — stick to the schema.

## Token rules (read `design-systems/_schema/AGENTS.md`)

There is **no shared global stylesheet** — every package's `tokens.css` must
declare every required token in its own `:root`, else artifact pastes silently
break.
- A1 identity (guard fails if missing): `--bg`, `--fg`, `--accent`,
  `--font-display`, type scale, `--container-max`.
- A2 (fallback exists, but must still be declared today): `--success`/`--warn`/
  `--danger`, `--font-mono`, `--space-*`, `--radius-*`, `--elev-*`, `--motion-*`,
  `--accent-on/hover/active` (defaults in `_schema/defaults.css`).
- B-slot (alias `var(--sibling)` or an independent value): `--fg-2`,
  `--surface-warm`, `--meta`, `--border-soft`.

## Catalog refresh

Scanned on every `/api/design-systems` request; refresh the Design System
surface after editing a package — no daemon restart needed.

## Extracting a live app's design (recreate)

1. Confirm it is absent first by checking for a `design-systems/<slug>/` dir with
   a `manifest.json` — do NOT rely on `grep -r <name>` alone, which
   false-positives on unrelated script/doc text.
2. Read the app's **shipped** CSS token block (for the Orchestrator app:
   `/home/ubuntu/projects/orchestrator/internal/httpapi/static/orchestrator-v4.css`
   has a full `:root` set incl. `html.dark` overrides).
3. Map the app's custom token names onto the required A1/A2/B-slot names, write
   `tokens.css`, derive `DESIGN.md` prose from the actual colors/type/spacing,
   `components.html` from the real UI views, and add `manifest.json` + preview pages.

## Pitfalls

- The nginx vhost lives at `/etc/nginx/projects/open-design-domain.conf`
  (server_name `designs.ahsanworks.com`, basic-auth), not in `sites-enabled`/`conf.d`.
- The daemon may also run under `/home/ubuntu/videos/open-design`; prefer editing
  `/home/ubuntu/projects/open-design` (the live one backing port 7461).