# Codex model selection and isolated worktree preview

Use when a user requests a specific Codex CLI model and wants to review frontend work before merging or changing production.

## Model selection

1. Do not assume a provider-qualified name from conversational shorthand is the CLI model ID. A name such as `cx/gpt-5.6-sol` may be rejected while `gpt-5.6-sol` is available.
2. Check the installed CLI help first. If there is no `models` subcommand, start the interactive TUI in a PTY and inspect its model picker/status (`/model` or the displayed footer). Account for trust/hooks prompts before sending slash commands.
3. Use the exact model ID shown by the CLI:

```bash
codex exec --sandbox danger-full-access \
  -m gpt-5.6-sol \
  -c model_reasoning_effort='"high"' \
  -o /tmp/codex-result.txt \
  "<self-contained task>"
```

4. A server error saying a model is unsupported for ChatGPT authentication can mean the identifier is wrong, not necessarily that new credentials are required. Verify the catalog before asking the user to re-authenticate.

## Isolated review workflow

1. Create a dedicated branch/worktree from the intended base branch.
2. Tell Codex explicitly: edit only that worktree, preserve behavior, test/build, commit there, and do not merge or deploy.
3. Independently verify the resulting commit, clean status, diff checks, focused tests, and production build. Do not repeat a worker's claimed pass count without rerunning the named tests; report baseline fixture failures precisely.
4. Push the feature branch if the user's normal workflow requires remote delivery, but do not merge.

## Public preview without changing production

A worktree checkout alone is not viewable. For a Vite app already served by nginx, create a distinct preview base and directory. Do not describe copying worktree-built assets into a separate preview directory as deploying to master/production; source branch, build output, and serving path are separate concerns. Clearly state all three.

Before building, inspect the app's runtime basename/API override mechanism. The build-time `VITE_BASE` only fixes asset URLs; React Router may still receive a production basename injected by the catch-all nginx location.

Create the preview build:

```bash
env -u VITE_NEON_AUTH_URL \
  VITE_BASE=/admin-tab-preview/ \
  VITE_API_BASE_URL=/api/v1 \
  npm run build
sudo mkdir -p /var/www/html/projects/komuna/admin-tab-preview
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/admin-tab-preview/
sudo chmod -R a+rX /var/www/html/projects/komuna/admin-tab-preview
```

Add a preview-specific nginx location before the generic SPA catch-all. Its fallback and injected runtime basename must match the preview path:

```nginx
location ^~ /admin-tab-preview/ {
    try_files $uri $uri/ /admin-tab-preview/index.html;
    sub_filter_types text/html;
    sub_filter '</head>' '<script>window.__BASENAME__="/admin-tab-preview";window.__API_BASE__="/api/v1"</script></head>';
    sub_filter_once off;
}
```

Run `nginx -t` before reload. Verify the preview HTML contains the preview basename injection, referenced hashed JS/CSS return 200 with correct MIME types, and a nested preview route returns the preview SPA. Finally perform rendered browser QA; HTML/assets returning 200 can still produce a blank or misrouted app. Keep the canonical production directory untouched. Confirm that the preview API base intentionally targets the existing backend, so reviewers see real data without deploying backend changes.

## Preview cleanup after approval

Once the preview is approved and production is deployed:

1. Determine whether the preview exists in Git, nginx/deployment state, or both. Do not create an empty cleanup commit when it was deployment-only.
2. Remove the preview-specific nginx location and restore the generic production SPA routing. Back up the config, run `nginx -t`, then reload.
3. Remove the deployed preview directory without touching the canonical production build directory.
4. Verify production root, a nested production route, and the API still respond correctly.
5. A removed SPA preview URL may still return `200` through the production catch-all. Status alone is not proof of removal: compare its response with production root (or inspect asset hashes/runtime basename) and confirm it is the ordinary production SPA, not the preview build.
6. Remove the feature worktree only after checking it is clean and its commits are integrated. Run `git worktree prune` and verify `git worktree list` no longer contains it.
7. Leave unrelated worktrees, untracked plans/docs, and branches untouched. Delete the feature branch only when explicitly requested.

## Pitfalls

- Do not infer that `codex --help` lists available models; model discovery may only exist in the interactive TUI.
- TUI slash commands sent before trust/hooks prompts are cleared can be swallowed or concatenated.
- Building a preview with the production base path causes blank pages or asset 404s under the preview URL.
- A successful build is not proof that a focused test suite passes; rerun it yourself.
- Clearly label preview URLs as temporary and isolated, and state that production/master remain unchanged.
- Do not report a preview as gone merely because its directory/config was deleted if the SPA fallback still serves `200`; verify the returned application identity.
