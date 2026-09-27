# SIMPLEE SOVEREIGN CLOUD — SC002 DURABLE OPERATIONS CONTRACT

Date: 2026-09-27. Source-only stacked on SC001 draft PR #65.
Branch: simplee-cloud-sc002-durable-operations. NO_GO production.

## Boundary and outcomes

SC002 adds operational source components only under simplee_cloud/.
Existing executive clouds/, Archive Vault and Tower are unchanged. No hosted
service, live credentials, external storage, commercial provider, personal
documents, payment, or real administrative privileges are created.

Cloud never owns Vault's original AES-GCM encryption, document metadata,
classification, retention/legal holds or canonical archival receipts.
The existing VLT1 encrypted envelope remains Vault's output. Source-only
journaled Cloud storage emits INTERNAL STORAGE ACK ONLY.

## Durable operational records

- SQLiteOperationalJournal requires an explicit process-private journal directory
  and a 0600 regular database file, FULL synchronous mode and BEGIN IMMEDIATE.
- The immutable logical write-intent table reserves H(namespace, request_id)
  plus opaque internal object_ref, expected SHA-256 and ciphertext size.
- A fixed-schema append-only event chain records reservation, write ACK,
  uncertain write, reconciliation intent/results, read/backup events and
  incident creation without document bytes, raw entity ID or Tower credentials.
- SQL triggers reject UPDATE and DELETE of intent/event/incident rows. A
  SHA-256 chain verifies sequential event continuity before subsequent writes.
- This is NOT certified WORM storage or protection from a privileged host or
  SQLite administrator replacing the whole file/history. Signed external
  checkpoints, independent retention/object lock, replicated journal,
  tamper-resistant access logs and restore testing remain activation gates.
- A durable intent and ACK are separate transactions around a provider call.
  If the provider accepts the object but times out, or the ACK transaction
  fails, state is unresolved. Never claim storage completion on the exception.

## Idempotency and reconciliation

- Fresh Tower authorization (in future actual issuer/receiver) must be verified
  for each operation including acknowledged replays and reconciliations. The
  SC001 source_test fake authority is NOT this issuer.
- First source write: trusted context, VLT1/checksum/bounds verification,
  durable intent reservation, one create-only backend write, durable ACK.
- Identical replay of an ACK/PRESENT intent verifies backend ciphertext anew
  and returns only the same internal StorageReceipt. Different object/digest/
  size for the same namespace and request ID is an idempotency conflict.
- Existing RESERVED/UNCERTAIN never runs a second PUT. A new separately gated
  RECONCILE_WRITE operation locates the original trusted journal intent;
  it reads and verifies the physical object's VLT1 shape, size and SHA.
- PRESENT emits a storage-only reconciliation result. It is not canonical
  Vault archival proof and does not finalize Vault's record transaction.
- MISSING/CORRUPT emit terminal HOLD and incident (corrupt); no silent rewrite,
  overwrite, delete, retry-as-new, release or premature promotion.
- Provider/read failure during reconciliation leaves the intent unresolved
  rather than guessing at physical state. Process crash between reservation
  and provider return similarly leaves a reconcilable reservation.
- If an already acknowledged object is later missing/corrupt, replay changes
  intent to REPLAY_INTEGRITY_FAILURE and opens a critical incident.
- The Cloud never exposes raw object refs/namespace hashes in application
  summaries, and its health() is metric-only and explicitly NO_GO.

## Source instrumentation and limitations

- JournaledCiphertextOperations must be constructed with the same journal
  attached as SC001's mandatory audit sink (including the existing backup
  service's source audit callbacks).
- Source tests simulate failures before and after provider acknowledgement,
  inability to durably ACK, conflict, cross-entity read, byte tampering,
  direct SQL mutation, chain mismatch, duplicate suppression, denied Tower
  test grant and no-leak health/metrics.
- This is NOT a real incident notification integration or hosted alerting.
  No external owner notification, pager, time-series metrics, dashboard
  user permission model or automatic remediation is active.
- A privileged database attacker can rewrite the whole database and hash
  chain; future external signed checkpoint and immutable/offsite replication
  are essential. App-level create-only also does not defeat host compromise.
- The local physical backend and independent backup backend may still share
  an actual hardware failure domain in synthetic tests. No disaster-recovery
  claim is made.

## SC003+ acceptance dependencies

SC003: provider capability abstraction and bounded real backend adapter
contracts; explicitly disclose provider, true server owner and jurisdiction.
SC004: independent Tower service issuer and authenticated Vault receiver,
expiry, revocation, nonces, replay checks and private service transport.
SC005: independent backup/ledger failure domain, key lifecycle,
offsite signed checkpoints, tested restore/RPO/RTO, resilience and alerts.
Only then consider separately owner-approved deployment and release.
