# Product/package image fallback tone

Use when Komuna package/product cards show the browser broken-image icon (small paper/logo in the image corner) or blank media space.

## Root cause pattern

A card renders an API-provided `<img src={imageUrl}>` without an `onError` fallback. If the URL is stale, missing from the deployed static assets, or cached incorrectly by CDN, the browser draws the native broken-image icon instead of the app's image-tone placeholder.

## Fix pattern

- Trace the specific card component (`ProductCard`, `PackageCard`, program/store sections) rather than only checking seeded `public/product-images` or `public/package-images`; valid assets do not help if the DTO URL is stale/missing.
- Reuse the existing visual language: `placeholder-warm`, `placeholder-warm-stripe`, mono uppercase label, matching aspect ratio/radius.
- Add local state: `const [imageFailed, setImageFailed] = useState(false)`.
- Render `<img>` only when `imageUrl && !imageFailed`; set `onError={() => setImageFailed(true)}`.
- Render the tone placeholder when the URL is missing or failed.

## Regression test

Testing Library pattern:

```tsx
render(<MemoryRouter><PackageCard pkg={pkgWithBadImageUrl} programId="prog_1" /></MemoryRouter>)
fireEvent.error(screen.getByRole('img', { name: pkgWithBadImageUrl.name }))
expect(screen.queryByRole('img', { name: pkgWithBadImageUrl.name })).not.toBeInTheDocument()
expect(screen.getAllByText(pkgWithBadImageUrl.name).length).toBeGreaterThan(0)
```

## Deploy verification

After `npm run build` and static deploy, verify the public/deployed bundle contains a fallback literal such as `placeholder-warm-stripe`, because Komuna deploys static Vite assets behind nginx/Cloudflare.
