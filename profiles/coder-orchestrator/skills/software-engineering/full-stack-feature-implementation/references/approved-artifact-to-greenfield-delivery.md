# Approved artifact to greenfield delivery

When a user approves a styled product plan/prototype and says “implement it,” treat that artifact as the implementation specification. Do not restart discovery. Preserve review artifacts, create the real app alongside them, and translate visible prototype behavior into tested domain rules.

## Group-scoped platforms

- Separate platform roles from group membership roles. A normal user may administer one group and be a member of another.
- Group creation transactionally creates the creator’s admin membership.
- Keep package-owned content/mastery separate from platform-owned identity, groups, assignments, points, rewards, notifications, and audit.
- Model points as an immutable ledger. Redemption reserves points first, then spends on approval or releases on rejection/cancellation.

## Release verification

- Use distinct authenticated cookie jars for member, group admin, and superadmin.
- Publicly exercise a real learning award, reward reservation, approval or rejection, and a forbidden role mutation. Dashboard text alone is insufficient.
- Deploy binaries and mutable databases outside the Git worktree, behind a loopback listener and reverse proxy. Verify service readiness before public checks.
- Report tests, build, service status, public role-flow E2E, commit, and push separately. If no remote exists, state that explicitly.
