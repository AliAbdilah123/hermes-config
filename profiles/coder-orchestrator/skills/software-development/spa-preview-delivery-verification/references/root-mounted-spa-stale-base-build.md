# Root-mounted SPA blank after a legacy-base build

## Symptom

A root-mounted SvelteKit SPA returns `200` for `/app/login`, and every JavaScript/CSS asset also returns `200`, but the page is blank. Browser logs can show:

```text
Error: Not found: /app/login
Uncaught (in promise) Error: goto: invalid URL
```

The fallback HTML may advertise runtime base `/`, while route metadata in the deployed bundle was generated for an older base such as `/projects/<slug>`.

## Diagnosis

1. Fetch public HTML and verify emitted assets have correct status and MIME.
2. Run the exact cache-busted route in a real browser and capture DOM plus console/stderr.
3. If assets load but the router reports `Not found` for a valid source route, compare the current mount with the environment used for the deployed build.
4. Remember that static-adapter fallback HTML can return `200` while stale client route/base metadata rejects the URL.

Example browser probe:

```bash
profile=$(mktemp -d)
chromium --headless --no-sandbox --disable-gpu \
  --user-data-dir="$profile" --virtual-time-budget=5000 \
  --enable-logging=stderr --v=1 \
  'https://dev-example.example.com/app/login?cb=<timestamp>'
rm -rf "$profile"
```

## Minimal fix

If source configuration is already correct, do not invent a code change. Rebuild from clean generated output with the current root base and deploy the whole artifact:

```bash
rm -rf .svelte-kit build
npm run build
rsync -a --delete build/ /var/www/html/projects/<slug>/
```

If prior elevated deployment commands left generated directories owned by another account, remove only `.svelte-kit` and `build` with the needed privilege, then rebuild as the normal project user. Do not merge stale hashed assets.

## Verification

- Cache-busted public login route renders route-specific heading, email field, and submit button.
- Browser console has no route `Not found`, invalid URL, or uncaught exception.
- Public HTML references a newly generated asset hash.
- Emitted JS/CSS return `200` with correct MIME.
- Project tests/typecheck pass before publishing.

This differs from a simple wrong asset base: all assets can load successfully while compiled route/base metadata remains stale.