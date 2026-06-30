# SQLite Runtime DB Recovery + Auth Error Triage

Use this when a deployed service uses SQLite and auth/signup suddenly reports misleading errors (for example every signup says `USER_ALREADY_EXISTS` while login cannot establish a session).

## Signals

- API signup for a brand-new email returns a conflict/duplicate-user error.
- Login returns success but the next `/get-session` is `null`, or the frontend says the session was not established.
- The SQLite DB path from the service env does not exist on disk, but the service is still running.
- `/proc/<pid>/fd` shows an open handle to `.../socialzen.db (deleted)`.

## Root-cause pattern

If a SQLite file is deleted while the process is running, the process can continue using the unlinked inode through its open file descriptor. New writes may fail or the file may disappear on restart. If auth code maps every DB insert error to `USER_ALREADY_EXISTS`, infrastructure/data-path failures are misreported as duplicate users.

## Investigation recipe

1. Reproduce with a truly fresh email via direct API calls and a cookie jar:
   ```bash
   EMAIL="verify+$(date +%s)@example.com"
   COOKIE=/tmp/app-auth-cookies.txt
   curl -i -c "$COOKIE" -H 'Content-Type: application/json' \
     -d "{\"name\":\"Verify User\",\"email\":\"$EMAIL\",\"password\":\"password123\"}" \
     http://127.0.0.1:<port>/api/auth/sign-up/email
   curl -i -b "$COOKIE" http://127.0.0.1:<port>/api/auth/get-session
   ```
2. Confirm the configured DB path from systemd/env and compare it to the files actually on disk.
3. Inspect the running process:
   ```bash
   PID=$(systemctl show -p MainPID --value <service>)
   sudo readlink /proc/$PID/cwd
   sudo ls -l /proc/$PID/fd | grep -E 'sqlite|\.db|deleted'
   ```
4. If the DB is open as `(deleted)`, recover it **before restarting**:
   ```bash
   sudo mkdir -p /path/to/runtime/data
   sudo cp /proc/$PID/fd/<db-fd-number> /path/to/runtime/data/app.db
   sudo chown <service-user>:<service-group> /path/to/runtime/data/app.db
   ```

## Fix pattern

- Ensure the runtime DB directory/file exists before restarting the service.
- Preserve the recovered DB before restart so users/sessions are not lost.
- In auth handlers, distinguish unique constraint errors from generic DB errors:
  - unique email constraint => `USER_ALREADY_EXISTS` / 409
  - other insert/session failures => 500 with a specific `SIGNUP_FAILED` or `SESSION_CREATE_FAILED` code
- Do not ignore session creation errors after signup/signin.
- Add a regression test where a non-unique DB write failure does **not** produce a duplicate-user response.
- Add runtime data directories such as `/data/` to `.gitignore` when they live inside the repo root.

## Verification

After deploy/restart, verify through the public route, not only localhost:

```bash
EMAIL="finalcheck+$(date +%s)@example.com"
COOKIE=/tmp/app-final-cookies.txt
curl -i -c "$COOKIE" -H 'Content-Type: application/json' \
  -d "{\"name\":\"Final Check\",\"email\":\"$EMAIL\",\"password\":\"password123\"}" \
  http://<host>/<app-prefix>/api/auth/sign-up/email
curl -i -b "$COOKIE" http://<host>/<app-prefix>/api/auth/get-session
curl -b "$COOKIE" -c "$COOKIE" -X POST http://<host>/<app-prefix>/api/auth/sign-out
curl -i -c "$COOKIE" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"password123\"}" \
  http://<host>/<app-prefix>/api/auth/sign-in/email
curl -i -b "$COOKIE" http://<host>/<app-prefix>/api/auth/get-session
```
