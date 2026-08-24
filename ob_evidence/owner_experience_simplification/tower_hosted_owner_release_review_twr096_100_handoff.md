# TWR096–TWR100 — Owner Release Review + Decision Receipt

## Baseline

Consumes the integrity-sealed hosted candidate release packet from
TWR091–TWR095.

## TWR096 — Owner release review

Builds a read-only owner review projection containing the candidate
revision, parity checks, failures, recommendation, and packet hash.

## TWR097 — Owner session and step-up gate

Requires an authenticated Tower owner session, owner role, verified
owner identity, fresh elevated session, and valid step-up.

## TWR098 — Explicit owner decision

Accepts only:

- APPROVE_RELEASE
- HOLD_RELEASE
- REJECT_RELEASE

Approval is unavailable unless the candidate packet is valid, parity
passes, the expected and actual revisions match, and no validation
failures remain.

## TWR099 — Decision receipt

Persists an append-only, SHA-256 integrity-sealed receipt containing
the owner reference, safe session reference, candidate revision,
decision, reason, packet hash, and previous receipt hash.

Duplicate decisions for the same release packet are rejected.

Hosted environments require an explicitly configured durable receipt
location before an owner decision can be recorded.

## TWR100 — Safety boundaries

An owner release decision does not:

- Deploy or promote a hosted candidate.
- Change STAGING_READY.
- Submit a brokerage order.
- Move capital.
- Authorize Manual Live.
- Authorize Live Auto.

A separate Tower release-execution gate remains required.
