# Unified AI request + agent run model

Use when planning or implementing general-purpose AI features with chat, agents, credits, and usage history.

## Durable pattern

Prefer one parent `ai_requests` table for all AI operations instead of separate request/run tables when the metadata overlaps.

- Chat: one `ai_requests` row with `request_type='chat'`.
- Agent: one `ai_requests` row with `request_type='agent'` and lifecycle `status` such as `queued`, `running`, `success`, `error`, `cancelled`.
- Shared parent fields: tenant/user/thread, provider/model, prompt/response or goal/final output, aggregate token usage, credits used, timestamps, error message.
- Tenant credit pool can coexist with per-user limits via a separate `ai_user_limits` table.

## Agent/tool-call detail

Do not overload the parent row with step detail. Add a child step/event table such as `ai_request_steps`:

- `request_id` references `ai_requests(id)`.
- `step_index` preserves ordering.
- `step_type` should distinguish at least: `thought`, `model_call`, `tool_call`, `tool_result`, `final`, `error`.
- Include `tool_name`, input/output payloads, input/output/cache token counts, credits used, error message, and timestamp.

This keeps usage/billing queries simple while preserving a full agent timeline for debugging and audit.

## Review-plan pitfall

If a plan proposes both `ai_requests` and `ai_agent_runs`, pause and ask whether the parent metadata truly differs. If not, merge them and use child steps for agent-specific work.