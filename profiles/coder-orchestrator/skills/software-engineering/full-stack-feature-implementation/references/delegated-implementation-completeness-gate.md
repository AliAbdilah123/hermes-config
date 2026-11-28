# Delegated implementation completeness gate

A delegated agent reporting “implemented” plus green build/API E2E is evidence, not acceptance. Before commit or deployment, reconcile the actual diff against every user-visible capability in the approved plan.

## Review method

1. Build a plan-to-surface checklist. Each capability needs a backend read/mutation path, reachable frontend control, visible state, and focused test.
2. Inspect the interaction path, not only imports, routes, types, or API methods. A display-only list does not satisfy CRUD; an unused client method is not implemented.
3. For administrative workflows, verify the complete loop: configure/create, target/select, execute, inspect status, correct/void where permitted, and retry/error handling.
4. Search for orphaned API methods and response fields—such as pin/unpin, record payment, assign member, or locked counts—that the UI never consumes.
5. Require the states named by the plan: loading, empty, error, success, permission denied, and domain-specific locked/paywall states. A generic query error is not a substitute for a recoverable HTTP 402 state.
6. Reject compressed proof-of-concept JSX and hard-coded business inputs when configurable fields were approved. Match existing component structure, accessibility, and visual conventions.
7. Run independent diff review before release. If it finds gaps, issue a precise remediation list and repeat fresh verification. Never deploy a partial version merely because broad E2E is green.

## Common false positive

API E2E proves hierarchy creation, payment settlement, member assignment, or pinning while the frontend only displays hierarchy/payment/unit/pin data and cannot perform those operations. Treat this as incomplete full-stack delivery.

## Backend robustness pass

Before accepting generated handlers, check path-ID validation, ignored DB/query/scan errors, empty-result indexing, trust-boundary string limits, required payment references/methods, transaction error responses, and group/resource compound scoping.