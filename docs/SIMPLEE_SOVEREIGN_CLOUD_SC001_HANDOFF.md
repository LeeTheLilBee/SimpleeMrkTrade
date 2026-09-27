# SIMPLEE SOVEREIGN CLOUD — SC001 SOURCE FOUNDATION AND VAULT INTERFACE

Date: 2026-09-26. Status: SOURCE ONLY / NO_GO for production.
Source branch: simplee-cloud-sovereign-foundation-sc001, base vault-dev.
No infrastructure, credentials, secrets, payment, provider approval, public route, production object, or production grant is created.

## Identity and naming collision

- simplee_cloud/ = NEW encrypted object-storage service, under this workstream.
- clouds/ = pre-existing The Clouds executive/owner command application. NOT storage.
- vault/ = Archive Vault, sealed documentary memory and record authority.
- tower/ = identity/permission/approval/step-up/route authority.
- No existing Vault/Tower/Clouds files are edited in this workstream.

## Precise application corridor

BuyBox/Teller → Tower → Archive Vault → Simplee Cloud.
No direct BuyBox/Teller/Soulaana/Clouds → Cloud or → Vault document body.
Cloud's only initial internal caller is authenticated archive_vault, on behalf of
a currently valid Tower-authorized Vault workflow. Cloud does not become an
independent user-access/permission authority merely because it rechecks the
trusted grant via the service transport.

## Compatibility anchor: existing Vault draft PR #38

As inspected 2026-09-26, PR #38 is open DRAFT at f8d9219077b1817ffef8f0864eb5cac8df694868.
Existing vault/real_operations_encrypted_storage.py owns VLT1 AES-256-GCM
envelopes, with TowerStorageDecision, fresh nonce and AAD binding entity_id,
evidence_id and document_version_id; returns internal
object_key objects/<48 lowercase hex> and ciphertext_sha256.
Existing vault/real_operations_managed_object_store.py is a separate S3-compatible
injectable adapter with conditional create-only IfNoneMatch=* and SHA metadata.
This SC001 branch does NOT modify or merge PR #38 and does NOT install a direct
Vault runtime dependency on Cloud; no parallel encryption rewrite occurs.

PROPOSED, NOT YET ACCEPTED, Vault↔Cloud v1 internal storage port:
1. Vault obtains independently authenticated and current Tower authorization,
   performs actual scan/provenance/digest verification, encrypts original into
   VLT1, allocates internal opaque object_ref objects/<48 hex>, records expected
   SHA-256 and source evidence/version bindings in its canonical DB.
2. A PRIVATE, mutually authenticated Vault service caller forwards the ciphertext
   bytes, expected ciphertext digest, opaque object_ref and a Tower decision
   reference into Cloud. Cloud's injected authority verifier must independently
   verify service identity and Tower decision (scope, purpose, operation, expiry,
   revocation, approval/step-up and replay protection) using trusted server-side
   state or verified signed capability. It MUST NOT accept a self-asserted
   verified_by_tower boolean, a raw browser JSON claim or test authority.
3. Cloud independently checks envelope magic/bounds/SHA and uses an HMAC-derived
   namespace per entity, then atomically create-only writes the bytes. Cloud
   returns internal StorageReceipt(object_ref, ciphertext_sha256,
   ciphertext_size, namespace_digest). This is a storage ACK, NOT a signed Vault
   archival receipt or proof of canonical metadata/retention commit.
4. Vault verifies and persists its canonical version and immutable archival
   receipt, reconciles uncertain/orphan provider writes, and returns only
   Tower-approved workflow-safe metadata to the requesting app. Neither raw
   object_ref nor namespace_digest reaches BuyBox, Teller, Clouds or public JSON.
5. For EACH read, Tower must freshly permit the requested Vault view/download/
   purpose/redaction scope. Vault supplies Cloud the expected SHA from its
   trusted canonical record; Cloud checks a NEW service-level authority grant,
   storage scope, digest, and envelope bytes; Vault authenticates AES-GCM,
   original digest, and disclosure. No public URL or presigned object link.

Existing Vault ManagedObjectStore.put_if_absent(key, ciphertext)/get(key)
is not itself a transport authorization contract. A narrow Vault-owned bridge
must bind per-request trusted authorization and checksum before calling this
Cloud port. It is intentionally NOT smuggled into the current draft PR.

## SC001 implementation

