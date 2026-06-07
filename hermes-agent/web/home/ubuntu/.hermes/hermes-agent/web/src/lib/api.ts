/* eslint-disable @typescript-eslint/no-explicit-any */

// The dashboard can be served either at the root of its host (e.g.
// https://kanban.tilos.com/) or under a URL prefix when reverse-proxied
// (e.g. https://mission-control.tilos.com/hermes/). The Python backend
// injects ``window.__HERMES_BASE_PATH__`` into index.html based on the
// incoming ``X-Forwarded-Prefix`` header so the SPA can address its own
// ``/api/...`` and ``/dashboard-plugins/...`` URLs correctly without a
// rebuild. Empty string means "served at root".
function readBasePath(): string {
  if (typeof window === 'undefined') return ''
  const raw = window.__HERMES_BASE_PATH__ ?? ''
  if (!raw) return ''
  const withLead = raw.startsWith('/') ? raw : `/${raw}`
  return withLead.replace(/\/+$/, '')
}

export const HERMES_BASE_PATH = readBasePath()
const BASE = HERMES_BASE_PATH

import type { DashboardTheme } from '@/themes/types'

// Ephemeral session token for protected endpoints.
// Injected into index.html by the server — never fetched via API.
declare global {
  interface Window {
    __HERMES_SESSION_TOKEN__?: string
    __HERMES_BASE_PATH__?: string
    /** Server-injected flag: ``true`` when the dashboard's OAuth gate is
     * engaged (public bind, no ``--insecure``). Toggles the SPA's
     * WS-upgrade path from legacy ``?token=`` to single-use ``?ticket=``
     * fetched via :func:`getWsTicket`. */
    __HERMES_AUTH_REQUIRED__?: boolean
  }
}
let _sessionToken: string | null = null
const SESSION_HEADER = 'X-Hermes-Session-Token'

function setSessionHeader(headers: Headers, token: string): void {
  if (!headers.has(SESSION_HEADER)) {
    headers.set(SESSION_HEADER, token)
  }
}

export async function fetchJSON<T>(
  url: string,
  init?: RequestInit,
  options?: FetchJSONOptions,
): Promise<T> {
  // Inject the session token into all /api/ requests.
  const headers = new Headers(init?.headers)
  const token = window.__HERMES_SESSION_TOKEN__
  if (token) {
    setSessionHeader(headers, token)
  }
  const res = await fetch(`${BASE}${url}`, {
    ...init,
    headers,
    // ``credentials: 'include'`` so the cookie-auth path (gated mode) works
    // for any fetch routed through here. Loopback mode is unaffected — the
    // server doesn't read cookies and the legacy session-token header is
    // already attached above.
    credentials: init?.credentials ?? 'include',
  })
  if (res.status === 401) {
    // Phase 6: the gated middleware emits a structured envelope so the
    // SPA can full-page-navigate to /login on session expiry. Parse it,
    // and only redirect on the known error codes — domain-level 401s
    // (e.g. "you don't have permission to read this monitor") bubble
    // up as regular errors so callers can handle them.
    let body: { error?: string; login_url?: string } = {}
    try {
      body = await res.clone().json()
    } catch {
      /* non-JSON 401 — let it fall through */
    }
    if (
      (body.error === 'unauthenticated' || body.error === 'session_expired') &&
      body.login_url
    ) {
      // Preserve where the user was so /auth/callback can land them back
      // after re-auth. The gate's login_url already carries a ``next=``
      // built from the request path, but the SPA may be deep inside a
      // SPA route the gate never saw — e.g. a hash route or a client-side
      // /sessions/<id> deep link. Save the current location as a
      // fallback the post-login handler can read.
      try {
        sessionStorage.setItem(
          'hermes.lastLocation',
          window.location.pathname + window.location.search,
        )
      } catch {
        /* SSR / privacy mode — ignore */
      }
      window.location.assign(body.login_url)
      // Never resolve — the page is about to unload.
      return new Promise<T>(() => {})
    }
    // Loopback mode: ``_SESSION_TOKEN`` rotates on every server restart
    // (``hermes update``, ``hermes gateway restart``, etc.). A tab kept
    // open across the restart holds the OLD token in
    // ``window.__HERMES_SESSION_TOKEN__`` from the previous HTML render,
    // so every fetch returns 401. The HTML is served ``Cache-Control:
    // no-store`` so a reload picks up the freshly-injected token. Trigger
    // that reload once on the first stale-token 401 — gated mode is
    // handled above, so reaching here in gated mode means a real
    // middleware failure that should not reload-loop.
    if (!window.__HERMES_AUTH_REQUIRED__ && !options?.allowUnauthorized) {
      let alreadyReloaded = false
      try {
        alreadyReloaded = sessionStorage.getItem('hermes.tokenReloadAttempted') === '1'
      } catch {
        /* SSR / privacy mode — fall through to throw */
      }
      if (!alreadyReloaded) {
        try {
          sessionStorage.setItem('hermes.tokenReloadAttempted', '1')
        } catch {
          /* SSR / privacy mode — best effort */
        }
        window.location.reload()
        return new Promise<T>(() => {})
      }
    }
  }
  if (res.ok) {
    // Clear the stale-token reload guard: a successful 2xx proves the
    // current ``window.__HERMES_SESSION_TOKEN__`` is valid, so the next
    // 401 — if any — should be allowed to trigger its own reload cycle.
    try {
      sessionStorage.removeItem('hermes.tokenReloadAttempted')
    } catch {
      /* SSR / privacy mode — ignore */
    }
  }
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json()
}

