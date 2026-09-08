# OBEVENT001–010 — Commands + Events + Causal Invalidation

## Sealed parent

`e5f6456f2c8dfad9276f7f5a2995b10601e3a40c`

## Canonical authority

`OB_COMMAND_EVENT_CAUSAL_V1`

## Core doctrine

**REQUEST ≠ TRUTH.**

A command requests change.

The target domain authority validates and either rejects the command or performs the accepted domain mutation.

Only an accepted domain change becomes an immutable canonical event.

A rejected command remains a durable rejected outcome and produces no domain-truth event.

## Canonical flow

`OB_COMMAND_V1`

→ target canonical domain authority

→ ACCEPT / REJECT

→ if accepted: `OB_DOMAIN_EVENT_V1`

→ causal dependency projection

→ `OB_CAUSAL_INVALIDATION_PLAN_V1`

## Authority boundary

OBEVENT does **not** mutate owner profiles, market truth, trade intent, Proof/Demo state,
policy state, broker state, or capital.

It owns the command/event causal envelope and ledger only.

## Existing domain histories

OBEVENT preserves rather than replaces:

- `OB_TRADE_INTENT_V1` local lifecycle events
- `OB_PROOF_DEMO_ACCOUNT_V1` simulated lifecycle events
- `OB_OWNER_OPERATING_PROFILE_V1` revision history

## Invalidation

Invalidation derives from the canonical authority registry dependency graph.

Only structural downstream dependents become stale/recompute-required.

No whole-system invalidation is performed.

No durable domain state is deleted.

## Causality

Accepted events preserve:

- command ID
- event ID
- correlation ID
- causation event ID
- source authority
- aggregate
- before-state reference
- after-state reference
- event fingerprint
- registry fingerprint
- invalidation-plan fingerprint

## Registry transition

`PENDING_OBEVENT` is retired to `OB_COMMAND_EVENT_CAUSAL_V1`.

Trade Intent, Proof/Demo, and Effective Policy no longer carry an `event_authority`
deferred integration.

The event authority is **not** inserted as a reverse structural dependency.

## Effective Policy

Effective Policy now identifies `OB_COMMAND_EVENT_CAUSAL_V1` as the event authority
for later explicit policy-change adoption.

Policy persistence remains false in OBPOLICY.

OBEVENT does not silently persist or adopt policy.

## Recovery note

The first OBEVENT build stopped because a literal indentation-specific marker count
expected all three deferred integrations to share identical formatting.

They did not.

Trade Intent and Proof/Demo are defined inside the original registry dictionary.
Effective Policy was appended later and uses a different indentation style.

The continuation corrected this by locating each exact authority record independently.

## Hard locks

- no broker submission
- no capital movement
- no automatic contract selection
- no Hybrid execution
- no automatic execution
- Live Auto remains locked
- no `app.py`
- Tower untouched

## Next

`OBCTX001–005 — Canonical Decision Context`
