# Task-run conversation attribution

Use this when a task timeline or agent session appears to contain work from another task.

## Evidence sequence

1. Identify the exact run from the application database using the supplied session ID. Join the run to its task/job and inspect prior runs for that same job.
2. Fetch the original session and full message list from the workspace-configured agent API. Do not infer ownership from UI excerpts or local conversation history.
3. Inspect the first user message for the injected project/workdir and original task prompt.
4. Review every user-message boundary and distinguish:
   - another task prompt inside the session: probable cross-task contamination;
   - tool exploration of old files/prototypes: same-task investigation;
   - repeated retries or changed implementation approaches: same-task execution drift;
   - comments that requeue a completed card into a new session: several sessions for one job.
5. Compare database run status, remote session end state, and final assistant output. A run still `running` with many tool calls and no final response is unfinished, not necessarily mixed.

## Keep the identities separate

- **Job/task ID**: persistent card receiving comments and retries.
- **Run/attempt ID**: one execution attempt for the card.
- **Agent session ID**: conversation backing a run, unless retry logic deliberately reuses it.

One job can legitimately have multiple runs and session IDs. Verify runner code and stored records rather than assuming session creation or reuse behavior.

## Classification

Report one conclusion with decisive evidence:

- **Confirmed cross-task contamination** — unrelated task prompt/messages occur inside the session.
- **Same-task execution drift** — messages trace to one prompt, but the worker explored several approaches or old repository artifacts.
- **Multi-attempt timeline confusion** — the UI combines runs/sessions belonging to one job.
- **Insufficient evidence** — the original session source could not be inspected.

State the exact job → run → session relationship and quote only the smallest decisive excerpts. Investigation is read-only unless the user explicitly asks for a fix.
