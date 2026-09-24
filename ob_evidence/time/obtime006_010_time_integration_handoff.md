# OBTIME006-010 Canonical Time Integration + Experimental Binding

## Purpose

OBTIME001-005 created canonical market-time authority.

OBTIME006-010 connects that authority to existing Observatory surfaces without turning time into execution authority.

## OBTIME006 - Experimental simulation binding

A verified OBTIME receipt may bind to a previously broadcast simulation market frame.

The binding is deliberately limited to EXPERIMENTAL.

CONTROL remains the frozen baseline.

INTEGRATED remains the accepted behavior lane.

Neither lane is silently upgraded.

## OBTIME007 - Frame/time alignment

The simulation frame timestamp must exactly match the OBTIME UTC observation instant.

The integration fails closed when:

- the OBTIME receipt is tampered
- the frame timestamp disagrees with OBTIME
- the frame already has an Experimental time binding
- OBTIME reports schedule-date mismatch
- the frame was never broadcast

A CLOSED market session may still be represented as canonical time because "market closed" is valid time truth.

## OBTIME008 - Operating Mode time context

Operating Mode remains its own authority.

Its stored state is not rewritten merely because OBTIME exists.

A separate verified projection may pair:

- immutable mode-state reference
- verified market-time reference

This avoids changing mode-policy identity every market tick and avoids treating an audit timestamp as canonical market time.

## OBTIME009 - Registry activation

The canonical authority registry now recognizes:

temporal_context -> OB_MARKET_TIME_V1

PENDING_OBTIME becomes a retired compatibility alias.

The source-provenance pending slot remains untouched.

## OBTIME010 - Deferred integration semantics

Activating an authority does not mean every existing consumer has already integrated it.

The registry therefore distinguishes:

1. whether an authority is canonical and active
2. whether a specific consumer has adopted that authority

A deferred integration may reference:

- a still-pending authority slot
- an already-active canonical concept whose consumer integration remains deferred

Unknown deferred references still fail closed.

This preserves the truth that older consumers such as candidate truth, options research, account identity, owner-fit eligibility, and Decision Context have not automatically consumed OBTIME merely because OBTIME became active.

## Safety boundary

Time integration cannot:

- submit broker orders
- move capital
- auto-select contracts
- unlock Manual Live 1
- unlock Hybrid
- unlock Automated
- select a winning simulation lane
- mutate Control
- mutate Integrated

## Next

The next OBTIME pack can extend verified time references into additional reasoning and continuity surfaces while preserving the same authority boundaries.
