# Frontend registries and optional metering

Plugin contributes owned route IDs/paths, navigation entries, providers and named slot renderers. Reject duplicate ownership and sort deterministically. Test capability-driven visibility.

Optional metering: transactionally decrement with `UPDATE balances SET amount=amount-? WHERE user_id=? AND amount>=?`; require one affected row; then insert run, step and usage ledger. Never seed credits during requests. Provider execution, pricing and payment-backed top-up need separate production contracts.
