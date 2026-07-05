# Frontend advanced filters ignored by backend

Use when a frontend search/autocomplete sends advanced filters (for example `filters=[{"field":"isTemplate","conditions":{"eq":true}}]`) but results include records that should be excluded.

## Symptom
- UI appears to pass the correct filter in the client helper.
- Backend response still contains unfiltered records, e.g. a “duplicate from template” picker returns non-template tasks.

## Root cause pattern
A typed frontend query builder can serialize rich filters (`filters`, `sort`, `limit`) while a simpler backend list handler only reads legacy query params such as `status` and `search`. The client code is correct, but the server silently ignores the filter envelope.

## Debug recipe
1. Trace from the UI component to the API client and capture the exact query params it sends.
2. Inspect the backend list handler for every query param it actually reads.
3. Add a server-side regression test that creates one matching and one non-matching record, calls the endpoint with the serialized filter, and asserts only the matching record is returned.
4. Fix at the endpoint filter parser, not in the picker component, so all clients using the query helper benefit.

## Minimal fix pattern
- Parse the `filters` JSON query param server-side.
- Whitelist supported fields/operators and map field names to DB columns (`isTemplate` → `is_template`) instead of interpolating client-provided names.
- Keep unknown filters ignored or rejected deliberately; do not splice arbitrary field/operator values into SQL.
- Include common operators the existing client helper emits (`eq`, `in`) before adding broader support.

## Verification
- Watch the regression fail before the parser exists.
- Run the targeted test and the package test suite after the fix.
- If deployed, rebuild/restart the API service and verify the public proxied health/API route.