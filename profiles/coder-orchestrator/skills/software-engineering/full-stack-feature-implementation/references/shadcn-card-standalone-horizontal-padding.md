# shadcn Card standalone horizontal padding pitfall

## Problem

shadcn's base `Card` component defaults to `py-6` (vertical padding only). It has **no horizontal padding**. This is intentional: `CardHeader` and `CardContent` supply `px-6`, so the full padding stack works correctly when used together.

However, when `<Card>` is used **directly** without `<CardHeader>`/`<CardContent>` wrappers — like inline forms, simple panels, or the delegate project's entire workspace — every card is missing left/right padding, making content butt against card edges.

## Fix

Change `py-6` to `p-6` in the Card component:

```tsx
// Before (shadcn default):
className={cn('bg-card ... py-6 shadow-sm', className)}

// After:
className={cn('bg-card ... p-6 shadow-sm', className)}
```

## Detection

Files to check: `src/components/ui/card.tsx`

Search pattern: look for `py-6` on the `Card` component's className — NOT on `CardHeader` or `CardContent`.

## Impact

When consumers use `<Card>` standalone (no CardHeader/CardContent), content lacks left/right padding. Changing `py-6` → `p-6` fixes all standaline cards without affecting properly-wrapped cards (CardHeader/CardContent already have their own `px-6`, so the extra horizontal padding collapses).
