# Generated embedded assets: final build and git hygiene

A verification build may rewrite tracked generated bundles after an implementation agent has already committed and pushed. Minifiers can even produce whitespace-only churn.

After the final build:

1. Run `git status --short` and inspect every generated-asset diff.
2. If a diff is nondeterministic formatting only and the committed bundle already represents the verified source, restore that generated file and re-check cleanliness.
3. If the build produced a real source-dependent change, commit and push the regenerated artifact. Never report synchronization while the tree is dirty.
4. Reconfirm `HEAD` matches its upstream before reporting completion.
5. Treat deployment as a separate side effect. A successful build, push, active service, or reachable public URL does not authorize deployment; deploy only when the request or standing project instructions explicitly permit it.

This check is especially important when frontend build scripts copy hashed assets into a backend embed directory.