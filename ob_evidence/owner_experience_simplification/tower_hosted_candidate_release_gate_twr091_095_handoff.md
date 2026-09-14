# Tower Hosted Candidate Release Decision Packet / TWR091–TWR095

## Purpose

TWR086–TWR090 answers:

> Does the hosted runtime exactly match the intended candidate?

TWR091–TWR095 answers:

> Given that parity result, what should the owner review?

## PASS

A valid exact parity pass becomes:

`READY_FOR_OWNER_REVIEW`

This is not deployment authorization.

## FAIL

Any parity failure, malformed result, opened safety boundary, or revision mismatch becomes:

`HOLD`

## Integrity

The release packet receives a canonical SHA-256 integrity hash.

Changing the revision, checks, failures, recommendation, or safety fields invalidates the packet.

## Owner boundary

Every packet requires owner review.

This layer does not record an owner approval and does not execute any release action.

## Safety

The packet always keeps:

- deployment authorization false
- promotion authorization false
- STAGING_READY unchanged
- broker submission false
- capital movement false
- Manual Live false
- Live Auto false

## Branch policy

This layer remains on draft PR #22.

No tower-dev merge, main promotion, or Render deployment occurs in TWR091–TWR095.
