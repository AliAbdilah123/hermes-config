---
name: feature-service-marketplace-workflows
description: Use when implementing service-marketplace bookings, open jobs, or bounties with proposals, assignment, proof, completion, disputes, reviews, audit events, and delayed release.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, marketplace, jobs, bounties, proposals]
    related_skills: [feature-xendit-payments]
---
# Feature: Service Marketplace Workflows

## Foundation
Use one participant-authorized state machine for bookings, open calls, and bounties. Snapshot pricing/fees at creation. Define proposals/assignments, proof, release schedules, append-only events, reviews, reports, violations, and notifications.

## Workflow
Creation validates eligibility/schedule. Bounty proposals may require verified email and payout details. Transition matrix keys current state, action, and actor role; state and event commit together. Proposal approval locks parent/quota and cannot over-allocate. Proof gates completion when configured. Dispute freezes normal completion/release. Reviews require completion, eligible counterparties, and uniqueness.

Delayed release uses bounded durable claims, idempotent completion, startup recovery, and provider calls outside claim transactions. Payment verification remains in `feature-xendit-payments`.

## Configuration
Data path/address plus provider/payment variables only when integrated. Never treat existing webhook columns as proof of secure payment handling.

## Templates
- `templates/marketplace-schema.sql`
- `templates/transition-matrix.go`
- `references/delayed-release-and-verification.md`

## Pitfalls
Unscoped participant queries; mutable fees; quota check outside transaction; persisted schedules without restart recovery; monolithic compatibility migrations copied as templates.

## Verification
Role/state matrix, repeated actions, concurrent quota approval, proof/dispute/review gates, append-only events, and restart-safe release.

## Provenance
Canonical `siapjasa`; `siapjasa-simple` is a compact lineage fixture only.
