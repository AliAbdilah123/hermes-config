# Smooth collapsible UI animation

When a React/Vite UI currently conditionally mounts a breakdown/details panel (`expanded && <div>...`) and the user asks for smoother open/close animation, avoid adding JS measurement or animation libraries for small panels.

## Minimal pattern

1. Keep the breakdown mounted whenever the data exists, not only while expanded.
2. Wrap the content in a grid container with `gridTemplateRows: expanded ? '1fr' : '0fr'`.
3. Put the actual content in a child with `overflow: 'hidden'`.
4. Transition `grid-template-rows` and optionally `opacity`.
5. Add basic accessibility state on the trigger and panel:
   - trigger: `aria-expanded={expanded}` and `aria-controls="..."`
   - panel: matching `id` and `aria-hidden={!expanded}`

```tsx
{hasBreakdown && (
  <div
    id="voucher-breakdown"
    aria-hidden={!expanded}
    style={{
      display: 'grid',
      gridTemplateRows: expanded ? '1fr' : '0fr',
      opacity: expanded ? 1 : 0,
      transition: 'grid-template-rows 220ms ease, opacity 180ms ease',
    }}
  >
    <div style={{ overflow: 'hidden' }}>
      {/* breakdown content */}
    </div>
  </div>
)}
```

## Verification

- Run the app's normal production build (`npm run build` for Komuna web).
- If deployed, copy the fresh build to the public path and verify the public JS contains a unique transition marker such as `grid-template-rows 220ms ease`.
- For broader visual changes, add screenshot/browser QA; for this tiny collapsible animation, build + deployed marker is usually enough unless the user asks for pixel QA.
