# Program rejoin membership reactivation

Use when a Komuna user says they left a program, clicked join/rejoin again, the UI briefly says joined, but the program page or checkout still requires joining.

## Root cause pattern

In the live Go + SQLite API, `POST /api/v1/programs/:id/join` can return success while leaving an existing `program_members` row unchanged. If the row already exists with `status='inactive'`, the detail endpoint keeps returning inactive membership and checkout gates payment.

Do not stop at frontend optimistic state. Verify the persisted row and the next detail/workspace responses.

## Investigation recipe

1. Confirm the running service and runtime path:
   - `systemctl cat komuna-api.service`
   - expect `ExecStart=/home/ubuntu/projects/komuna/api/server` and SQLite env from `/home/ubuntu/projects/komuna/.env`.
2. Inspect live membership state by email + slug:
   - Join `users`, `program_members`, and `programs`; check `users.email`, `programs.slug`, `program_members.status`.
3. Reproduce at API boundary with an auth token for the user:
   - `GET /api/v1/programs/<slug>` should report `membershipStatus`.
   - `GET /api/v1/me/workspace` should include the same program status.
4. Fix at the join handler, not checkout:
   - When an existing membership row is found, update `program_members.status` to the computed join status (`active` for public, `pending` for approval-required) instead of no-oping.
   - Handle non-`sql.ErrNoRows` lookup failures and insert failures as `db_error`.
5. Add a Go regression test:
   - Seed auth user/session + inactive `program_members` row.
   - `POST /api/v1/programs/<program>/join`.
   - `GET /api/v1/programs/<program>` must return `membershipStatus: "active"` for a public program.
6. If the reported user is currently stuck, repair their live row after deploying the code:
   - `UPDATE program_members SET status='active' WHERE user_id=(SELECT id FROM users WHERE email=...) AND program_id=(SELECT id FROM programs WHERE slug=...);`
   - Verify detail and workspace responses with that user's token.

## Verification / deploy

- From `/home/ubuntu/projects/komuna/api/v1`: `gofmt -w ... && go test ./...`.
- From `/home/ubuntu/projects/komuna/apps/web`: `npm run build` if frontend label/state changed.
- Rebuild deployed API binary from `api/v1` to `api/server`, restart `komuna-api.service`, and verify `systemctl is-active`.
- Copy web `dist/` to `/var/www/html/projects/komuna/` for the public Komuna domain.
- Smoke `https://komuna.ahsanworks.com/programs/<slug>` and the local API detail/workspace responses.
