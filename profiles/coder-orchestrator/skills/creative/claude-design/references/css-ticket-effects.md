# CSS Ticket / Voucher Visual Effects

Real-world ticket metaphors — perforation lines, punch holes, scissor cuts, "USED" stamps —
make claimed/used vouchers feel physically consumed rather than just dimmed.

## Scissor-Cut Torn Edge (clip-path zigzag)

Split a ticket into two physically separate halves along the perforation line,
each with a jagged torn edge. The stub is slightly rotated/offset to look
like it was physically torn off and placed back.

### ⚠️ Critical: close the polygon around ALL element corners

The #1 bug with this technique: only tracing the zigzag edge points in the
`clip-path: polygon()` without including the opposite corners. This clips
away the entire element content, leaving only a thin zigzag strip visible
("the vouchers are invisible" bug).

**WRONG** (only zigzag points → element content vanishes):
```css
/* DON'T DO THIS — missing top-left and bottom-left corners */
clip-path: polygon(
  100% 4%, calc(100% - 5px) 8%, 100% 12%, /* ... zigzag only ... */ 100% 100%
);
```

**CORRECT** (full element enclosed):
```css
/* Left half: torn right edge */
.ticket-main {
  clip-path: polygon(
    0% 0%,                        /* ← top-left corner (REQUIRED) */
    100% 0%,                      /* ← top-right corner (REQUIRED) */
    100% 4%, calc(100% - 5px) 8%, 100% 12%,    /* zigzag starts here */
    calc(100% - 5px) 16%, 100% 20%, calc(100% - 5px) 24%, 100% 28%,
    calc(100% - 5px) 32%, 100% 36%, calc(100% - 5px) 40%, 100% 44%,
    calc(100% - 5px) 48%, 100% 52%, calc(100% - 5px) 56%, 100% 60%,
    calc(100% - 5px) 64%, 100% 68%, calc(100% - 5px) 72%, 100% 76%,
    calc(100% - 5px) 80%, 100% 84%, calc(100% - 5px) 88%, 100% 92%,
    calc(100% - 5px) 96%, 100% 100%,           /* zigzag ends */
    0% 100%                       /* ← bottom-left corner (REQUIRED) */
  );
}

/* Right half (stub): torn left edge — mirror */
.ticket-stub {
  clip-path: polygon(
    0% 0%, 5px 4%, 0% 8%, 5px 12%,             /* zigzag starts at top-left */
    0% 16%, 5px 20%, 0% 24%, 5px 28%,
    0% 32%, 5px 36%, 0% 40%, 5px 44%,
    0% 48%, 5px 52%, 0% 56%, 5px 60%,
    0% 64%, 5px 68%, 0% 72%, 5px 76%,
    0% 80%, 5px 84%, 0% 88%, 5px 92%,
    0% 96%, 5px 100%,                           /* zigzag ends at bottom-left */
    100% 100%,                   /* ← bottom-right corner (REQUIRED) */
    100% 0%                      /* ← top-right corner (REQUIRED) */
  );
  transform: rotate(-1.2deg) translateY(3px); /* "torn off" feel */
}
```

The polygon must trace a closed path: start at one corner, go along the
straight edges to where the zigzag begins, trace the zigzag, then close
back along the opposite straight edge to the start. Any corner omitted
from the polygon is clipped away, along with all content behind it.

### Other key points

- The zigzag step (~4% vertical per tooth, ~5px horizontal indent) is the sweet spot
  — too small looks like noise, too large looks like corrugated metal.
- Slight `transform: rotate(-1.2deg) translateY(3px)` on the stub sells the "physically
  torn and placed back" illusion. Don't over-rotate — more than 2° looks intentional, not torn.
- A small `gap` between the two halves (flex parent) makes the cut look physical.
- Keep dashed perforation marks on both torn edges via `repeating-linear-gradient`
  so the "dashed line origin" is still legible.

### Responsive (mobile: horizontal cut)

On narrow viewports the ticket stacks vertically, so the cut goes horizontal.
Same closure rule applies — include all four corners:

```css
@media (max-width: 600px) {
  .ticket-main {
    clip-path: polygon(
      0% 0%, 100% 0%,              /* top edge (both corners) */
      96% calc(100% - 4px), 92% 100%, 88% calc(100% - 5px),  /* horizontal zigzag */
      84% 100%, 80% calc(100% - 5px), 76% 100%, 72% calc(100% - 5px),
      /* ... continue zigzag across bottom ... */
      4% 100%, 0% calc(100% - 4px)
    );                              /* ends at bottom-left */
  }
  .ticket-stub {
    clip-path: polygon(
      4% 0%, 8% 5px, 12% 0%, 16% 5px,  /* horizontal zigzag at top */
      /* ... continue ... */
      96% 5px, 100% 0%,
      100% 100%,                   /* bottom-right corner (REQUIRED) */
      0% 100%                      /* bottom-left corner (REQUIRED) */
    );
  }
}
```

### "USED" stamp overlay

```css
.used-stamp {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) rotate(-22deg);
  font-family: var(--font-mono);
  font-size: 28px; font-weight: 700;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: color-mix(in oklch, var(--danger) 28%, transparent);
  border: 4px solid color-mix(in oklch, var(--danger) 28%, transparent);
  border-radius: 10px; padding: 6px 18px;
  opacity: 0.7; pointer-events: none; z-index: 5;
}
```

- Use single-border for modern, `border: double` for a classic rubber-stamp look.
- Keep opacity ~0.6–0.7 so content remains readable underneath.
- `pointer-events: none` is essential — the stamp must not block clicks.

## Perforation Line (intact ticket)

For active/un-cut tickets, a dashed vertical line between the main body and the
stub conveys "tear here":

```css
.ticket-perforation {
  width: 2px;
  margin: 12px 0;
  background: repeating-linear-gradient(to bottom, var(--rule) 0 6px, transparent 6px 13px);
}
```

## Punch Holes (notch circles)

Semi-circle cutouts at the perforation line where the two halves meet:

```css
.ticket-main::before, .ticket-stub::after {
  content: ''; position: absolute; top: 50%;
  width: 24px; height: 24px; border-radius: 999px;
  background: var(--page-bg); /* match page, not card */
  transform: translateY(-50%);
}
.ticket-main::before  { left: -13px; }
.ticket-stub::after   { right: -13px; }
```

- Background must match the **page background**, not the card, so the notch
  looks like a hole punched through the card.
- For cut/torn tickets, hide these — the clip-path zigzag replaces them.

## When to apply

- **Active voucher**: intact perforation line + punch holes (no cut).
- **Claimed voucher**: scissor-cut effect + "USED" stamp + slight stub rotation.
- **Expired voucher**: scissor-cut + grayscale filter + lower opacity.
- **All-claimed pocket card**: jagged clip-path on the flap outline, grayscale
  voucher stack, "CLAIMED" double-border stamp.