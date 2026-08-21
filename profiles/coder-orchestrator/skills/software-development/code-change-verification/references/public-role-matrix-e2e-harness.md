# Public authenticated role-matrix E2E harness

Use this when completion requires Owner/Admin/Member proof on the deployed public application.

## Harness discipline

1. Create a dedicated uniquely named tenant and minimum role accounts in the actual runtime database; do not alter existing users. Back up the database first and record the fixture tenant ID for cleanup.
2. Authenticate through the public login UI for every role. Assert authenticated chrome before feature checks.
3. Navigate to the feature's real UI surface before checking visibility. For example, assert CSV import on Business Database, not Dashboard.
4. Prefer exact semantic locators scoped to the intended surface (`getByRole('heading', {name, exact:true})`). A value may legitimately appear in both a table row and detail heading; broad `getByText` then causes strict-mode ambiguity.
5. Classify locator ambiguity or an assertion made on the wrong page as harness failure, not product failure. Correct the harness and rerun the complete role matrix from the start; do not skip the interrupted behavior.
6. Make every mutation fixture unique across harness reruns using all effective deduplication keys, not only its display name. If duplicate matching considers phone/email, generate unique phone/email too; never disable or bypass duplicate protection just to make E2E pass.
7. Cover, per applicable role: authentication, visible/hidden navigation, missing-CSRF rejection, allowed mutations, forbidden privileged mutations, reload persistence, tenant isolation, responsive overflow, console errors, page errors, and failed network responses.
8. Capture failed responses as `method status URL` alongside console/page errors. Generic browser text such as “Failed to load resource: 503” is not classifiable evidence. Allowlist only exact intentional negative probes (for example the specific missing-CSRF 403 and tenant-isolation 404); fail every other 4xx/5xx rather than globally suppressing those status classes.
9. Treat hidden-feature network activity as a product regression, not merely console noise. Hiding a navigation button is incomplete if a dormant component still mounts and calls disabled/unconfigured APIs. Add a focused source/component regression proving the normal MVP render path has zero callers/mounts for the hidden feature while preserving dormant implementation and backend routes when deletion was not requested. Redeploy and require the public network trace to contain no such requests.
10. Preserve successful setup records during harness-only reruns unless cleanup is proven safe; use fresh unique records for each attempt. Save representative mobile screenshots outside the repository. Treat screenshots as supporting evidence, not a substitute for assertions.
11. Register cleanup before the browser run where practical. Record every created identity and top-level record ID as the harness runs. Cleanup must follow the effective foreign-key graph, including child tables that lack `tenant_id`; a generic `DELETE ... WHERE tenant_id=?` loop with foreign keys disabled can leave orphaned activities, events, files, or join rows. Prefer application-supported deletion or explicit child-to-parent cleanup inside one transaction. Afterwards, require zero residue by tenant ID, username/email prefix, recorded user IDs, and recorded business/opportunity/prospect IDs, then run database integrity and foreign-key checks. Preserve the fixture only when an unresolved failure requires diagnosis and report that explicitly.

## Status integrity

Deployment health and a fresh asset hash are separate from browser behavior. Keep status `VERIFYING` until the full matrix passes. Do not call a harness-selector failure a product regression, but do not mark E2E complete until the corrected harness reaches every assertion.
