# Local OTP auth and persisted CRUD browser verification

Use this for a locally built Go/SQLite + SPA application whose development OTP sender writes codes to an injectable log.

## Runtime isolation

1. Build the final binary before starting the test.
2. Allocate an ephemeral free port; never assume a familiar port is available.
3. Use a temporary SQLite database and a test-only server secret.
4. Start the exact binary and require a service-specific health payload before browser actions.
5. Keep the OTP log and browser dependencies outside the repository.
6. Register cleanup for the process, DB, WAL/SHM, logs, and temporary browser package directory.

## Browser flow

Exercise the product boundary rather than inserting sessions directly:

1. Submit the login email through the SPA.
2. Read the generated six-digit code from the development sender log.
3. Enter the OTP through the SPA.
4. Complete onboarding through the rendered form.
5. Perform the feature mutation through the UI.
6. Reload and assert persisted values from stable DOM controls or visible content.
7. Use a second isolated browser context for non-owner authorization checks.
8. Log out and assert the session endpoint returns `401`.

Use stable selectors from the actual rendered contract: exact accessible labels or durable element IDs. Before retrying a failed harness, inspect the current JSX/DOM. Do not guess IDs or use Testing Library-only helpers on Playwright `Page` objects.

## Failure classification

Treat these as harness failures, not product failures:

- strict-mode locator ambiguity after the expected page was reached;
- a selector based on a guessed field name or stale ID;
- use of an API belonging to another test framework;
- expected `401` resource messages during anonymous session bootstrap or after logout.

Capture `pageerror` separately from console/network errors. Allow only explicitly expected `401` requests; unexpected console errors still fail the gate.

If the browser completed a write but a final visual assertion was ambiguous, do not repeat the side effect blindly. Verify terminal state with the runtime DB and API instead: persisted row/state, `PRAGMA integrity_check`, public visibility, and owner/non-owner behavior. Rerun the whole flow only when those checks cannot establish the terminal state.

## Minimum evidence

- focused auth/authorization tests, preferably with Go race detection;
- full canonical tests, vet/typecheck, frontend production build, and exact binary build;
- browser login → OTP → onboarding → mutation → reload → logout;
- second-context owner-isolation assertion;
- SQLite integrity and confirmation that OTP/session/CSRF values are hashes/HMACs, never raw credentials;
- explicit process and temporary-data cleanup.
