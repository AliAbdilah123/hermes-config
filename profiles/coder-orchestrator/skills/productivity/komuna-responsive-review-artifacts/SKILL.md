---
name: komuna-responsive-review-artifacts
description: Use when creating Komuna plans, PRDs, specs, or review HTML artifacts. Ensure the published review page itself is mobile-readable, responsive, and visually aligned with Komuna's website/dashboard theme.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [komuna, review-artifacts, responsive, html, planning]
    related_skills: [plan, komuna-operations]
---

# Komuna Responsive Review Artifacts

## Overview

Komuna review artifacts are not just source documents. The user reviews them on the public PRD route, often from mobile. Any plan, PRD, spec, or design proposal published for Komuna must be readable on phones and must look like it belongs to Komuna.

This skill applies to the **review artifact page itself** (`/prd/<name>.html`), not only to the feature being planned.

## When to Use

Use when:
- Creating or updating a Komuna plan, PRD, spec, or review document.
- Publishing HTML under `docs/*.html` and `/usr/share/nginx/html/prds/*.html`.
- The user asks for a public review link for Komuna.
- Updating an existing public Komuna review artifact after user feedback.

Do not use this as permission to implement the planned product feature. A review artifact remains a review artifact unless the user explicitly asks to implement/deploy the feature.

## Required Review Page Behavior

Every Komuna review HTML page must:

1. Include `<meta name="viewport" content="width=device-width, initial-scale=1" />`.
2. Use a responsive outer width such as `width:min(100% - 20px, 1120px)` instead of fixed desktop widths.
3. Collapse any desktop sidebar/table-of-contents into a single-column or two-column mobile layout.
4. Avoid horizontal overflow from tables, code blocks, wide grids, long URLs, or long headings.
5. Make code blocks horizontally scrollable with `overflow-x:auto` and `-webkit-overflow-scrolling:touch`.
6. Make tables mobile-readable: either convert rows to cards under small breakpoints or wrap them in a scroll container.
7. Use readable mobile font sizes: body text around 15–16px minimum; headings should use `clamp()`.
8. Keep tap targets and TOC links comfortably spaced on mobile.
9. Verify the public URL with a cache-busting query string after changes.

## Komuna Theme Requirements

Use Komuna dashboard-style visual language:

- Dark paper backgrounds: `--paper-1`, `--paper-2`, `--paper-3`.
- Warm ink colors: `--ink-1`, `--ink-2`, `--ink-3`.
- Subtle rules/borders: `--rule`, `--rule-2`.
- Accent color: `--accent`, `--accent-soft`.
- Serif large headings, mono uppercase eyebrows/labels, rounded cards, subtle borders.

Do not introduce:
- A generic blue SaaS theme.
- Bright white pages unrelated to Komuna.
- Tiny desktop-only tables on mobile.
- Fixed sidebars that consume most mobile width.
- Raw unstyled markdown dumps.

## CSS Pattern

A safe baseline:

```css
:root {
  --paper-1:#17120f; --paper-2:#211a16; --paper-3:#2d241e;
  --ink-1:#f7efe5; --ink-2:#d2c3b4; --ink-3:#9e8d7c;
  --rule:#3a2d26; --rule-2:#564238;
  --accent:#d86f45; --accent-soft:rgba(216,111,69,.16);
}
* { box-sizing: border-box; }
body { margin:0; background:var(--paper-1); color:var(--ink-1); line-height:1.65; }
.wrap { width:min(100% - 20px, 1120px); margin:0 auto; }
.layout { display:grid; grid-template-columns:260px minmax(0,1fr); gap:20px; }
main, .card { min-width:0; }
pre { max-width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }
@media (max-width:880px) { .layout { grid-template-columns:1fr; } .toc { position:static; } }
@media (max-width:560px) {
  table, thead, tbody, tr, th, td { display:block; width:100%; }
  thead { display:none; }
}
```

## Publication Workflow

1. Save the canonical source plan under `.hermes/plans/` or `docs/`.
2. Save the styled HTML at `/home/ubuntu/projects/komuna/docs/<slug>.html`.
3. Publish with:

```bash
chmod 644 /home/ubuntu/projects/komuna/docs/<slug>.html
sudo ln -sfn /home/ubuntu/projects/komuna/docs/<slug>.html /usr/share/nginx/html/prds/<slug>.html
sudo nginx -t
```

4. Verify local and public:

```bash
curl -sI http://127.0.0.1/prd/<slug>.html
curl -sI https://komuna.ahsanworks.com/prd/<slug>.html
curl -sS 'https://komuna.ahsanworks.com/prd/<slug>.html?v=mobile-check' | grep -E 'viewport|@media|max-width'
```

5. If possible, run a browser/mobile viewport check at 390px width and inspect for horizontal overflow.

## Verification Checklist

- [ ] Public review page returns HTTP 200.
- [ ] HTML includes viewport meta tag.
- [ ] CSS includes mobile breakpoints for ≤880px and/or ≤560px.
- [ ] TOC/sidebar collapses on mobile.
- [ ] Tables or wide content do not force page-wide horizontal scrolling.
- [ ] Code blocks scroll independently if needed.
- [ ] Page uses Komuna theme tokens and visual style.
- [ ] Final response includes the public review link.

## Reference Notes

- `references/subscription-xendit-prd-mobile-fix.md` — concrete correction from the subscription/Xendit PRD: fix the published PRD page itself, not only the implementation-plan content; includes CSS and verification pattern.
- `references/subscription-package-entitlement-model.md` — domain model for subscription plans in Komuna review artifacts: packages are sellable bundles, subscription entries grant renewable entitlements, product scopes can be one-or-more products, and subscription bookings create `voucher_claims.subscription_id` claims rather than pre-generated vouchers.
- `references/wallet-voucher-pocket-animation-preview.md` — approved wallet voucher pocket preview/implementation pattern: preserve approved animation timing, animate the actual pocket stack out/back, allow overflow, avoid fake return voucher layers.
- `references/wallet-voucher-pocket-animation-preview.md` — preview-artifact pattern for wallet voucher pocket animation fixes: reuse live wallet component structure, demonstrate literal pull-out/empty-pocket/return sequencing, and avoid changing already-approved animation feel.

## Common Pitfalls

1. **Adding responsive requirements to the implementation plan instead of fixing the review page.** If the user says the public PRD is hard to read on mobile, update the HTML artifact itself.
2. **Desktop-only grid.** A sticky left TOC with a wide content column is fine on desktop but must collapse on mobile.
3. **Tables as tiny text.** Convert tables to block rows or scroll containers on phones.
4. **Forgetting cache busting.** Cloudflare may serve stale HTML. Verify with `?v=<label>` after updates.
5. **Changing product-plan content while fixing readability.** Keep content changes separate from artifact presentation fixes unless the user asked for both.
6. **Animation previews that fake the product component.** When the user asks for a Komuna animation preview, reuse the relevant product component geometry/class names and demonstrate the exact object relationship they care about. For wallet voucher pocket previews, the visible vouchers inside the pocket must be the animated objects: open should pull the existing stack out and leave the pocket empty; close should use the same stack path in reverse, not separate throwaway voucher elements that pop into the pocket afterward. Keep existing timing/easing if the user says the animation itself is good; change only source object, overflow, visibility, and sequencing.
