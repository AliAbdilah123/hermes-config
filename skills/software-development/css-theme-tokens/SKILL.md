---
name: css-theme-tokens
title: CSS Theme Token Fixes
description: "Fix light/dark mismatches caused by hardcoded colors; replace with theme-aware custom properties like var(--paper-1), var(--ink-1), var(--rule), and color-mix(in oklch,...) overlays."
---

# CSS Theme Token Fixes

## Core pattern

1. Identify the broken surface: hero, carousel caption, card drop shadow, badge, border, dot.
2. Search the component CSS for hardcoded colors: `rgba(0,0,0,...)`, `white`, `black`, `oklch(1 0 0 / ...)`, `rgb(0 0 0 / ...)`.
3. Replace surface/background colors with matching paper/role tokens:
   - Backgrounds: `var(--paper-1)`, `var(--paper-2)`, `var(--paper-3)`
   - Text: `var(--ink-1)`, `var(--ink-2)`, `var(--ink-3)`
   - Borders/rules: `var(--rule)`, `var(--rule-2)`
   - Accent: `var(--accent)`, `var(--accent-ink)`, `var(--accent-soft)`
4. For semi-transparent overlays/gradients over images, prefer:
   - `color-mix(in oklch, var(--ink-1) 88%, transparent)` instead of `rgba(0,0,0,.88)`
   - `color-mix(in oklch, var(--paper-1) 60%, transparent)` instead of `rgba(255,255,255,.6)`
   - Keep the original visual weight; only swap the base color to a theme token.

## Komuna example

In `apps/web/src/globals.css` the discovery carousel had hardcoded values:
- Caption gradient `rgba(0,0,0,.88)` → `color-mix(in oklch, var(--ink-1) 88%, transparent)`
- Carousel border `oklch(1 0 0 / .24)` → `var(--rule)`
- Dot border/fill `white` → `var(--ink-1)`

Run targeted discovery/carousel tests after the change. Do not rewrite unrelated CSS.

## Pitfalls

- Don’t add `prefers-color-scheme` media queries when the app already toggles `.dark` on `<html>`. The `.dark` block redefines the same custom properties; using the variables is enough.
- Don’t inline `style={{ background: 'rgba(...)' }}` on an element that belongs in the stylesheet. Move it to a token-aware class.
- Don’t “fix” by forcing dark-only aesthetics. In light mode, `var(--ink-1)` resolves to a dark brown in Komuna, not pure black—honor that.

## Verification

- Reproduce the component in both themes.
- Grep the changed CSS for the old hardcoded color to confirm removal.
- Run the component’s snapshot/unit tests; theme tokens should not break them.