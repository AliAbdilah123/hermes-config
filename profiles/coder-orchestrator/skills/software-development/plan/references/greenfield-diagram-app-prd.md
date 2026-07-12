# Greenfield diagram/planning app PRD pattern

Use when the user describes a new diagram/canvas product and expects a reviewable plan before implementation.

## Durable pattern

1. Treat the first response as a PRD/plan artifact, not an implementation, unless the user explicitly says to build now.
2. Capture the product's graph semantics separately from generic canvas mechanics:
   - what a node means,
   - what an edge means,
   - directionality/read direction,
   - whether relationships are one-to-many or many-to-many,
   - what happens when a node represents another object/project.
3. Prefer a relational graph model for MVP:
   - `projects` own diagrams,
   - `nodes` belong to a project and store position/type/content,
   - `edges` belong to a project and store `from_node_id`, `to_node_id`, optional label,
   - unique `(project_id, from_node_id, to_node_id)`,
   - `CHECK(from_node_id <> to_node_id)`,
   - nullable FK for linked project/object nodes.
4. For edge menus, define exact graph mutations, not just labels:
   - delete edge removes relationship only,
   - add node on edge rewires `A -> B` into `A -> New -> B`,
   - edit label updates edge metadata only.
5. For nested/linked diagrams, default to a side-panel/read-only preview for MVP. True nested embedded canvases are a later complexity unless explicitly requested.
6. Include an explicit implementation gate and open decisions. Do not treat the user's design choices as permission to build.

## Review artifact checklist

- Dark-first styled HTML with light/dark toggle.
- One visual mockup of the canvas/edge menu.
- MVP vs skipped scope.
- Data model and validation constraints.
- API shape.
- Implementation phases and acceptance criteria.
- Public URL verified with HTTP 200 and a grep for a distinctive phrase.
