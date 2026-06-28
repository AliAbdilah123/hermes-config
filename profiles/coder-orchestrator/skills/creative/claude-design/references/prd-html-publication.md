# Review-document HTML publication workflow

Use this when producing styled HTML artifacts for the user, including PRDs, implementation plans, migration plans, specs, audits, and other documents they need to review.

## Required shape

- Produce a designed/styled HTML artifact, not only a plain-text or markdown document, when the user needs to review the document.
- For PRDs/product concepts, keep the richer PRD-style layout; for plans/audits/specs, use a readable review-document layout with table of contents, code blocks, and clear decision/status cards.
- Store the canonical file under the relevant project path:
  - `<project path>/docs/<name>.html`
- Make it publicly accessible at:
  - `http://<publicip>/prd/<name>.html`
- Use a symlink from the web server PRD directory to the docs file rather than duplicating the public artifact.

## Discovery pattern

1. Determine the relevant project path. If no existing project exists, create or use a clearly named project directory rather than leaving the artifact in the home directory.
2. Determine the public IP with a live lookup, e.g. `curl -s https://api.ipify.org`.
3. Inspect the active web server config for the PRD alias/root. Existing deployments may use `/usr/share/nginx/html/prds/` for `/prd/` or `/prds/` routes.
4. Store the artifact in `<project path>/docs/`.
5. Create/update a symlink in the web server PRD directory pointing to the docs file.
6. If `/prd/` is missing but `/prds/` exists, add the singular `/prd/` route while preserving the plural route, then test and reload nginx.
7. Verify with both local and public HTTP requests before finalizing.

## Verification checklist

- Source file exists in `<project path>/docs/<name>.html`.
- Public symlink resolves to that source file.
- Web server config test passes before reload.
- Local URL returns HTTP 200: `http://127.0.0.1/prd/<name>.html`.
- Public URL returns HTTP 200: `http://<publicip>/prd/<name>.html`.
- Final response ends with the public PRD link.

## Pitfalls

- Do not leave PRD artifacts only as local files under `/home/ubuntu`. For this user, PRDs are expected to be published artifacts with the docs-source/symlink-public layout.
- When publishing via nginx symlink, verify the source HTML file is world-readable (`chmod 644 <project path>/docs/<name>.html` if needed). A symlink under `/usr/share/nginx/html/prds/` can still return HTTP 403 if the target file was written with restrictive permissions such as `600`; fix the target permissions, then re-test local and public HTTP 200.