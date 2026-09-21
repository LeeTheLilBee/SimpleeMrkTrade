# OBSIM001-005 Multi-Simulation Harness Foundation

## Purpose

Create one simulation comparison boundary with three isolated lanes:

- CONTROL
- INTEGRATED
- EXPERIMENTAL

The same market frame can be broadcast to all lanes while each lane retains independent capital, positions, decisions, trades, PnL, drawdown, review history, and receipt history.

## Lane doctrine

CONTROL is the frozen comparison baseline.

INTEGRATED represents the newest accepted Observatory behavior.

EXPERIMENTAL is where the next family or candidate behavior can be exercised before acceptance.

The harness does not choose a winning lane and does not promote code automatically.

## Trading simulation doctrine

The harness models simulation-only fills with explicit slippage and commission assumptions.

OPTION positions use multiplier 100.

STOCK positions use multiplier 1.

This harness does not call the existing paper broker, execution handoff, execution loop, or broker APIs. It is a comparison and accounting boundary, not a second decision engine.

## Time boundary

Market frame timestamps may be carried as simulation evidence, but OBSIM001-005 does not claim canonical market/session time authority.

Canonical time remains pending OBTIME.

## Safety boundary

Simulation results are evidence only.

Simulation performance cannot:

- unlock Manual Live 1
- unlock Hybrid
- unlock Automated
- submit broker orders
- move real capital
- select contracts automatically
- create execution authority

## Next

OBTIME can now be developed against the EXPERIMENTAL lane while CONTROL remains frozen and INTEGRATED remains the accepted reference.
