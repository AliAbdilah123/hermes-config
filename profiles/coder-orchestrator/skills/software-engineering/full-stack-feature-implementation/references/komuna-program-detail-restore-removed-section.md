# Restoring a Removed Program Detail Section

Use this when a recent Komuna redesign removed a section and the user asks to bring the pre-redesign version back in a specific position.

## Minimal restoration workflow

1. Identify the redesign commit from the target page history.
2. Read the page from the redesign commit's parent (`git show <redesign>^:<path>`) and copy the real imports, state, fetch parameters, component props, and interaction flow. Do not approximate the old UI from memory.
3. Add a failing page-level test that proves both:
   - the restored content renders from realistic API data;
   - its DOM position is before/after the requested neighboring section.
4. Restore the existing component rather than rebuilding it. For Upcoming Sessions this includes:
   - `HeroRightSessions`;
   - `getProgramSessions(program, {status:'upcoming', page:1, limit:3})`;
   - guest sign-in routing and authenticated `BookingModal` behavior;
   - voucher-summary refresh and session refresh after booking.
5. Reconcile tests introduced by the redesign. Assertions such as “sessions API is never called” become stale when sessions are explicitly restored; replace them with an exact call-count/argument assertion while retaining the original no-extra-fetch coverage.
6. Keep the redesigned hero and Product/Package catalog intact. Insert the restored section at the requested seam instead of reverting the whole page.
7. Verify targeted tests, scoped lint, clean-env Vite build, deployment, HTTP 200, and a screenshot showing the section in the exact requested order.

## Pitfalls

- A visual section is often coupled to booking/auth/voucher state. Restoring only its JSX produces dead CTAs.
- A test may pass while TypeScript build fails on optional DOM values. Run the production build after tests.
- Preserve canonical slug routes for “See all” and booking paths even when the page was opened using an internal ID.
