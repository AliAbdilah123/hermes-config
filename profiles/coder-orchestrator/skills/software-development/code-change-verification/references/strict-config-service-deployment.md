# Deploying an exact commit into a strict-config systemd service

Use this pattern when the working tree is dirty and a service must receive one exact commit without absorbing unrelated local edits.

## Safe sequence

1. Export the requested revision into a temporary directory:
   ```bash
   build_dir=$(mktemp -d)
   git archive <commit> | tar -x -C "$build_dir"
   ```
2. Build and test inside that export, not in the dirty checkout.
3. Before replacing the live executable, run the candidate as the service user with the real config path and a bounded timeout/readiness probe:
   ```bash
   timeout 10s sudo -u <user> /tmp/candidate -env /path/to/.env
   ```
   A strict config loader may reject keys added to the production environment after the target commit. A successful compile and unit suite do not detect this.
4. If startup rejects an existing compatibility key, do not edit or reveal the production value. Apply the smallest already-reviewed compatibility patch that only permits the key, test the config package and affected service package, and rebuild. Report that the runtime is the requested commit plus that compatibility patch rather than claiming it is the byte-exact commit.
5. Back up the current executable, install the candidate atomically, restart, then verify:
   - `systemctl is-active`
   - a fresh PID/start timestamp and zero restart loop
   - the direct service listener with an application-specific probe
   - the public proxied endpoint
   - recent journal output
6. If systemd reaches its start-rate limit during a failed cutover, install the corrected candidate first, then `systemctl reset-failed` and start it. Do not repeatedly restart the known-bad binary.

## Why this matters

An exact historical commit can be source-correct yet operationally incompatible with the current `.env`. Candidate startup against the real runtime contract catches this before downtime, while `git archive` prevents unrelated dirty-tree work from entering the deployed binary.
