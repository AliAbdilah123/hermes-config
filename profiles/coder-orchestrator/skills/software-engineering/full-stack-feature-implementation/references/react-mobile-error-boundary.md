# React Mobile Robustness: ErrorBoundary + Preload Errors + Lazy Heavy Deps

Use this when a React/Vite SPA shows white screens on mobile, especially when navigating to pages with heavy dependencies (charts, PDF libraries, video processing).

## Three-Layer Defense

### Layer 1: ErrorBoundary (catches everything)

Add a class-based ErrorBoundary component wrapping the entire app. Without one, any uncaught render error unmounts the React root → white screen.

```tsx
// components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react'

interface Props { children: ReactNode; fallback?: ReactNode }
interface State { hasError: boolean; error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) { super(props); this.state = { hasError: false, error: null } }
  static getDerivedStateFromError(error: Error): State { return { hasError: true, error } }
  componentDidCatch(error: Error, info: { componentStack: string }) {
    console.error('ErrorBoundary caught:', error, info.componentStack)
  }
  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="text-center max-w-md">
            <h2 className="text-lg font-semibold mb-2">Something went wrong</h2>
            <p className="text-sm mb-4">An unexpected error occurred. Please refresh.</p>
            <pre className="text-xs text-left text-red-500 bg-gray-100 rounded-lg p-3 mb-4 overflow-auto max-h-32">
              {this.state.error?.message ?? 'Unknown error'}
            </pre>
            <button onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg bg-violet-600 text-white">
              Reload Page
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
```

Wrap in main.tsx:
```tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

**Placement**: wrap as close to the root as possible (around `<Routes>` or `<App />`), NOT inside individual route components. A single ErrorBoundary at the root catches all errors.

### Layer 2: vite:preloadError handler (catches chunk-load failures)

On mobile with unreliable connectivity, large chunks (charts at 300KB+, PDF at 500KB+) can fail mid-load. Vite's preload helper throws, React's lazy() promise rejects, and without an ErrorBoundary → white screen.

```tsx
// main.tsx — before createRoot
window.addEventListener("vite:preloadError", (event) => {
  const e = event as Event & { payload?: unknown }
  console.warn("vite:preloadError — reloading page", e.payload)
  e.preventDefault() // prevents the throw
  window.location.reload()
})
```

This auto-reloads the page when a chunk fails — MUCH better UX than a white screen.

### Layer 3: Lazy-load heavy deps (don't bloat route chunks)

Heavy libraries (jspdf + autotable + html2canvas ≈ 564KB) should NOT be statically imported at the top of a lazy-loaded page component. They get bundled into the page's chunk, bloating the lazy-load payload.

**Bad** (imports at top → bundled into page chunk):
```tsx
import jsPDF from 'jspdf'
import 'jspdf-autotable'
import html2canvas from 'html2canvas'

async function handleExportPDF() {
  const pdf = new jsPDF()
  // ...
}
```

**Good** (dynamic imports → separate chunk, loaded only on user click):
```tsx
async function handleExportPDF() {
  const [{ default: jsPDF }, { default: html2canvas }] = await Promise.all([
    import('jspdf'),
    import('html2canvas'),
  ])
  await import('jspdf-autotable')
  const pdf = new jsPDF()
  // ...
}
```

Result: AnalyticsPage chunk drops from ~600KB to ~15KB. The PDF chunk (577KB) is only fetched when the user actually clicks "Export PDF".

### Layer 4: Null guards on API data

API responses may return `null`/`undefined` for optional fields. Calling `.toLocaleString()` or `.toFixed()` on these values throws during render.

```tsx
// Bad
{metrics.currentFollowers.toLocaleString('en-US')}
// Good
{(metrics.currentFollowers ?? 0).toLocaleString('en-US')}
```

For TanStack React Table cell functions:
```tsx
col.accessor('engagement', {
  // Bad
  cell: info => info.getValue().toLocaleString(),
  // Good
  cell: info => (info.getValue() ?? 0).toLocaleString(),
})
```

## Pitfalls

- **ErrorBoundary doesn't catch async errors**: Errors in event handlers, async functions, or `setTimeout` callbacks are NOT caught by ErrorBoundary. Use try/catch in those contexts.
- **Suspense only catches pending, not rejected**: The `<Suspense fallback={...}>` around `<Routes>` only catches *pending* Promises from `React.lazy()`, not rejected ones. A failed chunk load passes through Suspense to the (nonexistent) ErrorBoundary → white screen. That's why Layer 2 is critical.
- **Don't nest ErrorBoundaries unnecessarily**: One at the root is sufficient. Nesting only makes sense when you want different fallback UIs for different sections.
- **Test on slow 3G**: Desktop WiFi won't surface chunk-load failures. Use Chrome DevTools → Network → throttling → "Slow 3G" to verify Layers 1–3 work.
