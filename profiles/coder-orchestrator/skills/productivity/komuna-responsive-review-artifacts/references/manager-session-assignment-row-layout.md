# Manager Session Assignment and Row Layout

Session learning from the Komuna product-scoped manager dashboard.

## Symptom pair

- Activated sessions show **Manager required** even though the session DTO contains the assigned manager.
- Foreign-owned activated rows become misaligned only when the lock state appears.

## Root-cause pattern

A product-scoped manager surface may intentionally skip loading the full program-members collection. If a shared row resolves display identity only through `managers.find(...)`, that lookup can be empty while the occurrence still carries authoritative assignment fields such as `managerId`, `managerName`, and `managerImageUrl`.

Separately, CSS Grid alignment can break when a conditional ownership/lock badge is emitted as an extra direct child. A five-column row that normally renders date, manager, booking, status, and actions becomes six children only for locked active rows, causing auto-placement into an unintended column/line.

## Smallest safe fix

1. Keep the member-list visibility/scoping behavior unchanged.
2. Resolve display identity from the optional manager lookup first, then fall back to the occurrence DTO:
   - name: `manager?.name ?? occurrence.managerName`
   - image: `manager?.imageUrl ?? occurrence.managerImageUrl ?? null` when the occurrence type exposes it
3. Preserve the unassigned state: show **Manager required** only when neither source has an assigned name.
4. Keep exactly one status grid child. For foreign-owned active rows, render `Locked · <manager>` inside that existing status cell instead of adding another badge sibling.
5. Do not broaden API access or fetch all members merely to repair display data already present in the DTO.

## Regression shape

At the shared dashboard/page boundary, use realistic occurrences for:

- an active session owned by the current manager,
- an active session owned by another manager,
- optionally an inactive/unassigned session.

Assert:

- assigned manager names render in upcoming rows,
- **Manager required** is absent for assigned occurrences and remains for unassigned ones,
- the foreign row exposes its locked accessible label,
- restricted attendee/deactivate/reassign actions remain absent,
- every compact session row has exactly the expected number of direct grid children (five in the current layout).

The direct-child-count assertion is deliberate: text-only tests can pass while CSS Grid auto-placement remains structurally broken.

## Pitfalls

- Do not fix this by fetching the entire member directory on a scoped manager page; that is larger, slower, and may broaden role-visible data.
- Do not add a CSS exception for the sixth child. Preserve the semantic column invariant instead.
- Do not merge manager identity and ownership authority. DTO fallback is for display; action permissions must still use authenticated ownership fields.
