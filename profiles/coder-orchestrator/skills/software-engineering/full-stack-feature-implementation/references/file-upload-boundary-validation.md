# File upload boundary validation

Use this checklist when expanding uploads across job creation, comments/replies, messages, or similar sibling flows.

1. Trace every upload entry point end-to-end; do not update only the UI named in the request. Creation and reply flows often use separate request builders and handlers.
2. Remove file-extension and MIME allowlists when the requirement is “any type.” Treat client MIME metadata as advisory.
3. Enforce count and per-file byte limits in the client for immediate feedback and again in the server handler as the trust boundary.
4. Cap the entire HTTP body before multipart parsing. Account for multipart overhead when deriving the aggregate cap from `max_files * max_file_size`; do not set it to the exact payload sum.
5. Read each part through a bounded reader (`per_file_limit + 1`) and reject overflow. Do not trust multipart header sizes.
6. Validate attachment names before including them in prompts, logs, paths, or storage: reject empty, non-basename, control-character, and duplicate names as appropriate.
7. If attachments become model context, preserve UTF-8 text directly and encode arbitrary binary deterministically (for example Base64 with an explicit label). Never coerce arbitrary bytes into text silently.
8. Keep no-file requests on the existing JSON path when practical; use multipart only when files exist. This minimizes regression risk.
9. Make file-only replies possible if the product semantics allow them, and clear selected files after a successful submission.
10. Test both sibling flows plus boundaries: maximum accepted count, count+1 rejected, exact byte limit accepted, limit+1 rejected, and binary content handled safely.
11. Rebuild and verify generated/embedded frontend assets after source changes, then run backend tests, frontend tests, the production build, and a whitespace/diff check.

Prefer one shared backend parser and one shared frontend validator/request helper over duplicated guards in each handler.