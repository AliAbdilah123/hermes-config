# Facebook and Threads text-only posts

Use this when exposing an existing backend `TEXT` post type through SocialZen composers.

## Cross-layer contract

- Text-only is valid only when every selected destination is Facebook or Threads; reject Instagram combinations.
- Require nonblank trimmed text.
- When Threads is selected, enforce 500 Unicode code points with `Array.from(text).length`, matching Go rune counting. Otherwise retain Facebook’s existing caption ceiling.
- A `TEXT` payload must contain `media: []`. Clear media when switching types and also force empty media at the API boundary so stale hydrated state cannot leak.
- Preserve `TEXT` explicitly during load and duplicate hydration; do not let generic unsupported-type fallback coerce it to `PHOTO`.

## Composer coverage

Treat these as independent paths:

1. Regular composer: expose Text only for eligible destinations, hide upload/crop controls, skip media-required validation, and submit empty media.
2. Project child composer: cover both local-child POST and persisted-child PATCH payloads; validate against shared Project destinations, preserve hydrated `TEXT`, and hide child media controls.
3. Edit/retry: preserve account targets, hide media replacement for Text, and validate nonblank/Threads length before PATCH or retry.

## Focused provider contracts

- Facebook: assert `PublishTextPost` POSTs to `/{page-id}/feed` with `message` and `access_token`, returning the provider ID.
- Threads: assert top-level publishing creates `media_type=TEXT` with `text`, no image/video URL, follows readiness polling, then publishes the container ID.
- Do not change backend production code unless these contract tests expose a mismatch.

## Verification discipline

After the final source edit, rerun fresh verification rather than relying on an earlier passing run:

```bash
cd apps/frontend
pnpm exec vitest run \
  src/pages/posts/CreatePostPage.test.ts \
  src/pages/projects/ProjectWorkspace.test.tsx \
  src/pages/posts/EditPostPage.test.tsx \
  src/pages/posts/EditPostPage.integration.test.tsx
pnpm run build

cd ../backend-go
go test ./internal/facebook ./internal/threads ./internal/posts
```

Report unrelated full-suite failures separately and do not call the feature release-ready until authenticated public E2E passes.
