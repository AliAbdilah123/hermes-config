# Workspace-relative project directory resolution

Use when project creation accepts a directory path and relative paths fail even though absolute paths work.

## Symptom

Creating a project with `directory: "app"` returns a filesystem error pointing under the service/process working directory rather than the selected workspace root. Absolute paths may still pass, hiding the contract bug.

## Root cause

A shared canonicalization helper calls `filepath.Abs(relativePath)` before anchoring the path. `filepath.Abs` resolves against the process current working directory, not the application's workspace root. One create route may pre-join the root while another route that calls the same helper directly does not, producing inconsistent behavior across duplicate endpoints.

## Minimal root fix

Normalize relative paths inside the shared canonicalization boundary:

```go
if !filepath.IsAbs(path) {
    path = filepath.Join(root, path)
}
abs, err := filepath.Abs(filepath.Clean(path))
```

Keep the existing `EvalSymlinks`, containment, existence, directory, and readability checks. Do not weaken traversal/symlink protections merely to accept relative input.

## Regression test

1. Create a temporary workspace root.
2. Create a real child directory such as `<root>/app`.
3. POST project creation with `directory: "app"` through the route used by the frontend.
4. Assert `201` and that the persisted/returned directory equals the canonical child path.
5. Retain a traversal test such as `../escape` returning `400`.

The test must use a child directory, not the workspace root itself; posting an absolute root path will pass before and after the fix and cannot prove relative-path behavior.

## Duplicate directory conflicts

A workspace may enforce `UNIQUE(workspace_id, directory)`. Keep that constraint: two projects sharing one execution directory can corrupt execution assumptions. Do not “fix” creation by removing uniqueness or silently reusing the existing row.

Before insert, look up the canonical directory within the workspace and return a specific `409`, for example `directory is already used by <project name>`. Retain the unique constraint as the race-safe final guard; the preflight lookup exists to improve the common error message.

If project creation exists at both a general endpoint and a workspace-nested endpoint, apply the behavior to both. A regression test must call the route used by the frontend, create the first project successfully, repeat the same canonical directory under another name, and assert the specific `409` message. Run the test before implementation to confirm it initially receives the generic database-conflict message.

## Audit checklist

- Trace every project-create/edit endpoint and caller.
- Put relative-path semantics in the shared helper so all routes agree.
- Preserve directory uniqueness and translate expected conflicts into actionable messages.
- Verify the frontend's actual route, not only a legacy sibling endpoint.
- Run targeted RED/GREEN test, full backend suite, frontend tests/build, rebuild embedded assets/binary, restart, and probe readiness.
