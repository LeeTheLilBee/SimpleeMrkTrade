# SIMPLEE SOVEREIGN CLOUD — SC043 SIGNED NAMESPACE KEY-COMMITMENT CONTROL CHECKPOINT

Date: October 1, 2026. Based on merged SC042 `vault-dev` commit `e6e8dc0d37321e6330f8f4085ae3bfdb6c84d62d`. Source-only; production remains **NO_GO**.

## Why SC043 exists

SC042 makes the local namespace-binding ledger fail closed if it is reopened with a different binding key, but SC039's externally signable storage/replay/namespace checkpoint v1 only committed the namespace EVENT-chain head. It did not commit the new key-identity metadata. A local key commitment was therefore stronger than the signed external checkpoint evidence.

SC043 introduces `simplee.cloud.control-checkpoint.v2`. New source checkpoints now sign:

- storage journal event count + head;
- one-use grant replay event count + head;
- namespace binding event count + head;
- **the exact registered namespace binding-key commitment**;
- previous signed checkpoint digest;
- signer key ID, opaque checkpoint ref and UTC timestamp.

Verification with a supplied namespace ledger requires BOTH the historical namespace event prefix and the v2 key commitment to match the currently verified ledger. A correctly re-signed checkpoint carrying a different valid-looking 64-hex key commitment is rejected.

## Legacy v1 compatibility without upgrading its claim

Existing source-only v1 signed checkpoints remain verifiable. They simply do not contain or prove the namespace binding-key commitment. A single same-ledger-vector **v1 → v2 strengthening checkpoint** is permitted without requiring a fake storage/replay/namespace event merely to migrate the evidence schema. A second same-vector v2 checkpoint is still denied as a replay/non-progress checkpoint.

A v1→v2 sequence keeps its normal signed previous-checkpoint digest, so the stronger checkpoint explicitly descends from the legacy evidence. The source sequence report says whether its tip contains and matches the current key commitment.

The owner-local evidence desk labels a new v2 checkpoint as `SC043_STORAGE_REPLAY_NAMESPACE_KEY` and reports only a boolean that the local key commitment is signed. It never displays the actual commitment digest or key.

## Still NOT certified

A locally signed v2 checkpoint does not prove that an independent offsite custodian actually possesses the true latest checkpoint, that the sink is WORM/immutable, or that the namespace binding key is held in an approved KMS/HSM. Real signer custody, key rotation/recovery, offsite latest-tip attestation, Tower/Vault namespace-registry authority, provider security and owner release remain independent gates.

No live service route, real provider, paid infrastructure, production credential or user document is introduced.
