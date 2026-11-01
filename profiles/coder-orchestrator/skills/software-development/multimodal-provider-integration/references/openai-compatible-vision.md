# OpenAI-compatible vision reference

## Canonical request

```json
{
  "model": "verified-vision-route",
  "stream": false,
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "Return only {\"items\":[...]} using the required schema. File 0 is named menu.png."},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
    ]
  }]
}
```

Expected envelope:

```json
{"choices":[{"message":{"content":"{\"items\":[...]}"}}]}
```

Some compatible routers return `text/event-stream` even when `stream:false`; parse `data:` JSON records and ignore the terminal `data: [DONE]`.

## Minimal diagnostic sequence

1. Send the application's current payload and retain status plus a bounded, secret-free response excerpt.
2. Send the canonical multimodal request to the gateway endpoint.
3. Send the same request directly to the configured inference router from the server host.
4. Use an image with unmistakable known text; do not use a blank 1×1 pixel as a vision proof.
5. Compare the requested model, response model, and actual extracted text. If direct routing sees the image while the gateway says it cannot, inspect agent image routing and model-route configuration rather than changing OCR prompts.

## Structured extraction checks

- file count, per-file bytes, aggregate bytes
- declared MIME and magic bytes
- data URL construction
- source index and supplied filename
- allowed object keys only
- required strings and maximum lengths
- positive integer currency/amount fields
- bounded warnings arrays
- no persistence before explicit user confirmation

## Security

Never print or return provider keys. Compare credentials with hashes or lengths when diagnosing. Add authorization only in the backend request; assert the secret does not occur in the serialized body.