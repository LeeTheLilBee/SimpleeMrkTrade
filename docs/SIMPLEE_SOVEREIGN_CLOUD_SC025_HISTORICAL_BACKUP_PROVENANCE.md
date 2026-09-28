# SIMPLEE SOVEREIGN CLOUD — SC025 HISTORICAL BACKUP SOURCE PROVENANCE

Date: September 28, 2026. Based on merged SC024 `vault-dev` source at `657d225d6b66d08601f0d687a79dbcee083b2d8e`. Source-only. Production **NO_GO**.

## Why after SC024

SC024 requires an acknowledged matching primary before any NEW encrypted backup provider GET and rechecks atomically before creating its reservation. But read-only journal verification still accepted an existing, correctly self-hashed `BACKUP_RESERVED` row/event even if the historical backup's purported source primary had never been acknowledged **at the time the backup was reserved**. A later primary ACK could misleadingly make such an older record appear consistent in an ordinary current-state lookup.

SC025 extends the existing complete hash-chain/intent/incident audit verification. For every historical backup reservation, it requires an exact matching primary intent by namespace, original physical ref and ciphertext SHA, and inspects the most recent primary state event with a sequence number STRICTLY less than the backup reservation event. That actual prior state must be `WRITE_ACKNOWLEDGED` or `RECONCILE_PRESENT`. No primary, wrong ref/hash/entity, an earlier unresolved write, or a primary already in REPLAY_INTEGRITY_FAILURE at reservation time is a fail-closed integrity error. An ACK inserted *after* the backup does not retroactively authenticate it. Subsequent primary damage does not erase legitimate historical backup provenance.

This is a verification rule on the actual ordered, hash-bound local journal, not a new trusted timestamp, no permission to rewrite old rows, and not a replacement for SC024 first-time operations checks or canonical Vault backup receipts.

## Scope and acceptance

Synthetic adversarial tests construct deliberately self-consistent old-style reservation hashes and ordered event chains (not merely corrupt random bytes): orphan backup, backup before original primary ACK, backup after original primary integrity HOLD, wrong ref, wrong source SHA and cross-entity reservation. All deny on full journal verification, health, owner status and checkpoint prefix paths. Legitimate prior backups remain journal-valid after subsequent primary integrity failure, and multiple distinct backup destinations of one source remain permitted.

Older disposable source-test journals with such invalid historical provenance intentionally FAIL CLOSED. This is not a silent migration or a claim that no attacker can rewrite an entire local DB; the independently operated, offsite signed joint storage/replay checkpoint, immutable custody and actual latest-tip proof are still mandatory.

No new CI workflow is added. Existing consolidated synthetic Vault/Cloud test gate is authoritative for this PR. Tower's actual signer/private peer, Vault's scan/canonical receipt, an independently approved provider, separate physical backup, tested key custody, RPO/RTO, alerts, real documents and production acceptance remain separately gated in issues #66 and #99. No paid infrastructure or live route is changed.
