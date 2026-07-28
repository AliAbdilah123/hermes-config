# Live card preview and image fallback refinement

Use this pattern when a management form includes a live public-facing card preview or a list whose remote images may be absent/broken.

## Reuse the canonical visual primitive

Before inventing a fallback, inspect the public card component for the product’s established image placeholder. Reuse or minimally export that primitive so missing URLs and `img` load failures look identical across discovery and management surfaces.

Handle both states:

1. Empty image URL renders the placeholder immediately.
2. A present URL that fires `onError` switches that specific item to the placeholder.

Track failed images by stable entity ID. Do not hide every image because one request failed. Preserve the entity’s existing tone/label metadata, with a documented default tone when absent.

## Make live previews representative

A live preview should resemble the actual card hierarchy rather than a generic bordered summary. Include only information available from the form:

- image or canonical tone-striped placeholder;
- visibility/access badge;
- dominant title and useful description fallback;
- structured facts such as timezone/access;
- selected administrator identity;
- a quiet live-update status.

Keep it inside the same responsive form container: adjacent on wide screens, stacked on narrow screens. Prefer CSS and existing design tokens over JavaScript sizing.

## Focused verification

Add a regression test that:

- renders a card with an image URL;
- fires the image error with Testing Library’s `fireEvent.error` so React state updates are wrapped correctly;
- asserts the canonical placeholder and its label appear;
- checks that the create preview exposes its meaningful hierarchy and empty administrator state.

Run changed-file lint, the focused test, production build, and an exact cache-busted public deep-route/asset check after publishing.

## Pitfalls

- Testing only `imageUrl == null`; broken remote URLs are the common failure mode.
- Using decorative empty `alt` when the image is the only visual identifier in a management list.
- Duplicating tone stripe CSS in the management page instead of reusing the canonical placeholder.
- Adding preview-only facts the create form cannot actually supply.
- Running frontend Vitest from the repository root when project configuration lives in the frontend package directory.
