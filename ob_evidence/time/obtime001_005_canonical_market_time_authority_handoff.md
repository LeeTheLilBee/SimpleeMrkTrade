# OBTIME001-005 Canonical Market Time + Session Authority

## Purpose

OBTIME001-005 closes the gap between an observation timestamp and the question:

"What market session and trading date is this observation actually in?"

The prior temporal-validity authority correctly evaluates validity windows, but its compatibility API accepts current trading date and current session from its caller.

OBTIME does not remove that legacy API. It creates the canonical path above it.

## OBTIME001 - Canonical market schedule identity

A schedule is explicit about:

- market
- exchange timezone
- trading date
- open or closed trading-day status
- premarket boundary
- regular-session boundaries
- after-hours boundary
- calendar authority
- calendar reference
- calendar payload hash

Open schedules require all timezone-aware session boundaries in strict order.

Closed schedules cannot contain open-session boundaries.

## OBTIME002 - Canonical market-time receipt

One timezone-aware observation instant is normalized into:

- UTC
- exchange-local time
- exchange-local date
- bound schedule identity
- bound calendar-source identity

The receipt is tamper evident.

## OBTIME003 - Session classification

Market session is derived from the bound schedule.

OBTIME does not treat Monday through Friday as proof that a market is open.

OBTIME does not carry its own hardcoded holiday table.

The calendar/provider adapter remains an explicit upstream boundary.

## OBTIME004 - Temporal-validity binding

The canonical adapter calls the existing temporal-validity authority using:

- evaluated_at from the verified OBTIME receipt
- current_trading_date from the verified OBTIME receipt
- current_session from the verified OBTIME receipt

The canonical adapter has no current_session or current_trading_date caller arguments.

## OBTIME005 - Safety boundary

OBTIME cannot:

- place or submit an order
- move capital
- select a contract automatically
- unlock Manual Live 1
- unlock Hybrid
- unlock Automated
- override provenance
- override freshness
- override quality
- override lineage
- override revocation
- override any other foundation gate

Time authority answers time questions only.

## Next

The next OBTIME pack can bind the verified time reference into the EXPERIMENTAL simulation lane and replace PENDING_OBTIME references in canonical projections only where the receipt is actually present and verified.
