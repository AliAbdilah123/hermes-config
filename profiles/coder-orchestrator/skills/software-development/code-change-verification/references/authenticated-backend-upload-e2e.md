# Authenticated backend upload E2E

Use this for production API features whose route, persistence, and product invariants must be proven through an authenticated multipart upload.

## Preflight before deployment

1. Identify the exact public hostname and reverse-proxy route. Confirm the new nonstandard API prefix is proxied; an existing `/api/v1/` location does not cover `/api/...`.
2. Identify the running service's exact binary, working directory, environment file, database path, and listener.
3. Confirm an approved authenticated E2E identity is actually usable **before** deployment. A bootstrap credential variable may have been removed after first startup and is not a durable login mechanism. Never create/reset an account merely to obtain evidence unless explicitly authorized.
4. Snapshot the live database with SQLite `.backup` using a writable backup destination, then run `PRAGMA integrity_check`.

## Deployment and readiness

1. Build the exact executable named by systemd and install it atomically.
2. Add the exact reverse-proxy location for the upload endpoint. For streaming multipart uploads, set a compatible `client_max_body_size` and disable proxy request buffering when appropriate.
3. Run `nginx -t`, restart the API, poll the local health endpoint with a bounded loop, reload nginx, and probe the public route.
4. A public `401` proves routing and auth enforcement only. It is not authenticated behavioral evidence.

## Authenticated persistence proof

Upload a uniquely named CSV fixture through the public endpoint using a real session and CSRF token. Assert:

- HTTP response summary and batch identifier;
- the imported canonical record has the authenticated workspace/owner, source, lifecycle, review status, and import provenance;
- at most one non-empty primary contact exists;
- duplicate/invalid rows are skipped or failed without overwriting records;
- forbidden downstream tables gained no rows (prospects/leads, qualification, opportunities/CRM, activities, reports);
- the record appears through the public authenticated Business API/UI review queue.

Clean up only uniquely tagged synthetic records and their batch/audit rows after proving persistence. If credentials are unavailable, report deployment and route evidence separately and mark authenticated public E2E pending/blocked—never call it ready.
