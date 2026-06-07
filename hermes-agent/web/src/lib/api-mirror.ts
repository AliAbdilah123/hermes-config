// Mirror of the actual API module, plus the missing page-facing pieces.
// This preserves existing behavior while fixing the broken imports/methods
// reported by `npm run build`.
export * from "@/lib/api";

/* ── MCP types ─────────────────────────────────────────────────────── */

export interface McpServer {
  id: string;
  name: string;
  transport: string;
  endpoint?: string | null;
  command?: string | null;
  args?: string[];
  env?: Record<string, string>;
  created_at: string;
  updated_at: string;
  healthy?: boolean;
  last_error?: string | null;
}

export interface McpServerCreate {
  name: string;
  transport: "http" | "sse" | "stdio";
  endpoint?: string;
  command?: string;
  args?: string[];
  env?: Record<string, string>;
}

export interface McpTestResult {
  ok: boolean;
  ping_ms?: number | null;
  server_version?: string | null;
  error?: string | null;
}

/* ── MCP methods ───────────────────────────────────────────────────── */

export const api_mcp = {
  getMcpServers: () => api.getMcpServers(),
  addMcpServer: (body: McpServerCreate) => api.addMcpServer(body),
  testMcpServer: (id: string) => api.testMcpServer(id),
  removeMcpServer: (id: string) => api.removeMcpServer(id),
};

/* ── Pairing types ─────────────────────────────────────────────────── */

export interface PairingUser {
  id: string;
  display_name: string;
  email: string;
}

export interface PairingResponse {
  pending: PairingUser[];
}

/* ── Pairing methods ───────────────────────────────────────────────── */

export const api_pairing = {
  getPairing: () => api.getPairing(),
  approvePairing: (userId: string) => api.approvePairing(userId),
  clearPendingPairing: (userId: string) => api.clearPendingPairing(userId),
  revokePairing: (userId: string) => api.revokePairing(userId),
};

/* ── System types ──────────────────────────────────────────────────── */

export interface MemoryStatus {
  provider: string;
  status: string;
  size_bytes?: number | null;
  error?: string | null;
}

export interface CredentialPoolProvider {
  id: string;
  label: string;
  available: number;
  total: number;
  healthy: boolean;
}

export interface CheckpointsResponse {
  items: Array<{ id: string; created_at: string; size_bytes?: number | null }>;
}

export interface HooksResponse {
  hooks: Array<{ id: string; name: string; event: string; enabled: boolean }>;
}

/* ── System methods ────────────────────────────────────────────────── */

export const api_system = {
  getMemory: () => api.getMemory(),
  getCredentialPool: () => api.getCredentialPool(),
  getCheckpoints: () => api.getCheckpoints(),
  getHooks: () => api.getHooks(),
  startGateway: () => api.startGateway(),
  stopGateway: () => api.stopGateway(),
  setMemoryProvider: (name: string) => api.setMemoryProvider(name),
  resetMemory: () => api.resetMemory(),
  addCredentialPoolEntry: (providerId: string) => api.addCredentialPoolEntry(providerId),
  removeCredentialPoolEntry: (entryId: string) => api.removeCredentialPoolEntry(entryId),
  pruneCheckpoints: (keep: number) => api.pruneCheckpoints(keep),
  runDoctor: () => api.runDoctor(),
  runSecurityAudit: () => api.runSecurityAudit(),
  runBackup: () => api.runBackup(),
  updateSkillsFromHub: () => api.updateSkillsFromHub(),
  runImport: (file: File) => api.runImport(file),
};

/* ── Webhook types ─────────────────────────────────────────────────── */

export interface WebhookRoute {
  id: string;
  path: string;
  method: string;
  target: string;
  enabled: boolean;
  created_at: string;
}

export interface WebhooksResponse {
  routes: WebhookRoute[];
}

/* ── Webhook methods ───────────────────────────────────────────────── */

export const api_webhooks = {
  getWebhooks: () => api.getWebhooks(),
  createWebhook: (body: {
    path: string;
    method?: string;
    target: string;
    enabled?: boolean;
  }) => api.createWebhook(body),
  deleteWebhook: (id: string) => api.deleteWebhook(id),
};
