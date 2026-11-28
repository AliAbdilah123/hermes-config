# Community membership feature expansion planning

Use this reference when expanding an existing guild/community product with membership history, dues, custom member records, events, payments, badges, and cross-group posts.

## Reconcile before extending

1. Inspect both committed baseline and uncommitted/in-progress implementation.
2. Preserve working primitives already present (for example post↔group junctions, attachment storage, audit logs, dialogs, and transaction helpers).
3. State which earlier plan sections are superseded. Do not leave two conflicting billing or visibility models as equally authoritative.
4. Group the amendment by feature. For each feature include outcome, data/backend, frontend/UX, tests, and phase.

## Membership is a historical period

Model each join→leave interval as a unique entity:

```text
group_memberships
- id
- group_id, user_id, role
- joined_at, ended_at NULL
- ended_by, end_reason
- created_at, updated_at
- UNIQUE(group_id, user_id) WHERE ended_at IS NULL
```

Closing membership never deletes the period. Rejoining creates a new ID. History-sensitive rows—charges, settlements, custom field values, and badge assignments—reference `membership_id`, not only `(group_id,user_id)`.

Join-date edits must reject overlaps, impossible ordering, and invalid future dates, and must audit actor plus old/new values. Authorization uses only the active period.

## Monthly dues and debt

When the product must show unpaid months and permit settling arbitrary months, duration-only entitlement (`paid_days`) is insufficient. Model explicit monthly obligations:

- one idempotent charge per fee plan + membership period + service month;
- debt is the sum of overdue open charges;
- paid/waived/void/future months are excluded;
- batch settlement selects explicit months and stores list total, actual paid total, and discount;
- annual discounts settle every selected month while preserving the discount as first-class data;
- corrections append audited adjustments rather than overwriting payment history.

Use the guild's IANA timezone for month boundaries. Decide whether the join month is full, prorated, or starts next month.

## One settlement engine, several payment paths

Keep `admin_adjustment`, `manual_transfer`, and `gateway` as methods feeding one transactional settlement function.

- Manual transfer starts pending, includes private proof, and settles only after admin approval revalidates charges.
- Gateway amounts and ownership are recomputed server-side.
- Verified provider events are signature-checked, uniquely stored, and processed exactly once.
- Redirects never mark payment paid.
- Concurrent approval/provider completion must not settle a charge twice.

## Configurable member data

Use guild-scoped field definitions plus membership-period values. Prefer a constrained type set (`short_text`, `long_text`, `number`, `date`, `url`, `file`, `person_list`) over arbitrary schemas. Block incompatible type changes once values exist; archive definitions instead of deleting them. Sensitive files require authorized download handlers and content-sniffed uploads.

## Visibility matrices

Define visibility by audience and enforce it in server projections:

- Badge: `public | group | group_admin`.
- Post/event: `public | group`.
- Custom member field: `member_self | group_admin`.

Explicitly decide whether a holder can see their own `group_admin` badge. Public projections must omit private actor identity, email, private listings, member fields, and group-only event data.

## Cross-group posts and events

Reuse an existing post↔group junction rather than introducing tags stored on the post. Placement deletion affects only that group. Keep canonical events separate from posts and attach them by reference; event ownership remains with the origin group when a post is shared.

## Recommended delivery order

1. Finish and verify already-started compatible primitives.
2. Introduce unique membership periods and migrate active memberships.
3. Add explicit monthly dues, debt summaries, and batch admin settlement.
4. Add badge visibility and configurable member fields.
5. Add public/group post projection and event attachment.
6. Add manual-transfer approval.
7. Add one gateway only after provider choice and test credentials.
8. Run migration, authorization, desktop/mobile, anonymous/member/admin, and duplicate-settlement E2E checks.

## Required policy questions

Ask only decisions that change schema or behavior: gateway provider, guild timezone, first-month charging policy, self-visibility of admin-only badges, member edit rights for custom data, and one-vs-many events per post.
