# OBDATA046–050 — Observation Versioning + Supersession Authority

Status: **SEALED**

Parent:

`7f0c4de4d56be585dfbf8730eca9521e3d3f1e85`

## Purpose

OBDATA041–045 established immutable evidence lineage.

OBDATA046–050 establishes what happens when new evidence changes an observation.

The old observation is not rewritten.

A new version is created.

## Authority chain

`Source → Provenance → Source Authority → Freshness Evaluation → Cross-Source Corroboration → Observation Quality → Anomaly Evaluation → Effective Observation Synthesis → Conflict Resolution → Escalation Authority → Evidence Lineage → Observation Version → Supersession Authority → Current Effective Observation`

## OBDATA046 — Observation version identity

Canonical version states:

- `CURRENT`
- `SUPERSEDED`
- `HISTORICAL`
- `UNKNOWN`

An observation may have multiple historical versions.

Only one version may resolve as current.

## OBDATA047 — Immutable version history

Observation versions are immutable.

If v1 said:

`TRUSTED / HIGH`

and new evidence changes the result to:

`CAUTION / MODERATE`

OB does not rewrite v1.

It creates v2.

v1 remains historically intact with its original lineage hash.

## OBDATA048 — Supersession authority

A superseding version must explicitly record:

- its own version number;
- which previous version it supersedes;
- why it supersedes it;
- its own effective state;
- its own confidence;
- its own lineage hash.

Canonical supersession reasons:

- `FRESHER_EVIDENCE`
- `CORROBORATION_CHANGED`
- `QUALITY_CHANGED`
- `CONFLICT_CHANGED`
- `MANUAL_REVIEW`
- `OTHER`
- `UNKNOWN`

Supersession is explicit.

It is never inferred by silently replacing an old record.

## OBDATA049 — Current-version resolution + history boundary

A valid history must:

- begin at version 1;
- remain contiguous;
- contain no duplicate version numbers;
- contain only one observation identity;
- explicitly link each later version to its immediate predecessor.

Example:

`v1 → v2 → v3`

not:

`v1 → v3`

and not:

`v1 → v2`
`v1 → v3`

Every older version remains preserved.

The latest valid version resolves as current.

## Important distinction

`SUPERSEDED` does not mean:

- false;
- deleted;
- invalid history.

It means:

**this was the effective observation at that time, but later evidence produced a newer effective version.**

That distinction matters for:

- review;
- debugging;
- owner explanation;
- historical analysis;
- future Manual Live receipts.

## Preserved safety boundary

Versioning and supersession cannot:

- submit broker orders;
- move capital;
- auto-select contracts;
- unlock Manual Live;
- unlock Hybrid;
- unlock Automated;
- override MODE_POLICY;
- override source authority;
- override freshness;
- override corroboration;
- override quality;
- override anomalies;
- override synthesis;
- override conflict authority;
- rewrite evidence lineage.

## OBDATA050 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA046–050 tests pass;
2. OBDATA001–050 remains green;
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

- OBDATA046–050 focused regression: **GREEN**
- OBDATA001–050 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Observation versioning and supersession remain analytical/data-history authority only.

They do not grant execution, capital movement, contract selection, or mode unlock authority.
