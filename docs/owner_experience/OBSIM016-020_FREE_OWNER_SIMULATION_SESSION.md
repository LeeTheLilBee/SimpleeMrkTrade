# OBSIM016–020 — Free on-demand 30-second owner simulation session

**Status: source-only draft; not a deployed owner UI or a live-data service.**

## Owner decision

Build a no-paid-hosting beta session in OB. The owner starts an active session; the
local/active owner UI calls the session adapter at most once every **30 seconds**
with an explicit canonical market frame and one decision for each of Control,
Integrated, and Experimental. A local JSON archive records every accepted tick,
its report hash, lane metrics and deltas, source declaration/freshness, and
event/receipt identifiers. An owner can pause, resume or stop and retrieve prior
reports without relying on GitHub Actions as a perpetual server.

There is no automatic trade selection, no generated market price, no brokerage
connection, no fund transfer, no unattended host, and no paid Render provisioning.

## Existing authority reused

- web/ob_multi_simulation_harness.py: three isolated lanes and accepted fill math.
- web/ob_multi_simulation_replay.py: deterministic fresh-harness replay and
  one explicit decision per lane per canonical market-time frame.
- OBTIME: verifies the market-time receipt. **Time verification is not price-source
  verification.**
- CAPSIM: remains the only Experimental OPEN admission authority, subject to an
  existing effective policy. The session does not change protected floors.
- Replay reports retain simulation-only and no-live-unlock flags.

## Beta adapter contract

1. Start: owner initiates a new unique session ID with a **fresh** accepted OBSIM
   harness and explicit source kind: HISTORICAL / SYNTHETIC / LIVE_OBSERVED.
2. Caller supplies current, timezone-aware time. First tick is due >=30 seconds
   after start; a new tick is due >=30 seconds after the prior accepted tick.
   A timer in the owner-facing UI or local program, **not GitHub**, will call the
   adapter. Browser tab throttling/offline interruptions must be represented
   honestly, not filled in with fabricated 30-second reports.
3. Caller supplies a canonical ReplayStep: frame with source reference, verified
   OBTIME receipt, and three explicit decisions. Missing/stale source input
   must be displayed as waiting/stale, not interpreted as a profitable trade.
4. Adapter replays the accepted history from a fresh harness; on validation,
   policy, or storage failure, it returns no mutated session. The beta
   implementation intentionally limits each session to **120 accepted ticks**
   (one hour at 30-second intervals) to bound full-history replay work.
   A longer-running incremental/checkpoint mechanism needs independent review.
5. Local report per tick: Control, Integrated and Experimental cash/equity,
   realized/unrealized P&L, drawdown, trades, positions and receipt-chain checks,
   plus changes since the prior tick; source kind, age, timestamp, source
   reference, OBTIME receipt ID, event outcome and replay hash.
6. Pause/resume: no backfilling on resume; a fresh 30 seconds must pass.
7. Stop: final summary and original reports remain in the owner-selected local
   folder. Read-back checks hash and sequence. **Report recovery is available**;
   a process restart does not silently restore a live in-memory portfolio from
   report JSON. A new session requires fresh verified replay inputs.
8. Owner beta only. No customer access or real-money order authority is granted.

### No misleading data claims

SourceKind is explicitly declared by the upstream owner/market-data adapter;
this module does **not** authenticate the provider. Reports set
source_claim_verified=false. LIVE_OBSERVED marks a declared observation, not
broker execution or independently confirmed source authenticity. Historical
and synthetic inputs are labelled as such. The UI must not claim live results
while using fixtures or historical replay.

### Local storage and cost

GitHub is source control and CI only, **not** the 30-second job runner. Local
single-writer JSON files are archived under a caller-chosen folder/session ID.
Nothing here schedules a background task or provisions infrastructure. An
active browser/local runner still needs to be wired into the UI; a browser may
pause/trottle background timers, and an owner computer must be on for any
extended local session. Market-data-provider costs, if any, are a separate
decision and not authorized by this PR.

### Explicit out of scope

- No real-time provider integration, scraper, brokerage connection, continuous
  remote job, real account balance interpretation, trading recommendations,
  real or paper broker orders, automatic mode unlocks, or changes to mission
  account and protected-floor policies.
- No automatic source or strategy winner selection from simulation results.
- No 24/7 execution guarantee, no fake reports when the session is stopped.
- No beta deployment or Tower route changes in this PR.

## Acceptance checks

Run:

\`\`\`bash
python -m pytest -q tests/test_obsim016_020_on_demand_session.py
python -m pytest -q tests/test_obsim001_005_multi_simulation_harness.py tests/test_obsim006_010_deterministic_replay.py tests/test_obsim011_015_adverse_scenario_regressions.py
\`\`\`

Before converting this draft to ready for review, wire the owner-facing timer and
source adapter, confirm approved local storage and session authorization in
Tower, test actual pause/offline behavior, and walk through an end-to-end beta
without enabling Manual Live. No paid infrastructure may be provisioned as
part of this feature.
