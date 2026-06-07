# Ubuntu 24.04 apt/dpkg stuck-lock recovery

- Symptom: `apt-get` fails with `Could not get lock /var/lib/dpkg/lock-frontend`
- Safe recovery sequence:
  1. Remove stale frontend/apt locks and reconfigure dpkg.
  2. `sudo rm -f /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock`
  3. `sudo dpkg --configure -a`
  4. `sudo apt-get update`
- If a third-party repo key is missing, temporarily remove its source file instead of importing keys.
- If `apt-get update` still fails with an `apt lists` lock but no obvious apt process exists from `ps`, inspect `lsof /var/lib/dpkg/lock-frontend` and `fuser /var/lib/dpkg/lock-frontend` before rebooting.
