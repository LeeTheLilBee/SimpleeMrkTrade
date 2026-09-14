# OBDATA051–055 — Observation Lifecycle + Retention Authority

Status: **SEALED**

Parent:

`fd3f2dce5695aad842aa6ee80c1fda351193b6e9`

## Purpose

OBDATA046–050 established versioning and supersession.

OBDATA051–055 establishes the lifecycle of those observations.

The key distinction is:

**retained history is not automatically current analytical truth.**

## Authority chain

`Source → Provenance → Freshness → Corroboration → Quality → Anomaly → Effective Observation → Conflict / Escalation → Evidence Lineage → Observation Version → Supersession → Observation Lifecycle → Current-Reasoning Eligibility → Retention / Archive State`

## OBDATA051 — Observation lifecycle identity

Canonical lifecycle states:

- `ACTIVE`
- `SUPERSEDED`
- `HISTORICAL`
- `ARCHIVED`
- `RETAINED_EVIDENCE`
- `UNKNOWN`

These states describe what role an observation currently plays.

## OBDATA052 — Current-reasoning eligibility

Canonical eligibility states:

- `ELIGIBLE`
- `REVIEW_ONLY`
- `INELIGIBLE`
- `UNKNOWN`

Examples:

### CURRENT + TRUSTED

`ACTIVE / ELIGIBLE`

### CURRENT + USABLE

`ACTIVE / ELIGIBLE`

### CURRENT + CAUTION

`ACTIVE / REVIEW_ONLY`

### CURRENT + QUARANTINED

`RETAINED_EVIDENCE / INELIGIBLE`

### CURRENT + UNUSABLE

`RETAINED_EVIDENCE / INELIGIBLE`

### SUPERSEDED

Always excluded from current reasoning.

### HISTORICAL

Always excluded from current reasoning.

## OBDATA053 — Retention + archive authority

Canonical retention states:

- `HOT`
- `WARM`
- `ARCHIVE`
- `PERMANENT_EVIDENCE`
- `UNKNOWN`

Retention describes storage/evidence posture.

It does not grant analytical authority.

A superseded observation may remain `PERMANENT_EVIDENCE` while also being `INELIGIBLE` for current reasoning.

## OBDATA054 — Historical evidence boundary

Historical records remain available for:

- audit;
- owner explanation;
- review;
- debugging;
- comparison;
- future receipts;
- later reconstruction of what OB knew at a particular time.

Historical retention does **not** mean Soulaana may use that observation as current market truth.

## No implicit reactivation

A superseded or historical observation cannot become current merely because:

- the newer version disappears;
- it was once trusted;
- it is retained permanently;
- an archive record is reopened.

A future authority pack may explicitly define restoration/reinstatement if needed.

This pack does not.

## Preserved boundaries

Lifecycle authority cannot:

- rewrite version history;
- erase audit history;
- delete superseded evidence;
- reclassify archived records as current truth;
- override source authority;
- override freshness;
- override corroboration;
- override quality;
- override anomaly authority;
- override synthesis;
- override conflict handling;
- override evidence lineage;
- grant broker execution;
- move capital;
- unlock an operating mode.

## OBDATA055 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA051–055 tests pass;
2. OBDATA001–055 remains green;
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

- OBDATA051–055 focused regression: **GREEN**
- OBDATA001–055 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Observation lifecycle and retention remain analytical/history authority only.

Retention never grants execution authority or current-truth status.
