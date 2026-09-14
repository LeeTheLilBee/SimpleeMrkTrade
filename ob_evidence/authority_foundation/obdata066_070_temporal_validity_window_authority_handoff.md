# OBDATA066–070 — Observation Validity Window + Temporal Authority

Status: **SEALED**

Parent:

`8e1db5e2f938847af55ec9a91c29212ecd618717`

## Purpose

Freshness answers:

**How old is this observation?**

Temporal validity answers:

**Does this observation belong to the specific time, trading date, and market session in which OB is trying to use it?**

Those are separate questions.

A fresh observation can still be temporally invalid for the current reasoning context.

## OBDATA066 — Temporal validity identity

Canonical states:

- `VALID_NOW`
- `NOT_YET_VALID`
- `OUT_OF_WINDOW`
- `SESSION_MISMATCH`
- `TRADING_DATE_MISMATCH`
- `UNKNOWN`

Canonical market sessions:

- `PREMARKET`
- `REGULAR`
- `AFTER_HOURS`
- `CLOSED`
- `ANY`
- `UNKNOWN`

## OBDATA067 — Validity-window evaluation

Each temporal window requires:

- timezone-aware `valid_from`;
- timezone-aware `valid_until`;
- `valid_until > valid_from`;
- explicit trading date;
- explicit known session.

The interval is inclusive.

An observation is eligible only when evaluation occurs inside that window.

## OBDATA068 — Session/context binding

An observation bound to:

`REGULAR`

cannot silently become:

`PREMARKET`

or:

`AFTER_HOURS`

truth.

Likewise, an observation from one trading date cannot silently become another date's current truth.

`ANY` permits session-neutral observations but does not bypass date or time-window boundaries.

## OBDATA069 — Out-of-window reasoning boundary

Temporal failure does not erase evidence.

The observation may remain:

- retained;
- historically inspectable;
- auditable;
- explainable;
- comparable.

But it cannot act as current observation truth.

## Relationship to freshness

An observation may be:

`FRESH`

and simultaneously:

`SESSION_MISMATCH`

or:

`TRADING_DATE_MISMATCH`

or:

`OUT_OF_WINDOW`

Temporal authority still blocks current use.

Freshness does not override temporal validity.

Temporal validity does not rewrite freshness.

## Preserved boundaries

Temporal authority cannot:

- widen its own window;
- carry observations between sessions without explicit authority;
- carry observations between trading dates without explicit authority;
- rewrite provenance;
- rewrite freshness;
- rewrite versions;
- clear revocation;
- bypass rehabilitation;
- submit broker orders;
- move capital;
- select contracts;
- unlock Manual Live;
- unlock Hybrid;
- unlock Automated execution.

## OBDATA070 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA066–070 tests pass;
2. OBDATA001–070 remains green;
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

- OBDATA066–070 focused regression: **GREEN**
- OBDATA001–070 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Temporal validity remains analytical eligibility authority only.

It cannot widen its own context and grants no execution authority.
