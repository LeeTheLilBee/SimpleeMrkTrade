# TWR101–TWR105 — Owner Release Review Room + Protected Decision Routes

Tower now exposes its existing sealed owner-release decision service through an
actual owner-facing release-review room on the canonical Tower Flask application.

- TWR101 loads only a server-owned, sealed, fresh, exact-revision candidate packet.
- TWR102 provides an owner-only release room behind a fresh Tower step-up session.
- TWR103 adds one focused release-review card to the existing owner dashboard.
- TWR104 accepts approve / hold / reject only with same-origin, CSRF, owner,
  step-up, packet-hash, candidate-revision, and existing receipt-ledger gates.
- TWR105 verifies the persisted, append-only owner decision receipt before display.

The release-specific step-up returns to Tower release review. It never launches or
enters Observatory. Missing, stale, tampered, or wrong-revision packets fail closed.

Deployment, promotion, production promotion, STAGING_READY changes, broker
submission, capital movement, Manual Live, and Live Auto remain unauthorized.
A separate Tower release-execution gate is still required.

Observatory checkout remains untouched. This build creates no commit and performs
no push.
