# OBSIM026–030 — owner due hint and declared-live source freshness

**Source-only, no new paid service, no timer, no source feed, no real trading.**
Source parent: OBSIM016–025 draft branch obsim016-020-free-on-demand-session,
commit 215d873d1a2d377b993da68de95f899b29e25c32.

## Why this follow-up is needed

The owner-started session already stores three-lane replay reports and has a
30-second timestamp guard. Its source-kind field is explicitly declared:
it does not authenticate market data or broker execution. Before this pack,
a very old LIVE_OBSERVED observation could still advance a simulation tick
while the report merely labelled it STALE, and an at-most-120-second-old
claim was labelled FRESH without the word unverified.

## New source behavior

- inspect_owner_session_due(session, now=...) provides a pure read-only
  countdown/hint for an eventual active owner UI: WAIT_INTERVAL,
  READY_FOR_EXPLICIT_INPUT, PAUSED, STOPPED, or
  BOUNDED_BETA_EXHAUSTED. No background timer, synthetic report, queued
  event, owner authentication or auto tick is created. A ready hint means
  only that a new explicit canonical replay input may be supplied;
  it is not source authenticity, Tower permission or execution readiness.
- A declared LIVE_OBSERVED frame older than 120 seconds now raises before
  replay or report write; future frames remain denied. The caller may present
  a new explicitly sourced frame or leave the session waiting. Historical
  and synthetic replay retain their honest labels and old observations
  are allowed only as labelled historical data.
- Accepted declared-live reports use FRESH_DECLARED_UNVERIFIED, plus
  source_claim_verified=False and source_provider_authenticated=False.
  No price vendor is configured, and no source kind may imply provider
  authentication, live brokerage P&L or real-money settlement.
- No new broker API, Live Mode, Manual Live, Hybrid, Automated, capital
  movement, protected floor, auto winner, selected strategy or owner session
  authority.

## Acceptance

Synthetic regression tests prove no earlier-than-30-second tick hint,
pausing/stop with no backfilling, bounded history, stale/future source
denial before mutation, fresh declared source labelled unverified, old
historical source still labelled historical, and no execution flags. They
run with the established OBSIM016–025 tests and accepted replay suites.
No real owner beta or hosted app is claimed by this pack.

Remaining before real owner beta: an active local owner interface and
approved source adapter, explicit authenticated owner session, actual
on-device storage walkthrough, and independent Tower-protected access
acceptance. This code does not install a perpetual GitHub workflow or
incur recurring infrastructure charges.
