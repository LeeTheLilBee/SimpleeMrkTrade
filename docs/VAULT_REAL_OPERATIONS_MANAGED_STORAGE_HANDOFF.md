# ARCHIVE VAULT — REAL OPERATIONS 1 / MANAGED ENCRYPTED STORAGE

**Decision:** Managed encrypted cloud object storage first, with independent encrypted local backups. Tower remains the only identity/permission/approval/step-up authority. Vault remains sealed memory. BuyBox and Teller never call Vault directly.

## Audit finding
The GP001-era dashboard uses sample registry/receipt counts. GP011 explicitly blocks raw upload pending Tower clearance and storage configuration. GP261–GP370 implement genuine local storage/quarantine/registry/download foundations, but these do not establish an operational managed provider or deployed Tower authorization. GP151–GP160 explicitly says provider connection is readiness-only. Treat pack counts as implementation history, not production certification.

## This branch implements
- `vault/real_operations_encrypted_storage.py`: a real AES-256-GCM envelope with fresh random nonce and authenticated entity/evidence/version binding; SHA-256 verification of original and encrypted envelope; strict size limit; immutable object-store adapter protocol; restrictive exclusive local encrypted backup write; internal archival receipt fields.
- `vault/test_real_operations_encrypted_storage.py`: encryption round trip, tamper/wrong-key/wrong-scope rejection, scanned-hash mismatch, missing Tower gate, exclusive backup.
- In-memory adapter is **tests only**, not cloud storage. The Tower decision dataclass is an internal contract and cannot authenticate itself. The calling route must construct it from authenticated Tower middleware, never untrusted JSON. A scan receipt reference is not proof that malware screening happened; actual signed/verified scanner result must be bound by the integration before calling archive.
- The returned internal `object_key` must never pass to BuyBox, Teller, Clouds or public JSON.

## Required deployment gates (NOT implemented/authorized here)
1. Select and configure an approved managed object provider, dedicated private bucket/namespace, IAM least privilege, encryption/key management, versioning/object lock as supported, access/audit logs, lifecycle and retention/legal hold.
2. Use a real secrets manager/KMS and documented key rotation/recovery; never persist plaintext keys in repo, receipts or backups. Ensure backups use independently managed keys and independent recovery credentials.
3. Bind an authenticated Tower internal service request to the existing permission/approval/step-up and purpose/entity/classification checks. Implement replay protection and deny revoked/expired authorization.
4. Implement streaming bounded original-file ingress through Tower, file type/size validation, quarantine, real malware scanning, verified scan receipt and digest match. Scanner unavailable means fail closed.
5. Implement transactional canonical version registry, durable append-only receipts, reconciliation of cloud object vs database failures, idempotency, retention and legal hold, protected downloads with per-request Tower recheck and redaction.
6. Implement independent encrypted backup job, scheduled restore drill, disaster recovery metrics, audit log and alerting.
7. Run tests and deployment validation with non-sensitive test documents. No live provider credentials, provider calls, production writes or deployment were performed in this branch.

## Promotion proof
One authorized test original → scanned digest → encrypted provider object → durable canonical receipt → independently encrypted backup → Tower-gated retrieval → hash match → corrected version preserved independently → denied revoked request → restore from backup. Until all pass, production readiness is **NO_GO**.

## Parallel BuyBox integration
PR #35 is separate and draft. Merge only after shared Tower/Vault contracts and tests reconcile. No direct BuyBox-to-Vault transport is authorized. Recovery GP821–GP830 is independent.

## VRO-02 managed adapter follow-on
- `vault/real_operations_managed_object_store.py`: injectable private S3-compatible client, create-only conditional writes (`IfNoneMatch='*'`), ciphertext-only bodies, server-side AES256 defense in depth, bounded reads and SHA-256 metadata validation. No provider credentials, public ACL, presigned URLs, deletion or direct app route. This is real adapter code but not a connected/deployed provider.
- `vault/test_real_operations_managed_object_store.py`: fake-client tests for create-only semantics, tamper and invalid inputs. Tests are committed, not reported as executed.
- Deployment must verify chosen provider supports atomic conditional PUT and enforce versioning/object lock, IAM/KMS policies, bucket public-access block, logging, recovery and retention independently. Never pass raw object keys to BuyBox/Teller.
