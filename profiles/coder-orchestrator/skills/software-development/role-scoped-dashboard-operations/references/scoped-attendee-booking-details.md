# Scoped attendee booking details

Use when a manager/operator needs Admin-parity booking context inside an owner-scoped attendance panel.

## Data path

Expose booking provenance through the existing secured session-claims endpoint rather than fetching a broad member or bookings directory:

1. Authenticate the caller and resolve the session's program, product, and assigned manager.
2. Permit Program Admin, or an active product manager whose membership ID equals the session owner; return `403` for foreign managers.
3. For each authorized claim, reuse authoritative booking helpers where possible:
   - selected Simple product: resolve `voucher_claims.merchandise_product_id` to the product name;
   - submitted answers: load `custom_field_answers` joined to `custom_fields` so each value retains its field label;
   - attendee identity/avatar: return only the claim member's existing scoped identity fields.
4. Add optional DTO fields rather than creating a second manager-only response type.
5. Map the fields into the shared attendance claim model and render them in the shared Admin/manager attendance panel.

## UI rules

- Label the selection **Simple product**, never Merchandise.
- Render each answer as its custom-field label plus submitted value.
- Omit empty sections; do not display placeholders that imply a member submitted data when they did not.
- Keep attendance actions and booking details together, but preserve responsive wrapping when a new detail column is added.
- Treat these values as read-only operational context for managers unless editing was explicitly requested.

## Regression matrix

Backend:
- owning manager receives member identity, selected Simple product, and labeled answers;
- Program Admin retains parity;
- foreign manager receives `403` and no personal/booking details;
- absent selection/answers return null/empty values without errors.

Frontend:
- shared panel renders Simple product name and every labeled answer;
- absent details do not render empty labels;
- identity/avatar and attendance controls remain functional;
- narrow layouts do not overflow after adding detail content.

Public preview:
- seed or use an isolated claim with a real Simple-product choice and at least one custom-field answer;
- authenticate as the assigned manager;
- open the exact attendee panel and assert both values in the rendered DOM;
- inspect API failures and keep production data untouched.
