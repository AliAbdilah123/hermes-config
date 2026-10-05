---
name: feature-plugin-runtime
description: Use when implementing a backend/frontend plugin runtime with deterministic dependency resolution, capabilities, owned checksummed migrations, typed service seams, and UI extension registries.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, plugins, runtime, migrations, frontend]
    related_skills: [feature-multi-tenant-saas]
---
# Feature: Plugin Runtime

## Contract
Each plugin declares stable ID, dependencies, owned migrations, required/provided capabilities, and one registration entry. Reject duplicates, missing dependencies, and cycles before deterministic initialization.

Qualify migrations by plugin, persist checksums, transact each migration, and reject checksum drift. Cross-plugin calls use narrow typed services; missing required capabilities fail startup, never return silent nil.

Frontend plugins register routes, navigation, providers, and named slots with deterministic ordering and ownership.

## Packaging
Vendor all plugin source and migrations. Resolve external symlinks during extraction; a host that builds only on one workstation is incomplete.

## Optional metering reference
Atomic credit decrement plus run/step/usage ledgers is safe for bounded local jobs, but does not prove provider execution or billing.

## Templates
- `templates/plugin-runtime.go`
- `templates/plugin-migrations.go`
- `references/frontend-registries-and-metering.md`

## Pitfalls
Host wrappers hiding incomplete extraction; imperative schema mutation; nil service registries; UI registration/test drift; demo seeded credits/echo executors treated as production.

## Verification
Missing/cyclic dependency, deterministic order, checksum drift, capability failure, UI registry ownership, and distribution with no unresolved plugin symlink.

## Provenance
Boilerplate Core plus vendored plugins; corroborated by `rt16-community-app`. Seed-only dues reporting is excluded.
