# Business CRM Baileys QR Display

Use this reference when a business/CRM app integrates a Baileys WhatsApp worker and the UI must show the QR needed to pair a device.

## Durable lesson

Baileys emits a raw QR payload string on `connection.update`. That string is **not** directly usable as an `<img src>`. The worker/API boundary should convert it to a browser-renderable QR image, usually a PNG data URL, and expose both a boolean availability flag and the image source.

## Recommended worker contract

Worker state should track:

- `status`: `starting`, `qr_required`, `connected`, `disconnected`, `logged_out`, or `error`
- `connected`: boolean
- `phone`: connected WhatsApp account id when available
- `qrAvailable`: boolean
- `qr`: browser-renderable QR image source (`data:image/png;base64,...`) for backwards compatibility
- `qrDataUrl`: same data URL, explicit name for new clients
- `rawQr`: only on a dedicated `/qr` endpoint if needed for debugging
- `lastError`, `lastMessageAt`

When Baileys emits `qr`:

```js
import QRCode from 'qrcode';

async function setQr(rawQr) {
  const qrDataUrl = await QRCode.toDataURL(rawQr, { margin: 2, scale: 8 });
  state.rawQr = rawQr;
  state.qr = qrDataUrl;
  state.qrDataUrl = qrDataUrl;
  state.status = 'qr_required';
}
```

Expose `/status` with `qrAvailable`, `qr`, and `qrDataUrl`. Expose `/qr` with `rawQr` in addition to the image source if operators need it.

## Frontend pattern

Render `status.qrDataUrl || status.qr` as the image `src`; do not render the raw Baileys payload directly.

While disconnected, poll status every ~5 seconds until either `connected` or an error/logged-out state is reached. Keep a manual refresh button.

UX states:

- `qr_required` + QR data URL: show scannable QR image and “scan from WhatsApp linked devices.”
- `starting` or no QR yet: show “waiting for QR” placeholder.
- `connected`: hide QR and show connected account.
- worker not configured/unreachable: show honest `not_connected` / configuration state, not fake success.

## Backend proxy pattern

If the Go/API backend proxies the sidecar, pass through the worker JSON from `/status` without stripping the QR fields. Keep the app backend as the auth boundary: frontend calls `/api/v1/whatsapp/status`, backend calls `WHATSAPP_WORKER_URL/status`.

## Deployment checks

- Make the Baileys sidecar a supervised service, not an agent background process.
- Use a Node version compatible with the installed Baileys package.
- Persist auth/session files outside the repo, e.g. `/var/lib/<app>/whatsapp-auth`.
- Configure the backend with `WHATSAPP_WORKER_URL=http://127.0.0.1:<port>` and restart it.

## Verification checklist

1. `node --check src/index.js` or equivalent worker syntax check.
2. Unit/smoke check QR generation returns a `data:image/png;base64,` prefix.
3. Start worker with a fresh or logged-out session and verify `/status` returns `qrAvailable: true` and `qrDataUrl`.
4. Authenticate through the app backend and verify `/api/v1/whatsapp/status` preserves `qrDataUrl`.
5. Build frontend and verify the served bundle contains the QR rendering path.
6. If deployed, verify nginx serves the new frontend asset and the worker/backend services are active.
