# Static-site origin deployment

Use when replacing a placeholder response or publishing a dependency-free site directly through nginx.

1. Confirm the public hostname resolves to the intended origin and record the current response before changing it.
2. Copy the tested artifact into a dedicated web root. Exclude repository metadata and internal design/tooling state.
3. Normalize permissions after copying: directories `755`, static files `644`. Copy tools may preserve source mode `600`, which makes nginx return `403` even though the server block is correct.
4. Add the narrowest hostname-specific server block and run `nginx -t` before reload.
5. Verify server-block selection against loopback with the production Host header. Content assertions matter more than status alone.
6. Verify the public HTTPS URL separately, including expected page text and CSS/JS MIME types.
7. Render the public URL in a real browser at mobile and laptop widths. Assert expected DOM content and inspect browser stderr/console for runtime or network errors.

## Fast diagnosis

If reload succeeds but the content assertion fails:

- `403`: inspect web-root and file modes first (`755` directories, `644` files).
- Old placeholder content: inspect active server-block selection and duplicate `server_name` declarations.
- Public differs from loopback: inspect proxy/CDN routing and cache rather than rewriting the application.
- `200` with wrong UI: inspect body markers and asset MIME types; status alone is insufficient.
