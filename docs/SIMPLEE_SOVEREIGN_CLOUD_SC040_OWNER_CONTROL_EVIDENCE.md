# SIMPLEE SOVEREIGN CLOUD — SC040 OWNER EVIDENCE DESK: THREE-LEDGER CONTROL STATE

Date: October 1, 2026. Based on merged SC039 `vault-dev` commit `bf20c932ca28d9860e2eb0d4dbde3af32bea35b5`. Source-only; production **NO_GO**.

## Owner view upgrade

The owner-local evidence desk already combines verified local storage/backup/restore status, one-use grant replay state, optional historical backup-key readiness, provider-review pointers and fixed release gates. Until SC040 it understood only the older SC020 signed checkpoint covering storage + replay.

SC040 adds two optional, independently supplied source inputs:

- a verified SC038 `SQLiteNamespaceBindingLedger`, summarized only as binding/event counts with raw-entity persistence, external-registry and binding-key custody certifications explicitly false;
- an SC039 `SignedControlCheckpoint`, verified against the exact local storage journal, replay ledger **and namespace-binding ledger** under pinned Ed25519 public keys.

When the SC039 checkpoint verifies, the owner desk may state only that those three **local historical prefixes** match the signed source checkpoint. It sets:
- `local_storage_and_replay_prefix_verified=True`;
- `local_namespace_prefix_verified=True`;
- `local_cross_ledger_checkpoint_verified=True`.

It still keeps `actual_external_latest_attested=False`, `external_immutability_certified=False`, the existing top-level `cross_ledger_point_in_time_certified=False`, and `production_authorized=False`. A locally valid signature is not evidence that an independent custodian holds the true latest immutable checkpoint.

Legacy SC020 storage+replay checkpoints remain readable and are clearly labeled `SC020_STORAGE_REPLAY`; they cannot claim namespace-prefix verification.

## Fail-closed combinations

The desk rejects:
- simultaneous SC020 and SC039 checkpoint generations;
- any signed checkpoint without pinned public keys or vice versa;
- SC039 checkpoint without a verified namespace-binding ledger;
- a checkpoint paired with a different namespace ledger/prefix;
- a tampered namespace ledger even when no checkpoint is supplied;
- untrusted provider/release fields that attempt to create a production state.

Provider/release reference strings, candidate/provider labels, raw entity IDs, namespaces, object refs, hashes and key references remain absent from the owner report.

## Limits

This is an imported local source function, not a hosted dashboard, alert system or release endpoint. It does not contact a provider, authenticate real Tower/Vault transport, retrieve a true external checkpoint, verify HSM/KMS custody, prove backup bytes, certify namespace-registry replication or authorize production.

No paid resource, production credential, route, user document or owner release is introduced. Real external latest-tip evidence, immutable custody, authenticated Tower/Vault integration, provider approval, recovery proof and owner release remain separate gates.
