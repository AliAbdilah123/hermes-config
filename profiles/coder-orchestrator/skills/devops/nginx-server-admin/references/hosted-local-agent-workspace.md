# Hosting a local-first agent workspace behind nginx

Use this pattern for tools such as OpenDesign that normally bind to loopback, spawn coding agents, and edit imported server folders.

## Safe deployment sequence

1. Read the upstream repository's agent/operator instructions, especially its data-root contract.
2. Install the exact required runtime versions without replacing the host-wide runtime when avoidable. Build the production web surface using the upstream package manager.
3. Give the daemon one explicit persistent data root. Keep generated API credentials outside Git and make credential-bearing env files mode `600`.
4. Start daemon and web on separate unused loopback ports and verify both directly before adding nginx.
5. Import an existing project through the product's supported import command/API instead of copying it. Confirm the returned project ID and base directory.
6. Replace the development launcher with a systemd unit. If the upstream lifecycle command daemonizes child processes, a `Type=oneshot` unit with `RemainAfterExit=yes`, explicit `ExecStart`, and matching `ExecStop` can supervise the lifecycle command while its own status command verifies child health.
7. Reverse proxy only the web listener. Preserve WebSocket upgrade headers, disable proxy buffering for streaming, and use long read/send timeouts.
8. Put authentication at nginx before exposing the hostname. Agent workspaces can execute tools and access imported folders, so public unauthenticated access is unsafe even if the daemon itself binds only to loopback.
9. Verify at the origin and publicly through the CDN:
   - unauthenticated request is `401`;
   - authenticated request is `200` HTML;
   - referenced static assets load;
   - daemon health succeeds on loopback;
   - systemd is enabled and active after restart.

## Codex/OpenDesign-style MCP wiring

Do not blindly execute an install command printed by a development checkout: generated snippets may contain a different checkout path, Node path, data root, or sidecar socket. Inspect the local CLI's `mcp add --help`, then register the stdio server with absolute paths and the deployment's actual data root/daemon URL.

Verification must exercise the integration, not just list configuration: launch a cheap Codex probe that calls the MCP project-list tool and require the imported project name in its response.

## Credential handoff

Never paste generated passwords or API tokens into a group chat. Store them server-side with restrictive permissions; provide or rotate them only through an approved secure channel.
