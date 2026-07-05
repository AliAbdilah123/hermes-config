# Native select replacement for small view toggles

Use when a React/Vite page has two or more adjacent toggle buttons that only choose one view mode (for example `date` vs `category`) and the user asks to make them a select input.

## Pattern

1. Keep the existing state/actions; do not introduce a new state layer.
2. Replace the button group with a native `<select>` using the existing view value as `value`.
3. In `onChange`, map option values to the existing action functions.
4. Replace the old toggle CSS with one small select class; remove unused toggle button classes.
5. Add an accessible label via visible label text or `aria-label`.
6. Verify with the project build, deploy if this is a live app, then grep the deployed bundle for the new marker and absence of the old toggle marker.

## Example

```tsx
const handleViewChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
  if (event.target.value === 'category') {
    showCategoryView();
  } else {
    showDateView();
  }
};

<select aria-label="Group transactions by" value={view} onChange={handleViewChange}>
  <option value="date">Date</option>
  <option value="category">Category</option>
</select>
```

## Pitfall

Do not replace this with a custom dropdown dependency or autocomplete component when a native select satisfies the request. Native is smaller, accessible, and matches the user’s preference for minimal code.
