# SIMPLEE SOVEREIGN CLOUD — SC039 JOINT CONTROL-PLANE CHECKPOINT

Date: October 1, 2026. Based on merged SC038 `vault-dev` commit `2537b8aa872e398b3a2acd74f659f3ed4b66948a`. Source-only; production **NO_GO**.

## Why this exists

SC020 signs a joint source checkpoint for two security-critical histories: the Cloud operational journal and the consumed Tower-shaped grant replay ledger. SC038 added a third security-critical history: the durable redacted canonical entity→opaque namespace binding ledger.

Without an external commitment to that third history, storage/replay evidence could remain internally valid while a namespace-binding ledger was rolled back, forked or substituted separately.

SC039 adds a new `simplee.cloud.control-checkpoint.v1` contract that jointly commits:

1. verified Cloud operational-journal event count + historical prefix head;
2. verified grant-replay ledger event count + historical prefix head;
3. verified namespace-binding ledger event count + historical prefix head;
4. previous complete signed control-checkpoint digest;
5. signer key ID, opaque checkpoint ref and UTC creation timestamp.

The namespace ledger now exposes `checkpoint_head(event_count)` only after fully verifying its complete append-only row/event chain, allowing historical signed control prefixes to remain verifiable after later namespace enrollments.

## Source behavior

The control checkpoint is sealed only by an injected external signer callback under pinned Ed25519 public keys. A later checkpoint must be monotonic across all three ledgers and at least one ledger must progress. Delivery uses create-only sink semantics followed by exact byte-for-byte signed read-back and full three-ledger verification. Missing/substituted read-back fails closed and is never blindly re-PUT.

A claimed history is checked from genesis for exact previous signed digest links, unique opaque refs and monotonic three-ledger vectors. A valid older prefix can still be verified as a prefix, but the source result explicitly keeps `actual_external_latest_attested=False`, `independent_offsite_immutability_certified=False` and `production_authorized=False`.

## Synthetic acceptance

Tests cover exact three-head commitment/read-back, independent progress in storage/replay and namespace ledgers, namespace tamper invalidating an otherwise signed checkpoint, separate storage/replay tamper, fake external ACK/drop/substitution, missing-middle/fork/replay lineage, same-vector reseal denial, historical namespace-prefix validation after later enrollment, older valid prefix not claiming true external latest, wrong signer and default-disabled live modes.

This supersedes neither SC020 nor any real external custody requirement. It proves a stronger source contract only.

## Still external

No real external signer, HSM/KMS, immutable/WORM custodian, true-latest attestation, multi-region namespace registry, provider account, private mTLS Tower/Vault receiver, paid infrastructure, real user data or production release is created. A future operational control plane must independently manage signer custody/rotation, external sink ownership/retention, registry replication and incident response before this source contract can be relied upon.

See [Cloud tracker #66](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/66) and [Tower/Vault handoff #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99).
