const KEY = "checkout-attempt";

type Attempt = { intent: string; key: string };

function fallbackKey() {
  // Deduplication only; never use this fallback for authentication or secrets.
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export function checkoutKey(intent: unknown): string {
  const canonical = JSON.stringify(intent);
  const saved = JSON.parse(sessionStorage.getItem(KEY) || "null") as Attempt | null;
  if (saved?.intent === canonical) return saved.key;
  const key = globalThis.crypto?.randomUUID?.() ?? fallbackKey();
  sessionStorage.setItem(KEY, JSON.stringify({ intent: canonical, key }));
  return key;
}

export function clearCheckoutKey() {
  sessionStorage.removeItem(KEY);
}

export function assertXenditInvoiceURL(raw: string): string {
  const url = new URL(raw);
  if (url.protocol !== "https:" || !(url.hostname === "xendit.co" || url.hostname.endsWith(".xendit.co"))) {
    throw new Error("Unexpected payment URL");
  }
  return url.href;
}
