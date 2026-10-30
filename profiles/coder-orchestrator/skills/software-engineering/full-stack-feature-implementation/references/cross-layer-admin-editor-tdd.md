# Cross-layer admin editor TDD

Use for administration features that combine backend policy, editable forms, and assignment workflows.

## Acceptance matrix before production edits

Write one failing test at each changed boundary:

1. **Policy/API:** update succeeds, malformed dependencies fail, immutable records reject writes, and affected sessions are invalidated.
2. **Editor UI:** create and edit preload/persist all fields; dependency controls enforce the same rule as the API (for example, Edit selects View and clearing View clears Edit).
3. **Scope UI:** all/limited mode, category selection, individual-item selection, search, archived references, and effective-count behavior.
4. **Assignment UI:** an existing user can open edit, change profile/status, save, and see the refreshed assignment.

Run each new focused test and record the expected RED caused by missing behavior before implementing that boundary. A backend RED does not satisfy TDD for untested frontend production code.

## Paired permission audit

Do not infer every pair from naming alone. Build the UI matrix from the product-approved feature model, then verify each View and Edit key exists in the server allowlist. Legacy capability sets often contain broad dashboard keys or mutation-only names rather than true pairs. If explicit pairs are required, introduce or map both keys deliberately and test route/navigation behavior; merely relabeling unrelated existing capabilities as View/Edit is not sufficient.

## Completion evidence

Report focused RED and GREEN commands per boundary, then fresh full tests, lint, typecheck, and build. Distinguish warnings from errors and do not call the work strict TDD if any changed UI boundary was added without a prior failing test.
