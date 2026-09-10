# OBMODE001–010 — Canonical Operating Mode Authority

## Sealed parent

`6c166de83b14b90889d40f20c569c8f595e2b4c6`

## Canonical authority

`OB_OPERATING_MODE_V1`

## Operating modes

- `SURVEY`
- `PAPER`
- `MANUAL_LIVE_1`
- `HYBRID` — future locked
- `AUTOMATED` — future locked

## Core doctrine

Operating Mode answers:

**What kind of Observatory operating environment is this explicit account in?**

Operating Mode does **not** answer how mission capital should behave.
Future Capital Modes belong to OBCAP.

There is no global mode and no implicit default mode.

Each mode state is explicitly account-bound and owner-authorized.

## Current progression

`SURVEY → PAPER → MANUAL_LIVE_1`

Hybrid and Automated transitions are structurally represented but remain locked.

## Manual Live Level 1

Manual Live Level 1 permits the OWNER to use the brokerage separately after review.

It does not grant OB:

- broker submission
- capital movement
- automatic contract selection
- Hybrid execution
- Automated execution

## Effective Policy

OBMODE does not create another risk engine.

`OB_OPERATING_MODE_V1`

→ restriction-only `MODE_POLICY`

→ existing `OB_EFFECTIVE_POLICY_V1`

→ existing Owner Fit

Most-restrictive-wins remains authoritative.

## Trade Intent

New Trade Intents begin with the active mode authority in `UNBOUND` state.

No mode is inferred.

Mode is explicitly bound after account/profile identity and before Owner Fit.

## Decision Context

Decision Context now snapshots the active Operating Mode and verifies that the
Effective Policy contains the matching `MODE_POLICY` fingerprint.

Source provenance and canonical temporal context remain pending.

## Event boundary

OBMODE owns Operating Mode state.

OBEVENT remains the canonical command/event causal authority.

OBMODE exposes hash-bound before/after state references but does not reverse the
OBEVENT dependency graph.

## Hard locks

- no Tower modification
- no `app.py`
- no market truth mutation
- no candidate score mutation
- no capital movement
- no broker submission
- no automatic contract selection
- no Hybrid execution
- no Automated execution
- Live Auto remains locked

## Next

`OBDATA011–015 — Canonical Source Provenance`


## Focused regression recovery

The first focused OBMODE001–010 wall completed the OBMODE source build and canonical
registry probe successfully, with 86 tests passing and three stale pre-OBMODE expectations.

The three expectation corrections were:

1. Owner Fit now structurally consumes both `OB_EFFECTIVE_POLICY_V1` and
   `OB_OPERATING_MODE_V1` as policy inputs.

2. `MODE_POLICY` is now active and runtime-authorized. Future `CAPITAL_POLICY`,
   `PORTFOLIO_POLICY`, and `SAFETY_KERNEL_POLICY` remain pending.

3. A newly created Trade Intent no longer carries `PENDING_OBMODE`. The canonical
   authority now exists, so the intent begins with `OB_OPERATING_MODE_V1` in explicit
   `UNBOUND` state. No account or mode is inferred.

These changes update regression expectations to the new canonical authority graph.
They do not weaken policy, add execution authority, grant broker submission, move capital,
or unlock Hybrid or Automated operation.

No commit, push, or seal occurred before this correction.


## Owner Fit mode-order recovery

OBMODE activation makes Operating Mode an active authority rather than a future
placeholder.

Owner Operating Profile binding still does not select a mode. After profile binding,
Trade Intent carries `OB_OPERATING_MODE_V1` in explicit `UNBOUND` state.

The canonical decision order is now:

`Account / Owner Profile → Operating Mode → MODE_POLICY → Effective Policy → Owner Fit`

Owner Fit therefore fails closed when an explicit Operating Mode has not been bound.

This prevents an owner-fit result from being calculated against an Effective Policy
that accidentally omitted the current operating-mode restrictions.

OBRISK001–005 remains owner-profile authority only and does not choose mode.

OBRISK006–010 test fixtures now bind an explicit PAPER Operating Mode before evaluating
Owner Fit.

No broker submission, capital movement, automatic contract selection, Hybrid execution,
or Automated execution authority was introduced by this recovery.

No commit, push, or seal occurred before recovery.


## Effective Policy helper mode-order recovery

The OBMODE mode-order recovery wall identified one remaining pre-OBMODE test helper in
`tests/test_obpolicy001_010_effective_policy.py`.

`_bound_intent()` still bound the explicit owner operating profile and then returned the
Trade Intent directly to Owner Fit without first binding an Operating Mode.

That helper now follows the canonical OBMODE order:

`Account/Profile → Operating Mode → MODE_POLICY → Effective Policy → Owner Fit`

The helper explicitly binds `PAPER`.

No implicit/default mode is introduced.
No broker submission authority is introduced.
No capital movement authority is introduced.
No Hybrid or Automated execution is introduced.
