# Ordered stack migration and gate verification

Use when an approved multi-milestone product must be adapted to an organization’s existing stack.

1. Inspect the approved plan and the organization’s boilerplate before editing. Treat the boilerplate as authoritative for runtime, package manager, architecture, tests, and deployment shape; do not modify it.
2. Record explicit substitutions (for example SQLite/local disk/native SSE instead of PostgreSQL/S3/Redis) and remove infrastructure that is no longer needed rather than adding compatibility layers.
3. Execute one milestone at a time. Each delegation prompt must include the exact gate, prior verified baseline, path boundary, stack, TDD requirement, and prohibition on later milestones.
4. Independently verify subagent claims from the final workspace. Search for gate assertions, then rerun focused tests, full regression tests, static checks, and production builds. A targeted subagent report is not a full-suite claim.
5. Treat failed patches and missing artifacts as acceptance risks. Inspect whether behavior exists despite a failed patch. Check required documentation/examples as files, not merely test output.
6. Do not advance when any gate artifact is absent. Dispatch a narrow continuation for the gap, rerun the complete gate, then proceed.
7. For single-host native substitutions, leave one concise `ponytail:` ceiling comment identifying when distributed infrastructure becomes necessary.

Final completion still requires authenticated public E2E, deployment evidence, commit, and push when those are part of the user’s standing acceptance contract.