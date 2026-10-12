# SPA refresh modal flash

## Pattern

A gate starts with authoritative state unknown (`null`) and loading `true`, but renders its blocking modal for every state except an explicitly allowed result. During refresh, unknown is incorrectly presented as blocked.

```tsx
if (status && !status.requiresAcceptance) return children
return <BlockingModal />
```

Treat the gate as three states: unknown/loading, allowed, and blocked. Fail closed while unknown without rendering a false modal:

```tsx
if (status && !status.requiresAcceptance) return children
if (loading) return null
return <BlockingModal />
```

Protected children remain unmounted, so this removes the flash without weakening access control.

## Regression check

Hold the request unresolved and assert that neither protected content nor the dialog mounts:

```tsx
getStatus.mockReturnValue(new Promise(() => {}))
render(<Gate><ProtectedContent /></Gate>)
expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
expect(screen.queryByText("Protected content")).not.toBeInTheDocument()
```

Keep separate tests for resolved blocked and resolved allowed states.

## Release verification

1. Run the focused gate test, typecheck, and production build.
2. Deploy the built artifact.
3. Refresh the public route and inspect rendered DOM for absent modal text.
4. Do not treat an unauthenticated redirect as proof of an authenticated gate's behavior; retain the unresolved-state component test or run an authenticated browser check.
