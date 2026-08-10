---
name: visual-preview-feedback-loop
description: Deliver and revise visual web changes through exact-route previews, target disambiguation, responsive browser proof, approval, and production promotion.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [frontend, visual-qa, preview, responsive, deployment]
---

# Visual Preview Feedback Loop

Use for visual web changes that are reviewed in an isolated preview before production deployment, especially CSS and responsive changes across discovery, detail, checkout, or other route-specific surfaces.

## Workflow

1. **Name the target precisely.** Record the environment (preview or production), exact route, state/auth requirements, and viewport. Similar pages are not interchangeable. Treat a full detail page, board modal/inspector, drawer, timeline, and conversation view as separate products until code tracing proves they share the relevant renderer. Name each surface and its purpose before proposing edits.
2. **Trace route to renderer.** Follow the reported URL through pathname/query parsing to the mounted component and exact content renderer. Evidence from a sibling surface is not evidence for the target. Keep separate navigation, layout, and responsibilities as explicit invariants in the plan and regression tests.
3. **Make the smallest source change.** Inspect the route component and applicable breakpoint rules. For responsive changes, preserve desktop behavior unless requested otherwise.
3. **Verify mechanically.** Assert both the requested rule and removal of superseded styling. For a reverted effect, search for and remove its keyframes, selectors, reduced-motion override, and residual background declarations—not just the visible animation declaration.
4. **Build for the actual preview mount.** Publish the resulting hashed assets to the isolated route.
5. **Render exact public routes.** Exercise each changed route at the relevant viewport. A preview root, HTTP 200, source assertion, or build does not prove a detail route.
6. **Share deep links.** Give reviewers direct URLs to every changed surface, with a cache-busting query when useful. State plainly that production is unchanged and approval is pending.
7. **Disambiguate “still unchanged.”** Before editing again, determine whether the reviewer opened production or preview. Compare the viewed URL/environment and served asset. Do not guess or stack another CSS change.
8. **Revise the same preview.** Keep follow-ups in the existing clean feature worktree and preview. Interpret short corrections literally; when the user narrows the request (for example, “just remove the background”), remove the unrequested effect rather than replacing it with another design.
9. **Promote only after explicit approval.** Fetch the latest production branch, integrate both independently approved visual changes when requested, rebuild once from the clean integration commit, push, deploy, and render the exact live routes/viewports.
10. **Clean previews last.** Remove explicit preview routes and assets only after live verification. Remember that a production SPA fallback may still return HTTP 200 for the old preview URL; prove the explicit mount and directory are gone.

## Evidence boundaries

- **Source/build proof:** implementation compiles and intended selectors/components changed.
- **Preview proof:** exact public preview route visibly shows the requested state.
- **Production proof:** exact live route visibly shows it after the approved deployment.
- Never promote one boundary into another. If authentication or data blocks rendering, say visual verification is pending.

## Visual assertions

For heading emphasis removal, verify the real rendered heading has a single inherited/plain text color; do not merely search for one removed `<em>` because CSS descendant selectors or alternate components may still color text.

For mobile hero simplification, verify at the breakpoint that the carousel is absent, inherited hero imagery/decorative pseudo-elements are disabled, **and its grid track, min-height, aspect-ratio, margins, and reserved whitespace collapse too**. A hidden child with a surviving desktop hero row is a failed mobile simplification. Confirm discovery/content begins promptly after the hero copy, desktop behavior remains intact, and reduced-motion rules do not leave obsolete effect code behind.

### Screenshot critique pass

Before declaring a visual preview ready, capture fresh screenshots from the **exact public URL** at the requested desktop and mobile widths and inspect the pixels, not only DOM assertions. Check at minimum:

- clipped labels, captions, controls, and adjacent carousel slides;
- placeholder or fallback media occupying the primary composition;
- hidden mobile elements that still reserve layout space;
- horizontal overflow, ambiguous card-rail peeks, and undersized touch targets;
- contrast, readable metadata, heading wraps, and whether primary content appears early enough.

Treat screenshot findings as test failures: revise the same preview, rebuild, republish, and capture fresh screenshots. Do not share the review URL as ready while a central interactive surface visibly looks unloaded, clipped, or structurally empty. DOM presence and HTTP 200 remain transport/render evidence, not visual-polish evidence.

For populated carousels, verify the active image, caption, controls, and pagination form one coherent frame. Labels and metadata must be complete; outgoing or adjacent slides must not appear as accidental slivers. Also inspect whether the selected image plausibly matches its record. If genuine backend/gallery data is semantically mismatched, report it as a data-quality issue rather than fabricating replacement content in a visual-only redesign.

If the normal browser automation path times out, fall back to installed headless Chromium with an explicit viewport, virtual-time budget, `--dump-dom`, screenshot, and captured stderr. Re-run against the exact public URL. Distinguish harmless host-level Chromium noise (such as DBus/AppArmor messages) from page runtime failures using the rendered DOM and screenshot; do not encode a transient browser startup failure as a permanent tool limitation.

## Communication

Use concise status labels, and make them truthful about current execution:

- `WORKING` only while code, tests, deployment, or an explicitly tracked background process is actively running.
- `VERIFYING` only while verification commands or interactive checks are actively underway; do not leave this label in place after stopping.
- `READY FOR REVIEW` only after the exact public user interaction has passed.
- `BLOCKED` or `STOPPED / pending verification` when no work is currently executing.

When users have questioned whether work stopped, proactively post the next state transition when a background process completes; do not require them to ask again. Distinguish implementation completion, server restart, artifact publication, and public interaction verification.

Never say “done” or imply the user should see a preview-only change on production. Do not promote backend data, generated URLs, HTTP health, or source tests into UI proof: for notification/navigation work, click the actual rendered dropdown item and prove the destination UI opens in the required state.

See `references/truthful-status-and-role-sensitive-e2e.md` for role-overlap and exact-interaction verification patterns. See `references/distinct-detail-surfaces-and-session-reverts.md` for route-to-renderer disambiguation and safe correction when work touched the wrong UI surface.