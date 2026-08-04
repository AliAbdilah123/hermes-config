# Systemd preview environment precedence

When an application loads `.env` only for variables that are currently unset, a preview service can unexpectedly retain production values from `EnvironmentFile=` instead of intended preview overrides.

## Safe verification and fix

1. Start the preview service and inspect its startup log for the actual bind address.
2. Verify the unique preview socket is listening; do not trust `systemctl active` alone.
3. Call the local and public preview API and confirm JSON, then verify writes/read fixtures use the isolated preview database.
4. If intended overrides are ignored, make preview-critical values explicit at process launch:

```ini
ExecStart=/usr/bin/env ADDR=127.0.0.1:8138 DATABASE_PATH=/path/to/preview.db /path/to/api
```

5. Reload systemd, restart, and recheck logs, socket, API, and database isolation.

## Related E2E pitfall

Trace the actual routed component before declaring navigation complete. Similar-looking session cards can exist on program detail and program-wide Sessions pages. Browser-click the exact public card and assert the resulting pathname; component tests for only one card variant are insufficient.
