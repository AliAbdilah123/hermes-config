# Identity Routing Decision Checklist

Use this concise checklist while reviewing a social-inbox product plan.

## Product decisions

- Which platforms are genuinely functional at launch?
- Is personal OAuth absent, optional, or required?
- Can users skip social setup and use the core product?
- Is cardinality one identity total, one per platform, or multiple per platform?
- Must replacement be delete-then-register?
- Are unmatched historical messages discarded or imported later?
- Does each platform have its own dedicated receiving account?

## Identity contract

- Human display key: `(platform, normalized_username)`.
- Preferred routing key: `(platform, platform_user_id)`.
- Is the stable sender ID proven from a real webhook?
- Can the provider resolve username/profile data?
- Can a pending typed username correlate with the first incoming message?
- If not, is a short-lived first-message code acceptable?
- Are username metadata changes synchronized only when stable ID remains unchanged?

## Safe conflicts and constraints

For one slot per user per platform:

```sql
UNIQUE(user_id, platform)
UNIQUE(platform, normalized_username)
UNIQUE(platform, platform_user_id)
```

- Duplicate identities return “unavailable,” never owner details.
- API and DB enforce cardinality; UI alone is insufficient.
- Identity deletion stops future routing but preserves imported records.

## Webhook proof

- Current official permissions and review requirements verified.
- Verification challenge works over public HTTPS.
- Raw-body signature validation works.
- Body size is bounded.
- Stable sender ID and external event ID captured in redacted fixtures.
- Duplicate replay creates exactly one record.
- Invalid, self-sent, unsupported, inactive, and unmatched events create none.
- Activation and first-record creation are transactional.
- Message bodies are absent from routine logs.

## Acceptance matrix

| Scenario | Expected result |
|---|---|
| Core/manual use without identity | Works normally |
| Second identity on occupied user/platform slot | 409 conflict |
| Identity already owned by another user | Generic unavailable response |
| Same username on another platform | Allowed as separate namespace |
| Pending identity receives valid current activation message | Activates; triggering text creates one record |
| Message arrived before registration | Never imported retroactively |
| Stable ID with changed username | Routes normally and refreshes display metadata |
| Identity deleted | Future messages ignored; historical records remain |
| Same webhook delivered twice | One record total |
| Unsupported attachment | No empty record |
| User tampers with another user's record ID | Not found/forbidden; no disclosure or mutation |

## Scope guard

Do not add generic provider interfaces, queues, or future-platform UI before the second validated integration or measured operational need exists.
