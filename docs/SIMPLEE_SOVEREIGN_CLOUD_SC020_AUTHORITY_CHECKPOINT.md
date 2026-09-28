# SIMPLEE SOVEREIGN CLOUD — SC020 JOINT STORAGE/REPLAY AUTHORITY CHECKPOINT

Date: September 28, 2026. Source baseline: merged `vault-dev` commit `ff65525ae534d330243cfe9e1930e4e18072b844` after SC019. **Source-only / production NO_GO.**

## Why

SC005/SC010/SC011 signed and checked the Cloud operational storage journal. SC019 separately made the one-use Tower grant replay ledger append-only and hash-bound. A real external custodian eventually needs to detect rollback in **either** ledger, not only storage history.

SC020 adds a separate source-only `authority-checkpoint.v1` contract that signs both verified prefixes together:

- Cloud storage operational event count + head SHA,
- Tower-grant replay event count + head SHA,
- previous authority-checkpoint SHA,
- external signer key ID,
- opaque authority-checkpoint reference and UTC creation timestamp.

The replay ledger now exposes the same verified historical-prefix lookup behavior as the storage journal so an older signed checkpoint can be checked after later legitimate events.

## Verification and delivery

A checkpoint is accepted only when:

1. canonical JSON has exactly the authority-checkpoint fields,
2. pinned Ed25519 public-key verification succeeds,
3. the storage prefix exactly matches the fully verified local operational journal,
4. the replay prefix exactly matches the fully verified consumed-grant ledger,
5. external create-only delivery reads back the exact original payload and signature and re-verifies both local prefixes.

A linked sequence must begin at the genesis previous-hash, preserve each prior signed checkpoint digest, never decrease either ledger count, make progress in at least one ledger between checkpoints, and never repeat an opaque checkpoint reference.

## What the source tests prove

Synthetic tests cover a valid multi-checkpoint history, storage-journal tamper, replay-ledger tamper, fake external ACK followed by missing/substituted data, omitted middle checkpoint, correctly signed forked parent, no-progress checkpoint, wrong signer and historical replay-prefix verification.

A valid older sequence still returns `actual_external_latest_attested=False`. This is deliberate: local source code cannot prove that an external custodian disclosed its true latest checkpoint or that the external store is immutable.

## Limits

The signer and sink are injected test fakes. SC020 does not create HSM/KMS custody, independently administered WORM, multi-region/provider durability, real latest-tip attestation, authenticated owner alert delivery, trusted time, or production recovery authority. A complete malicious rewrite of both local ledgers and all independent external evidence is outside this local model.

Tower still owns real signer/current-policy/revocation/private service identity. Vault owns canonical archival/backup/recovery receipts and retention. Cloud owns opaque ciphertext storage/integrity/backup infrastructure. Owner approval is still required before any paid provider, real offsite custodian or production release.
