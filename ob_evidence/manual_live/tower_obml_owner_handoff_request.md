# TWR–OBML001–005 — Tower ↔ Observatory owner-only Manual Live L1 handoff request

**Request for Tower workstream.** Source-only contract, no live permission or deploy. Parent `08049ef80cc22d395cd9d53b48518aa1e02799d8` (accepted OBRES001–005).

The Observatory's next implementation is an owner-only Manual Live **review/readiness** view. User manually submits any eventual order at the **broker website/app**, not through OB API. Existing `/tower/launch/observatory` and protected `/ob/dashboard` should remain the Tower front door; please review current Tower branch PR #22, `tower/ob_tower_bridge_adapter.py`, `tower/ob_mode_clearance.py`, `tower/ob_tower_route_guard.py`, `tower/step_up_auth.py`, and existing owner-launch runtime before implementing. No parallel master-key/role engine, no duplicate authority, no paid Render resources.

## Tower deliverables

1. Implement or identify the **real** Tower server-verified handoff, bound to authenticated owner principal, active session/device, exact OB account identity, explicit purpose `OBML_OWNER_REVIEW`, audience, permitted route, fresh purpose-bound step-up, revocation epoch, issuance/expiry, and one-use nonce. An integrity hash asserted by a client or static manifest does **not** authenticate the issuer. Never embed secrets or raw keycards in OB/browser proof.
2. Define and expose a denial-by-default validation path usable by OB's review UI at the protected Tower crossing. Missing, revoked, stale, cross-account, beta/non-owner, wrong route/purpose/audience, replay, unverified attestation, safety/kill-switch and denied canonical mode all reject. Step-up cannot be inherited merely from an old walkthrough or a changed display flag.
3. Distinguish **Tower identity/route permission** from all other gates: OB canonical operating mode + Effective Policy + OBSAFE/OBREC/OBATTN/OBRES full lineage, fresh market evidence and human Review Center receipt; external broker account/permissions/settlement evidence and actual broker action reconciliation are separate. No source-only claim upgrades to real broker authentication.
4. Return amount-free, redacted allow-for-**review** or denial evidence with source references, not balance data. Log allow/deny decisions and replay/revocation failures without leaking credentials; preserve Tower default-deny and revocation.
5. Add integration/negative tests for owner, beta, account mismatch, purpose/route mismatch, expired and missing step-up, replay, revoked permission and session, forged/source-hash-only attestation, stale evidence, guard denial, and all forbidden execution capabilities. Verify the *actual protected hosted runtime* separately before any status changes from source-only.
6. Send the exact implemented versioned schema/endpoint, validation function and tests back to OB workstream. Until this is done, OBML should render an explicit **Tower handoff unavailable / readiness hold**, never assume a green flag.

## Contract and acceptance

Machine-readable `tower/contracts/twr_obml_owner_handoff_request_v1.json` specifies mandatory fields, deny codes, caps and acceptance cases. It is a **handoff request**, not an assertion that this contract is implemented. No auto broker orders, order API, capital release, Manual Live unlock, Hybrid/Auto or paid deployments from this PR. Owner-only Manual Live trading remains externally gated. BuyBox does not receive OB capital balances; it consumes only Tower-authorized Teller acquisition readiness.

## To the Tower development chat

Please inspect this PR and current Tower implementation, implement missing Tower-owned parts in the canonical Tower branch, and respond with source-evidenced handoff/PR or exact blockers. Do not merge speculative owner token implementations into Tower until identity, session/step-up, revocation and route tests pass. OB can build its **fail-closed consumer** independently while Tower work is pending.
