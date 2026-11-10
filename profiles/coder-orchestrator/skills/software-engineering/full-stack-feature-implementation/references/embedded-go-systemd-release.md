# Embedded Go web assets under systemd

Use this release sequence when a Go service embeds HTML, CSS, or JavaScript:

1. Read `systemctl cat <service>` and rebuild the exact binary named by `ExecStart`; restarting alone does not deploy source edits.
2. Read the service/running-process environment for the actual listen address. Do not probe a remembered or default port.
3. Restart and verify the focused API on that real local address.
4. Verify the same API publicly.
5. Confirm public HTML references the new asset generation and public JS/CSS contain feature-specific markers.
6. Exercise the changed browser interaction; an app-root HTTP 200 is insufficient.
7. Rename/version embedded JS and CSS together to prevent cached HTML from mixing asset generations.

This captures the durable release pattern, not any one service name, port, or binary path.