# Profile-owned resource actions

Use this pattern when an authenticated app lets users create a resource from their own profile and privileged operators create it for another user.

## Minimal design

1. **Reuse the canonical form/dialog.** Add an optional `ownerId` rather than creating a second admin-only form.
2. **Link account chrome to the profile.** Put “My profile” in both desktop/sidebar and mobile account menus; do not assume one responsive surface covers both.
3. **Place the action on the profile header.** Show it when `viewer.id == profile.id` or the viewer has the explicit privileged role.
4. **Constrain destinations to the target owner.** If the resource is shared into groups/tenants, offer only groups the target user belongs to—not every group visible to the privileged viewer.
5. **Enforce delegated ownership server-side.** Default ownership to the authenticated caller. Accept a different `ownerId` only for the privileged role; reject ordinary callers explicitly and return 404 for unknown owners.
6. **Keep authorization separate from presentation.** A hidden button is not permission enforcement.

## Test-first coverage

Add a focused API test before implementation:

- privileged caller creates for another user and response owner matches target;
- ordinary caller supplying another `ownerId` gets 403;
- unknown target gets 404;
- existing self-create behavior remains unchanged.

Then run the frontend type/build check, full backend suite, service restart with readiness polling, public smoke/E2E, exact-path staging, commit, and push.

## Deployment pitfall

A systemd restart can report `active` before the HTTP listener is ready. Poll the health endpoint briefly instead of treating the first immediate connection refusal as a deployment failure.