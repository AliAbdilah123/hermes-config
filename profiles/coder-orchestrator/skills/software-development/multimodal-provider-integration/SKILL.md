---
name: multimodal-provider-integration
description: Diagnose, implement, and verify server-side image extraction or vision workflows against OpenAI-compatible and Hermes-backed providers, including request contracts, real model routing, strict structured output, and public E2E.
---

# Multimodal Provider Integration

Use this skill when an application sends images to an AI provider for OCR, menu/receipt extraction, classification, or other structured vision work.

## Workflow

1. **Probe before coding.** Test the exact endpoint and application credential with a generated text-bearing image. Capability metadata is a hint, not proof: aliases may advertise vision while routing to a text-only backend.
2. **Confirm the wire contract.** OpenAI Chat Completions requires multimodal `messages[].content` parts with `text` and `image_url`; a custom `{prompt, images}` body is not interchangeable. Responses normally live in `choices[0].message.content`.
3. **Confirm effective routing.** A gateway may advertise a model alias but internally instantiate its profile default. A request `model` value may be cosmetic unless a model-route mapping exists. Verify which backend actually saw the pixels.
4. **Keep the server boundary.** Credentials remain backend-only. If an agent gateway cannot preserve native image parts, use a configured vision route or the same authenticated OpenAI-compatible inference router directly from the application server—never from the browser.
5. **Demand and validate structure.** Require JSON-only output, parse only deliberate envelope variants, then validate keys, types, lengths, ranges, item counts, and source indexes. Do not turn malformed prose into success.
6. **Supply non-pixel metadata.** Include original filenames and index mapping in the text prompt; the model cannot infer upload filenames from pixels.

## Robust response handling

Support only provider shapes observed in the integration: JSON chat completions, JSON embedded in message content, fenced JSON when explicitly tolerated, and SSE `data:` frames ending with `[DONE]`. Bound response size and timeout. Fail closed on empty output, unknown fields, fabricated defaults, or non-2xx status.

## Verification ladder

1. Unit-test request shape, bearer isolation, timeout, provider errors, envelope parsing, and malformed structured output.
2. Run a live parser call with a generated image containing known labels/prices; assert exact values and source filenames.
3. Restart the service after environment changes and poll the health endpoint until it is listening—`systemctl is-active` alone does not prove readiness.
4. Build and deploy the actual artifact.
5. Run public baseline E2E, then the real image workflow through upload → review → explicit save → reload/persistence.
6. If a broad UI suite has fixed-duration timeout failures, distinguish timeout-only failures from assertions and retain focused feature tests plus real public E2E; do not misreport the full suite as passing.

## Pitfalls

- Trusting `/v1/models` capability claims without a pixel-level probe.
- Assuming the requested model controls gateway routing.
- Parsing the response root when the JSON is assistant message content.
- Omitting source filenames from the prompt.
- Restarting without readiness polling.
- Calling a wrong E2E script name or relying on a stale default URL; inspect the project script and pass the actual public root explicitly.

See `references/openai-compatible-vision.md` for the canonical request and diagnostic probes.
