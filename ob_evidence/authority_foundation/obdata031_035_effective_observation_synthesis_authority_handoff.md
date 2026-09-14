# OBDATA031–035 — Effective Observation Synthesis + Confidence Authority

Status: **SEALED**

Parent:

`91bb64b781298d36605f208db9d19bc634745fa8`

## Purpose

OBDATA011–015 established source provenance and source authority.

OBDATA016–020 established freshness authority.

OBDATA021–025 established cross-source corroboration and disagreement authority.

OBDATA026–030 established observation quality and anomaly authority.

OBDATA031–035 now combines those existing authority layers into one
**effective observation state** for downstream reasoning.

The synthesis layer does not erase or replace any upstream authority.

## Authority chain

`Source → Provenance → Source Authority → Freshness Evaluation → Cross-Source Corroboration → Observation Quality → Anomaly Evaluation → Effective Observation Synthesis → Confidence Authority → Effective Observation State`

## OBDATA031 — Effective observation identity

Canonical states:

- `TRUSTED`
- `USABLE`
- `CAUTION`
- `QUARANTINED`
- `UNUSABLE`
- `UNKNOWN`

## OBDATA032 — Multi-layer synthesis authority

The synthesis layer consumes already-decided upstream states.

It cannot:

- make stale data fresh
- convert disagreement into agreement
- repair invalid data
- suppress an anomaly
- upgrade rejected data
- invent missing authority evidence

## OBDATA033 — Confidence authority

Canonical confidence:

- `HIGH`
- `MODERATE`
- `LOW`
- `NONE`
- `UNKNOWN`

Confidence is categorical and explainable.

There is no hidden or opaque numeric confidence score.

### Example

A value may be:

- from an authoritative source;
- fresh;
- corroborated;
- structurally valid;
- normal;
- accepted;

and therefore synthesize as:

`TRUSTED / HIGH`

But if that same value becomes stale, the authoritative label cannot rescue it.

The effective state must downgrade.

## OBDATA034 — Explainable effective-state boundary

Every effective state retains:

- source authority
- freshness
- corroboration
- quality
- anomaly
- disposition
- reasons
- limitations

Soulaana therefore receives an explainable state rather than a magic confidence number.

## Preserved execution boundary

Effective observation synthesis cannot:

- submit broker orders
- move capital
- select a contract automatically
- unlock Manual Live
- unlock Hybrid
- unlock Automated
- override MODE_POLICY
- override source authority
- override freshness
- override corroboration
- override quality
- override anomaly

## OBDATA035 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA031–035 tests pass;
2. OBDATA001–035 remains green;
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

- OBDATA031–035 focused regression: **GREEN**
- OBDATA001–035 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Effective observation synthesis remains analytical/data authority only.

It does not grant execution, capital movement, contract selection, or mode unlock authority.
