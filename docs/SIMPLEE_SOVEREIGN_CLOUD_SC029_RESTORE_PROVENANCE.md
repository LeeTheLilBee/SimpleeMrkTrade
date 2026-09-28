# SIMPLEE SOVEREIGN CLOUD — SC029 EXACT BACKUP RESTORE PROVENANCE

Date: September 28, 2026. Based on merged SC028 `vault-dev` commit `cada750b2e961348b264b0dfeff1c7910b9b1a77`. Source-only; **production NO_GO**.

## Gap

SC018 requires a separate trusted Vault `BackupReceipt` before the signed VERIFY_BACKUP source route can read the independent backup. The source port also verifies the Tower-shaped grant's backup ref/hash against that receipt. However, before SC029 a canonical-looking receipt plus physically present backup bytes could still reach the backup provider even when the Cloud operational journal had never durably acknowledged creating that exact backup.

That creates a provenance asymmetry: primary reads (SC027/SC028) require Cloud's durable primary history, while backup restore verification could rely on external/canonical receipt shape alone.

## Change

SC029 adds append-only, full-row-hash-bound `restore_intents` for the **bound SourceOnlyBoundCloudPort path**. Before any backup-provider GET, the port requires that the exact canonical receipt fields match a Cloud backup intent whose latest state is `BACKUP_ACKNOWLEDGED` or `BACKUP_RECONCILE_PRESENT`:

- opaque entity namespace digest;
- backup ref and backup ciphertext SHA-256;
- original source object ref and source ciphertext SHA-256;
- backup key reference.

The restore reservation is committed as `RESTORE_RESERVED`. After the isolated SCB1 → VLT1 verification succeeds, the existing low-level `restore_copy_verified` audit event must exist and the journal appends `RESTORE_BOUND_VERIFIED`. The full verifier checks that every bound restore reservation had an exact acknowledged backup **before** its reservation sequence; a backup ACK that appears later cannot retroactively legitimize an earlier restore.

Same restore request ID may only remain bound to the same receipt. A different backup receipt with the same logical restore request is an idempotency conflict. A later backup integrity hold blocks a new bound restore before provider access. A primary entering hold after a legitimate independent backup was created does not destroy that backup's earlier provenance; the acknowledged backup can still be verified, preserving recovery purpose.

## Deliberate compatibility boundary

`IndependentBackupService.verify_restore_copy()` remains a low-level source crypto primitive used by isolated tests. It can still verify a directly created SCB1 copy without asserting that the approved Tower/Vault→Cloud bound restore corridor authorized it. **Only the bound port adds RESTORE_RESERVED / RESTORE_BOUND_VERIFIED and requires Cloud journal backup ACK provenance.** This prevents tests of the low-level cipher primitive from being misrepresented as a production recovery authorization.

Generic low-level restore events remain non-authorizing. The actual bound success is the separately verified journal event.

## Acceptance

Synthetic adversarial tests cover:
- physical/canonical-looking backup with no Cloud backup journal ACK denied before backup GET;
- pending backup reservation denied;
- source-ref/source-SHA/key-reference receipt borrowing denied;
- later backup integrity hold denied before provider;
- valid independent backup still usable after primary enters hold;
- restore request-ID rebinding to another backup denied;
- historically injected restore before backup ACK rejected even after a later ACK;
- forged bound success without a preceding cryptographic restore verification event rejected;
- mutated restore metadata invalidates the audit chain and owner metrics;
- low-level isolated crypto helper remains available without claiming bound restore provenance.

This does not prove the Vault receipt is genuinely production-authenticated, the backup is physically offsite, the key is independently custodied, the provider is immutable, or that RPO/RTO and recovery commit have been approved. No paid infrastructure, hosted route, real user document, production key or owner release is introduced. Real Tower/Vault identity and canonical backup receipt service remain open in [handoff #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99).
