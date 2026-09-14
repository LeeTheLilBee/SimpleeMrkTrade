# OBDATA076–080 — Reasoning Target + Context Composition Authority

Status: **SEALED**

Parent:

`840a6c5b166d3ac3daee080875730513b10e2167`

## Purpose

OBDATA011–075 built individual data-authority layers.

OBDATA076–080 introduces the composition layer that combines those authorities for one exact current reasoning target.

This layer is veto-oriented.

It cannot manufacture authority.

## OBDATA076 — Reasoning-target identity

Each decision is bound to:

- target ID;
- observation ID;
- observation version;
- target symbol;
- target instrument kind;
- reasoning purpose.

This prevents a generic eligibility result from floating free of the context for which it was computed.

## OBDATA077 — Upstream authority composition

The required gates are:

- source/provenance;
- freshness;
- corroboration;
- quality;
- effective observation;
- conflict;
- lineage;
- current version;
- lifecycle;
- revocation;
- rehabilitation;
- temporal validity;
- instrument binding.

No required gate may disappear silently.

## OBDATA078 — Fail-closed eligibility verdict

Canonical gate verdicts:

- `ALLOW`
- `REVIEW`
- `BLOCK`
- `UNKNOWN`

Canonical composition states:

- `ELIGIBLE`
- `REVIEW_REQUIRED`
- `BLOCKED`
- `UNKNOWN`

Composition precedence:

1. any `BLOCK` → `BLOCKED`
2. otherwise any `UNKNOWN` → `UNKNOWN`
3. otherwise any `REVIEW` → `REVIEW_REQUIRED`
4. only unanimous `ALLOW` → `ELIGIBLE`

A missing gate produces `UNKNOWN`.

## Analytical meaning

`ELIGIBLE`

means only:

**this observation may participate in current analytical reasoning for this exact target.**

It does not mean:

- trade;
- buy;
- sell;
- recommend;
- select a contract;
- move capital;
- unlock Manual Live;
- submit an order;
- execute automatically.

## OBDATA079 — Explanation preservation

Composition preserves:

- every gate name;
- every gate verdict;
- every gate reason;
- blocking gates;
- review gates;
- unknown gates;
- target identity.

Soulaana and future review surfaces can therefore explain not merely:

**No**

but:

**No, because temporal validity and instrument binding both blocked this observation.**

## Important authority principle

Composition is not another trust source.

It cannot convert:

`BLOCK`

into:

`ALLOW`

and cannot convert:

`UNKNOWN`

or:

`REVIEW`

into:

`ELIGIBLE`.

It only composes the authority already established upstream.

## OBDATA080 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA076–080 tests pass;
2. OBDATA001–080 remains green;
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

- OBDATA076–080 focused regression: **GREEN**
- OBDATA001–080 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Composition remains analytical eligibility authority only.

It cannot create upstream permission and grants no trading or execution authority.