/** Encode a plugin registry key for URL paths (preserves `/` segment separators). */
function pluginPath(name: string): string {
  return name.split('/').map(encodeURIComponent).join('/')
}

async function getSessionToken(): Promise<string> {
  if (_sessionToken) return _sessionToken
  const injected = window.__HERMES_SESSION_TOKEN__
  if (injected) {
    _sessionToken = injected
    return _sessionToken
  }
  throw new Error('Session token not available — page must be served by the Hermes dashboard server')
}

/**
 * Fetch a single-use ticket for a WebSocket upgrade in gated mode.
 *
 * The dashboard's gated-mode WS auth (``hermes_cli.web_server._ws_auth_ok``)
 * rejects the legacy ``?token=<_SESSION_TOKEN>`` path and only accepts
 * ``?ticket=<minted>`` consumed against the in-memory ticket store. Browsers
 * can't set ``Authorization`` on a WS upgrade, so this round-trip via the
 * authenticated REST endpoint is the bridge from cookie auth to WS auth.
 *
 * Tickets are single-use and TTL=30s — every WS connect attempt must
 * fetch a fresh ticket.
 */
export async function getWsTicket(): Promise<{ ticket: string; ttl_seconds: number }> {
  const res = await fetch(`${BASE}/api/auth/ws-ticket`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) {
    throw new Error(`/api/auth/ws-ticket: HTTP ${res.status}`)
  }
  return res.json()
}

/**
 * Resolve the auth query-param pair (``[name, value]``) for a WebSocket
 * connect. In gated mode mints a fresh single-use ticket; in loopback
 * mode returns the injected session token.
 */
export async function buildWsAuthParam(): Promise<[string, string]> {
  if (window.__HERMES_AUTH_REQUIRED__) {
    const { ticket } = await getWsTicket()
    return ['ticket', ticket]
  }
  const token = window.__HERMES_SESSION_TOKEN__ ?? ''
  return ['token', token]
}

