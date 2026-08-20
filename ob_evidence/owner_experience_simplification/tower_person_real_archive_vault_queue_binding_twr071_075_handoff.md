# Tower Person Real Archive Vault Queue Binding / TWR071–TWR075

## Existing handoff reused

This layer binds directly to:

`tower.archive_vault_handoff`

using:

- `build_archive_vault_handoff_record`
- `queue_archive_vault_handoff`

No new transport is created.

## Important truth boundary

The existing Archive Vault handoff currently queues a Tower-side stub.

The existing source explicitly states that the Archive Vault app is not wired yet.

Therefore this layer uses:

`VAULT_HANDOFF_QUEUED`

and does NOT claim:

- Vault accepted
- Vault stored
- Vault sealed
- permanent archival durability

## Person flow

Approved person event

→ TOWER_PERSON_CHANGE_PROOF

→ existing Archive Vault handoff record

→ existing Archive Vault queue

→ handoff ID

→ append-only Tower queue receipt

## Next real boundary

A future Vault-side intake/acceptance layer must consume the queued handoff and issue an explicit Vault acceptance/sealing receipt before Tower can mark the person event `VAULT_SEALED`.
