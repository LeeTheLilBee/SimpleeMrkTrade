# Archive Vault Intake + Acceptance Receipt / TWR076–TWR080

## Purpose

This closes the application-level queue → intake → acceptance boundary for approved Tower person-change proofs.

## TWR076 — Intake

Archive Vault can consume a queued Tower handoff by handoff ID.

## TWR077 — Validation

The intake validates:

- queued handoff state
- Archive Vault destination
- Tower person-change source type
- TOWER_PERSON_CHANGE_PROOF packet
- packet schema
- Tower → Vault source/destination
- owner approval
- READY_FOR_VAULT state
- archive-ready state
- packet integrity hash
- Tower event integrity relationship

Invalid or tampered packets are rejected.

## TWR078 — Acceptance receipt

Successful intake produces:

- Vault acceptance ID
- Vault receipt ID
- handoff ID
- packet ID
- event ID
- person ID
- acceptance timestamp
- Vault record reference
- acceptance integrity hash

## TWR079 — Logical sealed record

Acceptance records are append-only JSONL application records.

A successful record is application-level `VAULT_SEALED`.

This does not claim hardened off-host or WORM archival infrastructure.

## TWR080 — Tower person history

After acceptance, Tower appends:

`PERSON_ARCHIVE_VAULT_ACCEPTED`

with:

- VAULT_SEALED
- Vault receipt ID
- Vault record reference
- acceptance integrity hash

## Truth boundary

Before this layer:

`VAULT_HANDOFF_QUEUED`

After valid Archive Vault intake:

`VAULT_ACCEPTED → VAULT_SEALED`

No live permission, broker, capital, or Live Auto action is performed.
