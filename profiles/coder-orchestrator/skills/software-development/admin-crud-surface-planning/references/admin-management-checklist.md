# Admin Management Checklist

## Inspect

- [ ] Route and navigation visibility
- [ ] Existing page/list/form implementation
- [ ] Shared modal, form-action, table, badge, and input components
- [ ] List/create/update/status endpoints
- [ ] Database fields and constraints
- [ ] Global versus tenant-scoped authorization
- [ ] Existing frontend, backend, and public E2E coverage
- [ ] Current design tokens and responsive shell

## Define each table

- [ ] Search fields
- [ ] Filter dimensions
- [ ] Sortable columns and default sort
- [ ] Visible columns
- [ ] Explicit primary create/add action button in the view toolbar or page header for every entity tab
- [ ] Row actions
- [ ] Result count
- [ ] Loading/error/empty/no-results states
- [ ] Mobile overflow or alternative presentation
- [ ] `aria-sort`, labels, focus states, and 44px targets
- [ ] Global context/shell selector synchronization after mutation

## Define each mutation

- [ ] Create/edit modal fields and validation
- [ ] Immutable identifiers
- [ ] Save/cancel/error behavior
- [ ] Focus trap, Escape, backdrop, and focus return
- [ ] Enable/disable confirmation policy
- [ ] Selected-context behavior after disabling
- [ ] Reload persistence
- [ ] Server authorization and CSRF

## Terminology rename

- [ ] New user-facing term is consistent
- [ ] Obsolete term is absent from touched UI
- [ ] Stable internal endpoint/schema/capability names are documented
- [ ] No cosmetic migration is proposed without need

## Verify

- [ ] Privileged route visible and usable
- [ ] Non-privileged route hidden and server-denied
- [ ] Search/filter/sort combinations work
- [ ] Dialog keyboard behavior works
- [ ] Status changes persist and affect operational access correctly
- [ ] Typecheck, lint, tests, backend tests, build pass
- [ ] Live artifact rebuilt/restarted/deployed
- [ ] Public E2E and console checks pass
- [ ] Changelog updated
