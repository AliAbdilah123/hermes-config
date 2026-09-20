# Node subpath service: runtime parity, cache freshness, and public E2E

Use for a Node application mounted behind nginx at a path such as `/projects/<slug>/`.

## Runtime parity before systemd deployment

A shell can resolve `node` from a user-managed installation while systemd uses `/usr/bin/node`. Features such as `node:sqlite` may therefore pass tests but fail at service startup.

Before authoring the unit:

```bash
command -v node
node --version
readlink -f "$(command -v node)"
/usr/bin/node --version
```

Set `ExecStart` to the exact verified runtime path, then restart and poll the real local route. Treat `systemctl is-active` without a successful HTTP probe as insufficient readiness evidence.

## Prefix contract

Keep all three aligned:

- application `BASE_PATH`;
- cookie `Path`;
- nginx proxy prefix.

For a prefix-aware backend, preserve the public prefix in `proxy_pass` instead of stripping it accidentally. Verify the local upstream with the prefixed route before testing nginx.

## Public cache freshness

When HTML or JavaScript changes but a public browser still executes old behavior, compare the public HTML and referenced asset URL against the final build. A fixed filename such as `app.js` can remain cached at the edge even when cache-busting only the HTML URL.

Prefer content-hashed assets. For a minimal vanilla build, rename the changed bundle deterministically and update the HTML reference, then verify the public HTML names that new file before rerunning E2E.

## Browser E2E readiness signals

Do not wait merely for a control that was visible before an asynchronous mutation. Wait for the state that proves refresh completion, such as the newly created workspace option being attached to the DOM.

Native `<option>` elements are commonly classified as hidden by Playwright. Use:

```js
await select.locator('option', { hasText: expected }).waitFor({ state: 'attached' });
```

not the default visible-state wait.

Log failed response URLs and console-message locations before changing product code. A generic console 404 may be a root `/favicon.ico`, not an application API failure. For subpath apps, an inline data-URL favicon avoids an unintended root request.

## Final gate

1. Run tests and build after the final edit.
2. Restart the exact systemd unit.
3. Poll the prefixed local route.
4. Confirm public HTML references the final asset.
5. Run authenticated public browser E2E through the exact HTTPS prefix.
6. Require clean page errors, unexpected failed responses, console errors, persistence after reload, workspace isolation, and mobile overflow checks.
