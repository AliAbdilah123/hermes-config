# Read-only MVP implementation audit

## Evidence ladder

For each requirement, inspect in this order:

1. Canonical product documents and architectural rules.
2. Database constraints and migrations.
3. Backend route registration, authorization, validation, persistence, and Activity creation.
4. Frontend route, request contract, state handling, and user-reachable behavior.
5. Focused tests.
6. Side-effect-free runtime/E2E behavior when available.

A page, table, endpoint, type, or test name alone is not proof. Trace the complete user action through UI → API → persistence → resulting state/activity.

## Exact status rubric

- `✅ COMPLETE`: full required behavior is wired end to end, with no material gap found.
- `⚠️ PARTIAL`: meaningful behavior works, but a required branch, guard, state, or surface is absent.
- `❌ MISSING`: no substantive implementation of the requirement.
- `🔴 BROKEN`: an exposed implementation fails, contradicts another layer, violates canonical architecture, or produces unsafe/incorrect state.

If runtime execution is unavailable, say so once in audit integrity and classify from code-path/test-source evidence without pretending E2E passed. Do not classify environment setup failure as product failure.

## Read-only integrity

1. Capture `git status --short` before inspection.
2. Avoid builds that emit artifacts, migrations, seeders, and production DB access.
3. Run only demonstrably side-effect-free checks.
4. Capture `git status --short` afterward and report whether it is identical.
5. Never clean pre-existing files merely to make the checkout look clean.

## Compact requirement row

Use:

`**Requirement — STATUS.** Exists: … Verified: … Gap: … FE: path:line. BE: path:line. DB: path:line/table. Blocker: Yes/No.`

Avoid repeating the same limitation under every item. Define shared evidence locations once, use grouped tables for simple requirements, and reserve prose for blockers, contradictions, and architectural violations.

## Completion percentages

Estimate based on weighted behavioral coverage, not arithmetic counts of files or rows. A central broken invariant (permissions, canonical identity, conversion prerequisites, tenant isolation) should reduce the affected module more than several complete cosmetic states increase it. Explain that percentages are estimates.

## Required synthesis

After the matrix provide:

1. Conservative module completion percentages.
2. Critical MVP blockers only, ordered by dependency and user-flow impact.
3. Partial features with exact missing behavior.
4. Broken features and the violated contract.
5. Genuinely complete features to prevent rebuilding.
6. Practical development order that repairs invariants before adding surfaces.
7. Questions only where canonical documents and repository behavior are genuinely ambiguous.

## High-value contradiction checks

Explicitly compare:

- frontend payloads against backend request models;
- list pagination against UI reachability;
- archive filters against restore paths;
- direct routes against modal-only implementations;
- role checks across every mutation, not merely navigation visibility;
- conversion prerequisites against the state created downstream;
- read-only GET handlers for hidden writes;
- canonical records against accidental duplication during module conversion;
- research/audit Activity against sales/CRM Activity separation;
- scheduled reminders against behavior triggered only when a page is opened.

## Token-efficient reporting

When low usage is requested:

- state integrity and runtime limits once;
- use one compact matrix per module;
- cite only the strongest FE/BE/DB evidence;
- avoid restating each gap in the matrix, partial list, blocker list, and development order unless needed for those sections;
- put exhaustive evidence in a report artifact when authorized, while keeping the chat summary focused;
- never trade away exact classifications or blocker clarity merely to shorten output.
