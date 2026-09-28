# SIMPLEE SOVEREIGN CLOUD — SC021 OWNER-LOCAL EVIDENCE DESK

Date: September 28, 2026. Based on verified `vault-dev` source commit `407de8a32e63a29a8143820f86aff63fb7c0cb9a` after SC020. This is a pure source function and synthetic test pack, **not a hosted dashboard or release permission**.

## Why this change

The current sources hold separate operational journal metrics (SC014), redacted provider questionnaire (SC003), fixed owner release gates (SC006) and jointly signable storage+grant-replay checkpoints (SC020). Reviewing them separately makes it easier to mistake a green local check or filled evidence-reference field for actual provider security or a production release.

`owner_local_evidence_desk()` composes these already verified sources into one bounded, redacted owner-safe object. It verifies BOTH the local storage event/intents/incidents chain and the separate consumed Tower-shaped nonce replay chain on every call. Optional signed SC020 joint checkpoint evidence must match independent pinned Ed25519 public keys and the exact local storage AND replay ledger prefixes. If either ledger is corrupt, absent, or the checkpoint signer/prefix is wrong, the entire desk fails closed rather than quietly replacing the result with a reassuring card.

Candidate/provider questionnaire and release-gate references are review pointers only. The desk uses the existing strict provider and release-reference validators, reports counts and missing **check IDs** but never displays candidate names, server locations, raw document hashes, signing keys or reference strings. Even if every supplied questionnaire field is filled and a locally valid joint signed checkpoint exists, `production_authorized`, `hosted_receiver_enabled`, `owner_release_recorded`, `actual_external_latest_attested`, `external_immutability_certified` and real provider/Tower/Vault proof remain false. An empty local source journal is explicitly not live health.

## What this does not integrate

This does not call real Tower, accept actual mTLS identity, fetch the Vault production canonical registry, provision or contact a provider, independently authenticate actual physical hardware/server ownership, prove external immutable custody, deliver alarms, accept real user files or release a hosted endpoint. Synthetic tests intentionally demonstrate that arbitrary reviewer-provided refs cannot promote the state to GO, wrong signer/other journal is denied and tampered storage/replay ledgers prevent even local owner display. No environment secrets, paid infra or production modes are introduced.

Owner may run the fixed `python -m simplee_cloud.owner_preflight` report without a local fixture; the richer source desk is an imported internal function requiring the explicitly supplied source-test journal and nonce ledger and optional review objects. It is not exposed over HTTP and does not serve as a replacement for Tower/Vault operational authorization.

Next independent gates remain in [Tower/Vault handoff #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99), with the [no-spend owner pilot packet](https://github.com/LeeTheLilBee/SimpleeMrkTrade/blob/vault-dev/docs/SIMPLEE_SOVEREIGN_CLOUD_SC012_OWNER_PILOT_DECISION_PACKET.md) and [Cloud master tracker #66](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/66). No owner decision is needed for this source-only pack.
