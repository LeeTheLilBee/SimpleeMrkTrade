# SIMPLEE SOVEREIGN CLOUD — SC003 PROVIDER PORT AND DISCLOSURE GATES

Date: 2026-09-27. Source-only; stacked on current SC001 development head (which includes merged SC002). Production **NO_GO**.

## Why this is separate

The existing executive `clouds/` package is not storage. `simplee_cloud/` is the separate storage service. Vault draft PR #38 already has its own injectable managed-storage adapter. SC003 does not rewrite or import that adapter or change Vault/Tower ownership: Vault produces VLT1 and owns documents, versions, scan receipts, legal retention decision and canonical archival receipts; Tower verifies the requesting authority; Cloud stores opaque encrypted envelopes and independently verifies ciphertext integrity.

## Adapter port

`S3CompatibleCiphertextBackend` implements the existing `CiphertextBackend` two-method port through an explicit injected S3-style client, bucket, opaque root prefix and primary/backup purpose. Constructor defaults to disabled and only allows source_test. No SDK factory, secret, endpoint, live provider, bucket, cloud account or infrastructure is selected or created.

- Storage key format is `<explicit-prefix>/<HMAC-entity-namespace>/objects/<48 hex>` for primary and analogous `backups/<48 hex>` for backup. No raw entity IDs, evidence IDs, version IDs or user-controlled paths in provider keys.
- Source writes accept only bounded VLT1 primary ciphertext or SCB1 independently encrypted backup bytes, use `IfNoneMatch='*'` with no read-then-write fallback, no public ACL, and request SSE-S3 AES256 defense-in-depth. An unsupported precondition, 412, 409, provider timeout, missing 200 acknowledgement or other error is not automatically retried; SC002 records uncertain state and requires separate gated physical reconciliation.
- Source reads validate declared ContentLength before bounded read, expected envelope metadata, body type/length and SHA-256, and close the stream. They do NOT trust ETag as canonical SHA. SC002/Vault still independently compare body digest to their own trusted canonical value.
- No list, delete, share, presigned URL, object body JSON route, direct BuyBox/Teller/Clouds/Soulaana caller or release toggle.
- Adapter application-level conditional create does NOT certify physical immutability: for versioned buckets with a delete marker as current object, conditional PUT may succeed even if an older retained version exists. Delete-marker/version manipulation permissions and external object-lock/retention settings must be independently assessed.
- The existing interface's acknowledgement is only an internal storage ACK. Vault's canonical archival receipt, original AES-GCM validation, retention and redaction are separately required.

## Provider evidence review before any deployment

The typed review requires documented actual physical-server owner, software operator, storage jurisdiction, external dependencies and review references for the complete checklist: atomic conditional PUT, private namespace/public-access-block, versioning and Object Lock, retention/legal hold, least privilege, authenticated transport, encryption and key control, access audit/alert delivery, independent backup failure domain, key restore test, physical ownership/data location, subprocessors, supplier security and separate owner funding/vendor approval.

References are NOT independently verified proof, nor an approval switch. Even all fields populated yields `NO_GO` and `storage_runtime_authorized=False`. Owner preference for Black American-owned vendors is a sourcing consideration requiring factual ownership/disclosure verification; no provider is selected by this pack. Owning this source code does NOT mean Simplee owns underlying hardware or transit networks.

Provider-specific SDK behavior, Object Lock/retention policy, versioning, audit and KMS/key controls must be independently verified with non-sensitive test objects after owner authorizes an isolated environment. Fake-client tests alone do not prove provider compatibility. Per-object versions/retention/legal-hold state and durable external evidence must be added to the future real provider adapter before live activation.

## Next source work

SC004: mutually authenticated Vault->Cloud service transport and Tower issuer/receiver evidence, short-lived operation-specific capabilities, replay/revocation checks and independent authorization verification. Source contract tests alone cannot grant authority.

SC005: backup keys/failure domain, restore drill, signed independent audit checkpoint, monitoring and recovery targets.

No paid resources, credentials, provider enrollment, real personal data or production usage in SC003.

## Public technical references reviewed for protocol caveats

- AWS S3 conditional writes: https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html
- Object Lock needs versioning and applies to object versions: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- ETag is not always full-object MD5: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html

These are protocol design references only, not provider selection or an assertion of current deployment.
