# Architecture and planning reference

## Make product verbs concrete

- **Save** mutates only the owner's draft.
- **Publish** validates and saves the submitted draft, then creates exactly one immutable version.
- **Marketplace** reads published snapshots, never mutable draft rows.
- **Install** records which published version the user can run.
- **Use** requires an explicit contract: collect input, validate, execute, validate output, and record status/errors.

Ask whether browsing is public, installations pin or auto-upgrade, publishers can unpublish, schemas use raw JSON or a builder, and execution uses a shared or per-app provider.

## Minimal durable model

- users and opaque server-side sessions
- apps: owner and mutable draft metadata
- app features: stable identity, order, prompt, input/output schema
- app versions: unique `(app_id, version)` and canonical immutable snapshot
- installations: unique `(user_id, app_id)` and installed version
- runs: user/app/version/feature, structured input/output, status/error, timestamps

Never reconstruct old versions from current feature rows.

## Publish transaction

1. Authenticate and enforce ownership in the query.
2. Validate the complete submitted app and schemas.
3. Save draft metadata and ordered features.
4. Calculate the next per-app integer version.
5. Serialize a canonical snapshot of the just-saved state.
6. Insert the immutable version and update `latest_version`.
7. Commit and return saved state plus published version.

Any error rolls back save and publish. Test first publish, sequential increments, invalid-save rollback, unchanged old snapshots, and concurrent publishes.

## Security baseline

- Normalize and uniquely constrain email; use a proven password hash.
- Generate high-entropy opaque session tokens, store only a hash, and support expiry/revocation.
- Use `HttpOnly`, `SameSite`, and HTTPS-aware `Secure` cookies.
- Return non-disclosing login errors.
- Enforce ownership server-side; never accept owner IDs from clients.
- Separate public catalog endpoints from authenticated Studio/install/run endpoints.
- Validate schemas and run inputs against the installed snapshot server-side.
- Validate structured output when an output schema exists.
- Never grant tools or credentials merely because an authored prompt requests them.

## Review artifacts

When implementation and UI both need approval, publish separate linked pages:

- **Plan:** semantics, model, API, ordered phases, tests, risks, open questions, implementation gate.
- **Design:** static proposal matching the existing product shell, responsive states, editor actions, marketplace/install flow, and visible “not live” labeling.

## Acceptance ledger

Prove that anonymous users cannot author or run; users cannot access others' drafts; save never publishes; publish saves and creates one next version; marketplace never exposes drafts; old versions never mutate; installations persist and run only published definitions; validation happens server-side; and build/restart/public E2E/release checks pass.

## Common failures

- Treating “use the app” as self-explanatory.
- Storing only `latest_version` and losing historical content.
- Publishing outside one transaction.
- Letting marketplace cards read mutable metadata.
- Premature visual schema builders, ratings, payments, moderation, collaboration, or per-app model selection.
- Combining a long plan and UI mockup into one overloaded review page.
