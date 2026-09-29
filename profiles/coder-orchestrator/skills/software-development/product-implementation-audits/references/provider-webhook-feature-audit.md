# Provider webhook feature audit

Use this checklist when assessing a proposed webhook-ingested capability such as attachments, reactions, or rich media.

## Trace the complete boundary

1. Record the exact decoded event struct and every accepted envelope variant.
2. Trace validation in execution order: body limit, signature, object/field filtering, echo/self filtering, required IDs/content, recipient validation, sender authorization, persistence.
3. Identify the authoritative routing identity. Treat usernames as labels when a stable provider sender ID is the security key.
4. Follow deduplication to its database constraint. Determine whether one provider message ID permits one record or several children.
5. Trace persistence through schema, store types/queries, API types, list/detail UI, search, ordering, and rendering/sanitization.

## Evidence hierarchy

Separate explicitly:

- **Code facts:** current source and tests.
- **Stored evidence:** fixtures, retained sanitized logs, database rows, or historical commits containing actual payloads.
- **Provider facts:** current authoritative docs or a fresh signed callback.
- **Unknowns:** payload nesting, event splitting, URL lifetime/authentication, retry behavior, media types/count/size.

Never infer a provider payload contract from memory, a similarly named API, or sample-shaped assumptions. If no real fixture exists, recommend a controlled capture before implementation.

## Inspection techniques

- Search source, tests, docs, history, fixture/log filenames, and database schema/content separately.
- Inspect dirty/untracked plans, but compare every claim with current `HEAD`; plans often describe gaps already fixed.
- Historical raw-body logging proves capture machinery existed, not payload shape, unless a retained payload is present.
- Inspect stored records without reproducing private content or credentials in the report; summarize or redact.
- Run the smallest fresh side-effect-free test command exercising the boundary and report its actual result.

## Minimum implementation

Preserve the existing trust boundary and dedupe unit:

- Parse rich content into the same event as text.
- Require text **or** supported rich content; do not create a bypass handler.
- Authorize recipient and stable sender before persistence or media fetching.
- If the database makes provider message ID unique per source, assemble text plus attachments into one parent record and one transaction.
- Keep verification challenges text-only unless product rules and provider evidence explicitly require otherwise.
- Reuse text/Markdown storage only when provider URLs are safe, durable, and user-accessible. If URLs expire or require authorization, define bounded download, validation, durable storage, access control, and retention first.
- Add no media dependency until native HTTP/JSON/HTML facilities demonstrably fall short.

## Test implications

Cover every supported webhook envelope and include:

- verified sender: attachment-only;
- verified sender: text plus one/multiple attachments, intended order, one parent record;
- replayed message ID;
- unknown sender for attachment-only and mixed content;
- recipient match not bypassing sender verification;
- echo/self event;
- missing IDs and malformed/unsupported attachment metadata;
- verification code combined with rich content;
- malicious URL/label/rendering input;
- logs excluding raw bodies, message text, secret-bearing URLs, and credentials.
