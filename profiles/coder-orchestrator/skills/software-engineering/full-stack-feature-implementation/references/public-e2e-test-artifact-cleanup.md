# Public E2E cleanup and JSON ID extraction

Two concrete pitfalls from shipping a full-stack feature and running the acceptance
flow end-to-end against the live deployment.

## E2E against a live deploy leaves test data behind

Running the acceptance flow (register → create → publish → install → run → logout)
against the public domain creates throwaway accounts and owned/public rows in the
production database. When the feature publishes content to a public surface
(marketplace, feed, catalog), that content is now visible to real users the moment
the flow succeeds.

Recovery order:

1. Snapshot first: `cp data/$DB /tmp/$DB.bak-$(date +%s)`.
2. List the test rows before deleting and confirm every one matches an identifiable
   test prefix (seeded emails like `e2e-%@example.com`), never real users.
3. Delete by that prefix with cascades enabled, and rely on `ON DELETE CASCADE`
   foreign keys to clear child rows (apps, versions, installations, runs):
   `sqlite3 data/$DB "PRAGMA foreign_keys=ON; DELETE FROM users WHERE email LIKE 'e2e-%@example.com';"`
4. Verify counts return to the pre-test baseline (often 0 when the environment was
   empty), and re-check the public endpoint is empty again.

Prefer a throwaway/staging environment for acceptance E2E when one exists. Clean
production back to baseline when it does not — do not leave test accounts,
published apps, or run rows sitting in a live marketplace.

## Extract IDs from JSON with a real parser, not sed/regex

Pulling `"id"` from a JSON response with `sed`/`grep` grabs the FIRST match, which is
frequently a nested field (a feature's `id`) rather than the top-level resource `id`
you actually wanted — silently turning every subsequent request into a 404 that looks
like a server bug.

Use `python3 json.loads(...)` (or `jq`) to read the specific path:

```bash
APPID=$(printf '%s' "$CREATE" | head -n -1 | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['app']['id'])")
```

Two details that matter together:

- `head -n -1` strips the trailing HTTP-status line when the response embeds a
  `curl -w $'\n%{http_code}'` status code, so the JSON parses clean.
- Index the exact key path (`['app']['id']`, not `['id']`) even though the top-level
  response also contains a feature with its own `"id"` field.