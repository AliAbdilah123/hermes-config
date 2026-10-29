# Feature flow and manual UI verification documentation

Use when the user asks for a `features/` directory or Markdown documentation of complete product flows and step-by-step UI verification.

## Deliverable shape

Prefer one index plus a small set of role/domain guides rather than one file per tiny feature:

- `features/README.md`: canonical environment URL, role map, product-area index, smoke sequence, and current verification record.
- Shared-platform guide: authentication, session, tenant scope, authorization, navigation, messages, accessibility, themes, and loading/empty/error states.
- Role/domain guides: full user flow followed by numbered UI verification steps, expected visible results, validation/error checks, persistence-after-refresh checks, and authorization boundaries.
- Update the project changelog when project convention requires it.

## Evidence workflow

1. Establish the project root and capture Git state.
2. Read route registration, navigation, role/capability mappings, data model, high-signal product docs, test credentials, and existing feature ledgers.
3. Trace behavior through visible entry → interaction → validation/authorization → persistence → resulting UI/retrieval.
4. Resolve and probe the canonical deployed URL from current deployment evidence instead of copying a historical URL from scripts or docs. Mention stale routes only when useful.
5. Run the existing public UI/E2E suite against the canonical URL and record its exact scope/result.
6. Write executable manual steps, including destructive confirmations, tenant leakage checks, responsive behavior, and refresh/persistence checks where applicable.
7. Validate Markdown files, links/file count, `git diff --check`, and final Git status.

## Wording rules

- Distinguish **verified now**, **supported by implementation/tests**, and **manual verification procedure**. A representative smoke suite does not prove every documented mutation was manually exercised.
- Clearly label simulations and mock-only boundaries, especially payment/provider flows.
- Use exact visible labels/headings where stable.
- Point to the repository credential file rather than duplicating passwords.
- Use source routes/components/backend contracts and runtime evidence, not generated bundles or dependency files.

## Common omissions

- Root-mounted deployment versus obsolete subpath URLs.
- Multi-tenant selector contents and foreign-data leakage.
- Direct-link authorization, not merely hidden navigation.
- Invalid-input behavior and required fields.
- Persistence after refresh and history retention after archive/delete/void.
- Mobile navigation, Escape/focus behavior, and horizontal overflow.
- Cross-surface synchronization such as kitchen availability reaching cashier and display.
