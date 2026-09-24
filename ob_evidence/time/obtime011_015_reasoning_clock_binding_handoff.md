# OBTIME011-015 Canonical Evaluation Clock + Decision Context Time Binding

## Purpose

OBTIME001-010 established canonical market time, registered it as temporal_context, and connected it to Experimental simulation and Operating Mode.

OBTIME011-015 closes the remaining canonical-clock gap for freshness and Decision Context.

## OBTIME011 - Freshness evaluation clock

The existing freshness authority still owns freshness classification and freshness policy.

OBTIME does not replace it.

The canonical path now supplies `market_time.observed_at_utc` as the evaluation clock through a verified OBTIME receipt.

This prevents the canonical path from inventing `now`.

## OBTIME012 - Active but unbound Decision Context time

OB_MARKET_TIME_V1 is already active.

New Decision Context snapshots therefore may not describe temporal_context as PENDING_OBTIME.

A new context begins with:

- temporal authority = OB_MARKET_TIME_V1
- status = UNBOUND_ACTIVE
- no fabricated receipt
- no fabricated snapshot

Source provenance remains pending.

## OBTIME013 - Verified immutable binding

A verified OBTIME receipt may be bound to Decision Context.

Binding:

- verifies the original Decision Context
- verifies the OBTIME receipt
- rejects schedule-date mismatch
- does not mutate the original context
- creates a new temporal snapshot
- creates a new context fingerprint
- creates a new context ID
- remains non-executing

## OBTIME014 - Historical compatibility

Old Decision Context snapshots may legitimately contain:

PENDING_OBTIME

Those immutable historical snapshots must not become invalid merely because OBTIME later became active.

The validator therefore preserves historical pending-time compatibility.

Upgrading one produces a new immutable snapshot rather than rewriting history.

## OBTIME015 - Integration closure

Decision Context now has an actual OBTIME integration path, so its registry record no longer lists temporal_context as deferred.

Source provenance remains deferred.

## Authority boundary

OBTIME still cannot:

- recommend a trade
- rank trades
- choose a contract
- submit an order
- move capital
- unlock Manual Live
- unlock Hybrid
- unlock Automated

## Family completion

After OBTIME011-015 is accepted and sealed, the OBTIME family is complete.

The next planned family is CAPSIM.

## Regression transition from OBTIME010

OBTIME010 established that an active canonical authority may remain deferred for a consumer that has not integrated it.

OBTIME015 does not reverse that rule.

Instead, Decision Context graduates out of the deferred set because OBTIME011-015 now provides a real verified `OB_MARKET_TIME_V1` binding path.

The remaining consumers still explicitly deferred are:

- market_candidate_truth
- options_research
- account_identity_truth_taxonomy
- owner_fit_eligibility

The historical OBTIME010 regression was updated to preserve the original rule while recognizing the new Decision Context integration.
