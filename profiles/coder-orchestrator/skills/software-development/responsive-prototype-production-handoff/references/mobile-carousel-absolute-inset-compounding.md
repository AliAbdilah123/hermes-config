# Mobile carousel: compounded absolute insets

## Symptom

A mobile carousel shows a correctly sized outer card and footer, but its image occupies only the upper portion, leaving a large solid or striped block above the pagination. The defect can look like missing content or an oversized card.

## Root cause pattern

A grouped selector applies a footer reservation to every nested absolutely positioned layer:

```css
.carousel__stage,
.carousel__stage article,
.carousel__stage a {
  bottom: 52px;
}
```

If all three elements also use `position: absolute; inset: 0`, each nested `bottom` shortens its containing block again. The reservation compounds rather than applying once.

## Minimal fix

Reserve the footer only on the outer stage and reset nested layers to fill it:

```css
.carousel__stage {
  bottom: 52px;
}

.carousel__stage article,
.carousel__stage a {
  bottom: 0;
}
```

Do not increase the outer carousel height to hide the symptom.

## Verification

1. Capture a real slide with an image and a missing-image placeholder; placeholders can be mistaken for empty space.
2. Confirm the image/placeholder fills all space above the footer.
3. Confirm caption and controls remain inside the stage and pagination remains in its dedicated footer.
4. Add a CSS contract test asserting the footer offset appears only on the outer stage.
5. Check light and dark themes at the reported physical viewport.

## Related alignment pitfall

When a hero, tab strip, and tab panel have equal outer widths but still look misaligned, inspect nested padding. A full-width tab shell with extra `padding-inline` can create a different visual indentation despite matching bounding boxes. Establish one mobile outer gutter and avoid adding a second gutter to the tab scroller unless intentional.
