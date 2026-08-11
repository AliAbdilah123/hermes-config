# Publishing-state and destructive-notification E2E

Use for SocialZen changes involving immediate/scheduled publishing state, notification deletion, or profile-media dialogs.

## Runtime and migration boundary

- Discover the database used by the running service before inspecting or seeding it. SocialZen may resolve a relative database under the service working directory (commonly `data/socialzen.db`); a nearby zero-byte `socialzen.db` is not evidence of the runtime database.
- Confirm the opened database with the running process, service configuration, recent modification state, or live schema/data. Back up that exact file before deployment.
- Deploy backend first for additive schema/API changes, poll `/api/health` through the readiness race, then deploy the frontend and compare the live `index.html` hash/asset names with the verified build.

## Publishing-state browser fixtures

A manually inserted due `PUBLISHING`/`NOW` record is not stable: the real scheduler can claim it and invoke a provider before the browser reaches the page. A fake disconnected target will then truthfully become `FAILED`, invalidating a queued-state assertion.

For a safe deterministic rendered-state probe:

1. Use a dedicated E2E account or harmless records clearly prefixed `e2e_`.
2. For a scheduled card, persist `status=SCHEDULED`, `publish_intent=SCHEDULED`, and a future `publish_at`; assert a date/time and no post-now countdown.
3. For queued rendering without provider side effects, persist parent `status=PUBLISHING`, `publish_intent=NOW`, and a sufficiently future `publish_at` so the scheduler cannot claim it during the assertion. Persist a matching pending target.
4. Locate the card from its unique title and inspect the nearest card container's text. Do not assume an `article` ancestor; SocialZen cards may use ordinary `div` containers.
5. Separately verify terminal `Posted` presentation from an existing safe published fixture or a controlled provider-backed flow. Do not manufacture a provider success in production.
6. Re-read the public API and database after any browser timeout. A transition from queued to failed can prove the real scheduler ran; classify fixture consumption separately from UI behavior.
7. Remove all E2E posts, targets, notifications, sessions, and disposable users afterward.

## Notification deletion safety

- Exercise selected deletion on uniquely named test notifications and verify an unselected notification survives reload.
- Never use `Delete all` on a real user's notification history merely to complete E2E.
- For delete-all, use a genuinely authenticated disposable account created through a supported auth/setup path. A directly inserted user/session is not valid browser evidence until the SPA visibly renders authenticated chrome.
- If disposable authentication fails, clean up the fixture and report delete-all public E2E as pending. Unit/API authorization tests, a successful build, or selected-delete E2E do not upgrade it to complete.
- Include a cross-user API test: mixed foreign/owned IDs delete and count only owned rows without revealing foreign existence.

## Avatar dialog safety

- A profile with no uploaded avatar cannot exercise the image-viewer trigger. Do not count the initials fallback as viewer E2E.
- Use an authenticated account with a real uploaded avatar, then verify keyboard activation, named dialog, full-size image, Escape close, focus restoration, and no console/page errors attributable to the flow.
- If the available real account lacks an avatar and disposable authentication cannot be established, leave public avatar E2E pending rather than mutating the user's profile without permission.

## Evidence integrity

Record each boundary independently: focused tests, typecheck/build, backend readiness/schema, live asset, authenticated selected deletion, queued/scheduled rendering, avatar dialog, and delete-all. Mark only the boundaries actually exercised as complete.