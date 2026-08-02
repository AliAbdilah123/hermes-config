# Session approval workflow preview verification

Use for role-gated session activation where managers request and admins approve.

## Approval invariant

Every manager activation entry point must create a pending request and must not activate or assign the session before approval. Audit all UI branches, especially persisted rows, generated/template occurrences, calendar details, and compact/mobile actions.

Generated occurrences must first be persisted without activation, then submitted through the same request endpoint. A frontend branch that calls the ordinary activation controller after generation silently bypasses approval even when the backend correctly gates persisted manager requests.

## Required regression matrix

For both persisted and generated occurrences, assert:

1. the manager action opens the reasoned request flow;
2. `requestActivation` is called;
3. direct `activate`/assignment is not called;
4. session state remains inactive and unassigned;
5. refresh occurs after submission;
6. the request appears pending in the manager log;
7. the same record appears in the admin inbox;
8. admin approval activates exactly once;
9. rejection requires a reason and leaves the session inactive;
10. admin-originated direct activation remains available.

Mocks should mutate the shared request fixture on submission before refresh/rerender; otherwise an inbox assertion against pre-seeded data does not prove the round trip.

## Public isolated preview

A reviewable preview needs an isolated API and database because request creation and approval are writes. Verify the exact public flow with separate manager and admin sessions, not only unit tests.

For profile images, expose a preview-aware media route through the preview API prefix, mount preview-safe uploads beside the isolated runtime, preserve the preview prefix in frontend asset normalization, verify an actually referenced avatar returns an image MIME type publicly, and retain initials fallback. A generic image probe is insufficient if the database references another filename.

## Dual-role authorization trap

A user can be both Admin and Product Manager. Never overload one activation endpoint and infer intent solely from the user's highest role: a Manager-dashboard request can be treated as an Admin direct activation. Use separate contracts:

- Admin direct activation endpoint: may activate immediately after admin authorization.
- Manager request endpoint: request-only by construction, always creates a pending record, and never activates—even for dual-role users.

Public E2E must use a real dual-role identity when that state exists. After submission, inspect persisted state: request is `pending`, session remains inactive, and manager assignment is null. Confirm both role-scoped inbox responses before approval, then confirm activation only after the Admin decision.

## Notification dropdown deep links

Verifying a stored notification body or generated URL is not enough. Trace the complete path: notification creation → DTO serialization → dropdown item `href` → router transition → route query parsing → relevant product inbox auto-open.

Activation notifications should include the product identifier and role-specific destination:

- request submitted → Admin Sessions route and product request inbox;
- approved/rejected → Manager Sessions route and product request inbox.

Test the actual dropdown click with a router location probe. Also cover legacy/plain-body notifications: if old rows only carry the activation-request ID in `target_id`, derive the destination from the request record during DTO serialization. Preserve a safe structured `action_url` when present; never fall back old activation notifications to a generic notifications page merely because their body predates deep links.

## Calendar selection UX

When a calendar stacks above details on mobile, selecting a time pill should scroll the actual detail panel into view after selection renders. Use a stable ref and `scrollIntoView({ block: 'nearest' })`; respect reduced motion. Guard optional browser APIs for non-browser test environments, then verify a real mobile viewport.

## Status communication during long verification

Use status labels literally and proactively:

- **WORKING** only while a tool, background process, or concrete next operation is actively underway.
- **VERIFYING** only while checks are actively running; do not stop after announcing it.
- **READY FOR REVIEW** only after the requested public interaction—not merely its API URL—has passed.
- **STOPPED** or **BLOCKED** immediately when no operation is active or progress cannot continue.

After a background process completes, continue with independent verification/deployment without waiting for the user to ask. Never repeatedly announce “verifying” while no command or browser flow is running.
