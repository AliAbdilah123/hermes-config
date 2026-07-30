# Shared Static Root Deployment Blast Radius

## Symptom pattern

Several unrelated nginx-hosted SPAs fail one after another with `500 Internal Server Error`. Nginx logs show:

```text
rewrite or internal redirection cycle while internally redirecting to "/index.html"
```

The corresponding configured document root or alias directory is absent. The API service may remain healthy, so service status and listening ports do not explain the frontend failure.

## Root cause

A static deployment used destructive synchronization against a shared ancestor, for example:

```bash
rsync -a --delete dist/ /var/www/html/
```

If sibling applications live below `/var/www/html/projects/<slug>/`, `--delete` removes those sibling directories because they are absent from the source `dist/`. The next SPA fallback repeatedly redirects to a missing `index.html`, producing nginx 500 rather than a straightforward 404.

## Diagnosis

1. Reproduce the public domain response and inspect the newest nginx error-log lines.
2. Extract every nginx `root` and `alias` below the shared static tree with `nginx -T`.
3. For each configured SPA, verify its deployment directory and `index.html` exist.
4. Check sudo/system journal history for recent destructive deploy commands, especially `rsync --delete` whose destination is `/var/www/html/` or `/var/www/html/projects/` rather than a project leaf.
5. Probe the API separately. A healthy backend plus missing frontend root confirms deployment-artifact loss.

## Recovery

1. Inventory all missing configured roots before restoring only the reported app; sibling apps may already be broken but unnoticed.
2. Locate each project's current build output or rebuild from its canonical frontend package.
3. Restore each app only to its leaf directory:

```bash
sudo install -d -m 755 /var/www/html/projects/<slug>
sudo rsync -a --delete dist/ /var/www/html/projects/<slug>/
sudo find /var/www/html/projects/<slug> -type d -exec chmod 755 {} +
sudo find /var/www/html/projects/<slug> -type f -exec chmod 644 {} +
```

4. If a domain vhost uses the shared ancestor as `root`, narrow it to the project's leaf directory. Keep explicit API/media aliases as needed.
5. Run `nginx -t`, reload, then verify every configured public app—not only the initially reported one.

## Verification

For each public domain and configured subpath:

- Fetch cache-busted HTML and require `200 text/html`.
- Parse at least one emitted JS/CSS URL, fetch it publicly, and require `200` with JavaScript/CSS MIME type.
- Follow redirects and check the final URL/scheme; a `200` reached after an accidental HTTPS-to-HTTP redirect is not clean verification.
- Confirm no new internal-redirection-cycle entry appears after the probes.

HTTP 200 for HTML alone is insufficient because SPA fallback can return HTML for missing assets.

## Prevention

- Never deploy a single SPA with `rsync --delete` to a directory that owns sibling applications.
- Canonical destination: `/var/www/html/projects/<slug>/`.
- Treat `/var/www/html/` and `/var/www/html/projects/` as containers, not deploy targets.
- Before accepting a deployment command, compare its destination with nginx's exact leaf root/alias.
- After any static deploy, verify the target application and at least inventory sibling roots when the destination or nginx root was recently changed.
