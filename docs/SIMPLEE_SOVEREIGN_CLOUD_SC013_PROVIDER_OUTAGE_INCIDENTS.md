# SIMPLEE SOVEREIGN CLOUD — SC013 BACKEND OUTAGE INCIDENTS

Date: September 28, 2026. Source-only hardening on verified `vault-dev` baseline `848226834dd24343c4405fcb9b989b810b32ad02`. Production remains **NO_GO**.

## Problem

The journaled Cloud operations already fail closed on provider read failures. They distinguish confirmed absent or hash-mismatched ciphertext from a successful write/read. However, a backend outage in read, acknowledged replay, uncertain-write reconciliation or isolated backup verification often propagated without its own durable outage incident. That makes operational triage difficult: an unreachable object store should not be classified as a permanently missing or corrupt object, and silently absent incident telemetry should not be interpreted as a healthy read.

## What this source pack implements

- Adds a strict, allowlisted, opaque backend-error taxonomy for PRIMARY_READ, PRIMARY_REPLAY, PRIMARY_RECONCILE, BACKUP_SOURCE, BACKUP_REPLAY, BACKUP_RECONCILE, and BACKUP_VERIFY. Incidents are append-only, full-row hash-committed under SC007B, and contain **no exception text, body, raw entity name, credentials or provider endpoint**.
- For these source operations, exceptions other than explicit `ObjectMissing`/`IntegrityError` now record the matching backend incident and re-raise. Confirmed missing or corrupted ciphertext retains the existing distinct integrity/terminal-hold treatment.
- A temporary outage during replay of an ACKNOWLEDGED primary/backup preserves that ACK and does not transition to `REPLAY_INTEGRITY_FAILURE`. An outage during original-ID reconciliation preserves the `WRITE_RESERVED/WRITE_UNCERTAIN` or corresponding backup pending state, with **no automatic second PUT** and no Vault final archival/backup commit.
- A primary outage while creating an independent SCB1 backup produces no phantom backup reservation. A backup-provider outage in isolated recovery verification creates an incident but never returns successful recovery evidence.
- Only safe aggregate `backend_error_events` is added to Cloud journal/backup health. `provider_incident_delivery_certified` stays false; this is local source instrumentation, NOT a hosted alert/notification integration.

## Independent real-world gates remain open

The backend failure taxonomy cannot itself diagnose external outages accurately without a real provider/observability contract. Tower/Vault live issuer and private identity, trusted Vault canonical scope/original proof, actual provider error mapping, independent offsite audit/backup key custody, exercised real DR, owner alert delivery and approved RPO/RTO are still required. No client-side exception or fabricated `verified_by_tower` may authorize the operation.

The tests use synthetic inaccessible wrappers and assert that raw exception detail never lands in the SQLite incident/event rows. No paid resources, credentials, real documents, external provider, API route or production mode is created. The existing owner preflight stays SOURCE_ONLY_NO_GO.

## Acceptance

Run `python -m pytest -q simplee_cloud/tests/` in the scoped CI checkout. The new SC013 tests cover seven distinct storage/recovery backend-failure surfaces, preserved original intent states, no duplicate physical PUT, safe aggregate incident counts, and rejection of a false/unauthenticated Tower-shaped grant as a provider incident.
