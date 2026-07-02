# Error Transcripts

## Threads: user_id type mismatch

**Symptom:** Threads OAuth callback redirects to dashboard, no account connected. Backend logs:

```
threads oauth callback failed: json: cannot unmarshal number into Go struct field .user_id of type string
```

**Actual response from `POST https://graph.threads.net/oauth/access_token`:**
```json
{"access_token": "THQVJ...", "user_id": 17841405793187218}
```

Note `user_id` is a JSON number, not a string. The Threads API returns numeric IDs, same
as Instagram's flat format. Use `json.Number` in Go struct tags.

**Fix:** Change `UserID string` to `UserID json.Number` and call `.String()` when using.

## Instagram: Media ID not available (9007/2207027)

**Symptom:** `#100/instagram-api-post: Instagram API error: Media ID is not available.`

Error code 9007, subcode 2207027 — the media container hasn't finished processing.

**Fix:** Add a polling loop between container creation and publish. See SKILL.md → Instagram Publishing section.

## Facebook: pages_manage_posts not available

**Symptom:** `Facebook API error 403: (#200) The permission(s) pages_manage_posts are not available.`

**Fix:** Add `pages_manage_posts` to OAuth scopes. Users must reconnect.

## Instagram: "account not connected for publishing"

**Symptom:** `publisher: post X target Y (instagram) failed: Instagram account not connected for publishing; reconnect Instagram`

**Root causes (check in order):**
1. **Missing `access_token_encrypted` column** — the DB table was created without it and the ALTER TABLE migration hasn't run on this DB instance. Verify with `PRAGMA table_info(instagram_accounts)`. If missing, run `ALTER TABLE instagram_accounts ADD COLUMN access_token_encrypted TEXT`.
2. **Account has wrong provider** — the publisher queries with `provider='instagram'` but the account has `provider='facebook'` (IG Business Account linked via Facebook flow). Fix: widen the query to `(provider='instagram' OR provider='facebook')`.
3. **Token genuinely empty** — the account was connected via Facebook OAuth which doesn't store an Instagram token. The user must reconnect Instagram directly.

**Symptom (parent post):** `All platforms failed to publish` — the parent post gets this error when ALL targets fail. This means EVERY platform target (instagram, facebook, threads) returned an error. Check each target's individual `error_message` in `post_targets` table to diagnose.

## Facebook: published=false hides photos

**Symptom:** Facebook photo posts succeed but don't appear in the feed.

**Fix:** Remove `published=false` or set to `true`. Default is `true`.
