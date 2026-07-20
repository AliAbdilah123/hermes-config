# Browser modal history

Use this pattern when Back should dismiss a modal/inspector without changing the underlying route.

## Minimal React pattern

```tsx
function useModalHistory(open: boolean, close: () => void) {
  useEffect(() => {
    if (!open) return;
    history.pushState(history.state, "", location.href);
    const onPopState = () => close();
    addEventListener("popstate", onPopState);
    return () => removeEventListener("popstate", onPopState);
  }, [open]);
}
```

Pass `() => history.back()` to normal close controls so they consume the synthetic entry. Keep the popstate callback responsible only for closing local modal state.

## Focused regression

1. Set a realistic underlying URL with `history.replaceState`, including any board/project query.
2. Render a harness with the modal initially open.
3. Assert `pushState` received the same URL.
4. Dispatch `PopStateEvent("popstate")`.
5. Wait for the dialog to disappear.
6. Assert the path and query remain unchanged.
7. Unmount and restore spies to avoid contaminating later UI tests.

## Deployment verification

If the SPA is embedded in a backend binary, build frontend assets, rebuild the exact service `ExecStart` binary, restart it, then compare the live HTML asset hash with the generated embedded HTML. Service-active plus HTTP 200 alone does not prove the new frontend is live.
