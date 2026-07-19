Review documents must be responsive styled HTML with a theme toggle and public link. Komuna docs stay under Komuna and its ERD tracks DB changes; unassigned docs go in ~/docs.
§
User wants every final update after working on a feature or fix to include the project's public link. Always commit and push to git after every feature implementation or bug fix.
§
User prefers small, straightforward errors to be fixed directly without a planning artifact; for larger or complex errors, create a plan and styled HTML review artifact first.
§
User prefers clean code: SRP, small focused functions/files, DRY, clear names, comments only for non-obvious logic, boundary validation, and simplest practical implementation.
§
Coding tasks: use Codex CLI to implement. Reuse first: inspect code/history and extend existing components/workflows before creating files; preserve full workflows.
§
User prefers bug-fix final reports to include the root cause of the bug.
§
User does not want live implementation/deployment from design-choice or debug requests alone. For substantial UI redesigns, work in a separate branch/worktree and provide an isolated public preview; merge/deploy live only after explicit approval.
§
Discord #p-paragentix channel conversations concern the Paragentix project by default unless explicitly stated otherwise.