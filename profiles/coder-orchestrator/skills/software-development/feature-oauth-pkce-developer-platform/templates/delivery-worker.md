# Delivery worker

Select a bounded due batch and close rows. Conditionally claim one delivery. Perform HTTP outside transactions with timeout and exact raw bytes. Record status/body excerpt safely. Success => delivered. Retryable network/408/429/5xx => exponential backoff with cap. Other errors or attempt ceiling => dead. Replay creates an audited new pending delivery; it does not erase history.
