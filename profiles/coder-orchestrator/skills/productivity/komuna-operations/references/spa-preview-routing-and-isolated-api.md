# SPA Preview Routing and Isolated API Verification

Use for Komuna previews mounted below `/previews/<slug>/`, especially when a frontend change depends on unapproved backend behavior.

## A `200` SPA shell is not proof

An SPA fallback can return HTTP 200 while React renders its internal Not Found page. Verify all layers:

1. The preview root and a real deep route (for example `/platform`) both resolve to the preview `index.html`, not production fallback.
2. Served HTML injects `window.__BASENAME__="/previews/<slug>"` before app startup.
3. Deep-route HTML references the preview's hashed assets.
4. The served feature chunk contains a deterministic marker from the requested feature.
5. The rendered page or a reviewer confirms the intended UI state.

A root URL may look correct only because the preview directory physically contains `index.html`; always probe a deep route.

## Nginx pattern

```nginx
location = /previews/<slug> { return 301 /previews/<slug>/; }

location ^~ /previews/<slug>/ {
    alias /var/www/html/projects/komuna/previews/<slug>/;
    try_files $uri $uri/ /previews/<slug>/index.html;
    sub_filter_types text/html;
    sub_filter '</head>' '<script>window.__BASENAME__="/previews/<slug>";window.__API_BASE__="/api/v1"</script></head>';
    sub_filter_once off;
}
```

Back up config, run `nginx -t`, reload, and inspect origin plus cache-busted public HTML. Duplicate-MIME warnings are not failures when syntax validation explicitly succeeds.

## Backend-dependent previews

A frontend preview pointed at production API cannot demonstrate an unapproved backend fix. Do not restart or replace live API merely to make a preview work.

1. Snapshot live SQLite safely with `.backup`; never raw-copy a live DB/WAL set.
2. Build the feature API from the isolated worktree.
3. Run it on an unused loopback port against the snapshot.
4. Add a preview-specific API location before the broad preview location:

```nginx
location ^~ /previews/<slug>/api/v1/ {
    proxy_pass http://127.0.0.1:<port>/api/v1/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

5. Inject `window.__API_BASE__="/previews/<slug>/api/v1"`.
6. Verify health, auth, and exact response shape against the preview endpoint. A snapshot may preserve sessions while isolating writes from production.
7. Label it snapshot-backed and temporary. Production stays unchanged until approval.

## Verification and continuity

- Compare aggregate and collection values (such as `total_programs` and `programs.length`) rather than checking HTTP status alone.
- Asset/API success is a boundary check, not rendered-behavior proof.
- If browser automation is unavailable, use deterministic basename, bundle-identity, feature-marker, and authenticated API assertions, then ask the reviewer to confirm rendering. Never claim visual verification.
- If a model/tool turn is interrupted, acknowledge briefly and immediately resume pending work. Do not let a progress update become an accidental stopping point; continue until the promised preview or a genuine decision/blocker.
