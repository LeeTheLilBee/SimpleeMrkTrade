# SIMPLEE SOVEREIGN CLOUD — SC024 PRIMARY ACK BEFORE FIRST BACKUP

Date: September 28, 2026. Source-only change based on verified merged `vault-dev` SC023 commit `7e07b332bc32dc0a6a90212ae9c7f352e1d38e74`. **Production NO_GO.**

## Actual gap

The SC005B journaled backup workflow previously relied on encrypted source bytes passing an exact SHA-256 physical GET. If the primary provider accepted bytes but lost its original write ACK, or a physical object appeared outside Cloud's durable primary journal, a separate signed source-test BACKUP_CIPHERTEXT request could reserve and acknowledge an SCB1 backup anyway. Physical presence is not a durable write acknowledgement or Vault archival receipt.

## Defense, without discarding useful recovery

SC024 adds a read-only, fully chain-verified source preflight to `SQLiteOperationalJournal`: the exact tuple of **opaque namespace digest, primary object reference, ciphertext SHA-256** must belong to an actual primary intent currently in `WRITE_ACKNOWLEDGED` or `RECONCILE_PRESENT`. `JournaledBackupOperations.create()` invokes this before any first-time primary provider GET or backup PUT. The journal enforces the same rule again inside the `BEGIN IMMEDIATE` backup reservation transaction, closing a race if primary integrity enters HOLD after the initial check.

An ACK-lost original write must first complete an explicit fresh-authorized RECONCILE_WRITE with the **original logical request ID**; no blind re-PUT occurs. The backup can then proceed after journaled reconciliation, but neither its success nor Cloud's durable primary ACK can by itself mark Vault ARCHIVED or create Vault's canonical backup receipt.

Importantly, an already acknowledged backup can still be re-verified/replayed under its exact original backup request if its PRIMARY is subsequently flagged corrupt: retaining a verified backup is necessary to support future independent Vault recovery. The new rule applies to **first-time backup source acceptance**, not destruction or automatic rejection of an existing independent backup.

## Verification

Adversarial tests cover physical-but-untracked source bytes, a direct journal reservation attempt without primary lineage, a provider that accepted the source but lost ACK, successful original-ID reconciliation then backup without a second primary PUT, signed wrong source SHA, the same physical ref under another entity namespace, primary integrity HOLD, and a source state change between the preflight and the atomic backup reservation. Existing SC023 direct-journal test fixtures now establish their primary ACK before checking destination-ref collisions. The consolidated full Vault/Cloud source gate remains the only broad CI gate.

All Tower grants and Vault canonical lookup in these tests are synthetic; this does not establish actual mTLS/Tower key custody, a real original malware scan or canonical Vault ARCHIVED state, independent physical backup hardware, external alert delivery, provider Object Lock, RPO/RTO or production authority. No paid provider, live service route, real user files or signing credentials are introduced.
