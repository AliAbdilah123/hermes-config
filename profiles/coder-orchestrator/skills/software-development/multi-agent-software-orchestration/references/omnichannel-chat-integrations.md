# Omnichannel Chat Integration Notes

Use this reference when drafting PRDs/API contracts for omnichannel inbox or customer-chat products.

## Key lesson from session
- Do not assume WhatsApp Business Cloud API is the desired MVP path.
- If the user asks for WhatsApp support, explicitly ask whether they want:
  - official WhatsApp Business Cloud API, or
  - Baileys / QR-session based WhatsApp integration for a faster MVP.
- If the user specifies Baileys, reflect it directly in the PRD/API contract instead of framing official APIs as non-negotiable.

## Baileys-oriented MVP architecture
- Keep the main app stack unchanged unless the user approves a change.
- For the default stack, use React + TypeScript frontend, Go HTTP API, SQLite.
- Add a separate WhatsApp adapter/worker boundary for Baileys if needed, because Baileys is Node-oriented.
- Model WhatsApp as `provider = whatsapp_baileys` so it remains replaceable later.
- Store connection/session state separately from OAuth token-based providers.
- Support QR/session lifecycle APIs:
  - `POST /api/v1/channels/whatsapp-baileys/session/start`
  - `GET /api/v1/channels/whatsapp-baileys/session/{id}`
- Add an internal event sink from the Baileys worker to the Go API:
  - `POST /api/v1/webhooks/whatsapp-baileys/internal`

## PRD risk language
Baileys is useful for fast MVPs but unofficial and subject to breakage if WhatsApp changes behavior. Phrase this as an engineering risk with an adapter-isolation mitigation, not as a refusal.

Recommended wording:
> WhatsApp MVP uses Baileys QR/session connection for speed. It is isolated behind a provider adapter so the system can later migrate to WhatsApp Business Cloud API without rewriting the inbox model.

## Pitfall
When the user says “from scratch” and “don’t use existing projects,” that does not necessarily mean “official APIs only.” It may mean “do not clone or depend on broken omnichannel platforms.” Clarify integration strategy before locking the PRD.