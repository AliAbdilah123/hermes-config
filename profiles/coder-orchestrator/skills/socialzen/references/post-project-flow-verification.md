# Post vs Project creation-flow verification

Use when changing SocialZen's shared post/project composer.

## Contract

- Regular Posts must not render, request, review, or synthesize a Project title.
- Projects must require a trimmed nonblank title in both frontend validation and API boundaries, including draft creation and preflight.
- Preserve legacy request behavior deliberately: do not accidentally classify payloads with no explicit `creationKind` as newly created Projects if old callers omit that field.
- Choice-card copy requested for removal must be absent from the rendered lazy route chunk, not merely hidden with CSS.

## Focused checks

1. Add a frontend regression covering choice-card data and title validation by creation kind.
2. For shared composer chrome removals (subtitles, step indicators, helper copy), add a narrow source-level regression that asserts the exact unwanted labels are absent from `CreatePostPage.tsx`. This covers both Regular Post and Project while they share the same render branch; do not duplicate route-specific component tests unless their branches diverge. Preserve functional form headings such as “Select destinations” when the request targets only the workflow subtitle/stepper.
3. Add an API regression proving blank explicit Projects are rejected while titleless Regular Posts remain accepted.
4. Run from the actual package roots:
   - `apps/frontend`: `pnpm run build` plus focused Vitest/typecheck as appropriate.
   - `apps/backend-go`: focused `go test ./... -run ... -count=1`.
4. Deploy the frontend from `apps/frontend/dist/` to `/var/www/html/projects/socialzen/` and rebuild/install the Go binary to `/opt/socialzen/socialzen-server`; restart `socialzen.service`.
5. Verify the exact public lazy `CreatePostPage-*.js` chunk. Assert removed choice descriptions and `(optional)` are absent, and the required-title marker is present. Do not use `Untitled Project` as a blanket absence assertion because duplicate-flow fallback copy may legitimately retain it.
6. Confirm `HEAD` equals `origin/master` and report the public route, commit, and push.

## Shared dirty-worktree pitfall

SocialZen may contain unrelated in-progress edits in the same test files. Prefer new narrowly scoped regression-test files when that avoids staging unrelated hunks. Stage explicit paths, inspect the cached diff, and never use a broad add. Build/test commands must be rerun after the final edit; a prior green command is stale evidence.
