# Radix dialog mobile centering reset

Use when a Radix/shadcn dialog is half off-screen on a phone after adding custom `.modal` mobile CSS.

## Identify the active dialog before editing

Map distinctive screenshot content (title, actions, fields) to the rendering component and follow its props to the final `DialogContent` class. Apps often reuse one shell with variants such as `.modal` and `.inspector`; fixing the generic modal does nothing when the broken job-detail view passes `inspector`. Inspect the live element’s classes or the callsite before choosing a selector.

## Root cause

`DialogContent` commonly carries utility classes equivalent to:

```css
position: fixed;
left: 50%;
top: 50%;
transform: translate(-50%, -50%);
```

A mobile rule that changes only `width`, scrolling, or alignment does not remove that transform. If another rule changes the horizontal anchor or layout assumptions, the retained `translateX(-50%)` can move half the panel beyond the viewport. Removing an unrelated `position: relative` override may preserve fixed positioning while still leaving this centering conflict unresolved.

## Minimal fix

Keep desktop centering, but make the narrow-screen geometry complete and internally consistent. Tailwind v4 may compile `translate-x-[-50%]` into custom properties plus a generated `translate:` declaration, so reset the variables too; `transform:none` alone may not neutralize the displacement.

```css
@media (max-width: 600px) {
  .modal {
    left: .5rem;
    right: .5rem;
    top: auto;
    bottom: .5rem;
    --tw-translate-x: 0;
    --tw-translate-y: 0;
    transform: none;
    --tw-translate-y: 0;
    transform: none;
    width: auto;
    max-height: calc(100dvh - 1rem);
    overflow-y: auto;
  }
}
```

This uses native fixed insets, avoids viewport-width arithmetic, and keeps the dialog inside the visual viewport. After building, inspect the generated CSS served by the public asset URL and verify both translation variables are zero in the mobile `.modal` rule; source-level tests can pass while the compiled utility transform still wins.

## Regression check

Assert the mobile rule contains both edge anchors, zeroed Tailwind variables, and the transform reset; checking only `overflow-y:auto` or absence of `position:relative` is too weak:

```ts
expect(css).toMatch(
  /@media\(max-width:600px\)[\s\S]*?\.modal\{[^}]*left:\.5rem[^}]*right:\.5rem[^}]*--tw-translate-x:0[^}]*--tw-translate-y:0[^}]*transform:none[^}]*overflow-y:auto/
)
```

Then run the native frontend tests/build, deploy the rebuilt embedded/static assets, restart the serving process when required, and fetch the public hashed CSS asset to verify the compiled mobile rule contains the resets. Finally visually verify at a phone viewport. Do not declare success from source tests or a new asset hash alone—the rendered mobile geometry is the acceptance check. The signature of this bug is distinctive: the backdrop covers the viewport correctly, but roughly half the dialog is clipped beyond one horizontal edge.
