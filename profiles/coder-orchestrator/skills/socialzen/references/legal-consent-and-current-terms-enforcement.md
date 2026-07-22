# Legal consent and current-Terms enforcement

Use this when integrating existing public legal documents into signup, authenticated access, shared public navigation, and account-data settings.

## Contract

- Keep public legal pages unauthenticated and informational; Data Deletion must point to authenticated Settings actions rather than expose destructive controls.
- Define one current Terms version shared by the frontend acceptance payload and backend validation. Persist both `terms_version` and `terms_accepted_at`; a timestamp alone cannot prove acceptance of the latest document.
- Add nullable acceptance columns through both SocialZen migration paths: production `internal/models.Migrate()` and test/legacy `app.migrate()`.
- New email and OAuth signups must explicitly send acceptance plus the exact current version. Reject missing/stale consent at the backend trust boundary; do not rely on a checked frontend box.
- Existing users with missing, blank, or stale acceptance require the gate after authentication.

## Signup UX

- Place the checkbox immediately above Create Account and initialize it unchecked.
- Open Terms and Privacy in new tabs with `target="_blank" rel="noopener noreferrer"`; this preserves entered form state.
- Disable Create Account until checked, but also keep submit-handler validation because keyboard/programmatic form submission and backend calls can bypass button state.
- Use a dedicated inline, accessible consent error (`role="alert"`, `aria-invalid`, `aria-describedby`) rather than a generic server error.
- If OAuth signup is offered on the same screen, apply the same consent gate and send the same version in that flow.

## Authenticated enforcement

- Add minimal authenticated status and accept endpoints. Acceptance must reject stale versions and return the recorded version/timestamp.
- Put the frontend gate above the complete authenticated application shell and do not mount children before acceptance. Hiding navigation after app content mounts is not sufficient: background fetches and route features may already run.
- The modal is controlled-open only: no close button, no Escape/outside dismissal, Accept disabled until checked, and Log Out remains available.
- Enforce the same rule in backend middleware for authenticated protected API requests. Exempt only health, login/signup/session/logout, verification/recovery, Terms status/accept, required config, and provider webhook endpoints.
- Keep public SPA/legal routes outside API enforcement. If middleware wraps a mixed API/static handler, explicitly exempt public document paths so an authenticated user with stale Terms can still review them.

## Shared legal navigation

- Update the reused `LandingFooter`, not one landing page, with exact public links for Privacy Policy, Terms of Service, Security, and Data Deletion.
- In Settings → Account & Data / Danger Zone, preserve existing export and deletion controls and add only an informational link to `/data-deletion`.

## Focused verification

1. Backend tests: signup rejects absent/stale consent, stores current version/timestamp, stale users receive `403 TERMS_ACCEPTANCE_REQUIRED`, status/accept/logout remain reachable, acceptance unlocks a protected endpoint.
2. Frontend tests: checkbox starts unchecked; legal links have new-tab security attributes; submit stays disabled; bypassed form submission shows validation; app children do not mount before acceptance; Escape/outside cannot unlock; logout redirects; footer and Danger Zone links are present.
3. Run frontend typecheck/build and focused Go tests/build.
4. Deploy backend before frontend when the new frontend sends a changed auth contract. Restart, verify health, then deploy a clean `dist/`.
5. Verify all four public routes, the generated JS content type, and a distinctive acceptance marker in the deployed bundle.
6. Commit and push only feature files; preserve unrelated untracked plans/docs.

## Suite-reporting pitfall

Run focused feature checks even if the repository-wide suite has unrelated pre-existing failures. Report both facts precisely: focused checks passed, and list unrelated full-suite failures without implying the feature caused or fixed them. Never omit the full-suite attempt when it is practical.
