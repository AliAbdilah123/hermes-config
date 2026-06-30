# Responsive data table mobile-card fix recipe

Use when a data-heavy HTML table looks clipped, shifted, or overlapped on phone widths.

## Root-cause pattern

A desktop table with `table-layout: fixed` and a large `min-width` (for example 980-1120px) is acceptable on desktop, but on phones it can become horizontally scrolled or partially shifted. The visible symptoms often look like overlapping headers/cells even when the table cells are technically laid out correctly.

Common contributors:
- missing explicit widths for some fixed-layout columns, causing compression in unexpected columns;
- long URLs, addresses, phones, or tag chips without `overflow-wrap` / `word-break`;
- mobile screenshots captured while the horizontal scroll container is not at `scrollLeft=0`;
- preserving desktop table semantics below ~640px instead of changing the presentation.

## Fix pattern

Keep the desktop table for larger breakpoints, then convert rows to cards at phone widths:

```css
.table-wrap table { min-width: 1120px; table-layout: fixed; }
.table-wrap th, .table-wrap td { overflow: hidden; }
.long-cell { overflow-wrap: anywhere; word-break: break-word; }

@media (max-width: 640px) {
  .table-wrap { overflow: visible; padding: 12px !important; }
  .table-wrap table,
  .table-wrap thead,
  .table-wrap tbody,
  .table-wrap tr,
  .table-wrap th,
  .table-wrap td {
    display: block;
    width: 100%;
    min-width: 0 !important;
  }
  .table-wrap thead {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0,0,0,0);
    white-space: nowrap;
    border: 0;
  }
  .table-wrap tbody { display: grid; gap: 12px; }
  .table-wrap tr {
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    background: #fff;
    overflow: hidden;
  }
  .table-wrap td {
    display: grid;
    grid-template-columns: 96px minmax(0, 1fr);
    gap: 10px;
    align-items: start;
    overflow: visible;
  }
  .table-wrap td:nth-child(2)::before { content: "Name"; }
  .table-wrap td:nth-child(3)::before { content: "Category"; }
  /* Continue labels for each visible column. */
}
```

## Verification

After deploying, verify the served artifact, not just the source:
- build successfully;
- copy/publish the new `dist/` assets;
- fetch the public HTML and confirm it references the new hashed CSS/JS bundle;
- fetch the served CSS and confirm a distinctive mobile rule exists;
- run a mobile-width browser check. Useful DOM metrics:

```js
(() => {
  const wrap = document.querySelector('.table-wrap');
  const rows = [...document.querySelectorAll('.table-wrap tbody tr')].slice(0, 3);
  return {
    wrap: wrap && {
      clientWidth: wrap.clientWidth,
      scrollWidth: wrap.scrollWidth,
      overflow: getComputedStyle(wrap).overflow,
    },
    rows: rows.map(r => ({ rect: r.getBoundingClientRect().toJSON(), text: r.innerText.slice(0, 250) })),
  };
})()
```

At phone widths, `clientWidth` should equal `scrollWidth` for the table wrapper and rows should render as full-width cards. Long addresses/URLs/tags should wrap inside the value column instead of forcing horizontal scroll.