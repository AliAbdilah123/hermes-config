# Routed-component and preview-service verification

## Verify the component that the public route actually renders

A repository can contain several visually similar card/list components. Editing and testing one does not prove the public route uses it.

Before implementation:

1. Trace the exact router entry for the requested URL.
2. Follow imports from the route element to the rendered card/list component.
3. Record the click handler in that component, including alternate modes such as `onSelect` that intentionally bypass navigation.
4. Add a focused test at the routed component boundary.

During public E2E:

- Query the rendered DOM for the expected link or clickable card.
- Click a real card from the exact route rather than opening the destination URL directly.
- Assert the resulting pathname.
- Separately verify alternate card modes still preserve their intended behavior.

If the expected element is absent while similar cards render, stop and trace the active component. Do not treat a matching string in the built bundle as proof that the route uses that implementation.

## Make preview runtime overrides unambiguous

A production-compatible `.env` reused through systemd may define `ADDR`, database paths, or public URLs that conflict with preview values. After starting the service, logs and the listening socket—not the unit source—are authoritative.

For high-risk isolation variables, make precedence explicit at process launch:

```ini
EnvironmentFile=/path/to/production-compatible.env
ExecStart=/usr/bin/env \
  ADDR=127.0.0.1:8138 \
  DATABASE_PATH=/path/to/isolated-preview.db \
  SQLITE_DB_PATH=/path/to/isolated-preview.db \
  KOMUNA_DB_PATH=/path/to/isolated-preview.db \
  /path/to/preview-api
```

Then verify:

1. `systemctl is-active <unit>` is `active`.
2. `ss -ltnp` shows the unique preview port.
3. Service logs state the preview port, not production's port.
4. The public preview API returns JSON through its specific proxy route.
5. A preview-only fixture is visible through the preview API and absent from production.

Do not continue to browser E2E while the service is restarting, bound to the production port, or returning 502.