# Post-pull refactor verification notes

Use when the user asks to pull latest Komuna/Goresan changes and verify that a simplification/refactor did not break behavior.

## Durable lessons

- Keep terminal output small: split `git`, test, build, deploy, and smoke checks into separate commands. Avoid one huge command that streams full test failure DOM dumps.
- Pull safely: inspect status/remotes first, then use `git fetch` + `git pull --ff-only` so local work is not overwritten.
- If verification discovers a regression introduced by the pulled change, fix the minimal production bug, update stale tests only when expectations are demonstrably outdated, then rerun the narrow failing test before the broader suite.
- Hono middleware pitfall: never call `await next()` inside a broad `try/catch` that also wraps downstream execution. If a downstream handler throws, the catch may retry `next()` and cause `next() called multiple times`. Initialize optional middleware state in the `try`, call `await next()` once after setup, then do best-effort cleanup separately.
- Date-sensitive voucher tests can become stale when fixtures expire relative to the current date. Prefer future fixture dates or injected `now` over changing lazy-expiry production behavior.
- Notification preference tests should track the full event type list; when a new event type is added, default preference count/ordering expectations may need updating.
- For frontend deploy verification, a passing `npm run build` plus origin/public HTTP checks for `index.html` and hashed JS/CSS assets verifies the static deploy path. Do not claim full browser click-through coverage if browser automation times out; report the limitation explicitly.

## Suggested command sequence

```bash
git status --short --branch
git remote -v
git fetch origin master --prune
git pull --ff-only origin master

# API: start narrow if failures are known, then broad.
npm run test -- --reporter=dot

# Web.
npm run test -- --reporter=dot
npm run build

# Static frontend deploy.
rsync -a --delete apps/web/dist/ /var/www/html/projects/komuna/

# Smoke static origin/public assets.
curl -sI http://localhost/projects/komuna/
curl -sI https://komuna.ahsanworks.com/
curl -s http://localhost/projects/komuna/ | grep -o 'assets/index-[^" ]*' | head
```

## Reporting checklist

- Pulled branch and final local SHA.
- Remote SHA after push, if fixes were committed.
- Exact tests/builds run and pass/fail counts.
- Any exclusions or environment prerequisites, e.g. DB-backed tests requiring `DATABASE_URL`.
- What was deployed and public link: `https://komuna.ahsanworks.com/`.
- Honest coverage note for browser/action testing if automation could not complete.
