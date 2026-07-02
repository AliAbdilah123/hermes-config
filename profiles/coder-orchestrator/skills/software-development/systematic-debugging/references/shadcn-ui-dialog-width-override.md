# shadcn/ui DialogContent Width Override Trap

## Symptom

You pass `max-w-4xl` (or any `max-w-*`) to a shadcn/ui `DialogContent` component and the dialog stays narrow (~384px) on desktop, crushing your two-column or wide layout.

## Root Cause

shadcn/ui `DialogContent` has a built-in `sm:max-w-sm` class:

```tsx
// dialog.tsx (shadcn/ui default)
className={cn(
  "fixed ... sm:max-w-sm ...",
  className  // your className comes second
)}
```

Even though `cn()` from `tailwind-merge` resolves conflicting classes, it treats `sm:max-w-sm` and `max-w-4xl` as **non-conflicting** because they use different breakpoint prefixes. Both classes survive, and the more restrictive `sm:max-w-sm` (24rem) wins over `max-w-4xl` (56rem) at `sm+` screens.

## Fix

Always match the breakpoint prefix when overriding:

```tsx
// ❌ Wrong — silently ignored on sm+
<DialogContent className="max-w-4xl rounded-3xl">

// ✅ Right — overrides the built-in sm:max-w-sm
<DialogContent className="sm:max-w-4xl max-w-[calc(100%-2rem)] rounded-3xl">
```

The `max-w-[calc(100%-2rem)]` keeps it full-width on mobile (below `sm`), where the built-in `sm:max-w-sm` hasn't kicked in yet.

## General Rule

When overriding any shadcn/ui component default class that has a breakpoint prefix (`sm:`, `md:`, `lg:`), **always include the same breakpoint prefix in your override**. Otherwise tailwind-merge won't remove the default.

## Affected Components

This applies to any shadcn/ui primitive that ships breakpoint-prefixed defaults:
- `DialogContent` (`sm:max-w-sm`)
- `Sheet` components
- Any popup/overlay with responsive width defaults

## Verification

After fixing, inspect the rendered DOM for the dialog element. It should show the intended `max-width` value in computed styles, not the default 24rem.