- contracts.py: explicit typed storage context, deny-all default authority,
  backend protocol, internal ACK, separate backup receipt.
- service.py: source-only mode, Vault-only caller shape, injected authority
  verification required for EVERY operation, HMAC namespace isolation,
  checksum-validated VLT1 create-only write and bounded verified read; no public
  routes or plaintext access.
- local_backend.py: process-private filesystem adapter, opaque names,
  O_EXCL create-only, no overwrite/delete, no symlink root, bounded reads and
  fsync. This is useful for source tests/isolated owned-hardware development,
  but NOT production storage, WORM certification, or cross-site replication.
- backup.py: independent backend instance and independently provided AES-256-GCM
  key adds SCB1 outer authenticated encryption with scope+object+digest AAD.
  Restore verification returns ONLY inner encrypted VLT1 to an isolated,
  explicitly authorized recovery operator; it cannot change primary data or
  finalize a Vault recovery commit.
- tests: fake authority and synthetic data ONLY. No actual Tower issuer,
  provider policy, hardware, KMS, scanner, Vault DB or host is certified.
- audit_event callback: safe event shape only. Until a real durable append-only
  sink, incident store, reconciliation and alert delivery exist, monitoring is
  not operational. health() unconditionally reports SOURCE_ONLY_NO_GO.

## Activation gates (ALL REQUIRED, independently verified)

1. Explicit owner approval of vendor dependencies, billing and location/data
   residency, or approved owner-owned equipment/site. Record who owns software
   versus physical hardware. Do not claim software sovereignty equals servers.
2. Separate service identity, authenticated transport, Tower issuer and Vault
   verified receiver with short-lived scoped grants, revocation and replay checks.
3. Vault verified ingest, scanner receipt, authenticated key/KMS retrieval and
   rotation/recovery; never commit plaintext keys, documents or reusable tokens.
4. Durable metadata, append-only Cloud operational event/incident ledger,
   uncertain-write reconciliation and canonical Vault registry/receipt
   transactions; independent SHA and Vault AES-GCM verification.
5. Private namespace/bucket, least privilege, conditional create semantics,
   object-lock/retention/legal hold, lifecycle, access logging and no public ACL.
   Logical create-only alone does NOT provide physical immutability against an
   administrator or host compromise.
6. Independent backup keys AND independent security/storage failure domain;
   scheduled restore drills, RPO/RTO targets, tamper and provider-loss drills.
   A second folder on the same machine is NOT disaster recovery.
7. Source tests, real provider feature/compatibility tests, actual authenticated
   cross-service adversarial tests, key-loss and replay/revocation tests, owner
   acceptance. No automatic production unlock via an environment toggle.
8. Owner approves the production release separately from accepting this PR.

## Deployment and owned-hardware route

Phase 1: software/interface test harness (this PR), then auditable ledger,
provider abstraction, private API behind transport, security CI and drills.
Phase 2: only after explicit funding/owner approval, isolated managed hosting
with disclosed physical owner, jurisdiction, keys and data processors.
Phase 3: migrate through the same bounded backend port into an office server
room using owned physical servers; plan UPS, redundant disks, ventilation and
cooling, fire suppression, physical access, network redundancy, monitoring,
restore-capable offsite backup. Data copy/re-encryption/verification and
cutover must be separately approved; do not silently change object identity.
Phase 4: hybrid replication and independent, geographically separate DR with
verified manifests, independent credentials/keys and documented failback.
Phase 5: commercial Cloud evaluation only after internal security/operations
maturity and a separate compliance, support and risk decision.

Owner vendor preference: investigate Black American-owned services first
where suitable. Provider identity, actual hardware ownership, sub-processors,
jurisdiction, cryptographic/key-control dependencies and costs require explicit
disclosure and approval. No branded provider or paid resource selected now.

## Required Vault/Tower handoff decisions

- Pin the canonical accepted context format, signature/issuer, service identity,
  decision ID, nonce/idempotency, expiration and replay semantics.
- Confirm Cloud is storage body only and Vault keeps classification, document
  versions, retention/legal hold policy, canonical receipts and redaction.
- Decide the adapter bridge after independent compatibility review of draft
  PR #38. No merge of PR #38 in this Cloud branch.
- Establish registry↔object uncertain-write reconciliation and restore
  authority binding; Cloud backup verification is NOT Vault recovery execution.
- Default release posture is NO_GO until all activation gates have proof.
