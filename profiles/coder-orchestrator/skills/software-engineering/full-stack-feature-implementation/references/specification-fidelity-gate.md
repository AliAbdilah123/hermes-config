# Specification-fidelity gate

Use after an autonomous agent implements a detailed, multi-step feature and before broad verification, deployment, or completion reporting.

## Requirement ledger

Compare the final implementation literally against the request, field-by-field and option-by-option. For onboarding/setup flows, audit:

- every step, field, required/optional rule, exact default option, custom-value path, and skip path;
- semantic fidelity: do not substitute nearby concepts (for example phone for business description, generic goals for monthly target/contact channel/team size, or broad service labels for an exact supplied catalog);
- persisted resume state and server-side access enforcement, not merely a frontend conditional;
- transactional, idempotent initialization with a uniqueness strategy for every generated record class;
- dashboard/checklist labels and completion predicates; unsupported predicates remain incomplete rather than receiving invented evidence;
- refresh, logout/login, manual protected-route access, double-submit, mobile layout, and validation/error states.

## Correction loop

If the first pass drifts from the specification, write focused failing tests for the missing contract, confirm RED, then correct the implementation and confirm GREEN before running final suites. A green build does not compensate for implementing the wrong fields or options.
