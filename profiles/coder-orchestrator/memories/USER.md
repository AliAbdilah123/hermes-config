Review artifacts: responsive themed HTML with toggle/public link; Komuna docs stay under Komuna, others in ~/docs.
§
Feature/fix work continues through verification without pausing at status updates; production finals include public link, commit, and push.
§
User prefers small, straightforward errors to be fixed directly without a planning artifact; for larger or complex errors, create a plan and styled HTML review artifact first.
§
User prefers clean code: SRP, small focused functions/files, DRY, clear names, comments only for non-obvious logic, boundary validation, and simplest practical implementation.
§
Coding: use Codex CLI, preferring `gpt-5.6-sol`, `medium` reasoning, and priority speed unless specified otherwise. Reuse existing code/workflows before creating files.
§
User prefers bug-fix final reports to include the root cause of the bug.
§
Komuna creation uses isolated worktree/public preview; production only after explicit approval; “not approved” removes preview. Other design/debug requests also do not authorize live changes.
§
Komuna reports: verify WIB date every time; use only that reporting period, never stale progress. Mondays cover Friday plus unreported weekend work.
§
Job UX: editable todos first; parallel columns, sequential jobs; history is grey text, not bubbles. Done/blocked replies requeue at todo end.