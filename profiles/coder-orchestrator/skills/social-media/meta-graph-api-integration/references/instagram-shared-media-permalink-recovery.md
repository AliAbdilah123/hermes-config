# Instagram shared-media permalink recovery

Use when an Instagram DM share arrives as an attachment-only webhook but the note needs a copyable canonical post/Reel URL.

## Observed provider pattern

The webhook may contain only:

```json
{"message":{"mid":"...","attachments":[{"type":"template","payload":{"generic":{"elements":[]}}}]}}
```

The webhook itself has no usable URL. A read-only Message API lookup by `mid` can return a richer document whose `attachments.data` contains the shared-media URL. Request only the needed fields, for example:

```text
GET https://graph.instagram.com/{version}/{mid}?fields=message,attachments,shares{data{name,description,type,url,id}}
Authorization: Bearer <Instagram access token>
```

Provider responses vary, so traverse the decoded lookup response for candidate strings rather than binding only one speculative nested schema. Accept only canonical HTTPS Instagram permalinks:

- hosts: `instagram.com`, `www.instagram.com`
- paths: `/p/...`, `/reel/...`
- reject userinfo, query strings, fragments, and all other hosts/paths
- deduplicate accepted links

Store the canonical value separately from preview/CDN media URLs (for example, `permalink` alongside `url`). Feed-post preview URLs such as `lookaside.fbsbx.com/...` are not the user-copyable canonical post URL. Reel webhook URLs may already be canonical and can be used as the fallback permalink.

## Processing-order pitfall

Do not finalize `missing_text` before the Message API lookup. For an attachment-only event:

1. Parse directly supported webhook attachments.
2. If the event has a MID and is not an echo, perform the lookup.
3. Extract and append validated canonical links.
4. Clear the provisional `missing_text` ignore reason when lookup produced a supported link.
5. Route the resulting attachment through the normal verified-sender note creation path.

A diagnostic-only lookup that logs response shape but leaves the original ignore decision unchanged does not implement the feature.

## UI contract

In note details, render the canonical URL as selectable link text and provide an accessible copy button using `navigator.clipboard.writeText`. Keep `target="_blank" rel="noopener noreferrer"` for opening the source. Do not render a canonical `/p/...` URL as an image source; only render known CDN preview URLs as images. Reels may use the canonical permalink to build the Instagram embed URL.

## Verification

- Fixture test: nested lookup response yields one post and one Reel permalink; unsafe host/query candidates are rejected.
- Webhook test: attachment-only empty-template event becomes processable when lookup returns a valid permalink.
- Store/API test: `permalink` survives JSON persistence and note retrieval.
- Frontend test: URL text, accessible copy control, and clipboard call are present.
- Run backend tests, frontend tests/typecheck/build, deploy both binary and static assets, then verify the deployed immutable JS contains the copy-control contract.
- Final live proof still requires a fresh real share after deployment; local fixtures and artifact inspection do not prove the provider’s current response shape end to end.
