# Contract revision checklist

Use after a user changes provider configuration, endpoint names, or payload semantics.

## Canonical plan

- [ ] Architecture summary names the new provider and routes.
- [ ] Exact environment-variable names are documented.
- [ ] Request and response examples match the new payload.
- [ ] Authentication, CSRF, tenant source, limits, and errors are explicit.
- [ ] Tasks and tests use only the new endpoints.
- [ ] Acceptance criteria cover single and bulk behavior when applicable.
- [ ] Obsolete draft IDs, tables, commit routes, and replay language are removed.

## Single/bulk array endpoint

- [ ] One element creates one record.
- [ ] Multiple elements create records in request order.
- [ ] Empty and oversized arrays are rejected.
- [ ] Every item is validated before mutation.
- [ ] One invalid item rolls back the entire batch.
- [ ] In-batch and existing-record duplicates have defined behavior.
- [ ] Tenant, revision/concurrency, audit, and created-ID behavior are tested.

## Provider secrecy

- [ ] URL and secret are read only by the backend.
- [ ] Missing URL/secret produces an unavailable error.
- [ ] Timeout and malformed provider output are normalized.
- [ ] Responses, client configuration, logs, state, and audit events are checked for secret leakage.

## Published artifact

- [ ] Public URL returns HTTP 200.
- [ ] Exact new endpoint strings are present.
- [ ] Exact environment-variable names are present.
- [ ] Single/bulk semantics are present.
- [ ] Old endpoint, schema, draft, and replay phrases are absent.
