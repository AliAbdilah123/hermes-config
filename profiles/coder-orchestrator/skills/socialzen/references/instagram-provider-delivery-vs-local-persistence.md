# Instagram DM delivery versus local persistence

Use this when a dedicated Instagram inbox is configured correctly but a named sender's DM is not saved.

## Separate the boundaries

Trace the path as distinct claims:

1. The sender created a DM in Instagram.
2. Meta exposed it through a signed webhook or Conversations API.
3. The app accepted and routed the provider payload.
4. The app persisted the note under the correct owner.

Do not infer step 2 from the message being visible/read in Instagram, and do not infer steps 3–4 from an HTTP `200` with `data: []`.

## Read-only evidence order

1. Resolve the dedicated token via `/{version}/me?fields=id,username`; compare its ID to the effective configured dedicated account ID and the active `instagram_integrations` row.
2. Query `/{account-id}/subscribed_apps` and verify `messages` is subscribed.
3. Query `/{account-id}/conversations?platform=instagram`; record status and conversation count separately. `200` plus an empty list proves request acceptance, not conversation visibility or messaging permission completeness.
4. Inspect the live runtime database, not a repository-local SQLite file. Verify integration owner, Instagram-note count, external message IDs, and whether the named sender is represented.
5. Prove the local boundary independently with a signed synthetic webhook using a unique message ID; assert note owner and clean up the fixture. This proves routing/storage only, not provider delivery.
6. Check public webhook reachability and recent access logs. A verification `403` without the correct verify token can be expected; it is not proof that signed POST delivery fails.

## Interpretation

- **Provider returns the conversation/message, but no row appears:** investigate recipient filtering, stale account IDs, signature validation, ownership lookup, idempotency, and DB errors.
- **Provider returns zero conversations and no webhook POST is observed:** the app has no authentic payload to persist. Investigate Meta app mode, tester/role acceptance, authorization scopes, account subscription, token/account pairing, and account messaging/spam restrictions.
- **Synthetic webhook saves correctly while provider evidence is absent:** report local processing/storage healthy and provider delivery/visibility as the blocked boundary. Do not claim a specific Meta policy cause without dashboard or provider evidence.

## Recovery and acceptance

Old read messages may not be recoverable if Meta no longer exposes them. Do not manually insert a row and call it provider-backed proof. Ask for one fresh, unique, text-only DM after provider configuration is corrected, then verify its real Meta message ID and text in the live DB.

Status remains VERIFYING/STOPPED until that fresh provider-backed E2E passes. A synthetic webhook is a useful boundary test but never substitutes for real delivery acceptance.
