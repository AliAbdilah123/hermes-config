# Project-bound job initial prompt context

Use when a board Column/Lane is linked to a Project and an agent asks the user to identify the project despite that linkage.

## Minimal implementation

1. Trace the execution claim/start path, not only the job-creation form.
2. Resolve the Project through the persisted Job → Column/Lane → Project relationship.
3. Fetch both:
   - the effective execution directory (which may be a Column worktree), and
   - the canonical Project name and directory.
4. Prepend stable context to the first agent prompt:

```text
Unless otherwise specified, this conversation concerns the project <name>, located at <directory>. Use this project as the default when creating or modifying jobs.

<task>

Done definition:
<criteria>
```

5. Keep execution-directory selection separate from conversational identity: a worktree may be the process working directory, but the canonical Project should remain the default project context unless product requirements explicitly say otherwise.
6. Do not change Done-definition validation while fixing missing Project context; investigate that behavior separately.

## Verification

Add a focused test for the prompt-construction helper that asserts the exact Project name, canonical directory, task ordering, and Done-definition ordering. Then run the full backend suite and build/restart the deployed service when implementation was requested.

## Pitfalls

- Do not rely on the model to infer project identity from the process working directory.
- Do not inject only a path; include the human-readable Project name as well.
- Do not use the worktree path as the canonical Project directory in the context sentence unless that distinction is explicitly desired.
- If source delivery requires a push, inspect the Git remote before the final delivery command so deployment/commit success is reported separately from a missing push destination.
