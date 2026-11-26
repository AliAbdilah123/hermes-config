# Retrieving an OpenDesign artifact directly from a VPS

Use this when a user supplies an authenticated `designs.../projects/<project-id>/conversations/<conversation-id>/files/<file>` URL and says the OpenDesign project is available on the VPS.

## Retrieval path

1. Parse the URL into `project-id`, `conversation-id`, and filename.
2. Identify the running OpenDesign daemon's data directory from its process environment (`OD_DATA_DIR`). Do not assume the repository-local `.od` directory.
3. Read the canonical artifact from:

   ```text
   <OD_DATA_DIR>/projects/<project-id>/<filename>
   ```

   Read adjacent `<filename>.artifact.json` for renderer/status metadata when present.
4. Confirm conversation identity from `<OD_DATA_DIR>/app.sqlite` rather than relying on a stale Next.js cache:

   ```sql
   SELECT id, title, created_at, updated_at
   FROM conversations
   WHERE project_id = '<project-id>'
   ORDER BY created_at;
   ```

5. Treat `.next/server/app/...` files as rendered route-cache evidence only. They may reference another conversation under the same project and are not the canonical design source.
6. Derive implementation scope from the canonical artifact's actual screens, controls, and interactions. Keep prototype-only affordances separate from durable backend requirements.

## Planning workflow

- For complex greenfield work, publish the ordered implementation plan before coding when the user's delivery preference requires a plan gate.
- Cite the canonical local source path and conversation ID so implementation can later be checked against the same artifact.
- Keep the new app isolated from similarly named existing projects unless the user explicitly asks to extend one.
- Include an explicit implementation gate; access to or approval of the design source is not implementation permission.

## Pitfalls

- Do not repeatedly retry the protected public URL after HTTP 401 when the user directs you to use the VPS copy.
- Do not mistake an existing similarly branded application for the requested greenfield project.
- Do not use generated `.next` route output as source of truth when daemon-managed project artifacts exist.
- Do not copy a standalone prototype literally into production; translate visible interactions into persisted workflows, authorization rules, rejection paths, and E2E acceptance criteria.
