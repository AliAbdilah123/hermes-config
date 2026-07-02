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

## Facebook: published=false hides photos

**Symptom:** Facebook photo posts succeed but don't appear in the feed.

**Fix:** Remove `published=false` or set to `true`. Default is `true`.
