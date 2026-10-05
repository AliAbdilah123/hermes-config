# Receipt ingestion

Apply auth, business scope, CSRF, multipart byte ceiling, MIME allowlist and magic-byte detection. Store generated server filename; invoke parser with timeout outside transactions; persist result/error. Frontend assigns each request an identity and ignores results not matching the current upload. Parsed merchant/date/line items are editable draft data; user confirmation creates the expense.
