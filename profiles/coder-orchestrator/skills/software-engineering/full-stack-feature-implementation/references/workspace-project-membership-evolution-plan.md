# Planning Workspace → Project → Column and Membership Evolution

Use this when an existing multi-user app already has partial Workspace/Project tables but product feedback changes ownership, authorization, and creation flows together.

## Read-only inspection before planning

1. Inspect the live schema/migrations and trace the actual route handlers and frontend forms.
2. Check whether the requested entity already exists but has incomplete CRUD/UI. Extend it; do not create a competing model.
3. Record dirty working-tree files before proposing implementation. Explicitly preserve/reconcile unrelated edits.
4. Separate current evidence from requested outcomes in the review artifact.

## Minimal model transition

- Workspace owns collaborative identity and memberships; remove directory input from Workspace UI/API.
- Project belongs to Workspace and owns its directory.
- A child execution container such as Column references one Project; one Project can serve many Columns.
- Introduce membership as the authorization boundary instead of owner IDs scattered through queries.
- Keep legacy owner/root columns temporarily when that makes additive SQLite migration safer.
- Backfill existing owners into memberships and legacy Workspace directories into deterministic default Projects before requiring child `project_id`.
- Make the new FK nullable during additive migration; enforce required selection in application code first, then rebuild with `NOT NULL` only after live migration safety is proven.

## Authorization and invitation rules

- Centralize `member` and `owner` checks and apply them to Workspace, Project, Board, and Column queries; hidden buttons are not authorization.
- Protect the last owner from removal.
- Invitations should normalize email, use random one-time tokens, persist token hashes, expire, and accept idempotently in a transaction.
- Registered and unregistered recipients share one invite flow: authenticate/signup, then resume acceptance.
- If email transport is not already present, call that out as an explicit integration decision. Prefer a tiny fakeable mail seam and stdlib SMTP over a new SDK; never claim delivery without configured transport and a real result.

## Review artifact shape

For this cross-cutting change, publish separate responsive pages:

1. **Plan:** problem ledger, current code evidence, confirmed domain model, feature-grouped backend/frontend/tests, migration order, risks, open policy questions, and implementation gate.
2. **Design:** workspace list, tabbed detail, Project modal, Users/invite states, and the child Project selector in real app-shell context.

Do not implement from feedback alone when the user's workflow expects design review first. Answers to policy questions update the artifacts; implementation still requires explicit wording.

## Verification checklist

- Migration runs twice safely against a copy of the existing DB.
- Cross-user and cross-Workspace IDs are rejected without leaking records.
- Existing records receive deterministic memberships/Projects/FKs.
- Workspace creation has no directory field in UI or payload.
- One Project can be selected by many child records.
- Invite tests use a fake mailer and cover registered, unregistered, expired, reused, and wrong-recipient cases.
- Desktop/mobile browser checks cover list → detail tabs → modals and outside-click menu dismissal.
