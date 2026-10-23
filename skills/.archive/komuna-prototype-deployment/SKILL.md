---
name: komuna-prototype-deployment
description: >
  Create previewable React prototype pages inside the Komuna web app and ship them
  to static hosting under `/projects/komuna/` on `dev.ahsanworks.com`.
  Use this whenever the task is a one-off UI prototype, design proof,
  or standalone preview that does not need production auth/data.
  Trigger: “add a prototype”, “preview page”, “design prototype”, deploy UI proof.
---

# Komuna Prototype Deployment

Goal: fast iteration on standalone UI prototypes without modifying production
flows or auth, with a stable preview URL under the Komuna nginx prefix.

## Route & Structure

- New prototype page: `apps/web/src/prototypes/<feature>/<Feature>PrototypePage.tsx`
- CSS: `apps/web/src/prototypes/<feature>/<Feature>Prototype.css`
- Route inside `apps/web/src/App.tsx` inside the prototypes tree, e.g.:

  ```tsx
  <Route path="/prototypes/<feature-name>" element={<FeaturePrototypePage />} />
  ```

Do not mount prototype routes inside dashboard/admin sections. Keep them under
`/prototypes/*` to avoid auth guards.

## Reusing App Utilities

- Prototypes run inside the real app tree, so import from `../../lib/...` or
  `../lib/...` as needed. For toasts, prefer `useToast` from `../../lib/useToast`.
- Prototypes may use imperative DOM rendering (`document.createElement`, etc.).
  In strict TS, Coin-safety is OK, but avoid patterns that break `tsc -b`:
  - cast unknown HTMLElements when accessing element-specific properties
  - ensure all event handlers attach safely before consuming elements
  - keep event wiring in a setup pass after the first render

## Building

```bash
cd /home/ubuntu/projects/komuna/apps/web
npm run build
```

Built assets land in `apps/web/dist/`.

## Deploy to Nginx

This project serves at `/projects/komuna/` using an alias to
`/var/www/html/projects/komuna/` with `sub_filter` rewrites for basename
and API base. The safest deployment method is full copy of the new build:

```bash
sudo rm -rf /var/www/html/projects/komuna/*
sudo cp -r /home/ubuntu/projects/komuna/apps/web/dist/* /var/www/html/projects/komuna/
sudo chown -R www-data:www-data /var/www/html/projects/komuna/
```

Do not symlink or rsync incrementally; stale `index.html` or chunk files
cause route/asset mismatches after renames.

## Verify

- HTTP: `curl -I http://dev.ahsanworks.com/projects/komuna/<route>` → expect `200`.
- Ad-hoc bundle check: inspect `assets/index-*.js` for prototype class/id strings.
  This is especially useful when browser rendering is unavailable in the host.

## Pitfalls

- Browser snapshot/render checks may be unavailable in this environment
  because Chromium dependencies are missing; treat bundle checks as the
  authoritative preview verification.
- TS strictness: unused functions/idempotent names can break production
  builds. Wire everything together or mark intentionally unused APIs
  explicitly. Avoid `@ts-ignore`; prefer minimal focused fixes.
- Nginx prefix: asset URLs live under `/projects/komuna/assets/...` due to
  `sub_filter` in `default.conf`. Do not hardcode bare `/assets/` paths in
  manual HTML inside prototypes.

## References

See `references/deployment-notes.md` for the exact nginx `sub_filter`
behavior, the canonical build/deploy sequence, and verification patterns.