# OBPROOF006–010 — Sanitized Scoreboard Projection

## Sealed parent

`b922d79d98387dc8a6bbb1bfad0e6731d3e63f4f`

## Canonical authority

`OB_PROOF_SANITIZED_SCOREBOARD_V1`

## Source authority

`OB_PROOF_DEMO_ACCOUNT_V1`

## Flow

```text
PROOF / DEMO DURABLE STATE
      ↓
COMPLETED CLOSED PAPER POSITIONS
      ↓
SANITIZED AGGREGATE PROJECTION
      ↓
PUBLIC-SAFE SCOREBOARD METRICS
```

## Public-safe output

- completed sample count
- sample-size band
- wins / losses / flat
- win rate
- aggregate realized paper P&L
- average realized paper P&L
- aggregate positive / negative paper P&L
- profit factor
- explicit simulated / paper disclosure

## Explicitly suppressed

- symbols
- option / instrument IDs
- lifecycle IDs
- candidate fingerprints
- owner-fit fingerprints
- position fingerprints
- entry / exit prices
- quantities / multipliers
- position timestamps
- source payloads
- opening demo cash
- current demo cash
- demo equity
- unrealized P&L
- open-position details

## Boundaries

- projection only
- deterministic for the same durable state
- no durable writes
- no source-state mutation
- no market-truth mutation
- no candidate rescoring
- no broker submission
- no capital movement
- no contract selection
- no Hybrid execution
- no automatic execution
- Live Auto locked
- no Flask route
- no `app.py` change
- no Tower change

## Historical preservation

OBPROOF001–005 evidence and handoff remain untouched as historical records.
The live contract and its transition assertion move from
`PENDING_OBPROOF006_010` to `OB_PROOF_SANITIZED_SCOREBOARD_V1`.

## Next

**OBAUTH001–005 — Canonical Authority Registry**
