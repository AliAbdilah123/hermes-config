# shadcn Card retrofit spacing in legacy React/Vite dashboards

Use when converting existing custom `.panel` sections to shadcn-style `<Card>`, `<CardHeader>`, and `<CardContent>` in an app that already has panel/header/content CSS.

## Problem observed

A direct wrapper replacement can make cards look padded incorrectly because shadcn primitives commonly add default padding (`CardHeader p-6`, `CardContent p-6 pt-0`) while the legacy section already has spacing such as `.panel-title { padding: ... }` and content wrappers like `.opportunity-list { padding: ... }`.

Symptoms:
- Large empty gaps between the card title and body.
- Segment/tile cards looking too tall or cramped inside an overly padded container.
- Header actions visually drifting away from titles.
- Multiple converted sections accidentally sharing the same legacy layout class/grid area and overlapping or stacking awkwardly.

## Practical fix pattern

1. Keep real shadcn primitives in JSX, but add a retrofit class to converted legacy cards:
   ```tsx
   <Card className="panel segment-panel shadcn-section-card">
     <CardHeader><PanelTitle title="Segments" /></CardHeader>
     <CardContent>...</CardContent>
   </Card>
   ```
2. Reset wrapper padding for the retrofit class instead of changing the global UI primitive:
   ```css
   .shadcn-section-card { border-radius: 18px; overflow: hidden; background: #fff; }
   .shadcn-section-card > div:first-child { padding: 0 !important; }
   .shadcn-section-card > div:first-child + div { padding: 14px 16px 16px !important; }
   .shadcn-section-card .panel-title { height: 54px; padding: 0 18px; border-bottom: 1px solid #edf0f6; }
   .shadcn-section-card .opportunity-list { padding: 0; }
   ```
3. Tune nested tile spacing separately:
   ```css
   .shadcn-section-card .segment-strip { margin-bottom: 0; gap: 12px; }
   .shadcn-section-card .segment-strip button {
     min-height: 88px;
     padding: 16px 18px;
     border-radius: 14px;
     display: grid;
     align-content: center;
     gap: 8px;
   }
   ```
4. If two converted cards previously reused one legacy class (for example both had `.opportunity-panel`), split semantic layout classes before deployment:
   ```tsx
   <Card className="panel segment-panel shadcn-section-card">...</Card>
   <Card className="panel best-opportunity-panel shadcn-section-card">...</Card>
   ```
   ```css
   .dashboard-grid { grid-template-areas: "segments opportunity challenge" ...; }
   .segment-panel { grid-area: segments; }
   .best-opportunity-panel { grid-area: opportunity; }
   ```
5. Verify with both build output and screenshot/DOM-level visual QA. If login is required, prefer a safe temporary local verification path and clean it up immediately; do not leave token setter files or token logs behind.

## Pitfalls

- Do not globally reduce `CardHeader`/`CardContent` padding in `components/ui/card.tsx` just to fix one legacy page; it will affect every future card in the app.
- Do not assume a successful build means visual layout is correct. The overlap/shared-grid-area problem only showed up after screenshot review.
- Avoid leaving temporary auth helper files in the deployed static directory after screenshot QA.
