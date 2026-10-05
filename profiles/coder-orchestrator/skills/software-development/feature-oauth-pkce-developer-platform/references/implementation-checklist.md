# Implementation checklist

Use cryptographically random client secrets, codes, and tokens; return plaintext only once and store hashes. Redirect URI comparison is exact. Authorization code issuance binds PKCE S256, app, user, redirect and scopes; exchange transactionally marks it consumed. Scope middleware checks every API. Signing secret rotation needs key identity/version. Webhook receiver validates timestamp skew before constant-time signature comparison. Delivery inspector masks sensitive payload fields and authorizes app ownership.
