# Implementation vs deployment authorization

Use this when an approved planning artifact contains separate implementation, deployment, and READY gates.

## State and authorization sequence

1. An explicit “implement the plan” authorizes product-code changes, local tests, and a reviewable working tree.
2. It does not automatically authorize deployment if the plan or project workflow separately requires deployment approval.
3. Report `WORKING` only while implementation is actively executing.
4. Report `VERIFYING` while rerunning canonical tests/builds, checking the working tree and `git diff --check`, reviewing API/UI contracts, and obtaining an independent pre-commit review.
5. A coding-agent completion summary is not verification evidence; rerun checks directly.
6. Ask for deployment approval after local verification passes when deployment is separately gated.
7. Run authenticated public E2E against the deployed artifact. Do not report `READY` before that E2E passes.
8. Commit and push only when the project’s delivery gate permits them; preserve unrelated dirty/untracked files through explicit path staging.

## Pitfalls

- Do not collapse “implementation approved” into “deployment approved.”
- Do not claim READY from unit tests and a build alone when public authenticated E2E is required.
- Do not trust an autonomous coding agent’s stated test results without fresh direct execution.
- Do not stage pre-existing planning artifacts or unrelated files merely because they are present in the working tree.