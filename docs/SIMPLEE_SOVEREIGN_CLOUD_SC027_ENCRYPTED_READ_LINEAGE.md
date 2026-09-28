# SIMPLEE SOVEREIGN CLOUD — SC027 ACKNOWLEDGED SOURCE REQUIRED BEFORE ENCRYPTED READ

Date: September 28, 2026. Based on merged SC026 `vault-dev` source at `95e9ebfbf7835c5c3e16c83f1dc71b642b53ff74`. **Production NO_GO**.

## Reason for this hardening

SC024 verifies Cloud journal provenance before creating a first backup, while the journaled encrypted read previously accepted exact signed Vault scope and a physically matching primary provider GET without independently confirming that the Cloud primary intent was durably acknowledged. This meant raw bytes placed outside journal provenance, or provider-accepted bytes whose original write acknowledgement was lost, could be returned as an encrypted read before original-ID reconciliation.

SC027 adds `journal.require_acknowledged_primary()` to `JournaledCiphertextOperations.get()` after source-only Tower-shaped authority and namespace derivation but BEFORE any read-intent audit or provider GET. The exact namespace digest, object ref and ciphertext SHA-256 must match a fully chain-verified Cloud primary in `WRITE_ACKNOWLEDGED` or `RECONCILE_PRESENT`. Missing, uncertain, wrong-entity/ref/digest, corrupted journal or primary integrity HOLD deny without a physical GET or a misleading "missing/corrupt provider" incident. A source whose original PUT lost ACK needs a separately fresh-authorized `RECONCILE_WRITE` on the ORIGINAL request ID first; this never rewrites the provider bytes and cannot create a Vault canonical archive receipt.

After a primary is later placed in integrity HOLD, the ordinary primary read stays denied; separately encrypted existing backup verification remains available through the independently authorized Vault backup-receipt path and never overwrites primary or authorizes recovery finality.

## Boundaries

This protects the source `JournaledCiphertextOperations` and its `SourceOnlyBoundCloudPort` path. Legacy SC001 stand-alone helper primitives remain test-only, default-disabled for production and must never be exposed as an alternate hosted route. Signed Tower grants and Vault scopes in the regression suite are synthetic, not real issuer, private peer, malware scan or canonical final receipt proof.

CI updates the earlier foreign-entity read tests: denial now occurs BEFORE provider access rather than being mislabeled as a physically missing object, so no storage-integrity incident is fabricated for an invalid request. New tests cover physical-but-untracked bytes, accepted-but-ACK-lost write then explicit original-ID reconciliation, wrong signed source hash/ref and cross-entity bytes, primary integrity HOLD with viable backup verification, tampered journal and successful ordinary acknowledged read.

This is one full consolidated source CI run, no new duplicate workflow. No live provider, real user documents, private keys, paid infrastructure or production GO.
