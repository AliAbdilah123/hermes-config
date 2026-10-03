# Threads shares through Instagram Messaging: official contract map

Use when determining whether an Instagram Direct webhook or Graph Message lookup can identify a shared Threads post. Re-check the live URLs because Meta changes permissions, fields, versions, and wording.

## Authoritative sources

- Instagram Messaging webhooks: https://developers.facebook.com/documentation/business-messaging/instagram-messaging/webhooks
- Markdown rendering: https://developers.facebook.com/documentation/business-messaging/instagram-messaging/webhooks.md
- Graph Message node: https://developers.facebook.com/docs/graph-api/reference/message/
- Threads post retrieval/profile discovery: https://developers.facebook.com/documentation/threads/retrieve-and-discover-posts/retrieve-posts
- Threads media retrieval reference: https://developers.facebook.com/documentation/threads/reference/media-retrieval
- Threads keyword/topic search: https://developers.facebook.com/documentation/threads/keyword-search
- Threads mentions: https://developers.facebook.com/documentation/threads/threads-mentions

## Instagram webhook contract

The `messages` webhook explicitly includes “a share (media/post shares).” Its generic message shape is `object=instagram` → `entry[]` → `messaging[]` with `sender`, `recipient`, `timestamp`, and `message`. A message can contain `mid`, optional `text`, and optional `attachments[]`.

For attachments, Meta says they are included for “multiple media attachments or a URL for a story mention or share.” Documented types are `audio`, `file`, `image`, `share`, `story_mention`, `video`, `ig_reel`, and `reel`; the demonstrated payload is `{ "url": "LINK" }`.

Critical limitation: “Only the URL for the shared media or post is included in the notification when a customer sends a message with a share.” There is no separately documented Threads-specific Instagram webhook shape and no guarantee of a Threads media ID, shortcode, author, or permalink.

Webhook permissions currently documented: `instagram_basic`, `instagram_manage_messages`, and `pages_manage_metadata`; non-role-owned data requires App Review/prerequisite grants, and the app must be published.

Other explicit limits: carousel forwards/reactions may identify the first image rather than the selected image; GIF/sticker messages do not trigger a webhook; disappearing media is unsupported, although an example shows `type=ephemeral` with no URL.

## Graph Message lookup

Use `GET /{message-id}`. A MID comes from webhooks or the conversation endpoint. Relevant fields include `attachments`, `created_time`, `from`, `id`, `is_unsupported`, `message`, `reactions`, `shares`, `story`, `tags`, and `to`.

Meta states: “If a field has no data, it will not be returned in the JSON response.” It describes `shares` as media shares such as posts, reels, or product templates and warns that share subfields must also be requested. The documented ordinary share shape is `shares.data[]` with `name`, `description`, `type`, `url`, and `id`; request explicit expansion rather than bare `shares` when testing.

Message-node limits: only Instagram Professional accounts linked to a Facebook Page can access the endpoint, and only the 20 most recent conversation messages are queryable. The page currently names `instagram_manage_messaging`, while the webhook page names `instagram_manage_messages`; report this as a Meta documentation inconsistency, not as proof that either scope enriches payloads.

An omitted `shares` field after explicit subfield expansion means this Message response exposed no share data. It does not prove that all Threads shares behave that way.

## Threads lookup and discovery

- `GET /{threads-user-id}/threads`: app-scoped user’s posts; `threads_basic`.
- `GET /profile_posts?username=...`: exact public username; `threads_basic` + `threads_profile_discovery`. Standard access is restricted to selected official Meta accounts; profiles need at least 100 followers; 1,000 requests per rolling 24 hours.
- `GET /{threads-media-id}`: known media ID; `threads_basic`. Without advanced access, retrieval is limited to tester-created posts; after approval, other public posts are retrievable.
- `GET /keyword_search`: keyword or topic-tag search; `threads_basic` + `threads_keyword_search`. Without approval, searches cover only the authenticated user’s posts; after approval, public posts are searchable. Supports TOP/RECENT, KEYWORD/TAG, TEXT/IMAGE/VIDEO, date bounds, exact `author_username`, default 25/max 100. Limit is 2,200 counted queries per rolling 24 hours across apps; sensitive/offensive terms return an empty array; no-result queries do not count.
- `GET /{threads-user-id}/mentions`: `threads_basic` + `threads_manage_mentions`; only actual public mentions, with tester-only behavior before advanced access.

Threads media fields include ID, media type/URL, permalink, username/text/timestamp/shortcode, children, quote/repost data, attachment fields, topic/spoiler fields, and selected profile metadata. Search excludes `owner`.

## Fact versus inference

Documented fact: Instagram webhook and Message contracts can expose a share URL/ID, while Threads lookup can retrieve a known media ID, list a known user, discover an exact username, or search text.

Inference: when a webhook has only text + MID and an explicit Message lookup exposes neither share nor attachment metadata, there is no documented deterministic MID-to-Threads-post bridge. Keyword search is a heuristic and may return zero, one, or many candidates; text equality cannot prove which post was shared.

## Reporting discipline

1. Quote official text exactly where material and provide the direct URL.
2. Separate webhook fields, Message-node fields, and Threads API fields; never merge them into an invented unified payload.
3. Label observed runtime payloads separately from published contracts.
4. State absence narrowly: “not documented” or “field omitted in this response,” never “Meta never sends it.”
5. Include access level, App Review, account type, linked-Page, recency, and rate-limit constraints.
