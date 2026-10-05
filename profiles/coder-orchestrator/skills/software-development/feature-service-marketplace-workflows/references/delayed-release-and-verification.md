# Release and verification

Select/close due rows; conditionally claim pending/failed rows; call providers outside DB transaction; finalize idempotently and append event; back off retryable errors; startup runs recovery immediately. Tests cover every role/action/state, repeats, concurrent quota approval, proof requirement, dispute freeze, review uniqueness, release crash windows and provider-payment verification through `feature-xendit-payments`.
