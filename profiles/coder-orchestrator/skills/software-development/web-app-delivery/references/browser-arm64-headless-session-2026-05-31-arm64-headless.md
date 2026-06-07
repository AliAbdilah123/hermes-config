Observations from this session:
- System/user-reported: `chromium-headless.aarch64` installed.
- Broker search landed on Playwright-managed Chromium at `/home/opc/.cache/ms-playwright/chromium-1223/chrome-linux/chrome`.
- `agent-browser open https://example.com` succeeded with `AGENT_BROWSER_EXECUTABLE_PATH` set to that path.
- `browser_navigate` still failed with "Chrome not found" after writing `~/.agent-browser/config.json`; the Hermes browser stack invokes launch paths that differ from `agent-browser` CLI resolution.
- `/home/opc/.agent-browser/browsers/` did not exist before writing `~/.agent-browser/config.json`; `agent-browser install` did not populate Playwright-managed binaries there.
