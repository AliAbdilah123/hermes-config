# Typography Preview Verification

Use this for iterative whole-site font comparisons published as isolated SPA previews.

## Minimal implementation contract

- Change the shared typography tokens rather than chasing every component:
  - `--font-sans` for body and controls
  - `--font-serif` for headings, even when the candidate is a sans face
  - `--font-mono` for utility labels, codes, and compact metadata
- Update the webfont import to include every weight/style actually used, especially italic emphasis and bold headings.
- Choose a companion face from the same visual family. Examples:
  - slab/editorial serif → restrained mono such as IBM Plex Mono
  - geometric sans → related geometric mono such as DM Mono
- Remove superseded imports so a stale face cannot hide a broken token change.

## Iterative comparison workflow

A request such as “try it again with X” is a revision of the existing typography comparison. Reuse the same clean worktree and public preview rather than creating another preview URL. Commit and push each candidate so the reviewed state is recoverable. Keep production unchanged until explicit approval.

Use a neutral preview slug such as `typography` or `font-comparison`; do not name the durable route after the first candidate, because later candidates make that URL misleading. If an existing route already has a candidate-specific slug, preserve it during the active review rather than risking a broken link, then use a neutral slug next time.

## Public verification gates

1. Build with the exact preview base path.
2. Confirm public HTML has one effective preview basename injection. A production catch-all may append a second basename and cause a valid bundle to render `Page not found`; add an explicit Nginx preview location before evaluating typography.
3. Confirm the public hashed CSS contains the new shared token and the public HTML references the new preview bundle.
4. In a browser on the exact public URL:
   - await `document.fonts.ready`;
   - inspect computed `font-family` for `body`, the hero heading, and one utility label;
   - check `document.fonts.check()` for primary and companion faces;
   - require the intended page content and absence of `Page not found`;
   - capture desktop and mobile screenshots when layout can change due to font metrics.
5. Compare the production asset identity before and after to prove isolation.

A screenshot proves visual character and layout, but not exact font loading. CSS token inspection proves deployment intent, but not that the font downloaded. Report exact-face verification only when computed styles and loaded-font checks pass.

## Approval, production promotion, and cleanup

When the user approves the latest candidate:

1. Treat the final candidate state—not every intermediate candidate commit—as the approved contract. Re-fetch the remote default branch, rebase the clean feature worktree, and inspect the net default-branch-to-feature diff. The final diff should contain only the approved imports/tokens and no superseded candidate faces.
2. Squash into a clean integration worktree from the freshly fetched default branch. Run token/import assertions and the production build from that clean squash commit before pushing or deploying.
3. Deploy that clean artifact, then verify public production HTML references its exact hashed JS/CSS. Confirm served CSS contains the approved primary and companion tokens, and browser-render the exact public page.
4. Do not claim the exact webfont loaded from CSS-token inspection, a font-provider response, or screenshot appearance alone. Exact-face proof still requires computed styles plus `document.fonts.ready` / `document.fonts.check()` in the public page. If those probes are unavailable, report only that deployed typography tokens and visible treatment were verified.
5. Remove the explicit preview web-server location and preview directory only after production verification succeeds. A removed preview URL may still return HTTP 200 through the production SPA catch-all; prove cleanup by checking the explicit location and directory are absent and the response no longer contains preview basename injection.
6. For a squashed feature, ancestry cannot prove the feature tip is merged. Before deleting its worktree/branch, require the clean feature tree's approved files to match the pushed default branch (or otherwise prove patch equivalence), while requiring the squash integration commit itself to be an ancestor of the remote default branch.

## Reporting

Provide the stable preview URL, candidate names, commit SHA, and a concise statement that production is unchanged and approval is pending. Do not describe a visual preview as approved or production-ready before the user explicitly accepts it. After approval, report the production URL, pushed squash SHA, exact verification boundary (tokens versus loaded faces), and preview cleanup result.
