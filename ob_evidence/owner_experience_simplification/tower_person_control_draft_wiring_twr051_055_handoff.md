# Tower Person Control Draft Wiring / TWR051–TWR055

Branch: `tower-person-control-room-twr046-050`

Parent TWR046–TWR050 commit:

`28cddf770dfa14f05639caef739277f2f3c5a2f8`

## Purpose

TWR051–TWR055 turns Person Control Room buttons into validated Tower draft actions while keeping all live identity and permission mutation disabled.

## TWR051 — Real profile binding

Person rooms load the existing `TowerPersonProfile` data rather than generic placeholder identity.

## TWR052 — Control Room JSON

Adds:

`/tower/owner-dashboard/person/<person_id>/control-room.json`

This returns:

- profile
- allowed designation options
- app matrix
- access levels
- allowed status values
- person-related staged queue items
- fail-closed safety state

## TWR053 — Validated control drafts

Adds:

`POST /tower/owner-dashboard/person/<person_id>/control-draft`

Supports:

- designation
- app access
- responsibilities
- status
- freeze
- restore
- paperwork note

Existing Tower draft builders are reused where available.

## TWR054 — Queue projection

Existing staged queue items are projected into the relevant person room.

## TWR055 — Receipts

The browser submits drafts to Tower and displays the returned validation/receipt packet.

## Persistence boundary

These are validated draft packets.

They are not yet durable database or append-only audit records.

A later layer should add durable owner-reviewed storage.

## Safety

No real accounts, invitations, access grants, access revocations, real freezes, restores, permission mutation, broker execution, capital action, or Live Auto unlock is performed.
