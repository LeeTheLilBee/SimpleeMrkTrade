# SIMPLEE SOVEREIGN CLOUD — SC030 RESTORE ATTEMPT FINALITY

Date: September 28, 2026. Based on merged SC029 `vault-dev` commit `7c03b073cc234942c6eb154b47c8ccca9955d028`. Source-only; **production NO_GO**.

## Why this exists

SC029 binds a restore request to one exact Cloud-journal-acknowledged backup before provider access. A remaining lifecycle question was what happens after that bound restore attempt fails.

A missing/corrupt/authentication-failed backup is materially different from a temporary provider outage. Reusing the SAME logical restore request after someone repairs/replaces bytes would blur the audit history: one authorization would contain both an integrity failure and a later success. SC030 closes that ambiguity.

## Rules

For a bound restore request:

- `BACKUP_INTEGRITY_FAILURE` permanently puts that logical restore request ID on HOLD.
- A later retry under the same restore request ID is denied **before backup provider GET**, even if physical bytes were repaired.
- A new restore request ID, with a fresh Tower-shaped grant and current canonical receipt, may verify the repaired/available exact backup. The old failed request remains intact in history.
- `BACKUP_VERIFY_BACKEND_ERROR` is treated as provider reachability uncertainty, not evidence of corruption. The same exact restore request may be retried after service returns, using a fresh one-time signed grant.
- Once `RESTORE_BOUND_VERIFIED` is recorded, that logical restore request is complete; a later attempt under the same request ID is denied before provider GET. A new verification action needs a new request ID.
- Historical verification rejects more than one bound-success event for one restore request and rejects any bound success whose timeline contains an earlier `BACKUP_INTEGRITY_FAILURE`.

`record_restore_verified()` independently rechecks the exact backup ACK, the absence of an integrity HOLD, absence of previous bound success and existence of the lower-level authenticated `restore_copy_verified` event before committing bound success.

## What remains retryable

Provider or network unavailability is deliberately retryable because lack of a GET response is not proof that bytes are missing or corrupt. The journal retains the redacted backend-error incident and the original exact restore reservation. A fresh grant can retry that same request when the provider becomes reachable.

## Source acceptance

Synthetic tests cover:

- corrupt backup → restore integrity incident → physical repair → same logical restore denied before provider → fresh restore request succeeds;
- missing backup behaves the same;
- provider outage → same logical request can later succeed;
- completed restore cannot re-read backup under the same request ID;
- journal API cannot append bound success after an integrity incident even if a fake low-level success event is injected;
- historical integrity-failure-then-forged-success is rejected;
- duplicate historical bound success is rejected;
- one failed restore ID does not poison a distinct newly authorized restore ID.

This is source state-machine evidence only. It does not certify real Vault backup receipt origin, live Tower identity, immutable/offsite provider behavior, key custody, physical failure-domain independence, external incident delivery, RPO/RTO or production recovery authority. No paid resources, user files, provider signup, network route, credential or release state are introduced.
