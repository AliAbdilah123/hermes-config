# Tailwind Responsive Class Override with cn()/tailwind-merge

## The problem

When a shared component (e.g. a `DialogContent`) has `sm:max-w-sm` in its default className
and you pass `max-w-4xl` via the consumer's `className` prop, tailwind-merge does NOT merge them.
They operate at different breakpoints (`sm:` vs none), so both apply, and the _more restrictive_ value wins.

### Example: DialogContent

```tsx
// DialogContent defaults include: "... sm:max-w-sm ..."
// Consumer passes:
<DialogContent className="max-w-4xl ...">  // ❌ does NOT override sm:max-w-sm
```

Result: on screens ≥640px, the dialog is still constrained to `24rem` (sm), not `56rem` (4xl).

### Fix

Match the breakpoint prefix:

```tsx
<DialogContent className="sm:max-w-4xl max-w-[calc(100%-2rem)] ...">  // ✅
```

The `max-w-[calc(100%-2rem)]` handles the mobile/unsized case so it doesn't overflow the viewport.

## Why tailwind-merge doesn't catch this

`tailwind-merge` only merges classes that _conflict_ — same property, same breakpoint.  
`max-w-4xl` and `sm:max-w-sm` are different properties as far as it's concerned, so both stay.
The browser's CSS cascade then applies the more restrictive `max-width: 24rem`.

## When to watch for this

- Any component with built-in responsive Tailwind classes (DialogContent, Sheet, Drawer, etc.)
- The component uses `cn()` or `clsx` with `twMerge` to merge consumer className with defaults
- You're trying to make the component wider on desktop
