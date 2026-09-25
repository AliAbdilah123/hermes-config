# Relocation Checklist

## Before moving

- [ ] Confirm app user (who runs the process)
- [ ] **Thoroughly** search for `.env` files with elevated privileges: `sudo find / -maxdepth 6 -type f \( -name '.env' -o -name '.env.*' \) 2>/dev/null`
  - Regular `find` misses files in `drwxr-x---` dirs like `/var/lib/<app>` owned by a different user (e.g. `www-data`).
- [ ] Search for hardcoded references: `grep -r '<old_path>' <project> /opt /etc`
- [ ] Note any systemd service files that may reference the old `.env` path (search: `grep -r 'EnvironmentFile' /etc/systemd/system/*.service`)

## Moving

```bash
# 1. Cross-user move
sudo mv /var/lib/<app>/.env /home/<user>/<app>/.env

# 2. Fix ownership AFTER move
sudo chown <app_user>:<app_user> /home/<user>/<app>/.env

# 3. Verify
ls -la /home/<user>/<app>/.env
```

## After moving

- [ ] Update systemd unit files if service uses `EnvironmentFile=` pointing at the old path:
  ```bash
  sudo sed -i 's|EnvironmentFile=/old/path|EnvironmentFile=/new/path|' /etc/systemd/system/<app>.service
  sudo systemctl daemon-reload
  sudo systemctl restart <app>.service
  sudo systemctl is-active <app>.service
  ```
- [ ] Remove or archive `.env.bak.*` stales
- [ ] Smoke test the app if feasible
- [ ] Update any fallback-path documentation or code references
