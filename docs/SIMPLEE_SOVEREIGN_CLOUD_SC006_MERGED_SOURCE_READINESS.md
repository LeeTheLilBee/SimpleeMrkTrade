# SIMPLEE SOVEREIGN CLOUD — SC006 MERGED-SOURCE COMPATIBILITY AND RELEASE READINESS

Date: 2026-09-27. Base: verified `vault-dev` commit `55a285b42141e55b613b8eb36996b48fba38474f`. Production status: **NO_GO**.

## Important change in branch reality

Vault managed-storage source PR #38 merged on 2026-09-27 at `8579cc92919738ed6302eb6fd02c688d5a653785`. Cloud SC001 parent PR #65 also merged to `vault-dev` at `16d167a6a3aa65e35310397e0c7a36a9d27792d0` (the current target branch may have further integration commits). Their historical descriptions as still-draft/unmerged are stale. Both integrations added SOURCE code; no hosted private transport, live Tower issuer, Vault canonical registry, provider, recovery drill, paid resource, live credential or release were established merely by GitHub merge.

New SC006 code is isolated to `simplee_cloud/readiness.py`, an actual Vault-envelope/Cloud compatibility test, this handoff and scoped CI. No Vault or Tower files are changed.

## Compatibility test added

The source tests import the **actual merged Vault** `encrypt_original` and `decrypt_original`, rather than merely inventing a byte string with a VLT1 prefix. Synthetic originals and in-memory 32-byte encryption keys produce genuine VLT1 AES-GCM envelopes whose original hash and ciphertext hash are independently verified.

The tests exercise the source-only Tower-signed, trusted Vault scope `SourceOnlyBoundCloudPort` from SC004B and SC005B: write the actual Vault envelope under an opaque ref; read and verify its ciphertext SHA; authenticate the recovered original only with Vault's own decryptor, correct evidence ID, entity, version, key and original SHA; create independently encrypted SCB1 backup and verify its isolated inner VLT1 copy. Wrong entity/evidence/version/key/original SHA and forged canonical scope are rejected. A passing test demonstrates **source protocol compatibility**, not an independently operated Tower signer, actual malware scanning, real mTLS peer, production Vault registry transaction, WORM retention, audit independence or legally reliable archival receipt.

## Owner-focused release preflight

`source_preflight()` returns a concise gate matrix with ownership and required independent evidence. Even when every evidence reference is populated, its state remains SOURCE_ONLY_NO_GO with zero externally verified certifications and production authorization false. A reference is a review pointer; it is neither a signed attestation nor a live release switch. Unknown keys, oversized/injected refs and secret-like freeform text are rejected.

Required independently reviewed gates cover: Tower signer/rotation/current approvals; authenticated Vault peer; Vault canonical scan/version/retention/receipt; nonce/revocation failover; private owner-approved provider with actual hardware/operator/jurisdiction disclosure and Object Lock; independent backup domain/key custody; offsite signed audit checkpoint; actual outage/Vault original recovery drill and agreed RPO/RTO; owner incident alert delivery; and explicit owner vendor/funding/release decision.

### Responsibility boundary

BuyBox/Teller → Tower → Archive Vault → Simplee Cloud. Tower alone authenticates and authorizes. Vault alone owns canonical document and records semantics and original encryption/decryption. Cloud owns opaque encrypted storage, integrity and backup infrastructure. Existing executive `clouds/` stays distinct. Neither a Cloud storage ACK nor a signed-grant source test constitutes a Vault canonical receipt.

## Actual next steps still gated

1. Tower workstream independently accepts #99 and supplies issuer/private transport/current policy + durable revocation and signed grant rotation in a separately reviewed PR.
2. Vault workstream independently supplies canonical record/version/scan/retention source lookup and protected receipt transaction in its own PR.
3. Cross-service integration tests use actual authenticated service identities, do not trust HTTP JSON claims and prove deny-on-unavailability/replay/entity mismatch.
4. Owner explicitly approves provider and cost before any hosted pilot. Verify provider private bucket, conditional writes, versioning/Object Lock/retention/hold, actual physical ownership and subprocessors.
5. Independent offsite encrypted backup and journal checkpoint custody, real site-loss/restore/Vault original authenticity proof, RPO/RTO measurement and alert delivery.
6. Separate owner production GO/NO_GO record only after external evidence is verified. Do not infer authorization from this merged source branch or a CI green check.

No paid resources, real documents, signing secrets, live provider, hosted route or production access added in this pack.
