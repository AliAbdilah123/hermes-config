# Post-signup social connection onboarding

Use when newly registered users should be prompted to connect Instagram or Facebook without navigating to Settings.

## Minimal architecture

- Add a protected, focused route such as `/app/onboarding/connect` rather than placing an OAuth modal across the public signup/authenticated-app boundary.
- Reuse `fetchInstagramAccounts`, `fetchFacebookPages`, `startInstagramConnect`, and `startFacebookOAuth`; do not duplicate OAuth or account persistence logic.
- Reuse the existing platform requirements/announcement step before starting OAuth.
- Keep onboarding signup-driven, not a global blocking gate for existing users. Include an explicit `Skip for now` path.

## Routing precedence

1. Unverified email signup remains in email verification.
2. Preserve an onboarding intent through verification so successful verification continues to account connection.
3. Paid-plan checkout keeps precedence over onboarding.
4. Verified free/no-plan email signup and Google signup go to onboarding.
5. Successful connection, Continue, or Skip goes to the dashboard.
6. Normal login behavior remains unchanged.

## OAuth return behavior

- Return callbacks to onboarding, refresh live provider state, and show connected/success or actionable error state.
- A successful first connection must not auto-navigate to the dashboard. Keep onboarding open, mark the connected provider complete from refreshed API state, and allow the second supported provider to be connected.
- Navigate to the dashboard only from explicit `Continue to Dashboard` or `Skip for now` actions; keep both actions visible even after one provider connects.
- Do not change Meta scopes, provider tokens, database schema, or backend account APIs unless source inspection proves the existing helpers are insufficient.

## Onboarding page UX contract

- Lead with concise benefit copy naming the real outcomes: scheduling, publishing, comment replies, and analytics; state that connection is optional and remains available later in Settings.
- Use a lightweight visual-only three-step indicator: `Create Account ✓`, `Verify Email ✓`, and `Connect Accounts (current)`. It must not drive routing or persistence.
- Reuse each provider's existing pre-OAuth requirements gate and connection helpers rather than duplicating Settings implementation details.
- Treat connected state as API-derived state after refresh, not a local success assumption from callback query parameters.

## TDD pitfall

- Assert the exact requested progress labels and benefit concepts in the component test. A generic `Step 2 of 2` bar or vague benefit sentence can compile and pass broad tests while missing the approved UX.
- Await initial account refresh before interaction assertions (for example with `findBy*` or `waitFor`) so React state updates do not leak `act(...)` warnings into otherwise passing tests.

## Focused verification

- Route-decision tests: verified free signup, paid-plan signup, unverified signup plus post-verification intent, and Google signup.
- Component tests: requirements gate, connect action, callback refresh, connected state, error state, and Skip.
- Run focused Vitest tests, `pnpm typecheck`, and `pnpm run build` after the final artifact/source edit.
- If a review HTML artifact is the only changed file but workspace policy requests the canonical frontend build, run it before reporting verification; artifact-specific assertions complement rather than replace the canonical build.
- On deployment, confirm the generated onboarding asset is served as JavaScript rather than the SPA HTML fallback.
