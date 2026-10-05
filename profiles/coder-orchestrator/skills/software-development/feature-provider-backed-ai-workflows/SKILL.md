---
name: feature-provider-backed-ai-workflows
description: Use when implementing server-mediated AI editing, chat, generation, delegation, usage metering, or structured extraction with streaming, cancellation, persisted continuity, and honest provider capability status.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, ai, provider, streaming, metering]
    related_skills: [provider-backed-ai-applications, feature-approval-gated-ai-jobs]
---
# Feature: Provider-backed AI Workflows

## Boundary
Credentials stay server-side. Capability endpoint reports configured/model/base URL but never keys. Missing configuration is an honest unavailable error, never mock success. Provider URL/model use allowlists; requests have timeout, cancellation, bounded input/output, and normalized errors.

Persist user input before invocation when conversation history requires it; persist assistant output only after successful completion. Persist provider session IDs for continuity. For document edits, capture note ID/range/text and revalidate against current document before apply. Serialized autosave flushes before navigation or entity switching.

Structured extraction validates a strict schema and preserves original uploads. Async work uses durable jobs when restart loss is unacceptable. Optional usage metering conditionally debits balance and records run/step/usage atomically; pricing is policy, not a hard-coded demo constant.

## Configuration
Provider base URL, API key/token, model allowlist, timeout/output limits, database path, public API base, and storage path where uploads apply.

## Templates
- `templates/provider-runner.js`
- `templates/ai-ledger.sql`
- `references/editing-extraction-metering.md`

## Pitfalls
Shell invocation; unbounded output; assistant rows on failed calls; stale selections; saves landing on another record; request model override; in-memory-only important queues; seeded demo credits treated as billing.

## Verification
Timeout/abort, stream failure, provider unavailable, secret redaction, session reuse, stale selection, autosave flush, malformed structured response, restart recovery, and concurrent insufficient-credit debit.

## Provenance
`ai-notes`, `flora-copy`, `delegate`, `share-expense`, and corroborating boilerplate/RT16 AI modules. Paragentix lifecycle remains in its dedicated skill.
