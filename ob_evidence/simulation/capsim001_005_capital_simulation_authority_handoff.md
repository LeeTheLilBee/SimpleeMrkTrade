# CAPSIM001-005 Canonical Capital Simulation Foundation

## Purpose

CAPSIM begins after the OBTIME family is fully sealed.

The Observatory already has two important sources of truth:

1. Effective Policy owns the owner's restrictive capital limits.
2. OBSIM owns independent lane accounting.

CAPSIM connects those truths without replacing either one.

## CAPSIM001 - Capital policy snapshot

CAPSIM consumes these existing Effective Policy limits:

- max_loss_per_trade_pct
- max_position_allocation_pct
- daily_loss_cap_pct

The snapshot binds:

- account
- Effective Policy ID
- Effective Policy fingerprint
- exact capital limits
- integrity hash

CAPSIM does not widen those limits.

## CAPSIM002 - Capital state snapshot

The capital-state snapshot consumes the existing OBSIM lane state:

- starting capital
- cash
- realized PnL
- unrealized PnL
- equity
- peak equity
- max drawdown

The original simulation lane is not mutated.

## CAPSIM003 - Capital-use assessment

A proposal binds:

- account
- simulation lane
- capital required
- declared maximum loss when known
- risk reference when maximum loss is declared

CAPSIM can immediately block a proposal when it can prove:

- insufficient simulated cash
- position allocation above Effective Policy
- declared per-trade loss above Effective Policy

## Daily-loss truth remains intentionally incomplete

Effective Policy already contains daily_loss_cap_pct.

However, OBSIM001-005 does not yet provide a canonical session/day realized-loss ledger.

CAPSIM001-005 therefore does not pretend to know daily loss.

The daily-loss check remains REVIEW_REQUIRED.

CAPSIM006-010 will derive session/day realized loss from:

- lane-local trade history
- frame identity
- verified OBTIME trading date/session evidence

Only then can daily-loss admission become canonical.

## CAPSIM004 - Fail-closed identity

Capital assessments are bound to:

- account
- simulation lane
- Effective Policy
- capital state
- capital proposal

Tampering changes integrity identity.

Cross-account and cross-lane substitution fail closed.

## CAPSIM005 - Authority boundary

CAPSIM001-005 is simulation only.

It cannot:

- mutate Effective Policy
- widen owner limits
- mutate simulation lane accounting
- select positions
- select strategies
- rank trades
- choose contracts
- submit broker orders
- move real capital
- unlock Manual Live
- unlock Hybrid
- unlock Automated

## PENDING_OBCAP remains pending

This pack does not activate the Effective Policy CAPITAL_POLICY source.

That happens only after the capital authority has a canonical session-loss path and has been integrated into Experimental simulation.

## Next

CAPSIM006-010 should:

- derive trading-date/session realized loss from OBSIM + OBTIME
- turn daily_loss_cap_pct into a real simulation check
- bind verified capital assessment to EXPERIMENTAL OPEN admission
- call the existing OBSIM decision/fill path rather than create a second fill engine
- keep CONTROL frozen
- keep INTEGRATED on the accepted OBTIME baseline
