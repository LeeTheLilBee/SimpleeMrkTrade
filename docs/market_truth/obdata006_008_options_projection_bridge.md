# OBDATA006–008 — Existing Options Intelligence Projection Bridge

## Purpose

This build does not create another options engine.

The Observatory already contains option selection intelligence, contract
ranking, lifecycle handling, and premium repricing.

OBDATA006–008 makes those existing research outputs available to the canonical
web projection.

## Existing authorities

Preserved without replacement:

- `engine/options_intelligence.py`
- `engine/options_lifecycle.py`
- `engine/vehicle_selector.py`
- `engine/option_repricing.py`

## Canonical path

Existing engine snapshot

→ `/ob/engine-feed-snapshot.json`

→ OBDATA003 `projectPayload(payload)`

→ OBDATA007 options research projection

→ existing Symbol Room `optionsContainers(...)`

No second engine is created.

## Market-truth boundary

Options inherit the existing `displayEligible` projection gate.

Therefore options are not surfaced as canonical room intelligence when
provenance is:

- unknown/incomplete
- demo
- preview
- fallback
- seed
- rehearsal/practice

## Selection authority

Engine scoring and rankings may be displayed as research evidence.

They are not equivalent to a human contract selection.

### Survey

Observe.

### Paper

User chooses the paper contract.

### Manual Live 1

Owner independently chooses the contract.

Owner places the trade externally.

### Hybrid

OB may expose a ranked/objective option set.

User chooses.

### Automated

Existing historical engine best-contract machinery remains preserved for the
future automated lane.

Current automated UX remains locked.

## Hard boundaries

- no duplicate options engine
- no fake option contract fallback
- no browser yfinance
- no direct browser option fetch
- no broker API
- no brokerage execution
- no automatic execution
- no automatic contract selection in Manual Live 1 or Hybrid
