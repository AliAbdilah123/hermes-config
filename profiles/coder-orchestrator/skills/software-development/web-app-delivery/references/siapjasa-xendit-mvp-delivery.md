# SiapJasa Xendit MVP delivery notes

Use this as a compact reference for similar local marketplace MVPs on the house stack.

## Spec correction after PRD approval

When the user approves a PRD but changes one provider (e.g. Midtrans → Xendit) and says “go ahead”:
1. Patch the published PRD/API artifact in place.
2. Verify the PRD URL still returns 200.
3. Continue implementation without asking for another broad approval.

## Xendit-first escrow prototype shape

For a working MVP without live payment credentials:
- Keep API routes provider-specific enough to avoid stale copy: `/webhooks/xendit`, `xendit_invoice_id`, `xendit_payment_token`.
- Use a mock payment endpoint such as `POST /jobs/{id}/pay/mock` that transitions escrow from `pending_payment` to `held` and records metadata `{gateway:"xendit"}`.
- Preserve immutable transaction snapshots: customer price, platform fee pct/idr, provider payout.
- Keep the real webhook handler idempotent and map Xendit statuses onto internal escrow states.

## Go toolchain fix on hosts with older local Go

If `go test` tries to download an unavailable toolchain because `go.mod` asks for a newer Go version, do not rewrite the stack. Pin `go.mod` to the installed local Go version when compatible and run with:

```bash
GOTOOLCHAIN=local gofmt -w ./cmd/server
GOTOOLCHAIN=local go test ./...
GOTOOLCHAIN=local go build -o bin/<app> ./cmd/server
```

## Visual smoke fallback

If the browser automation tool times out, use CLI Chromium to capture the served page:

```bash
/usr/bin/chromium-browser --headless --no-sandbox --disable-gpu \
  --virtual-time-budget=5000 \
  --screenshot=/tmp/<project>-smoke.png \
  http://127.0.0.1/projects/<project>/
```

Snap Chromium may print DBus/AppArmor warnings even when it succeeds. Check that the screenshot file exists and is non-empty, then inspect it with vision before reporting visual verification.
