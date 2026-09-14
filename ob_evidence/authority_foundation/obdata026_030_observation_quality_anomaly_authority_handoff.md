# OBDATA026–030 — Observation Quality + Anomaly Detection Authority

Status: **SEALED**

Parent:

`5f3f0b4da3b5173d2d1dd0059d57c8978f9d18df`

## Purpose

OBDATA011–015 established source provenance and source authority.

OBDATA016–020 established freshness authority.

OBDATA021–025 established cross-source corroboration and disagreement authority.

OBDATA026–030 establishes a separate question:

**Is the observation itself structurally credible enough to use?**

A fresh value from an authoritative source may still be malformed, impossible,
broken, anomalous, or unsuitable for normal reasoning.

## Authority chain

`Source → Provenance → Source Authority → Freshness Evaluation → Cross-Source Corroboration → Observation Quality → Anomaly Evaluation → Effective Observation State`

## OBDATA026 — Observation quality identity

Quality:

- `VALID`
- `DEGRADED`
- `INVALID`
- `UNKNOWN`

Anomaly:

- `NORMAL`
- `SUSPECT`
- `OUTLIER`
- `IMPOSSIBLE`
- `UNKNOWN`

Disposition:

- `ACCEPT`
- `REVIEW`
- `QUARANTINE`
- `REJECT`
- `UNKNOWN`

## OBDATA027 — Structural validity authority

Examples of observations that may become invalid:

- non-numeric values
- NaN
- infinity
- policy-impossible negatives
- impossible zero values where zero is forbidden
- values outside configured structural bounds

OB does not manufacture a replacement.

## OBDATA028 — Anomaly detection authority

An observation may be structurally valid but still anomalous.

OB may classify deviation as:

- normal
- suspect
- outlier

An outlier is quarantined rather than silently rewritten.

A median-based peer reference may be used as an analytical anchor only.
It is not a replacement market price.

## OBDATA029 — Observation quarantine boundary

`ACCEPT`

Observation passed quality and anomaly checks.

`REVIEW`

Observation is degraded or suspect.

`QUARANTINE`

Observation is structurally valid but anomalous enough that it must not quietly
flow forward as settled truth.

`REJECT`

Observation is structurally invalid or impossible.

These dispositions do not grant trading authority.

## Preserved boundaries

Observation quality cannot:

- submit broker orders
- move capital
- auto-select contracts
- unlock Manual Live
- unlock Hybrid
- unlock Automated
- override MODE_POLICY
- override source authority
- override freshness
- override corroboration
- fabricate corrected data
- suppress anomalies silently

## OBDATA030 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent test surface is not part of this OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA026–030 tests pass;
2. OBDATA001–030 remains green;
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

- OBDATA026–030 focused regression: **GREEN**
- OBDATA001–030 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Observation quality and anomaly detection remain analytical/data authority only.

They do not grant trade execution, capital movement, contract selection, or mode unlock authority.
