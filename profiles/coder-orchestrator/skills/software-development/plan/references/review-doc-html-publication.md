# Review document HTML publication workflow

Use this whenever a plan or other document is produced for the user to review.

## Required shape

- Save the canonical markdown/source document under `.hermes/plans/` or the relevant project `docs/` path as usual.
- Also produce a styled, readable HTML version for review.
- Store the HTML under the relevant project path when a project is known:
  - `<project path>/docs/<document-slug>.html`
- Publish the HTML via the web server PRD/review-doc route using a symlink, usually:
  - source: `<project path>/docs/<document-slug>.html`
  - symlink: `/usr/share/nginx/html/prds/<document-slug>.html`
  - public URL: `http://<publicip>/prd/<document-slug>.html`

## Styling expectations

- Use a complete standalone HTML file with embedded CSS.
- Include a clear title/hero, table of contents for long docs, readable typography, styled code blocks, and responsive layout.
- Do not leave a large review doc as raw markdown only.

## Updating an existing public review artifact

When the user adds requirements after a review artifact is already published, do not create a disconnected second document by default. Patch the existing canonical markdown/source plan and the existing published HTML so the public URL remains the current review surface.

For each requirement amendment:
- Update the markdown/source plan first so the canonical plan is complete.
- Update the HTML artifact with a visible section/table row/nav link as appropriate; do not rely on markdown-only changes.
- Keep existing public symlink/URL stable unless the user asks for a versioned new artifact.
- Verify the public HTML contains the specific newly-added terms, not only HTTP 200.

## Verification checklist

- Source markdown/source doc exists.
- HTML file exists and is world-readable (`chmod 644` if needed).
- Symlink resolves to the HTML source file.
- `nginx -t` passes before relying on the route. If bare `nginx -t` fails with `/run/nginx.pid` permission errors, retry `sudo nginx -t` before treating it as a real configuration failure.
- Local URL returns HTTP 200: `http://127.0.0.1/prd/<document-slug>.html`.
- Public URL returns HTTP 200: `http://<publicip>/prd/<document-slug>.html`.
- Confirm the public HTML contains expected section titles and at least one exact phrase from each new amendment.
- Final response ends with the public link.

## Pitfalls

- If direct symlink creation under `/usr/share/nginx/html/prds/` fails with permissions, use `sudo ln -sfn` rather than moving the artifact elsewhere.
- Do not encode a transient browser-preview timeout as a blocker if `curl` verifies HTTP 200 and content checks pass; report browser verification limitations only if relevant.
