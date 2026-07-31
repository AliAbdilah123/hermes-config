---
name: responsive-project-review-artifacts
description: Create evidence-backed, styled HTML project audits and improvement reports; publish them for review and verify both the artifact and relevant project checks.
version: 1.0.0
metadata:
  hermes:
    tags: [review, audit, html, responsive, verification, publication]
---

# Responsive Project Review Artifacts

Use when the user asks for a styled HTML report explaining what can be improved in an existing software project. This is a read-only review workflow unless implementation is separately approved.

## Workflow

1. Resolve the project root from current conversation context or durable project defaults.
2. Inspect source, schema, tests, runtime configuration, documentation, and current data where safe. Separate confirmed defects from recommendations.
3. Run independent audit tracks in parallel when useful: security/architecture and product/UX/operations. Require exact file and line evidence.
4. Re-run the repository's existing checks directly in the project workdir. Passing checks are a baseline, not proof that uncovered security or workflow defects are absent.
5. Rank findings by user impact and risk. Put production blockers first, then trust/workflow gaps, then maintainability and polish.
6. Create one self-contained responsive HTML artifact in the project's `docs/` directory. Include:
   - clear executive summary;
   - prioritized findings with evidence;
   - concrete next action for each finding;
   - staged delivery order;
   - verification baseline;
   - theme toggle;
   - mobile-safe layout, tables, long paths, and code references.
7. Publish the artifact to the configured review-document route, preserve a canonical source in the repository, and verify local and public HTTP 200 responses with a cache-busting query.
8. Run an artifact-specific self-check after writing it (viewport, theme toggle, breakpoints, reduced motion, expected findings). Then run the relevant project verification again after the changed artifact so verification evidence is fresh.
9. Before committing, inspect the changed paths and keep the report concise, KISS, and consistent with surrounding repository conventions. Commit and push only the intended artifact.
10. Final response must include the public report URL, the project's public URL when known, the checks that actually passed, and the commit identifier.

## Evidence Rules

- Cite exact source locations; do not infer implementation from UI copy alone.
- Label conditional risks as conditional.
- Never invent metrics. Use measured values or explicitly marked unknowns.
- Do not present simulated/demo behavior as completed production behavior.
- A read-only design or audit request does not authorize product changes or deployment of product code.

## Artifact Quality Floor

- `<meta name="viewport">` present.
- Responsive at phone and tablet widths with no page-wide horizontal overflow.
- Body text remains readable; headings use fluid sizing.
- Tables become scroll containers or cards on narrow screens.
- Theme toggle has an accessible label and persisted preference.
- Visible `:focus-visible` treatment and reduced-motion support.
- Tokens drive colors and typography; avoid a generic SaaS dashboard aesthetic.
- The report is useful without requiring the reader to inspect source code.

## Blueprint + Multi-page Prototype Requests

When product planning combines a written MVP blueprint with a static multi-page prototype:

1. Read the supplied validation/review artifact first and treat validated decisions as architecture inputs, not optional background.
2. Resolve product inconsistencies visibly before defining entities, pages, or phases. Distinguish canonical records from workflow views so labels do not create duplicate domain objects.
3. Keep documentation and prototype as separate deliverables, cross-linked from one stakeholder-facing review page.
4. Prefer shared static CSS/JS for navigation, persisted theme, command palette, drawers, and modals; retain every requested route as a real HTML page.
5. Add a deterministic stdlib verifier for required files, internal links, viewport/theme/mobile hooks, prohibited frameworks, and validated product concepts. Run it after the final edit.
6. Publish a multi-page artifact by symlinking a named directory into the PRD web root rather than copying individual files. Publicly verify the review page, prototype index, and at least one interior page.
7. Stage only requested blueprint/prototype paths. Formatting or cleanup helpers must use an explicit file allowlist; never sweep every existing file in a shared `docs/` directory.

## Verification Pitfalls

- Verification run before the artifact edit becomes stale after the edit. Re-run the relevant canonical command after the final write, even when the artifact is documentation-only.
- Fresh verification evidence can be command-sensitive. If the workspace/runtime explicitly requests a canonical command, run that exact command after the last edit (for example, `pnpm run build` rather than relying on a prior successful `npm run build`), even when both invoke the same package script.
- A public `curl` 200 verifies publication, not visual quality. Also run deterministic HTML checks; use browser/mobile inspection when available, but do not treat unavailable browser automation as a blocker when source checks and HTTP verification pass.
- For a standalone interactive HTML prototype with no canonical suite, create a focused temporary verifier under `/tmp` using the host language's OS-safe tempfile API and a `hermes-verify-` filename prefix (for example, Python `tempfile.NamedTemporaryFile(prefix='hermes-verify-', ...)`). Assert the exact changed behavior in the artifact source—responsive hooks, initial media fit, overlay geometry, guide lines, interaction handlers, persistence, accessibility hooks, cross-links, and requested read-only/mutation semantics as applicable—run it, and clean it up in a `finally` block. Report this explicitly as **ad-hoc artifact verification**, never as the application suite being green. Run it after the final artifact edit and before committing or calling the artifact done. If the verifier itself has a syntax error or an assertion exposes a mismatch between intended wording and the artifact, fix the verifier or artifact and rerun; only the final successful rerun counts as evidence. Never cite an earlier pass after either artifact changes.
- Build output can regenerate ignored files. Confirm the staged diff contains only the intended report before committing.
- Nginx warnings are not failures when `nginx -t` explicitly reports successful syntax and configuration tests; report only actionable blockers.

## Supporting Reference

See `references/evidence-backed-improvement-audit.md` for the compact audit rubric and report content pattern.
