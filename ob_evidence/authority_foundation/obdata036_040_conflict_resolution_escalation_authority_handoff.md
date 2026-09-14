# OBDATA036–040 — Observation Conflict Resolution + Escalation Authority

Status: **SEALED**

Parent:

`19b63bc0d1bd437aebc8d7480af9b2d1448a5412`

## Purpose

OBDATA031–035 gave OB an effective observation state.

OBDATA036–040 answers the next question:

**What does OB do when multiple effective observations still conflict?**

The answer is not "pick the best one."

Conflict resolution must preserve evidence, uncertainty, and upstream authority.

## Authority chain

`Source → Provenance → Source Authority → Freshness Evaluation → Cross-Source Corroboration → Observation Quality → Anomaly Evaluation → Effective Observation Synthesis → Conflict Resolution → Escalation Authority → Effective Observation State`

## OBDATA036 — Conflict identity

Canonical conflict states:

- `NONE`
- `RECONCILABLE`
- `AMBIGUOUS`
- `MATERIAL`
- `UNRESOLVED`
- `UNKNOWN`

## OBDATA037 — Safe reconciliation authority

Minor disagreement may sometimes be reconciled analytically.

This means:

- all source observations remain preserved;
- the disagreement remains documented;
- no source is declared the winner;
- no original value is overwritten.

`ANALYTICALLY_RECONCILED` means the difference is manageable for reasoning.

It does **not** mean the sources became identical.

## OBDATA038 — Ambiguity preservation authority

Material disagreement must remain visible.

OB may preserve multiple competing observations as valid evidence.

Ambiguity is a legitimate system state.

OB does not need to manufacture a single answer when the evidence does not justify one.

## OBDATA039 — Escalation authority

Canonical escalation:

- `NONE`
- `REVIEW`
- `OWNER_REVIEW`
- `HARD_BLOCK`
- `UNKNOWN`

Examples:

### REVIEW

Small, manageable disagreement.

Soulaana may explain the conflict and continue guarded analysis.

### OWNER_REVIEW

Material or unresolved ambiguity.

Soulaana should surface:

- what disagrees;
- which sources are involved;
- their effective states;
- confidence states;
- why automatic resolution was refused.

### HARD_BLOCK

One or more observations are unusable or quarantined in a way that makes the conflict unsafe to normalize.

The evidence remains visible, but it cannot become settled observation truth.

## Important doctrine

Escalation is not authorization.

Owner review does not itself:

- unlock Manual Live;
- select a contract;
- submit an order;
- move capital;
- override MODE_POLICY.

It only means the observation requires human judgment.

## Preserved boundaries

Conflict resolution cannot:

- override source authority
- override freshness
- override corroboration
- override quality
- suppress anomalies
- override effective observation synthesis
- manufacture consensus
- silently select a source winner

## OBDATA040 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA036–040 tests pass;
2. OBDATA001–040 remains green;
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

- OBDATA036–040 focused regression: **GREEN**
- OBDATA001–040 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Conflict resolution and escalation remain analytical/data authority only.

Escalation does not grant broker submission, capital movement, contract selection,
or operating-mode unlock authority.
