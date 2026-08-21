# The Observatory — Symbol Room / OBUX036–OBUX040

Base source:

`87c60ede441593652e6718cdb0ce6e609eee2948`

Market Map ancestor:

`43d28c9b6a723256d46a85cc34d07f58585fafc0`

Branch:

`ob-symbol-room-obux036-040`

## OBUX036 — Canonical Symbol Room shell

Replaces the legacy Symbol Page shell with a focused owner-facing
investigation room.

The room no longer loads `ob_market_data.js`, because that file is the
quarantined demo/static market fixture boundary.

## OBUX037 — Mode contract

Symbol Room behavior is explicitly defined for:

- Survey
- Paper
- Manual Live 1
- Hybrid
- Automated

The room does not grant itself a higher mode. Missing authority fails
closed to Survey.

## OBUX038 — Options-first investigation

Adds:

- underlying evidence
- canonical source/freshness state
- Options Sky
- expiration map
- strike field
- contract inspection
- Greeks when source-backed
- liquidity/spread context
- star facts
- Soulaana interpretation

Missing options-chain fields remain unavailable. No synthetic chain or
market fallback is generated.

## OBUX039 — Mode-specific page behavior

Survey:
observe / inspect / compare facts.

Paper:
hypothetical paper construction and paper-only Trade Center handoff.

Manual Live 1:
owner independently selects a contract; OB does not select one.
Owner executes externally at the brokerage.

Hybrid:
OB surfaces deterministic matches to displayed objective filters.
The user chooses the option.

Automated:
modeled but locked.

## OBUX040 — Safety acceptance

Every mode keeps:

- broker API false
- brokerage execution false
- automatic execution false
- automatic contract selection false

Symbol Room → Trade Center uses a nonexecuting session handoff packet.

No Tower source files are modified.
