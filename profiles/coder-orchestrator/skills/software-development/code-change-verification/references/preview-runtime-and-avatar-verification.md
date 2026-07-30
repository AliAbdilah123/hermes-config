# Preview runtime and avatar verification

## Restart isolated preview APIs without losing parity

When rebuilding/restarting a preview API manually, first capture the running process environment and open DB path from `/proc/<pid>/environ` and `/proc/<pid>/fd`. Reuse the exact `SQLITE_DB_PATH`, port, and other required preview-safe variables in the replacement command.

A successful listener message is not enough: an omitted DB variable can silently open the app's default empty database while health and public routes still return normally.

After restart, verify:

1. The listener PID has the expected `SQLITE_DB_PATH` in `/proc/<pid>/environ`.
2. Its open file descriptors point to that same database.
3. `PRAGMA integrity_check` is `ok`.
4. A known preview-safe identity exists in `auth_users`.
5. The public preview auth endpoint reaches the preview API prefix. Prefer a non-mutating wrong-password probe for an existing identity when credentials are unavailable; it proves routing and identity lookup without changing data.

Keep bounded preview APIs under a durable process supervisor when practical. If launched through a tracked background session, do not kill the session while reporting the API as running; restart it with the complete environment if the build/deploy shell owns the server process.

## Verify avatars on every rendered state

Avatar support is a data path plus multiple UI surfaces. A picker can render a profile picture correctly while the selected chip/card still hardcodes initials.

For manager/member selectors, test at least:

- unselected picker result;
- selected chip/card after choosing;
- edit hydration for an already-selected user;
- fallback initials when `profilePicture` is absent;
- failed image behavior if the component supports it.

Every surface should pass stored upload paths through the existing preview-aware asset helper (for example `apiAssetUrl`) rather than rendering raw `/uploads/...` URLs.

Public verification must use an image path known to exist in the preview database/filesystem and assert `200` plus an image MIME type. A random or inferred user filename returning `404` does not invalidate the rendering fix, but it also is not evidence that avatars work.
