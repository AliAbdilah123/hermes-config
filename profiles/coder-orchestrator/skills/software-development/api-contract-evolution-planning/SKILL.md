---
name: api-contract-evolution-planning
description: Plan and revise application API contracts when providers, endpoint boundaries, payload shapes, or single-versus-bulk semantics change, while removing superseded architecture and keeping review artifacts consistent.
version: 1.0.0
metadata:
  hermes:
    tags: [planning, api, contracts, provider, bulk-operations]
---

# API Contract Evolution Planning

Use when an implementation plan introduces or revises API endpoints, provider configuration, payload shapes, or generic single/bulk operations.

## Core workflow

1. Inspect the existing route, authorization, tenant, transaction, state-revision, and audit conventions before proposing a contract.
2. Write the exact method, URL-safe path, authentication/CSRF requirements, tenant source, content type, request schema, success response, and normalized errors.
3. When the user corrects the contract, treat it as an architectural decision—not a text rename. Propagate it through:
   - architecture and configuration summaries;
   - request/response examples;
   - data model and persistence assumptions;
   - implementation tasks and file targets;
   - tests, acceptance scenarios, risks, and deployment configuration;
   - canonical markdown and every published review artifact.
4. Remove superseded routes, draft IDs/tables, replay rules, lifecycle steps, and terminology. Do not preserve an obsolete persistence model beneath renamed headings.
5. Re-verify the canonical source and public artifact for exact new phrases and absence of stale phrases.

## Provider boundary

- Name backend environment variables exactly.
- Keep provider URL and secret backend-only.
- Missing configuration must return an honest unavailable response, never mock success.
- Include timeout, cancellation where practical, bounded input/output, strict structured-response validation, and normalized errors.
- Add explicit checks that URL/secret never appear in responses, frontend configuration, persisted business state, logs, or audit text.

## Generic single and bulk creation

When one endpoint accepts an array for both single and bulk creation:

- A one-element array is the single-create contract; larger arrays are bulk creation.
- Define empty-array and maximum-batch behavior.
- Validate every item before mutation.
- Commit all items atomically or none.
- Test duplicate entries within the batch, collisions with existing records, invalid middle members, tenant isolation, revision/concurrency conflict, audit behavior, and response ordering/created IDs.
- Prefer one generic endpoint over parallel feature-specific commit routes when both create the same canonical entity with the same authorization and validation.

## URL normalization

HTTP paths cannot contain literal spaces. If a requested label contains spaces, normalize it to a URL-safe path (usually hyphenated), mention that normalization briefly, and then use the normalized path consistently.

## Review-artifact verification

After edits, verify HTTP 200 and exact content markers for every new endpoint and environment variable. Also assert that old endpoints, obsolete tables, draft IDs, and superseded terms are absent. See `references/contract-revision-checklist.md`.

## Pitfalls

- Renaming endpoint headings while leaving old tasks and acceptance criteria intact.
- Keeping a temporary import-draft table after the revised flow no longer uses server-side drafts.
- Saying “supports bulk” without defining one-item behavior and atomic rollback.
- Putting provider secrets in client-visible capability/config endpoints.
- Treating a user’s invalid path spelling literally instead of safely normalizing it.
