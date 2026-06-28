# Local project rename deployment pattern

Use when renaming an already-deployed local full-stack project, especially when the rename must cover code, env, systemd, nginx, deployed static assets, and filesystem paths.

## Workflow

1. **Discover all live paths before editing**
   - Inspect the project working tree and git status.
   - Locate the deployed copy, public static directory, nginx route(s), and systemd service.
   - Inspect systemd with `systemctl cat <service>` and `systemctl show <service> -p EnvironmentFiles -p WorkingDirectory -p ExecStart -p ActiveState`.
   - Search nginx for the old project slug/name.
   - Do not print secret-bearing `.env` values; only list keys or transform values in-place.

2. **Rename code/config first**
   - Update frontend base paths, API base fallback paths, document title/brand strings, storage keys, and deployment docs.
   - Update backend module/service identifiers, default DB filename if it is project-named, health service labels, and tests that assert names/paths.
   - Update `.env.example` with key names only.
   - Update the real `.env` by path transformation without logging values.

3. **Build before moving runtime paths**
   - Run backend tests and build from the API directory.
   - Run frontend lint/build from the frontend directory.
   - Confirm built `dist/index.html` references the new public base path.

4. **Move runtime filesystem and DB safely**
   - Stop/disable the old systemd service before moving its working directory.
   - Rename the project directory.
   - If the SQLite filename contains the old project name, rename the db, `-wal`, and `-shm` files together, then update `.env` to match.

5. **Replace service and nginx entries**
   - Create a new systemd unit with the new service name, `WorkingDirectory`, `EnvironmentFile`, `ExecStart`, and `ReadWritePaths`.
   - Enable/start the new service and remove the old unit after confirming it is inactive/disabled.
   - In nginx, change the API proxy to the new public slug and add old-slug redirects if useful.
   - Deploy frontend `dist` to the new static directory and remove the old static directory if the old URL should no longer serve content.
   - Run `nginx -t` before reload.

6. **Verify from both localhost and public URL**
   - `systemctl show <new-service> -p ActiveState -p SubState -p EnvironmentFiles -p WorkingDirectory`.
   - Curl local API health/ready/bootstrap via direct port and via nginx public path.
   - Curl public index, parse referenced JS/CSS/favicon paths, and curl each asset for 2xx.
   - Curl old public path and confirm it redirects to the new slug.
   - Search `/etc/systemd`, nginx, and the project for old absolute runtime paths; expected leftovers should be limited to intentional redirects.

## Pitfalls

- Do not leave the systemd unit pointing at the old directory after `mv`; the service may appear healthy until restart.
- Do not update only nginx: Vite `base` and frontend API fallback path must match the new public slug, or assets/API calls break.
- Do not rename only the `.db` file; SQLite WAL/SHM sidecars must move with it when present.
- Do not remove the old static directory until the new public index/assets and API are verified.
- Avoid printing `.env` contents while transforming old paths to new paths.
