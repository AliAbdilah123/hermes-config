# Instagram disconnect consent persistence

Use when a user says Instagram reconnects after refresh or still appears connected after disconnecting all platforms.

## Root cause pattern

- The frontend can correctly avoid auto-selecting platforms, but refresh still shows Instagram if a direct `instagram_accounts.provider='instagram'` row remains in the live DB.
- Settings can also mislead users if Facebook-derived rows are displayed in the Instagram connected-card. Keep direct Instagram consent separate from Facebook-linked data unless the product explicitly asks otherwise.
- A DELETE endpoint that ignores `Exec` errors / `RowsAffected()` can return success even when nothing was deleted, making a failed or wrong-account disconnect look successful.

## Fix pattern

1. Check direct rows for the affected user:
   ```bash
   sudo sqlite3 /opt/socialzen/data/socialzen.db \
     "SELECT id,user_id,provider,ig_username FROM instagram_accounts WHERE user_id='<user_id>';"
   ```
2. Backend `DELETE /api/instagram/accounts/:id` should:
   - delete only `id=? AND user_id=?`,
   - return `500` on SQL error,
   - return `404` when `RowsAffected() == 0`,
   - return `204` only after a real delete.
3. Frontend Settings and New Post should treat Instagram as direct rows only:
   ```ts
   accounts.filter(a => a.provider === "instagram")
   ```
   Do not include `mock` or `facebook` rows in the Instagram selector/card when the complaint is consent/reconnect confusion.
4. If the user already disconnected and the DB still has their direct row, remove that stale row from production after identifying the user.
5. Replace emoji placeholders in New Post with styled platform icons/SVGs so platform identity is clear without emoji rendering drift.

## Verification

- `pnpm --dir apps/frontend typecheck && pnpm --dir apps/frontend build`
- `cd apps/backend-go && go build -o /tmp/socialzen-backend .`
- Deploy frontend and backend, restart `socialzen.service`, verify `/health`.
- Verify live DB count for the affected user is `0` after cleanup:
  ```bash
  sudo sqlite3 /opt/socialzen/data/socialzen.db \
    "SELECT COUNT(*) FROM instagram_accounts WHERE user_id='<user_id>' AND provider='instagram';"
  ```
- Grep deployed `CreatePostPage-*.js` for `provider==="instagram"` and ensure old emoji markers are gone.
