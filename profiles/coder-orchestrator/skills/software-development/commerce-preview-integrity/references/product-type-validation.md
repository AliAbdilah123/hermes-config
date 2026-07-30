# Product-type validation matrix

Use this when an admin product form supports both scheduled/session and simple products.

| Boundary | Session product | Simple product |
|---|---|---|
| Product managers | At least one required | None required; submit `[]` |
| Weekly schedule | Required and validated | Omitted/ignored |
| Capacity | Positive value required | Omitted/ignored |
| Manager synchronization | Persist selected assignments | Clear stale assignments safely |
| Package entry | Validate under package rules | Validate under package rules |

## Regression checks

1. Create a simple product with no manager: no manager error in UI and API accepts it.
2. Edit a simple product with no manager: API accepts it and stale manager rows are removed.
3. Create/edit a session product with no manager: frontend blocks it and backend independently returns `manager_required`.
4. Switch an in-progress form from session to simple: hidden manager/schedule state must not leak into the payload.
5. Run focused form tests, backend handler tests, preview-scoped build, then exercise the exact public admin route against the isolated preview API.

Avoid validating only the visible error string: UI and API must agree on the product-type rule.