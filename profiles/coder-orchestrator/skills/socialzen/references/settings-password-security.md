# Settings Password Security

Use this when implementing Settings → Security password add/change behavior.

## Compact implementation pattern

Backend:
- Add authenticated `GET /api/auth/security` returning `{ hasPassword, email }` from the canonical `users` row.
- Add authenticated `POST /api/auth/password` with `{ currentPassword, newPassword }`.
- If `users.password_hash` is non-empty, require and verify `currentPassword`; return explicit `INVALID_CURRENT_PASSWORD` on mismatch.
- If `users.password_hash` is empty (Google-only user), allow setting a password from the active session without reset-token/OTP in V1.
- Require `len(newPassword) >= 8`; hash with the existing `hashPassword()` helper.
- On success, update `password_hash`, mark `email_verified=1`, delete every other row in `sessions` for that user while preserving the current `brand_session` token, and queue a password-changed email notification.
- Do not log raw passwords, reset tokens, or verification tokens. Logging user IDs for email-send failures is okay.

Frontend:
- Add a Settings quick-menu item (`security`) using a key/lock icon and translations in `lib/language.tsx`.
- Render `SecurityTab` from `SettingsPage.tsx`.
- Load `/api/auth/security`; show "Add password" when `hasPassword=false`, otherwise show current password + new/confirm fields and "Change password".
- Use `ApiError.code` to map `INVALID_CURRENT_PASSWORD` to a specific user message.
- Keep this small and app-native: existing `Input`, `Label`, `Button`, token colors, no new form dependency.

Tests/checks:
- Targeted Go test should cover: Google-only add password, email/password sign-in after add, wrong current password rejected, change password succeeds, other session is invalidated.
- If using `track(Event.SETTINGS_CHANGED, { section: "security" })`, update the typed event union in `posthog-events.ts`.
- Verify with targeted Go test, `pnpm typecheck`, `pnpm build`, deploy backend/frontend, grep deployed SettingsPage chunk for distinctive Security copy, and verify the chunk is `application/javascript`.

## Known unrelated noise

Full `go test ./...` in this repo may fail for unrelated legacy OAuth/hashtags/Threads expectations. Still run/record the targeted auth-security tests and report unrelated full-suite failures honestly if present.