# OBDATA071–075 — Observation Scope + Instrument Binding Authority

Status: **SEALED**

Parent:

`fdc422cc1ea30298b89c482b811d5ce6595347cf`

## Purpose

OBDATA066–070 established temporal validity.

OBDATA071–075 establishes instrument identity and scope authority.

A valid observation is not globally reusable.

It belongs to a specific analytical target.

## Core rule

A current observation may participate in current reasoning only when its instrument identity matches the reasoning target.

For ordinary instruments that means:

- instrument kind;
- symbol;
- underlying identity.

For options that additionally means:

- option right;
- strike;
- expiration;
- contract identity.

## OBDATA071 — Instrument identity

Canonical kinds:

- `EQUITY`
- `ETF`
- `OPTION`
- `INDEX`
- `FUTURE`
- `FOREX`
- `CRYPTO`
- `UNKNOWN`

Option rights:

- `CALL`
- `PUT`
- `NOT_APPLICABLE`
- `UNKNOWN`

Option identities require:

- symbol;
- underlying symbol;
- CALL or PUT;
- strike;
- expiration;
- contract ID.

## OBDATA072 — Observation-scope binding

An observation for:

`SPY`

cannot silently become current truth for:

`QQQ`

Likewise:

`AAPL`

cannot silently become:

`MSFT`.

Instrument-kind mismatch is also blocking.

A stock/ETF observation is not automatically an option-contract observation.

## OBDATA073 — Option-contract binding

Two option observations are not equivalent merely because they share an underlying.

A contract match requires exact:

- symbol;
- underlying;
- CALL/PUT right;
- strike;
- expiration;
- contract ID.

Thus:

`SPY 650C 2026-09-18`

cannot silently become:

`SPY 655C 2026-09-18`

or:

`SPY 650P 2026-09-18`

or:

`SPY 650C 2026-09-25`.

## Underlying boundary

OB may know that an option contract belongs to SPY.

That does not mean SPY-underlying evidence is automatically contract-level evidence.

Likewise, contract-specific evidence is not automatically underlying-level truth.

A future explicit analytical projection layer may define safe transformations.

This pack does not.

## OBDATA074 — Cross-instrument reasoning boundary

A scope mismatch does not erase historical evidence.

The observation remains available for:

- audit;
- review;
- explanation;
- comparison;
- reconstruction.

But it cannot act as current truth for another instrument.

## Relationship to temporal authority

Current reasoning therefore increasingly requires:

`trusted`
+
`current version`
+
`not revoked`
+
`lifecycle eligible`
+
`temporally valid`
+
`instrument scope match`

No one layer may silently override another.

## Preserved boundaries

Instrument authority cannot:

- substitute symbols;
- substitute underlyings;
- turn underlying data into contract truth;
- turn contract data into underlying truth;
- substitute CALL/PUT;
- substitute strike;
- substitute expiration;
- promote one contract into another;
- select a trade contract automatically;
- submit broker orders;
- move capital;
- unlock Manual Live;
- unlock Hybrid;
- unlock Automated execution.

## OBDATA075 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA071–075 tests pass;
2. OBDATA001–075 remains green;
3. OBMODE001–010 remains green;
4. OBUX091–095 remains green;
5. full Observatory `tests/` remains green;
6. generated OB residue is restored;
7. Tower remains untouched;
8. implementation remains byte-identical through testing;
9. exact pack is committed;
10. feature branch is pushed;
11. main is fast-forwarded without force.


## Final validation

- OBDATA071–075 focused regression: **GREEN**
- OBDATA001–075 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Instrument binding is reasoning-scope authority only.

It grants no contract selection or execution authority.
