# Komuna Sessions tab: implementing an approved design artifact

Use when implementing Komuna admin Sessions tab changes from a previously published `/prd/...sessions...design.html` artifact.

## Workflow lesson

- If the user references an existing design artifact, treat that artifact as the visual source of truth. Inspect it before coding and port its actual class/layout patterns, not a simplified interpretation.
- Do not replace a proposed design with a flatter/minimal version unless the user explicitly asks for simplification. For the Sessions tab, the approved pattern was: product header with left circular chevron, dominant product title, right-side meta chips, compact-but-carded date cells, status pills, expanded detail panel, dashed `See detail` section, and a styled manager modal.
- If a previous implementation went beyond the plan and the user asks to revert “weird changes,” revert only the unwanted behavior, then re-implement missing requested requirements from the plan. Do not drop plan requirements such as the manager picker just because they were part of the reverted commit.

## Manager picker acceptance pattern

- The manager picker belongs in the expanded session detail area below the time/QR section as `Leading manager`, with visible manager option rows and a `Choose manager…` action.
- Activation should open the manager picker modal when no manager is selected.
- Modal should match the design artifact: large rounded dark gradient panel, rounded search bar, scrollable manager list, avatar/initials, single-select radio-dot state, lazy-load/scroll-more cue, and `Assign & activate` CTA.
- Persist assigned manager on the concrete session instance (`assigned_manager_id`) and return `managerName` / `managerImageUrl` in session APIs so other session consumers can display the selected coach.

## Verification markers

After deploy, verify the public bundle contains design-specific markers such as:

- `coach-picker`
- `manager-search`
- `radio-dot`
- `Open product detail`
- `next 5 sessions shown`
