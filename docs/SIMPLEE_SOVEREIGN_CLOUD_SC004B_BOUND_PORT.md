# SIMPLEE SOVEREIGN CLOUD — SC004B SOURCE-ONLY BOUND INVOCATION CONTRACT

Date: 2026-09-27. This pack is stacked on the draft SC001 Cloud development branch after SC005. **NO_GO for production.**

## What was actually integrated

The `SourceOnlyBoundCloudPort` composes source components from SC001–SC005. It consumes a one-time, standard Ed25519 Tower-shaped grant using SC004's independently injected peer/current-policy verifier; asks an independently injected Vault-canonical-state lookup for the exact request and operation; and passes ONLY the resulting typed signed entity/context/object/digest to SC002's journaled storage or SC005's isolated backup drill.

This code has no HTTP ingress, authenticated network transport, mTLS, Tower private signing key, real Tower issuer, real Vault record registry, live provider, paywall, credential, production switch or real document input. Constructors default to disabled; all tests use synthetic in-memory keys, false service identities and local ciphertext. The pre-existing SC001 source-test verifier is still source-only and may not be used as real authorization.

## Call shape and trust boundaries

- Each operation accepts `SignedTowerGrant`, an opaque authenticated-transport peer marker and an opaque canonical Vault request-ID lookup key. It does not accept a caller-controlled `StorageContext`, entity, object key or expected SHA. The lookup resolver MUST be built from real authenticated Vault canonical state later; taking its answer from HTTP JSON, a browser `verified_by_tower` boolean or a fake assertion is prohibited.
- The trusted lookup returns `TrustedVaultScope` with matching request ID and operation; SC004 verifies the Tower signature, issuer/audience, entire exact Vault scope including classification, current Tower decision/approval/step-up and authenticated peer, expiry and nonce. The one-time nonce is consumed before the storage call. SC001 source gate remains independently active.
- A write checks supplied VLT1 bytes against signed/canonical SHA and bounded length before SC002 creates a durable idempotent write intent and one create-only provider PUT. A failed content check consumes the grant but creates no write intent. Caller obtains a fresh signed nonce/permission to retry; no rollback/reuse of authorization.
- An encrypted read requires a distinct READ_CIPHERTEXT grant bound to the exact ref/digest. Only inner encrypted VLT1 bytes reach the trusted Vault-side source port; this is not a public download or original-plaintext release.
- Reconciliation takes the ORIGINAL logical write request ID, but with a FRESH Tower-issued signed RECONCILE_WRITE grant/nonce, approved decision and current policy. The bridge independently compares that grant's ref/digest/entity to the original SC002 durable intent before looking at physical ciphertext. SC002 then records a reconciliation intent and verifies actual VLT1 SHA/size; PRESENT is a storage-only acknowledgement, NOT a canonical Vault archival receipt. MISSING/CORRUPT remain HOLD/incident; never repeat provider PUT automatically.
- Backup creation similarly binds the source ref/digest. Isolated backup verification uses separately looked-up trusted canonical BackupReceipt; signed VERIFY_BACKUP ref/digest must exactly match the backup receipt before SC005 tests the SCB1→VLT1 inner encrypted copy. Only safe synthetic recovery evidence is returned. No primary overwrite, plaintext release, Vault final recovery commit or verified independent data center is implied.

## What Tower/Vault still own

The Tower workstream must independently implement and certify service signer/private key custody/rotation, actual current decision+approval+step-up revocation checks, and authenticated private Vault transport identity. SC004's source callbacks are NOT those services. Vault must implement the canonical scope/backup lookup and bind its actual scan, version, retention and original hash evidence, and independently produce canonical archival/recovery receipts. Cloud is never the source of legal retention or approval.

A source-level passing CI suite is only evidence for these code contracts. It does not certify object lock, WORM, external checkpoint delivery, independent backup failure domain, provider terms/hardware owner, external owner alerts, RPO/RTO or owner funding approval.

## Next release gates

1. Tower and Vault accept source handoff issue #99, agree and independently implement authoritative issuer, transport and lookup.
2. Adversarial cross-service tests prove rejected wrong peer, expired/revoked approval, scope/hash mismatch, reused grant, replay after failover, missing signer/nonce store and provider uncertainty.
3. Actual provider/private access, retention and Object Lock proof, separate keys, signed offsite journal anchor and backup/site-loss restore test under approved resources.
4. Owner approves any paid hosted pilot, provider/operator/physical ownership, jurisdiction/subprocessor disclosure and release decision in a distinct go/no-go record.

Both the SC001 parent and this pack remain production NO_GO until the independent owners accept the bridge and these gates pass.
