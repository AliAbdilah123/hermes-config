# External-Design-Driven Page Redesign

When the user provides a design from an external tool (Google Stitch, Figma export, etc.) and wants to apply it to an existing page in the codebase.

## 1. Obtaining the Design Source

Google Stitch (`stitch.withgoogle.com`) and similar Google design tools require Google authentication. The browser will timeout on auth redirects. Diagnose with curl:

```bash
curl -sI -m 15 "https://stitch.withgoogle.com/design/<ID>" | head -5
```

Signals that the design is auth-gated: `content-length: 0`, `Nemo` in CSP/reporting headers, `ESF` server header. When auth-gated, ask the user to:
- Export the HTML/CSS from the tool (Stitch has an "Export Code" option)
- Or share screenshots (analyze with vision tool)
- Or paste the exported source HTML

## 2. Analyze the External Design

Extract from the exported HTML/design source:

- **Color tokens**: hex/oklch values, dark-only vs. light+dark, named tokens (e.g. Material Design 3 `surface`, `primary`, `on-surface`)
- **Fonts**: font families, weights, size scale, line heights
- **Layout**: grid columns, max-width, spacing scale, breakpoints
- **Interaction patterns**: modals, tabs, accordions, hover effects, animations
- **Icon system**: Material Symbols, Lucide, custom SVG, text glyphs
- **Visual metaphors**: textures, shadows, border styles, clip-paths, mask-images

## 3. Cross-Reference with Existing System

Read the project's design system before asking adaptation questions:

- `globals.css` / root CSS — CSS custom properties (`--paper-1`, `--ink-1`, `--accent`, etc.)
- `tailwind.config.ts` — mapped color tokens, font families, spacing
- `index.html` — loaded font links
- The target page component — inline styles vs. Tailwind classes, data model, functional features

## 4. Clarify Before Implementing

Use the `clarify` tool with multiple-choice options for each key decision. Ask these adaptation questions (pick relevant ones):

1. **Color/Font strategy**: Adapt design's visual style to existing CSS variable system (consistent, light+dark) vs. use design's colors scoped to page only vs. replace site-wide
2. **Interaction model**: Modal vs. inline vs. responsive hybrid (e.g. modal on desktop, inline on mobile)
3. **Existing features not in design**: Keep as separate styled sections vs. integrate vs. skip (e.g. subscriptions, expired toggle)
4. **Layout**: Match design's grid (e.g. 2-column) vs. keep current vs. responsive (2-col desktop, 1-col mobile)
5. **Icons**: Add design's icon font to project vs. use existing approach vs. inline SVG
6. **Global elements in design**: Skip if not page-specific (e.g. bottom nav bar) vs. add to page vs. add globally (separate task)

## 5. Token Mapping

Map the external design's tokens to the project's existing CSS variables. Example (Stitch Material Design 3 → Komuna oklch system):

| External Token | Hex | Existing Variable |
|---|---|---|
| background | #17130f | `var(--paper-1)` |
| surface-container | #231f1b | `var(--paper-2)` |
| surface-container-highest | #393430 | `var(--paper-3)` |
| on-surface | #eae1db | `var(--ink-1)` |
| on-surface-variant | #e4beb1 | `var(--ink-2)` |
| outline-variant | #5b4137 | `var(--rule-2)` |
| primary | #ffb59a | `var(--accent)` |
| Newsreader | — | `var(--font-serif)` (DM Serif Display) |
| Hanken Grotesk | — | `var(--font-sans)` (Inter Tight) |

Include this mapping table in the planning artifact so the user can verify the adaptation.

## 6. Planning Artifact

Create a styled HTML planning document (per user preference: styled, responsive HTML with public link). Include:

1. Decisions summary table (all clarify answers)
2. What's preserved (functional features staying intact)
3. Numbered implementation plan (file-level tasks)
4. Visual mockup of the redesigned page using the EXISTING design system (not the external design's colors)
5. Color mapping reference table

Store under `<project>/docs/<name>.html`, publish via nginx, verify HTTP 200 and content contains expected text.

## 7. Implementation Notes

- Add new fonts (e.g. Material Symbols) to `index.html` `<head>` — one `<link>` tag
- Add page-specific CSS classes to `globals.css` (wallet pocket, voucher ticket, perforation, animations) — scoped class names, using existing CSS variables
- Rewrite only the visual layer of the target page component — preserve all data fetching, state management, i18n, routing, and business logic
- Map each external design element to the existing data model (e.g. Stitch "program card" → `WalletItemDTO` group, "voucher ticket" → `VoucherDTO`)
- Preserve functional features not shown in the design (payment confirmation, loading/error/empty states, expired toggle, etc.)
