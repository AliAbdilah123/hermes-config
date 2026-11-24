# Indonesia: payments, compliance, and the design-system numbers

Condensed knowledge bank, verified 23 Nov 2026. Re-verify anything price- or policy-shaped before quoting it as current. Sources are named inline so any line can be re-checked.

## Payment gateway fees (Midtrans, official `/id/biaya` page)

Excl. PPN. Gaming & digital-goods merchants get different rates across the board.

| Method | Fee |
|---|---|
| Virtual Account (BCA/BNI/Mandiri/Permata/BRI/CIMB/Danamon/BSI/SeaBank/Saqu) | IDR 4,000 / txn (flat) |
| QRIS | 0.7% |
| GoPay | 2% |
| ShopeePay | 2% |
| DANA | 1.5% |
| OVO | 1.5% |
| Credit card | 2.9% + IDR 2,000 |
| Minimarket (Indomaret/Alfamart/Alfamidi/DAN+DAN) | IDR 5,000 |
| Akulaku PayLater | 1.7% |
| Kredivo | 2% |
| Payout | IDR 5,000 to bank / IDR 2,500 to e-wallet *(EN page says 2,500 to all banks — pages conflict, confirm in dashboard)* |

**The design insight that matters more than the table:** a flat IDR 4,000 VA fee is 40% of a IDR 10,000 ticket and 0.4% of a IDR 1,000,000 ticket. Method choice is a UX decision *and* a unit-economics decision — don't render all 25 methods for every cart.

## Xendit fee *structure* (from `docs.xendit.co/docs/transaction-fees.md`)

Per-method numbers are behind a Cloudflare-walled pricing page — take those from the merchant dashboard.

- **Minimum monthly fee USD 50.** Billed as the difference when accrued fees fall short. No billable activity → no invoice. A real fixed cost for pre-revenue products.
- **Card fees charged on every attempt, succeed or fail.** Local methods (VA, e-wallet, QRIS, retail, direct debit) only on success. Makes card retry logic financially different from local retry logic.
- **Refund fee is retained** on the original payment *and* each refund is charged its own processing fee → one refund costs ~2× a fee.
- **Chargeback fee** non-refundable regardless of outcome.
- Payout coverage spans ID/PH/MY/TH/VN/SG/AU/CN/SEPA/HK/MX/KR/UK/US — the reason to pick Xendit is multi-country payout, not Indonesian card rates.

**Practical split:** Midtrans for single-country low volume (no monthly minimum). Xendit when multi-country payout is the actual requirement.

## Domestic payment rails

- **BI-FAST** — real-time interbank transfer, ~IDR 2,500 to the customer per transfer (confirmed on BCA.co.id, Mandiri/Livin, BTN coverage in Kompas/CNBC/detikFinance). Makes "plain bank transfer" expensive per transaction vs a VA.
- **QRIS** — MDR 0.7% baseline. BI expanded **0% MDR for UMKM effective 1 Oct 2026**, but headlines conflict on the cap (**IDR 100,000** vs **IDR 500,000** per transaction) and bi.go.id was unreachable for primary confirmation. Do not put a number in a pricing model until the PBI/EDWM is read directly.
- **VA** — unique number per invoice, so reconciliation is 1:1. This is why VA dominates Indonesia despite worse UX (user must open their banking app).

## Compliance

- **PSE registration** — `pse.komdigi.go.id`, filed through OSS. Legal basis PP 71/2019 + Permenkominfo 5/2020. Applies to **foreign operators serving Indonesian users too** — "my server is in Singapore" is not an exemption. Step one for any platform with users, not step last.
- **UU PDP (UU 27/2022)** — administrative sanction up to **2% of annual revenue**; criminal exposure up to **6 years** and/or **IDR 6 billion** for unlawful personal-data collection (BSSN statement, echoed by CNBC Indonesia / Bisnis Tekno / Harian Jogja). Breach-notification duty. The 2-year transition ended Oct 2024, so it is live.
- **Data localization is narrower than people think.** PP 71/2019 governs placement of data centers and DR centers with a preference for Indonesian territory for specified (public-service) systems — not a blanket "all data must stay in Indonesia". Cross-border personal-data transfer under UU PDP is permitted with an adequate-protection finding, binding safeguards, or data-subject consent. Field practice: keep **PII** in-country, put the rest where it's cheapest. Read PP 71/2019 Art. 21 and UU 27/2022 Art. 55–57 directly before an architecture decision.
- **Supervisory body (LPDB)** was still being constituted as of 2026 — real regulatory uncertainty, and "no supervisor yet" is not "no risk".
- Payment gateways require an Indonesian legal entity (PT/CV) plus business documents. This, not pricing, is usually the real blocker that pushes people toward Stripe — which then loses on local-method coverage (QRIS/VA/e-wallet), i.e. conversion.

## Infrastructure

- AWS APAC region codes: Jakarta `ap-southeast-3` (only Indonesian region), Singapore `ap-southeast-1`, Malaysia `ap-southeast-5`, Thailand `ap-southeast-7`.
- Jakarta↔Singapore RTT is roughly high-teens to ~30 ms. One request: invisible. Fifty sequential queries: over a second. **The lever is round-trip count, not region.**
- Jakarta list prices tend to run above Singapore/us-east for equivalent instances; cross-region egress is the bigger and less-modelled cost.
- Real ordering of "why is it slow": unindexed query → uncompressed images → N+1 queries → JS bundle → *then* server location. Measure with `mtr` / `curl -w "%{time_total}"` / RUM before touching regions.

## Design-system reference numbers (W3C + vendor, stable facts)

- Contrast: 4.5:1 normal text, 3:1 large text (≥24px, or ≥18.66px bold) — WCAG 2.2 SC 1.4.3.
- Target size: **24×24 CSS px** minimum (SC 2.5.8, new in 2.2); practice 44×44 (Apple HIG) / 48×48 (Material).
- Focus indicator must be visible — SC 2.4.11.
- Core Web Vitals: LCP < 2.5 s, INP < 200 ms (replaced FID Mar 2024), CLS < 0.1.
- Spacing on a 4px scale; body text ≥16px on mobile or iOS Safari zooms inputs; line length 45–75 chars; motion 100–150 ms micro / 200–300 ms panel, respect `prefers-reduced-motion`.
- Six states every component needs: default, hover/focus-visible, active, disabled (with a visible reason), loading (skeleton), error/empty/success.
- Figma pricing Nov 2026, USD/seat/mo: Professional $16 full / $12 dev / $3 collab (monthly); Organization $55/$25/$5 (annual); Enterprise $90/$35/$5 (annual). Paid plans allow view+comment without buying a seat. Open-source alternative with native DTCG tokens: Penpot.

## Payment system-design checklist (reusable for any feature review)

1. If this request is sent twice, what happens? (idempotency key)
2. If the DB dies for 30 s mid-flow, what is lost?
3. If the webhook never arrives, how does the status resolve? (reconciliation job)
4. If the user refreshes mid-flow, where do they land?
5. What happens at 100× the current volume?
6. Who can see this data, and how is that proven?
7. If the numbers don't match, how is the cause traced? (double-entry ledger, not `UPDATE balance`)
8. What single metric tells you this feature is healthy?

Also non-negotiable in payment flows: never store balance as a mutable number (sum the ledger entries); model status as a constrained state machine (pending → authorized → paid → settled → refunded, with voided/expired/chargeback branches); treat webhooks as unreliable by default (verify signature, persist raw event, idempotent handler, retry + DLQ, and never as the sole source of truth); daily 3-way reconciliation between ledger, gateway settlement report, and bank statement.
