# SIMPLEE SOVEREIGN CLOUD — SC034 BACKUP KEY ROTATION / HISTORICAL RESTORE CONTRACT

Date: October 1, 2026. Based on merged SC033 `vault-dev` commit `8ac967c9b87527ccdcf63aa79931badcbbec6ec8`. Source-only; production remains **NO_GO**.

## Gap

The original backup service intentionally used one separately supplied 32-byte AES-256-GCM backup key plus one opaque key reference. That is sufficient for a fixed synthetic test key, but it cannot model a normal future rotation: if new backups move to key v2, old immutable backups written under key v1 still need exact historical key resolution during a separately authorized restore.

SC034 keeps fixed-key mode for all existing source fixtures and adds an **optional injected key resolver**. Cloud still stores only the opaque `key_reference` in the immutable backup intent/receipt. It does not own a key catalog. Resolver mode may fetch the exact 32-byte key for the receipt's historical reference; a future KMS/HSM/custodian must implement that outside this package.

For new backup creation, the active key reference is resolved **before any primary ciphertext provider read**. Key service unavailability therefore denies without needlessly reading protected source bytes and without reserving/writing a backup. For restore verification, the historical receipt's key reference is resolved **before backup provider GET**. A retired/unavailable key denies before reading backup bytes. If the resolver returns a different 32-byte key under the same reference, SCB1 AES-GCM authentication fails rather than silently re-labeling or corrupting provenance.

A rotated service can use active `backup-key-v2` for new immutable backups while still verifying a durable old receipt carrying `backup-key-v1`, provided the external resolver can still supply v1. The same logical backup request cannot be replayed under a different active key; its durable original `key_reference` remains authoritative and the request fails as an idempotency conflict.

## Source tests

The tests cover:

- new v2 backups plus old v1 restore through one external resolver;
- retired v1 reference denied before backup-provider read;
- wrong v1 key material causing cryptographic authentication failure;
- forged/unknown key reference denied before backup-provider read;
- active key resolver outage denied before primary-provider read and before backup reservation;
- invalid resolver key length and ambiguous fixed+resolver construction rejected;
- legacy fixed-key mode remains compatible and rejects a foreign receipt key reference;
- an existing logical backup request cannot be rebound to a newly active key.

## What remains external

This is **not** KMS/HSM integration, dual control, escrow, rotation schedule, cryptoperiod policy, key deletion ceremony, legal recovery custody, hardware-backed keys, external audit, or proof that old keys are safely available during an actual disaster. The callback used by tests is an in-memory dictionary.

A real release still needs independently authenticated KMS/HSM/key-custody evidence, least-privilege identities, rotation and revocation policy, recovery/escrow procedure, old-key availability drill, owner-approved RPO/RTO and full Tower/Vault/provider authorization. No production secrets, provider account, paid resource or live route are introduced.
