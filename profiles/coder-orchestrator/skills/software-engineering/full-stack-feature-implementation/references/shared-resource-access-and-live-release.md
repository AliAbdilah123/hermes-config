# Shared-resource access and live release

Use this pattern when adding owner-controlled, read-only access to an existing resource.

## Minimal authorization model

- Keep one canonical owner row; add a join table such as `(resource_id, recipient_user_id)` with a composite unique key and cascading foreign keys.
- Read queries admit `owner OR explicit share`; write, delete, re-share, attachment mutation, and bulk mutation remain owner-only.
- Return an explicit capability (`can_edit`) and owner attribution rather than making the frontend infer authorization from identity fields.
- Owner detail responses may include the share roster; recipient responses must not expose it.
- Normalize and exact-match an existing account, make duplicate sharing idempotent, and reject self-sharing.
- Revocation must immediately remove read access. Deleting the resource or recipient should cascade share cleanup.
- Shared resources in bulk-action lists must be disabled or excluded from owner-only operations.

## Test-first contract

Before implementation, add tests proving:

1. Owner can share with an existing exact-email account.
2. Recipient can read and list the resource.
3. Recipient cannot update, delete, re-share, or invoke owner-only auxiliary mutations.
4. Unrelated users receive not-found semantics.
5. Duplicate sharing is idempotent.
6. Revocation immediately restores not-found behavior.
7. CSRF protection applies to share and revoke endpoints.

For collection fields such as `shares`, choose the API contract deliberately. If clients expect an empty array, do not use `omitempty`; otherwise an empty collection disappears from JSON.

## Live release verification

Repositories can retain stale, similarly named services after moves or renames. Do not assume the first matching unit is the deployed app.

1. Identify the canonical service from its active unit, `WorkingDirectory`, `ExecStart`, and listening port.
2. Build and install the exact backend binary used by that unit; restart it and verify its observed local health endpoint.
3. Publish the fresh frontend build to the actual nginx document root using a clean sync (`rsync --delete` where appropriate).
4. Verify public health and that public HTML references current assets.
5. Run public authenticated E2E across two temporary users: create, share, recipient read, recipient write rejection, revoke, recipient read rejection. Clean up afterward.
6. Verify local HEAD equals the remote branch SHA.

A browser timeout is not proof of application failure. Continue with HTTP/API E2E when it validates the same behavior; report missing visual inspection when exact visuals are part of acceptance.
