# SIMPLEE SOVEREIGN CLOUD — SC019 ONE-USE GRANT REPLAY LEDGER INTEGRITY

Date: September 28, 2026. Source baseline: merged `vault-dev` commit `ec243f548f37bfd5c971093a180d2e94bd023f98` after SC018. **Source-only / production NO_GO.**

## Gap

SC004 introduced a durable SQLite nonce ledger so each signed Tower grant can be consumed once. Until SC019, the database enforced nonce uniqueness but the consumed rows themselves were not bound into an append-only integrity chain. A privileged source-test process that bypassed SQLite triggers or edited the file could delete or alter a consumed nonce row and potentially make replay state appear different without a local integrity alarm.

## Source hardening

SC019 makes each grant consumption an atomic pair:

- append-only `consumed(nonce_tag, expires_at)`,
- append-only `replay_events(seq, nonce_tag, expires_at, previous_hash, event_hash)`.

The event hash commits the sequence number, opaque SHA-256 nonce tag, expiry and previous event hash. Both tables block UPDATE/DELETE in ordinary SQLite operation. Before every new consumption and every count/read, the complete chain is verified and the consumed rows must exactly equal the event rows in both directions.

A new `verify_chain()` surface returns only safe aggregate metadata: consumed/event count, current head SHA, and explicit `external_checkpoint_certified=False` / `production_authorized=False`.

Old temporary source-test replay databases containing consumed rows without SC019 events fail closed. There is deliberately no silent migration because the missing historical event provenance cannot be reconstructed as trustworthy evidence.

## Adversarial acceptance

The tests cover:

- duplicate nonce replay,
- mutation of nonce tag or expiry,
- deletion of a consumed row,
- insertion of an orphan consumed row,
- mutation or deletion of replay events,
- old unbound source-test DBs,
- eight concurrent unique nonce consumptions into one valid chain,
- and a tampered replay DB blocking a later otherwise-valid signed Cloud read **before provider access**.

Existing SC006B concurrent replay tests continue to exercise same-nonce races through the actual signed-grant verifier.

## Limits

This improves local source integrity only. It does not create independently operated multi-host replay state, HSM/KMS signing custody, external WORM, consensus, high-availability failover, trusted clock infrastructure, or real Tower revocation service. A malicious administrator who can rewrite the complete replay DB and every independent checkpoint is outside this local model.

The real Tower/Vault corridor still needs independently authenticated private service identity, authoritative current policy/approval/step-up/revocation, protected replay persistence across failover, and owner-approved production release. No provider, secret, paid resource, live route or real document is introduced.
