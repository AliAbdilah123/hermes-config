# Shared Card Broken Image Fallbacks

When a public listing/discovery/search page shows blank or broken image areas inside reusable cards:

1. Locate the shared card component first, not the individual page. Discovery and search/listing pages commonly reuse the same card, so one component-level fix covers both.
2. Distinguish missing image data from failed image loading:
   - `imageUrl == null/empty` should render the existing placeholder immediately.
   - A non-empty but stale/bad `imageUrl` must use an `<img onError>` fallback; otherwise the browser shows a broken image icon/blank area.
3. Reuse the app's existing placeholder/tone system before adding new assets. If the placeholder label is absent, fall back to the entity/program name so the placeholder is not visually empty.
4. For "card looks cut off" reports, inspect internal padding and grid stretching before redesigning. Common small root fixes:
   - Give the card `height: 100%` so grid siblings stretch evenly.
   - Keep body/content as a flex column with the footer row `margin-top: auto`.
   - Ensure desktop and mobile overrides leave bottom padding; `padding-bottom: 0` makes cards look clipped.
5. Add one focused component test that fires an image `error` event and asserts the placeholder renders.
6. Verify with build plus a browser/screenshot check on the public listing route; inspect the shared component's other route only if it has a separate card implementation.

Minimal React pattern:

```tsx
const [imageFailed, setImageFailed] = useState(false)

{imageUrl && !imageFailed ? (
  <img src={imageUrl} alt={name} onError={() => setImageFailed(true)} />
) : (
  <ImagePlaceholder label={imageLabel || name} tone={imageTone ?? 'warm'} />
)}
```
