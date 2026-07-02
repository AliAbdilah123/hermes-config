# Zod Validator Field Mismatch — Silent Button Failures

## Symptom

CRUD toggle buttons (attended/no-show, approve/deny, any binary state toggle) appear to work visually (optimistic UI update) but the backend never receives the change. No console error, no toast, no network error — the request succeeds with HTTP 200 but the data doesn't change.

## Root Cause

The frontend sends a payload where **field names don't match the backend Zod validator schema**. Zod's default behavior (with `zValidator`) is to **strip unknown fields** — the request passes validation but the intended field is silently dropped. The backend handler receives `undefined` for the real field and proceeds with default/no-op behavior.

### Example

**Frontend sends:**
```json
{ "claim_id": "abc", "status": "present" }
```

**Backend validator:**
```typescript
z.object({
  claim_id: uuidSchema,
  method: z.enum(['qr_scan', 'manual']),
})
```

`status` is stripped, `method` is required but missing → Zod strict rejection OR silent strip depending on implementation. Either way, the handler doesn't get the intended payload.

## Detection

1. Check the actual network request payload in DevTools
2. Compare against the backend Zod schema (search for `z.object` in the relevant `validators/` file)
3. Mismatch = the bug

## Common Mismatch Patterns

| Frontend sends | Backend expects | Result |
|---|---|---|
| `status` | `new_status` | Field stripped |
| `status` | `method: 'manual'` | Field stripped + required field missing |
| `reason` (for override) | not in schema | Stripped silently |
| `claim_id` (snake_case from TypeScript) | `claimId` (camelCase in DTO) | Usually OK with Drizzle `casing: 'snake_case'`, but check |

## Fix Strategy

1. **Match the frontend payload to the validator** — either fix the frontend field names or add the missing fields to the backend schema
2. **If the backend handler fundamentally doesn't support the operation** (e.g. `markAttendance` always sets `'present'` but you need `'absent'`), find or use the correct endpoint (`overrideAttendance` instead of `markAttendance`)
3. **Don't add `reason` or extra fields** to the payload unless the backend schema accepts them; Zod will strip them

## Prevention

- Write an integration test that sends the exact payload the frontend constructs and asserts the backend state changed
- Consider adding a Zod `.strict()` to reject unknown fields with a clear error instead of silently stripping them
