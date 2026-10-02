# Threads shares delivered as empty Instagram templates

Use when a Threads post sent with **Instagram message** reaches a valid signed Instagram webhook but no note is created.

## Observed contract and safe diagnosis

A provider callback can contain one attachment shaped as `type=template`, `payload.generic.elements=[]`, with no text, URL, title, image, or media ID. Log only signature-gated structure: attachment count/type, sanitized key names, nested value types/counts, presence flags, URL parse state, and coarse allowlisted host labels. Never log raw payloads, text, URLs, IDs, signatures, or tokens.

Capture nested shape recursively with a strict depth limit. An empty `elements` array is evidence that the provider supplied no usable attachment metadata; do not invent parser fields, infer a post URL, or claim a code fix can reconstruct the post.

## Scope changes

Adding a Meta scope does not change application parsing by itself. Compare a fresh post-change callback against the prior safe shape. Existing access tokens generally do not gain newly requested permissions automatically: complete required review/advanced access and reauthorize the relevant account through the product's real OAuth flow.

Do not inspect, print, rotate, or replace tokens during webhook-shape diagnosis unless the user explicitly asks for token operations.

## OAuth redirect URI versus webhook callback

These are separate endpoints:

- **OAuth redirect URI:** browser return route used to exchange an authorization code and issue a token with requested scopes. Configure it only when the application implements that OAuth flow, and require an exact URI match.
- **Webhook callback URL:** public GET verification and signed POST event receiver. Successful signed POST delivery proves this transport is already configured.

Never point an OAuth redirect URI at a webhook receiver. Adding an arbitrary redirect URI cannot enrich an already-delivered empty webhook template.

## Decision boundary

When the fresh callback remains `template → generic → elements=[]`, code has nothing trustworthy to persist as media. Ask for an explicit product decision before creating a deduplicated placeholder such as `Shared Threads post`; otherwise keep ignoring the empty event and continue provider configuration/app-review triage.

## Verification

After any diagnostic change, run focused privacy tests, the owning webhook package suite, and static analysis. Deploy the exact service binary, verify local health, then correlate a fresh provider event by timestamp and report whether processing ran, while keeping identifiers hashed or omitted.