export const api = {
  getStatus: () => fetchJSON<StatusResponse>('/api/status'),
  /**
   * Identity probe for the dashboard auth gate (Phase 7).
   *
   * Returns the verified Session as JSON when gated mode is active and a
   * valid cookie is attached. Loopback mode is unaffected — the endpoint
   * still exists but is never useful there (no Session, no cookie). The
   * AuthWidget component swallows 401s from this call: if the gate isn't
   * engaged, /api/auth/me returns 401 and the widget renders nothing.
   *
   * ``allowUnauthorized`` is load-bearing: in loopback mode this endpoint
   * 401s by design, and fetchJSON's default loopback behaviour treats a
   * 401 as a rotated session token and full-page-reloads to pick up a
   * fresh one. Because every *other* dashboard request succeeds (and so
   * clears the one-shot reload guard), that turns this expected 401 into
   * an infinite reload loop. Opting out keeps the 401 a plain throw the
   * widget can catch.
   */
  getAuthMe: () =>
    fetchJSON<AuthMeResponse>('/api/auth/me', undefined, {
      allowUnauthorized: true,
    }),
  logout: () =>
    fetch(`${BASE}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    }).then((r) => {
      // /auth/logout returns 302 → /login. Follow that with a full-page
      // navigation rather than letting fetch() opaquely consume the
      // redirect — the SPA needs to leave the protected area.
      window.location.assign('/login')
      return r
    }),

  // MCP
  getMcpServers: () =>
    fetchJSON<{ ok: boolean; servers: McpServer[] }>('/api/mcp/servers'),
  addMcpServer: (body: McpServerCreate) =>
    fetchJSON<{ ok: boolean; server: McpServer }>('/api/mcp/servers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  testMcpServer: (id: string) =>
    fetchJSON<McpTestResult>(`/api/mcp/servers/${encodeURIComponent(id)}/test`, {
      method: 'POST',
    }),
  removeMcpServer: (id: string) =>
    fetchJSON<{ ok: boolean }>(
      `/api/mcp/servers/${encodeURIComponent(id)}`,
      { method: 'DELETE' },
    ),

  // Pairing
  getPairing: () =>
    fetchJSON<PairingResponse>('/api/pairing'),
  approvePairing: (platform: string, code: string) =>
    fetchJSON<{ ok: boolean }>('/api/pairing/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform, code }),
    }),
  clearPendingPairing: () =>
    fetchJSON<{ ok: boolean; cleared: number }>('/api/pairing/clear', {
      method: 'POST',
    }),
  revokePairing: (platform: string, user_id: string) =>
    fetchJSON<{ ok: boolean }>('/api/pairing/revoke', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform, user_id }),
    }),

  // System / ops
  getMemory: () => fetchJSON<MemoryStatus>('/api/system/memory'),
  getCredentialPool: () =>
    fetchJSON<CredentialPoolProvider[]>('/api/system/credentials'),
  getCheckpoints: () =>
    fetchJSON<CheckpointsResponse>('/api/system/checkpoints'),
  getHooks: () => fetchJSON<HooksResponse>('/api/system/hooks'),
  startGateway: () =>
    fetchJSON<{ ok: boolean }>('/api/gateway/start', { method: 'POST' }),
  stopGateway: () =>
    fetchJSON<{ ok: boolean }>('/api/gateway/stop', { method: 'POST' }),
  setMemoryProvider: (name: string) =>
    fetchJSON<{ ok: boolean }>('/api/system/memory', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: name }),
    }),
  resetMemory: () =>
    fetchJSON<{ ok: boolean }>('/api/system/memory/reset', { method: 'POST' }),
  addCredentialPoolEntry: (provider_id: string) =>
    fetchJSON<{ ok: boolean }>('/api/system/credentials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider_id }),
    }),
  removeCredentialPoolEntry: (entry_id: string) =>
    fetchJSON<{ ok: boolean }>(
      `/api/system/credentials/${encodeURIComponent(entry_id)}`,
      { method: 'DELETE' },
    ),
  pruneCheckpoints: (keep: number) =>
    fetchJSON<{ ok: boolean }>(
      `/api/system/checkpoints/prune?keep=${encodeURIComponent(String(keep))}`,
      { method: 'POST' },
    ),
  runDoctor: () =>
    fetchJSON<{ ok: boolean; output?: string }>('/api/system/doctor', {
      method: 'POST',
    }),
  runSecurityAudit: () =>
    fetchJSON<{ ok: boolean; output?: string }>('/api/system/security-audit', {
      method: 'POST',
    }),
  runBackup: () =>
    fetchJSON<{ ok: boolean; output?: string }>('/api/system/backup', {
      method: 'POST',
    }),
  updateSkillsFromHub: () =>
    fetchJSON<{ ok: boolean; output?: string }>(
      '/api/system/skills/update',
      { method: 'POST' },
    ),
  runImport: (file: File) => {
    const form = new FormData()
    form.set('file', file)
    return fetchJSON<{ ok: boolean; output?: string }>('/api/system/import', {
      method: 'POST',
      body: form,
    })
  },

  // Webhooks
  getWebhooks: () =>
    fetchJSON<WebhooksResponse>('/api/webhooks'),
  createWebhook: (body: {
    path: string
    method?: string
    target: string
    enabled?: boolean
  }) =>
    fetchJSON<{ ok: boolean; route: WebhookRoute }>('/api/webhooks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  deleteWebhook: (id: string) =>
    fetchJSON<{ ok: boolean }>(
      `/api/webhooks/${encodeURIComponent(id)}`,
      { method: 'DELETE' },
    ),

  getSessions: (limit = 20, offset = 0) =>
    fetchJSON<PaginatedSessions>(`/api/sessions?limit=${limit}&offset=${offset}`),