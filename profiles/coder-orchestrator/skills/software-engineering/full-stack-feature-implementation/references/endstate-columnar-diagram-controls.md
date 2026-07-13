# Endstate columnar diagram controls

Use when updating a small React/Vite + Go/SQLite diagram/canvas app that persists the whole graph through `PUT /api/projects/:id/diagram` and already has node `x/y` plus directed edges.

## Durable pattern

- Prefer a frontend-only graph mutation when the existing schema already supports the request:
  - arbitrary relations = existing `edges(fromNodeId,toNodeId,label,notesMarkdown)`;
  - connected node creation = add a node and an edge in the same local diagram state update;
  - modal node edit = reuse node `title/body/type/linkedProjectId/notesMarkdown` fields.
- Remove broad/global add actions when the UX asks for process-local creation. Put small contextual controls on the node itself.
- For process-stage layout, keep persisted `x/y` as source of truth and create new nodes at deterministic offsets rather than adding drag/drop or auto-layout unless explicitly requested.

## UI controls that worked

- Tiny plus buttons around each node:
  - top/bottom: same-column sibling node; connect current node → new node;
  - right: next process-stage node; connect current node → new node;
  - left: previous process-stage node; connect new node → current node.
- Tiny triangle/corner button per node opens a compact menu:
  - `Edit node` opens the node modal;
  - `Delete node` respects locked nodes.
- Relation mode can be one state variable (`relationFrom`): first selected node becomes source, clicking another node creates a directed edge if it is not a duplicate/self edge.
- Keep relation label/notes on the existing edge menu/modal rather than inventing a separate relation model.

## Tests / verification

- Add React tests for behavior markers:
  - general `Add node` button is absent;
  - node-local plus controls are present by accessible label;
  - corner menu opens an edit modal that includes notes.
- Run the project-native test command as-is. If a repeated CLI flag fails (e.g. duplicate Vitest `--environment jsdom`), rerun the script without repeating the flag rather than treating it as app failure.
- For subdomain deployments served from `/var/www/html/projects/<slug>/`, deploy Vite `dist/`, then verify the public `index.html` references the new asset and the public JS bundle contains an app-specific marker string.
