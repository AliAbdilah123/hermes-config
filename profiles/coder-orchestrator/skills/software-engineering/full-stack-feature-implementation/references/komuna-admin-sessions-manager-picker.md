# Komuna admin sessions manager picker implementation note

Use this when implementing admin session-product UX that changes per-session managers.

## Durable pattern
- Frontend activation and manager reassignment can share one picker state: `{ mode: 'activate' | 'change', session, generatedSessionId? }`.
- Keep activation behavior as-is, but route change mode to a dedicated API method such as `PATCH /sessions/:id/manager`.
- Filter picker candidates to managers scoped to the selected product (`role === 'manager' && role.product_id === session.product_id`) so managers from other products never appear.
- In tests, use future-dated sessions and at least one session-template slot; otherwise the sessions tab may not render the row/details path expected by the test.

## Backend guardrails
- Validate the requested manager against `product_managers` for the session product before updating `assigned_manager_id` and `coach`.
- Preserve admin/product-manager authorization checks on the same route family as activate/deactivate.
- Add a small backend test that inserts a valid product manager, calls the manager endpoint, and checks both `assigned_manager_id` and display `coach`.

## Deploy verification pitfall
- Building/copying the web dist only proves the frontend is live. If the feature includes a backend endpoint, verify the API process has been restarted or clearly report that only the pushed code is available when service restart permissions block deployment.
