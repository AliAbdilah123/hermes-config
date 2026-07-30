# Approval-gated agent job workflows

Use this pattern when a board turns one agent session into proposal review followed by approved implementation.

## State and session invariants

- Persist review versus implementation explicitly; never infer phase from assistant prose.
- Use atomic transitions such as `todo → in_progress(review) → in_review → in_progress(implementation) → done`; guard double approval.
- Resume the same agent session for approval and feedback. Approval sends an explicit implementation instruction. Feedback records a timeline event and requeues at the end of Todo without losing session identity.
- Treat the session title as display identity and the task as private execution input. Create a bounded fallback immediately, then synchronize the authoritative title through the documented session-metadata endpoint. Do not invent response fields or call another model merely to generate a title.

## UX and notification invariants

- Structure notifications as lifecycle action plus job title. Emphasize the action, render the title as subdued secondary text, and omit the prompt.
- Scope localStorage drafts by user, board, and entry point. Persist every serializable field whose loss changes submission—including a top-level form's selected column—but never persist `File` objects.
- Clear drafts only after successful creation or explicit discard.
- Prevent backdrop and Escape dismissal for loss-sensitive creation dialogs. Provide a close path that preserves the draft and a separate destructive discard action.
- Bound long textareas visually with internal scrolling rather than allowing indefinite growth.

## External channels

- Keep provider credentials server-side; expose only availability plus workspace routing settings.
- Use short HTTP timeouts, escape provider markup, include a safe deep link when configured, and make delivery failure non-blocking for the underlying job transition.
- Do not introduce a provider abstraction until a second external channel genuinely requires it.

## Verification boundary

Run state-transition, migration/foreign-key, draft serialization, notification privacy, settings authorization, frontend tests, and production build checks. On deployment, distinguish served-bundle markers and API reachability from authenticated visual E2E. If browser automation cannot exercise the logged-in flow, report that boundary as unverified rather than calling production E2E complete.
