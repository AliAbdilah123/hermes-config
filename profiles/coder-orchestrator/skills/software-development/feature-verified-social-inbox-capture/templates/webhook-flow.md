# Webhook flow

Read a bounded raw body. Verify provider signature before JSON parsing. Resolve the configured integration and verified identity. In one transaction insert the unique provider receipt and user-owned record; duplicate receipt returns success without another record. Store provider media IDs/URLs only. Never fetch remote media in webhook processing. Keep webhook logs free of message text and tokens.
