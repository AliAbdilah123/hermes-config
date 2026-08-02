# Role-context approval and notification E2E

Use for workflows where one authenticated account may hold multiple roles and a role-specific action requires approval.

## Contract rule

Do not infer action intent from the user's highest database role. Use intent-specific endpoints: a request-only endpoint must be structurally unable to perform the privileged direct action, even for a dual-role account. Keep the privileged endpoint explicit and separate.

## Required regression

Exercise a dual-role Admin + Manager account through the public preview:

1. Submit from Manager context.
2. Assert HTTP `202` and a persisted `pending` request.
3. Query the isolated database: target remains inactive/unassigned.
4. Confirm the same request is visible in Admin and Manager role-scoped inbox data.
5. Approve/reject as Admin.
6. Assert state changes exactly once and only after approval; rejection requires its reason where applicable.
7. Confirm requester notification records the outcome.

An API unit test or mocked controller test alone does not prove this flow.

## Notification deep links

For request and decision notifications, include enough destination context—normally program, role-specific Sessions route, product ID, and optionally request ID—to open the relevant inbox automatically. Verify all of:

- generated `action_url` for Admin and Manager;
- public notification payload;
- click/navigation pathname and query/state;
- correct product card/inbox opens automatically;
- request row is visible after navigation;
- preview basename is preserved by the client/router.

A notification database row or `href` assertion alone is insufficient.

## Deployment proof

After backend/frontend changes, rebuild both artifacts, replace/restart the isolated API, publish the preview-path frontend, and prove the replacement is served using listening/health evidence plus public hashed asset names. Then rerun the authenticated public flow against the isolated database. Production must remain unchanged until explicit approval.
