# Metadata-only Project Edit null-contract debugging

## Trigger

Use when a metadata-first SocialZen Project opens from the Project Library but Edit crashes on `.length`, `.map`, or another strict composer operation.

## Trace order

1. Confirm the library Edit action and exact route.
2. Confirm which lazy route/component loads.
3. Inspect the detail request and real JSON response.
4. Trace the backend query through nullable SQL scan fields and DTO serialization.
5. Trace API-boundary normalization, React state hydration, and the first render-time use.
6. Name the exact null property before proposing a fix.

## Contract pattern

Metadata-first creation intentionally omits composer content. SQLite may therefore store nullable scalar content as NULL and have no child rows.

The durable runtime contract should be truthful and stable:

- scalar composer content required by state, such as `caption: string`, is canonicalized once to `""` at the response or API boundary;
- absent child records serialize as arrays, such as `media: []` and `targets: []`;
- TypeScript types match the normalized runtime object;
- React state stays strict rather than accepting hidden nulls;
- do not scatter optional chaining or `?? []` through render code;
- do not fabricate a placeholder media row whose URL/thumbnail is null.

Fix the backend DTO contract first when it emits an invalid shape. A small frontend boundary normalizer may retain compatibility with legacy payloads, but it should be centralized and validated.

## Required scenario matrix

Verify the same Edit flow for:

1. Metadata-only draft: composer opens with title/description and truthful empty content.
2. Draft with content: persisted caption, destinations, and media hydrate unchanged.
3. Published/non-editable Project: detail loads without a runtime exception and existing state policy blocks editing.
4. Missing Project: intentional not-found behavior, no partial composer state.
5. Foreign-owner Project: owner-scoped not-found behavior to avoid existence disclosure.

For every case, inspect browser runtime errors, not only HTTP status, tests, or build output.

## Common pitfall

Do not assume the failing collection itself is null. A metadata-only aggregate can return `media` as an array while a nullable scalar such as `caption` is placed into state and later crashes at `caption.length`. Trace the exact value end to end.
