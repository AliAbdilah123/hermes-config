# Desktop session-calendar detail-panel handoff

Use this pattern when replacing a desktop “upcoming sessions” rail with selected-session details while preserving a separate mobile experience.

## Minimal production change

- Initialize the desktop selected-session ID to `null`; do not silently fall back to the earliest session.
- Render the empty state and selected details in the existing left/list panel itself, rather than nesting another bordered details card inside it.
- Remove the desktop upcoming-list derivation/rendering and obsolete date-selection state, handlers, controls, keyboard behavior, and tests together.
- Keep calendar event buttons as the sole desktop selection mechanism and retain `aria-controls`/live-region semantics.
- Increase detail typography only under the desktop calendar’s scoped classes.
- If the mobile UI is a separate component hidden by a breakpoint, do not modify its markup, state, filters, list behavior, or breakpoint.

## Verification

1. Add a focused behavior test proving the initial empty state, calendar-event selection, booking choices, absence of the removed control, and existing mobile tests.
2. Run the focused test file and production build before commit.
3. When the environment requires explicit artifact evidence, create an OS-safe temporary probe with `mktemp /tmp/hermes-verify-...`, assert the source contract, run it, and remove it. Report this as ad-hoc verification, not suite green.
4. Verify deployed asset hashes and that local HEAD equals its upstream branch.

## Pitfalls

- Do not preserve a now-meaningless glow animation merely because the old right-side panel used it.
- A scoped commit does not imply a clean workspace; stage only the feature files and leave unrelated dirty work untouched.
- Large multi-section patches can partially apply or be hard to inspect. Prefer small replacements, then search for stale identifiers before testing.
