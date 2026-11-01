# Chat request state and session-status debugging

Use when a chat drawer says “not connected,” sent messages appear unanswered, or long-running replies have no visible feedback.

## Diagnose before changing UI

1. Determine whether the initial status label is real health/session state or hardcoded copy.
2. Trace every assignment to it. Success-only updates conflate untouched draft, in-flight, and failed requests.
3. Trace submit end to end: user bubble → HTTP request → upstream timeout → response parsing → assistant bubble.
4. Inspect the upstream timeout. A long timeout without pending UI makes a healthy slow request look dead.
5. Check the persistence boundary. If conversation creation occurs only after upstream success, a failed first turn leaves no recoverable thread.
6. Check whether switching chat/project while active lets a late response render into the new view.

## Minimal state model

- **draft:** no session yet; say it starts on send, not “not connected.”
- **working:** assistant-style three-dot typing indicator, `role="status"`, screen-reader text, and duplicate-submit prevention.
- **connected/idle:** first turn succeeded or a persisted thread was restored.
- **failed:** replace pending UI with a concise inline error and Retry.

Preserve failed text and context. Retry through the same submit path without duplicating the user bubble. Use a request generation token or cancellation so late responses are ignored after New chat, project changes, or thread switches. Respect `prefers-reduced-motion`.

## Persistence and verification

Persist only real successful assistant output; never synthesize transcript content after failure. Explicitly decide whether failed user turns persist.

Verify draft wording, immediate pending feedback, success replacement, visible error + Retry, no duplicate bubble, no late-response misrouting, intended first-turn persistence, keyboard/screen-reader announcements, and reduced motion.
