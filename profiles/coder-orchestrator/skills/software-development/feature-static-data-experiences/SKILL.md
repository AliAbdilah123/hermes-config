---
name: feature-static-data-experiences
description: Use when implementing static data-driven leaderboards or similar content surfaces with pure ranking logic, accessible metadata, executable content integrity checks, and root/subpath-safe SPA deployment.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, static, leaderboard, accessibility, deployment]
    related_skills: [spa-preview-delivery-verification]
---
# Feature: Static Data Experiences

Keep source data declarative and ranking/podium helpers pure. Validate member uniqueness, score ordering, preservation of all entries, podium presentation order, movement metadata, and accessible badge descriptions with an executable script.

Use build-provided base URL for assets/routes. Configure host SPA fallback separately from asset caching. Content identity needs a stable fallback when optional slugs are absent.

## Templates
- `templates/leaderboard-check.mjs`
- `references/accessibility-and-deployment.md`

## Pitfalls
Confusing rank order with visual 2-1-3 podium order; badges with tooltip-only meaning; accidental tabs/period variants; root/subpath mismatch; SPA fallback swallowing assets; cache headers lost on fallback fixes.

## Verification
Checker passes, keyboard/tap labels exist, all records render once, root and nested direct routes load, assets use correct base, and cache/fallback headers are verified.

## Provenance
`balikpapan-dev-web` leaderboard helpers, content checker, accessibility behavior, and deployment history.
