# SIMPLEE SOVEREIGN CLOUD — SC011 SOURCE CHECKPOINT LINEAGE VERIFICATION

Date: September 27, 2026. Based on merged SC010 `vault-dev` commit `0f7504b874149bda773ec9b8ebc3cea6b856de5c`. Default-disabled, source-test-only, production **NO_GO**.

## Additional control

SC010 verified that a checkpoint sink can return the exact signed bytes after a claimed create-only PUT. That is necessary, but it is still possible to present a validly signed checkpoint which is not connected to the externally held previous checkpoint, to replay an older sequence, or to omit an entire suffix.

SC011 adds `verify_source_checkpoint_sequence` to check a bounded, separately supplied chronological checkpoint history from the genesis link, using the independently pinned Ed25519 public keys and the FULL locally verified SC002 journal prefix for each entry. It requires each checkpoint's `previous_checkpoint_sha256` to match the complete signed digest of the previous entry, strictly increasing event counts and unique opaque checkpoint references. Any missing middle entry, wrong order, duplicate, forged-but-validly-signed fork, altered signature or local rollback fails closed. Existing SC005 signature and SC010 exact read-back validation remain mandatory.

The result contains safe metadata about **the supplied source-test sequence**, with `actual_external_latest_attested=False`, `independent_offsite_immutability_certified=False` and `production_authorized=False`. This code deliberately CANNOT establish whether an untrusted sink omitted a newer valid checkpoint. The actual offsite operator/custodian must independently attest its latest tip and immutable full history, and Vault/Tower must review custody, signer rotation and incident escalation before any genuine operational reliance.

## Synthetic tests

In-memory test-only keys and create-only fake sinks build three independently signed/read-back checkpoints, then inject missing/reordered/duplicated entries, a validly re-signed wrong parent, a same-count re-signed replay, a wrong public key, an altered signature and a separate empty local journal. The tests explicitly show that a valid older prefix can still pass as a prefix while the output refuses to certify it as the true external latest checkpoint.

No production signer, real offsite/WORM account, provider selection, KMS, actual infrastructure, paid resource, real documents, route or production permission is created. Independently authenticated external custodian latest-tip evidence and restore drill remain separate owner-approved release gates.
