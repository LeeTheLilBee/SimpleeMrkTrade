# Tower Person Event Ledger + Vault-Ready Packets / TWR056–TWR060

Branch: `tower-person-control-room-twr046-050`

Parent commit:

`957da924e364de182d85420581522d9f41d2039c`

## TWR056 — Person event contract

Introduces canonical append-only Tower person-event records.

Each event carries:

- event ID
- person ID
- display name
- event type
- action
- before state
- requested state
- resulting state
- reason
- Tower validation
- owner-review status
- related receipt IDs
- Vault archival state
- integrity hash

## TWR057 — Append-only local ledger

Tower can append person events to a JSONL-backed operational ledger.

This is intentionally NOT labeled permanent production archive storage.

Vault remains the sealed archive authority.

## TWR058 — Person history

Adds:

`/tower/owner-dashboard/person/<person_id>/history.json`

and:

`POST /tower/owner-dashboard/person/<person_id>/event`

## TWR059 — Vault-ready packet

Adds canonical packet:

`TOWER_PERSON_CHANGE_PROOF`

with schema:

`tower.vault.person-change-proof.v1`

Vault states:

- NOT_READY_FOR_VAULT
- READY_FOR_VAULT
- VAULT_DELIVERY_FAILED
- VAULT_SEALED

Approved owner decisions can produce READY_FOR_VAULT packets.

No delivery happens in this layer.

## TWR060 — Person-room history surface

Person rooms receive operational history and visible Vault archival state.

## Architecture boundary

Browser → Tower only.

Tower → Vault delivery will reuse the existing authorized Vault handoff path in a later adapter layer.

No browser-direct Vault access is introduced.

## Safety

No real account creation, invitation, permission grant/revocation, real freeze/restore, Live Auto unlock, broker execution, or capital action is performed.
