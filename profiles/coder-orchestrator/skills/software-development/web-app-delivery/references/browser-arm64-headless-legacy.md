# Legacy skill package: `browser-arm64-headless`

This file preserves the former `browser-arm64-headless` SKILL.md after consolidation into `web-app-delivery`. Relative support-file links have been rewritten to the re-homed files under `web-app-delivery`.

---

---
name: browser-arm64-headless
description: "Headless browser troubleshooting on ARM64 Linux hosts. Covers Playwright/Puppeteer launch failures, missing OS libraries, OS-package mapping for Debian vs RHEL, and the reliable Docker fallback when host Chrome is unavailable."
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [browser, playwright, puppeteer, chromium, arm64, headless, linux, troubleshooting]
    related_skills: [systematic-debugging, dogfood]
---

# Browser ARM64 Headless

## Overview

Headless Chromium on ARM64 often fails because:
- No native Google Chrome ARM64 build is available for the host distro
- Playwright auto-detects an OS family and may download binaries built for a different distro
- Host libraries are missing or have distro-specific names

This skill gives the decision tree and fast-recovery paths for `Browser stack is unavailable` style errors.

## When to Use

Use this skill when:
- The host is `aarch64`/`arm64` Linux and browser automation reports it cannot launch Chrome/Chromium
- Playwright `install-deps` prints unsupported-OS warnings or attempts to use `apt-get` on a RHEL/Oracle host
- Docker is available but local Chrome/Chromium is not installed

## Decision Tree

1. Is Docker available?
   - YES → Use `mcr.microsoft.com/playwright:<version>-noble` (or `-jammy`). This image already has verified Ubuntu + browser binaries. Preferred when host OS mismatch blocks local installs.
   - NO → Continue below.

2. Use Playwright, not Google Chrome, on ARM64.
   - `npx playwright install chromium` gets the ARM64 build Playwright supports.
   - If Playwright says the host is unsupported, treat it as a libs problem and continue.

3. Map missing dependencies to the host package manager.
   - Oracle/RHEL: `dnf install` with RHEL package names
   - Debian/Ubuntu: `apt-get install` with Debian package names
   - Do NOT run `playwright install-deps` when the underlying package manager does not exist on the host

4. Verify with a minimal launch before running full workflows.

## Distro-Specific Package Mapping

Oracle/RHEL/Rocky names for common Playwright deps:

| Library family | RHEL/Oracle package |
|---|---|
| GTK/ATK/AT-SPI | `gtk3`, `atk`, `at-spi2-core` |
| X11 composite | `libXcomposite` |
| X11 damage | `libXdamage` |
| X11 fixes | `libXfixes` |
| X11 randr | `libXrandr` |
| X11 xf86vm | `libXxf86vm` |
| audio | `alsa-lib` |
| GBM/EGL/GL | `mesa-libgbm`, `mesa-libEGL`, `mesa-libGL`, `libdrm` |
| cups | `cups-libs` |
| xkbcommon | `libxkbcommon` |

Debian/Ubuntu names for the same set:

| Library family | Debian/Ubuntu package |
|---|---|
| GTK/ATK/AT-SPI | `libgtk-3-0`, `libatk1.0-0`, `libatk-bridge2.0-0`, `libatspi2.0-0` |
| X11 composite | `libxcomposite1` |
| X11 damage | `libxdamage1` |
| X11 fixes | `libxfixes3` |
| X11 randr | `libxrandr2` |
| X11 xf86vm | `libxxf86vm1` |
| audio | `libasound2` |
| GBM/EGL/GL | `libgbm1` |
| cups | `libcups2` |
| xkbcommon | `libxkbcommon0` |

## Verified Patterns

### A. Playwright deps on RHEL/Oracle

```bash
sudo dnf install -y gtk3 atk at-spi2-core cups-libs libxkbcommon alsa-lib mesa-libgbm libXcomposite libXdamage libXfixes libXrandr libdrm
```

### B. Docker fallback

```bash
docker run --rm mcr.microsoft.com/playwright:v1.49.0-noble node -e "console.log('ok')"
```

Use the container for tasks that need real browser execution when the host is blocked.

## Verification

```bash
npx playwright --version
npx playwright test --browser=chromium path/to/minimal.spec.ts
```

If the launch still fails, use `ldd` or the host error message to identify the specific missing `.so`.

## Pitfalls

- `playwright install-deps` assumes Debian-family tooling; it hard-`apt-get`. Do not call it on RHEL/Oracle.
- Installing `mesa-libgbm` often resolves the common ARM64 headless launch failure.
- The Oracle Linux host may need `/proc` unmounted as well if later runs hit browser sandbox permission errors.
- x86_64-only Chromium/Chrome packages break ARM64 hosts. The package installs but Chrome ARM64 falls back to "not supported on this architecture" and silently skips downloading a valid binary. Do not rely on Google Chrome download flows on aarch64.
- `chromium-headless` RPMs often place `headless_shell` under `/usr/lib64/chromium-browser/` with no `/usr/bin` symlink. Do not assume `headless_shell` is on `PATH` just because the RPM is installed.
- Playwright does not put Chromium in the standard Chrome search locations. Its ARM64 binary lives at `~/.cache/ms-playwright/chromium-<VERSION>/chrome-linux/chrome`.
- `/home/opc/.agent-browser/browsers/` is often empty after a fresh install. The agent-browser auto-install script does not seed Playwright-managed Chromium there. When Chrome search locations fail, explicitly point at the Playwright Chromium path with `--executable-path` or config instead of re-running install commands.
- `/home/opc/.agent-browser/config.json` matters: write `{"executable_path": "..."}` there for `agent-browser` CLI auto-pickup. Hermes internal browser tooling can still diverge from this config.
