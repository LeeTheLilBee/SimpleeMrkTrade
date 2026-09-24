# CAPSIM006-010 Canonical Session Loss + Experimental Capital Admission

## Purpose

CAPSIM001-005 created the capital-policy snapshot, lane capital-state snapshot, and fail-closed proposal assessment.

Its daily-loss check intentionally remained incomplete.

CAPSIM006-010 closes that gap and introduces the first capital-gated Experimental OPEN path.

## CAPSIM006 - Canonical session-loss ledger

The ledger reads Experimental simulation CLOSE trades.

A CLOSE trade is not assigned to a trading day merely because its frame contains a timestamp.

The canonical path requires:

trade.frame_id
-> Experimental SimulationTimeBinding
-> matching verified OB_MARKET_TIME_V1 receipt

The verified receipt supplies:

- trading date
- market session
- market-time integrity
- exact observation instant

If any historical CLOSE trade cannot be resolved through verified time evidence, coverage is incomplete.

Incomplete coverage cannot silently pass admission.

## Daily-loss semantics

For the selected OBTIME trading date:

net_realized_pnl =
sum(realized_pnl for verified CLOSE trades)

daily_loss_amount =
max(0, -net_realized_pnl)

The ledger also retains:

- gross realized losses
- gross realized gains
- trade IDs
- frame IDs
- market-time receipt IDs
- sessions

This pack uses realized PnL only.

Unrealized PnL remains in OBSIM capital state but is not silently redefined as daily realized loss.

## CAPSIM007 - Projected daily-loss admission

Before a new Experimental OPEN, CAPSIM computes:

projected_daily_loss_amount =
verified current daily_loss_amount
+ declared maximum loss of proposed trade

The percentage denominator is current Experimental simulated equity.

That percentage is compared against the existing Effective Policy `daily_loss_cap_pct`.

No new threshold is invented.

If historical time coverage is incomplete, the daily-loss check becomes UNKNOWN.

If the proposed trade does not have proven maximum loss, the check remains REVIEW_REQUIRED.

Only a fully passing assessment becomes ALLOW.

## CAPSIM008 - Exact OBSIM open-cost preview

CAPSIM does not duplicate fill math.

OBSIM now exposes a read-only OPEN preview using the same internal:

- slippage
- commission
- multiplier
- fill-price math

The real simulated OPEN path itself uses that same preview.

This prevents drift between capital admission cost and actual simulated fill cost.

## CAPSIM009 - Experimental capital admission

The admission wrapper is Experimental-only.

It requires:

- verified current OBTIME receipt
- exact current-frame time binding
- verified session-loss ledger
- Effective Policy capital snapshot
- current Experimental capital-state snapshot
- exact OBSIM open-cost preview
- declared maximum loss and risk reference
- final CAPSIM assessment = ALLOW

Only then does it call the existing OBSIM OPEN path.

The resulting simulation decision carries:

- CAPSIM assessment ID
- session-loss ledger ID
- capital-policy snapshot ID

as evidence references.

CONTROL remains unchanged.

INTEGRATED remains unchanged.

## CAPSIM010 - Authority boundary

This pack does not:

- submit a brokerage order
- move real capital
- choose a contract
- choose a strategy
- rank opportunities
- unlock Manual Live
- unlock Hybrid
- unlock Automated

Simulation performance still grants no Live authority.

## PENDING_OBCAP remains pending

CAPSIM now has a proven runtime simulation capital gate.

However, this pack still does not promote `PENDING_OBCAP` into Effective Policy.

That promotion should be handled separately as a restriction-only policy integration so Effective Policy does not become circular:

Effective Policy -> CAPSIM -> Capital Policy -> Effective Policy

## Next

CAPSIM011-015 should decide and implement the non-circular capital-policy promotion boundary, then close the CAPSIM family if all remaining capital-defense authority is connected.
