# shadcn Card Section Retrofit

Use when an existing React/Vite app already has shadcn-compatible primitives and the user asks to convert named dashboard/app sections to use shadcn cards rather than custom `div.panel`/`section.panel` wrappers.

## Pattern

1. Confirm `Card`, `CardHeader`, and `CardContent` are already available under `src/components/ui/card.tsx`; if not, follow the broader `react-vite-shadcn-migration.md` reference first.
2. Keep the app's existing layout classes for grid placement and visual compatibility, but move them onto `<Card>`:
   - Before: `<section className="panel opportunity-panel">...content...</section>`
   - After: `<Card className="panel opportunity-panel shadcn-section-card"><CardHeader>...title...</CardHeader><CardContent>...content...</CardContent></Card>`
3. Preserve existing title/action helpers by placing them inside `CardHeader` instead of rewriting behavior:
   - `<CardHeader><PanelTitle title="..." action="..." onAction={...}/></CardHeader>`
4. Replace both dashboard cards and secondary/side panels in the same pass when the user says “sections like … etc.” Look for related named headings, not only the exact list.
5. For dense pages, update all siblings in a layout consistently so mixed wrapper types do not create spacing or border inconsistencies.

## Verification

- Run the project’s production build (`npm run build` for this class of Vite app).
- Deploy/copy the build to the actual nginx/static directory if the app is public.
- Verify the public index and new JS/CSS assets return 200.
- Because Vite indexes often contain no visible app text, check deployed JS for markers such as the new class (`shadcn-section-card`) and the requested section headings.
- Optional visual QA: a headless Chromium screenshot of the public path is enough to catch blank pages or obvious render regressions; if the app requires auth, the login page rendering verifies asset loading, while bundle markers verify the changed authenticated UI shipped.

## Pitfalls

- Do not claim a shadcn conversion if you only add shadcn-like CSS. Use the actual `Card` primitive.
- Do not remove existing grid/placement classes such as `opportunity-panel`, `wide-panel`, `side-panel`, `wa-status`, or `wa-chat`; they often drive responsive layout.
- Avoid broad refactors during a scoped visual request. Wrap the named sections and verify, leaving unrelated components alone.
