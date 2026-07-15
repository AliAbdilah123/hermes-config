# SelfFlow bulk task edit field additions

When adding another editable task field to SelfFlow's bulk edit dialog, keep the change thin and aligned to the single-task form.

## Pattern

1. Inspect `packages/fe/src/components/dialogs/TaskDialog.tsx` for the canonical field options and labels.
2. Patch `packages/fe/src/components/dialogs/BulkEditTasksDialog.tsx`:
   - import the field type from `@/types`;
   - add local state for the optional field;
   - include it in `canApply`, reset/cancel cleanup, and the `updates` payload;
   - add a `Select` using the same option values as `TaskDialog`;
   - show current selected-task distribution and preview badge when applicable.
3. Patch frontend API typing in `packages/fe/src/lib/api-client.ts` and the caller typing in `packages/fe/src/pages/HomePage.tsx`.
4. Before adding backend code, inspect the active Go handler. For task bulk updates, `packages/api/v1/internal/store/handlers.go` already allows `status`, `effort`, and `priority` through `validateItem("tasks", updates, false)` and the bulk `switch`.
5. Verify with `corepack pnpm build` from `packages/fe`, deploy `dist/` to `/var/www/html/projects/self-flow/`, then grep the deployed/public bundle for a unique UI marker.

## Pitfall

Do not invent a new status list in the bulk dialog. Reuse the existing `TaskStatus` values shown in `TaskDialog`: `todo`, `in progress`, `blocked`, `completed`, `not done`, `delegated`, `commitment`.
