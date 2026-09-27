# SIMPLEE SOVEREIGN CLOUD — SC005B DURABLE BACKUP INTENT + RECONCILIATION

Date: September 27, 2026. Separate source-only branch stacked on draft Cloud SC001 after SC004B. Production **NO_GO**.

## Failure this closes

The original SC001 IndependentBackupService source helper generates an opaque backup object reference just before PUT. If a provider commits the SCB1 bytes but loses the ACK, the caller gets an exception and has no returned reference. Blind retry risks creating another ciphertext at a new path, leaving an orphan. That original helper remains for earlier source tests and isolated verification, but it MUST NOT be wired as a direct operational backup entrypoint.

SC005B introduces JournaledBackupOperations. Its backup path is now used by the SC004B SourceOnlyBoundCloudPort. This makes the backup source-operation shape parallel to the SC002 journaled primary object path, while preserving Vault as canonical backup/receipt/retention owner.

## Source-only design

- Extend the existing single append-only operational SQLite journal with immutable backup_intents holding opaque namespace, original request, source ref/digest, generated backup ref, independent SCB1 SHA/size and non-secret key reference. BACKUP_RESERVED is durably inserted in the same transaction as its event. All backup events contribute to the SC005 signed journal prefix checkpoints.
- The primary VLT1 hash/size is checked before creating the independent 32-byte-key SCB1 encrypted outer envelope, with existing AAD binding entity namespace, original object and original digest.
- Once BACKUP_RESERVED commits, attempt exactly one create-only physical backup PUT. Success requires a durable BACKUP_ACKNOWLEDGED before internal receipt is returned. Ambiguous provider errors record BACKUP_UNCERTAIN; an ACK-journal failure leaves BACKUP_RESERVED. No error means nothing about a remote write having or not having occurred.
- A fresh signed Tower-shaped BACKUP_CIPHERTEXT grant may replay the same logical request only if its original durable backup reservation is acknowledged/physically verified; it returns the same internal BackupReceipt. An unresolved/terminal state never repeats PUT. A mismatched original source ref/digest or key reference conflicts rather than silently forking the archive.
- A new signed operation RECONCILE_BACKUP binds the ORIGINAL logical backup request ID, source ref/digest, entity, purpose, classification, current approval/step-up and a FRESH one-use nonce. No caller-provided backup ref is accepted. Cloud retrieves the generated ref from its own existing journal and checks actual backup bytes against the canonical reserved SCB1 SHA/size.
- PRESENT returns a **storage-only backup receipt** and explicit vault_backup_committed=False; MISSING/CORRUPT are durable hold + incident. A provider read outage leaves the operation unresolved. If a previously acknowledged backup is later corrupted/missing, replay records BACKUP_REPLAY_INTEGRITY_FAILURE and denies.
- The separate backup key, independent backend, original Vault AES-GCM authentication and true independent failure domain remain separately gated. Source tests use local/fake backends; never claim full DR, immutable hardware or Vault recovery commit.
- Only count/health metadata is exposed, with NO_GO status. The journal is not independently anchored/WORM until the externally operated SC005 checkpoint/key/sink is certified.

## Required Tower and Vault adoption

Tower must explicitly review/issue the additional RECONCILE_BACKUP operation with current decision, approval and step-up state; the SC004B source grant is not a real signer or authenticated peer. Vault must maintain its original logical backup request ID, independently resolve canonical source ref/hash and only commit a Vault backup/canonical archival receipt after its own transaction and evidence. No direct application, browser or executive Clouds body access.

## Real-world gates (still open)

Actual private transport and issuer/receiver in issue #99, provider versioning/Object Lock and true conditional write behavior, offsite independent credentials/domain, key custody/rotation/loss recovery, signed independently retained journal checkpoint, malware/original-auth Vault validation, measured RPO/RTO and owner-approved funding/provider/release.

No provider, external account, paid resource, production credential, route or user document is added by this pack.
