# OBDATA041–045 — Evidence Lineage + Decision Trace Authority

Status: **SEALED**

Parent:

`eed5998912f0a7e6fe25051f64700db365fea394`

## Purpose

OB now has authority for:

- provenance;
- freshness;
- corroboration;
- quality and anomaly handling;
- effective observation synthesis;
- conflict resolution;
- escalation.

OBDATA041–045 makes that reasoning traceable.

The system must be able to answer:

**Why did this observation become this state?**

## Authority chain

`Source → Provenance → Source Authority → Freshness Evaluation → Cross-Source Corroboration → Observation Quality → Anomaly Evaluation → Effective Observation Synthesis → Conflict Resolution → Escalation Authority → Evidence Lineage → Decision Trace → Effective Observation State`

## OBDATA041 — Evidence lineage identity

Canonical lineage stages:

- `SOURCE`
- `PROVENANCE`
- `SOURCE_AUTHORITY`
- `FRESHNESS`
- `CORROBORATION`
- `QUALITY`
- `ANOMALY`
- `SYNTHESIS`
- `CONFLICT`
- `ESCALATION`
- `FINAL`

Canonical trace states:

- `COMPLETE`
- `PARTIAL`
- `BROKEN`
- `UNKNOWN`

## OBDATA042 — Immutable transformation trace

Every trace step records:

- sequence;
- authority stage;
- input state;
- output state;
- explanation;
- involved source IDs.

Trace steps are immutable.

Past analytical states cannot be rewritten simply because later information changes.

If later evidence changes the answer, that should create a new trace rather than falsify the previous one.

## OBDATA043 — Decision trace authority

The complete trace exposes the exact decision path.

Example:

`SOURCE:OBSERVED`

→ `PROVENANCE:COMPLETE`

→ `SOURCE_AUTHORITY:AUTHORITATIVE`

→ `FRESHNESS:FRESH`

→ `CORROBORATION:CORROBORATED`

→ `QUALITY:VALID`

→ `ANOMALY:NORMAL`

→ `SYNTHESIS:TRUSTED`

→ `CONFLICT:NONE`

→ `ESCALATION:NONE`

→ `FINAL:TRUSTED`

That allows Soulaana to explain not only the result, but how OB arrived there.

## Deterministic trace hash

A canonical hash is generated from:

- observation identity;
- ordered trace steps;
- states;
- reasons;
- source IDs.

The hash helps detect whether a trace changed.

It is evidence identity only.

It is **not** execution authorization.

## OBDATA044 — Explainability + audit boundary

Lineage may support:

- explanation;
- review;
- debugging;
- evidence comparison;
- historical inspection;
- owner review.

It cannot:

- submit a broker order;
- move capital;
- select a contract automatically;
- unlock Manual Live;
- unlock Hybrid;
- unlock Automated;
- override MODE_POLICY;
- override any prior observation authority.

## Missing history

OB does not invent missing trace steps.

A missing required authority stage produces:

`PARTIAL`

A broken step sequence produces:

`BROKEN`

No trace produces:

`UNKNOWN`

The system must not label an incomplete history `COMPLETE`.

## OBDATA045 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA041–045 tests pass;
2. OBDATA001–045 remains green;
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

- OBDATA041–045 focused regression: **GREEN**
- OBDATA001–045 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Evidence lineage and decision tracing remain descriptive authority only.

They do not grant execution, capital movement, contract selection, or mode unlock authority.
