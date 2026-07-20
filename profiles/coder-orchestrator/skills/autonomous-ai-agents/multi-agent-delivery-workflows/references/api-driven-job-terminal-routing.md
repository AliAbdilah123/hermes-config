# API-driven coding jobs: terminal routing and delivery verification

Use this when a project scheduler submits a coding job to Hermes through the API server and the job edits files but later claims it could not test, build, deploy, commit, or push.

## Diagnostic pattern

1. Search the originating API session, not only the current chat, and inspect the exact tool trace.
2. Confirm the API platform's effective toolsets with `hermes tools list --platform api_server`.
3. Separate **capability availability** from **the attempted execution path**:
   - Direct `terminal` being enabled proves the session can run shell commands.
   - Failure of an indirect wrapper or a restricted subagent does not prove direct terminal is unavailable.
4. Check delegated task toolsets. Shell-dependent work should explicitly receive `terminal` and usually `file`; do not rely on an ambiguous convenience label when the child trace shows no shell tools.
5. Before reporting a blocker, retry the smallest harmless command with the direct `terminal` tool and the project directory as `workdir`.

## Scheduler prompt contract

For API-created implementation jobs, append concise execution guidance to the generated prompt:

- Use the direct `terminal` tool with the selected project/worktree as `workdir` for shell commands.
- Do not route a simple shell command through another execution layer.
- Any delegated shell task must explicitly request terminal access.
- If an indirect attempt fails, retry through direct terminal before claiming terminal is unavailable.

Keep the user's task and done definition unchanged. Add an exact prompt regression test so future scheduler edits preserve the contract.

## Delivery checklist

After changing the scheduler:

1. Run the focused prompt/API tests and the project build.
2. Rebuild and restart the scheduler service if it is deployed.
3. Verify the local service and public endpoint.
4. Commit only task-owned files; preserve unrelated dirty-tree changes.
5. Push when a remote exists. If no remote is configured, report the local commit and the precise push blocker rather than claiming full delivery.

## Root-cause wording

Report the narrow truth: terminal capability was enabled, but the job selected an execution path that did not expose shell access and failed to retry the direct tool. Avoid broad claims that the platform or terminal feature is unavailable.
