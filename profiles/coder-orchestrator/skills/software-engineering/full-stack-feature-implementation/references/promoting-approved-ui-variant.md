# Promoting an approved UI variant

Use this when a user selects one of several review mockups and asks to implement it in the current product branch.

## Procedure

1. Re-open the exact production route/component and its tests. A sketch's fake content is illustrative, not an API contract.
2. Preserve the selected design stance and hierarchy, but map covers, badges, counts, controls, and states to fields the real API already returns. Do not add backend work merely to reproduce decorative mock data.
3. Write a failing behavior test first for the defining elements of the selected direction. For a visual portfolio this commonly means cover selection, destination labels, counts, search, and status filters.
4. Implement the smallest production diff that passes. Preserve navigation behavior and accessible names; label search and filter controls and keep a plainly named resource link even when the cover is also clickable.
5. Verify the focused test, typecheck, production build, and diff check. If the repository is dirty, stage only the exact implementation paths.
6. When asked for the current branch, commit and push that branch, then prove local and remote SHA equality.
7. Separate source delivery from deployment. HTTP 200 only proves the route responds. Compare the served asset reference, deployment marker, or build metadata against the new build/commit. If stale, report push complete and deployment pending rather than saying the UI is live.

## Pitfalls

- Implementing directly from the mockup without inspecting the real DTO.
- Treating placeholder copy or metrics as required backend fields.
- Dropping loading, error, empty, keyboard, or mobile states because the review artifact did not show them.
- Claiming deployment from a successful route probe while the host still serves the previous asset bundle.
