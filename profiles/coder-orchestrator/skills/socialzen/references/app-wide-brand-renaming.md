# App-wide brand renaming

Use this checklist when replacing a legacy product name in SocialZen.

1. Search the active application source for the old name in exact and case-insensitive forms. Do not bulk-edit historical plans/specs unless explicitly requested.
2. Update every user-facing surface: document title/metadata, sidebar and auth wordmarks, landing navigation/previews/footer, login/signup copy, localized strings, and current legal/privacy copy.
3. If the visible mark is a legacy initial, update it consistently with the wordmark.
4. Review bulk replacements for duplicated prose such as `SocialZen, SocialZen` and for formatting drift around edited JSX.
5. Search the application source again for the old name, run `git diff --check`, and build the frontend.
6. Preserve unrelated working-tree changes: stage only the branding files.
7. Commit and push only after verification.
8. For a live-app request, deploy the newly built `dist/` to the exact nginx document root serving the public hostname. A successful source edit, build, commit, or push is not completion and must not be reported as if deployed.
9. Verify both boundaries after deployment:
   - origin: fetch with the public `Host` header and confirm the new title/asset hash;
   - public URL: use a cache-busting query, confirm the new brand in HTML and the referenced JS bundle, and confirm the old brand is absent from the live artifact.
10. Only then report completion. Include the app link, commit, and push status; if authenticated surfaces changed, complete authenticated public E2E too.
