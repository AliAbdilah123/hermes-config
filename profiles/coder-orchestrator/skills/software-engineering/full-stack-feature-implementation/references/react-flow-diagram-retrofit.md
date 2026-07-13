# React Flow diagram retrofit in small React/Vite apps

Use when replacing a hand-rolled absolute-position diagram/canvas with `@xyflow/react` while preserving an existing persisted graph JSON shape.

## Pattern

- Keep the persisted model stable when possible:
  - existing nodes with `id`, `x`, `y`, title/body/type/notes fields map to React Flow nodes with `position: {x, y}` and `data` carrying the original node;
  - existing directed edges with `fromNodeId`/`toNodeId` map to React Flow edges with `source`/`target`;
  - on drag stop, write React Flow `position.x/y` back into the persisted node fields;
  - save through the same existing `PUT /api/projects/:id/diagram` endpoint.
- Use one custom node component to preserve existing node-local controls (plus buttons, corner menus, notes, relation mode). Add React Flow `Controls`, `MiniMap`, and `Background` instead of rebuilding pan/zoom/minimap behavior.
- Move CSS from absolute positioning on the custom node body to React Flow positioning:
  - `.canvas { overflow: hidden }` rather than scroll-based manual canvas;
  - inner `.node { position: relative }`, because React Flow positions the wrapper;
  - size the `.react-flow__node` wrapper if the old node had a fixed width.
- Mark interactive controls inside a custom node with `nodrag` and stop pointer/mouse propagation so React Flow drag handlers do not swallow button interactions.

## Testing notes

- `@xyflow/react` needs browser APIs missing in jsdom; stub at least `ResizeObserver` in tests:
  ```ts
  class ResizeObserver { observe(){} unobserve(){} disconnect(){} }
  vi.stubGlobal('ResizeObserver', ResizeObserver)
  ```
- Test behavior markers that survive React Flow internals:
  - React Flow controls such as `Zoom In` and `Mini Map` exist;
  - old node labels render;
  - node-local plus controls are still accessible;
  - old generic/manual canvas-only controls are absent.
- If old `node_modules` was installed by a different package manager or has a stale hidden lockfile, npm may fail with Arborist errors like `Cannot read properties of null (reading 'edgesOut')`. The durable fix is a clean install (`mv node_modules node_modules.bak... && npm install`) and then delete the backup so Vitest does not discover tests under `node_modules.bak*`.

## Deployment verification

- After deploying Vite `dist/`, verify the public index references the new asset hash.
- Grep the deployed JS bundle for React Flow markers like `react-flow__` rather than expecting app text in `index.html`.
