# Project Edit nullable-contract debugging

Use when SocialZen’s Project Library → Edit flow crashes on collection/string operations, especially for metadata-only Projects.

## Trace before fixing

Follow the complete boundary chain:

1. Project Library edit callback and generated route.
2. Lazy route registration and page component.
3. Detail request path (`GET /api/posts/:id`).
4. Backend query scan types (`sql.NullString`, nil slices, nullable thumbnails).
5. JSON serialization shape.
6. Frontend hydration and composer render expressions such as `.length`, `.map`, and `.filter`.

Identify the exact nullable field; do not assume every crash is an empty-list issue.

## Metadata-only aggregate contract

Metadata-first Project creation intentionally persists no caption, destinations, media, version, run, or quota reservation. SQLite may therefore hold `NULL` for optional scalar columns and zero rows for child collections.

The API view model must still expose canonical composer runtime state:

- textual composer fields such as `caption`: empty string when absent;
- collection fields such as `media` and `targets`: non-nil empty arrays;
- no synthetic media item with a null thumbnail when no media row exists.

Fix the backend DTO/response construction first. Add one narrow frontend normalizer at the detail API boundary for legacy/deployed nullable responses, then keep React state strict. Do not scatter optional chaining or `?? []` throughout rendering.

## Required regression matrix

- Metadata-only draft: detail returns canonical empty values and composer renders.
- Draft with content: persisted caption/media/targets survive unchanged.
- Published Project: detail renders without crashing and existing non-editable state remains enforced.
- Missing Project: 404 behavior is intentional.
- Foreign/unauthorized Project: owner-scoped lookup remains non-disclosing (typically 404); unauthenticated access remains an auth error.

Test backend response shape and frontend hydration separately.

## Verification command pitfall

For exact Vitest files, run `pnpm exec vitest run <file...>`. Avoid `pnpm test -- --run <file...>`: the extra separator/flag combination can be interpreted incorrectly and run the entire suite, obscuring focused evidence.

Run the canonical frontend build separately with `pnpm run build`. If the broad suite has an unrelated failure, report focused passes and the broad failure as separate boundaries.

Deployment evidence must include the rebuilt backend service, the exact lazy Edit route chunk, and a public API/health probe. Do not call the work exact public E2E unless an authenticated browser actually exercises the requested edit scenarios; if browser execution is blocked, say that explicitly while reporting the other verified boundaries.
