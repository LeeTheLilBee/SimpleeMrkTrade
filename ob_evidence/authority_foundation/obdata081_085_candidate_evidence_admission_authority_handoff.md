# OBDATA081–085 — Analytical Candidate Admission + Evidence-Set Authority

Status: **SEALED**

Parent:

`9b857104f6f89db33630feca6b3ccfaf32a41800`

## Purpose

OBDATA076–080 established current analytical eligibility for one exact reasoning target.

OBDATA081–085 establishes the next boundary:

**analytical eligibility does not automatically equal candidate admission.**

A candidate evidence set must remain internally coherent.

## OBDATA081 — Candidate evidence identity

Each candidate is explicitly bound to:

- candidate ID;
- reasoning target ID;
- target symbol;
- target instrument kind;
- analytical purpose.

Each evidence item is explicitly bound to:

- observation ID;
- observation version;
- lineage hash;
- reasoning target ID;
- target symbol;
- target instrument kind;
- upstream composition state.

## OBDATA082 — Evidence admission authority

Admission requires upstream composition state:

`ELIGIBLE`

Anything else is blocked.

Candidate identity must also match:

- reasoning target;
- symbol;
- instrument kind.

This layer cannot repair upstream ineligibility.

## OBDATA083 — Contamination controls

The active candidate evidence set blocks:

### Exact duplicate

The exact same observation/version/lineage may not be counted twice.

### Multiple active versions

Version 1 and Version 2 of the same observation may not coexist as independent active evidence inside one candidate set.

A future replacement/supersession workflow can explicitly replace evidence.

This pack does not silently do so.

### Duplicate lineage

Two differently named observations sharing one lineage cannot masquerade as independent corroboration.

That prevents:

`same evidence -> copied twice -> looks like two independent confirmations`

## OBDATA084 — Evidence-set integrity

The evidence set can independently verify itself.

Integrity requires:

- every item explicitly upstream-eligible;
- one reasoning target;
- one target symbol;
- one target instrument kind;
- no exact duplicates;
- no conflicting active versions;
- no duplicate lineage.

Manual construction of an invalid set does not make it valid.

## Relationship to prior authority

Current flow is now:

`observation`
→ upstream data authority
→ reasoning-context composition
→ current analytical eligibility
→ candidate admission
→ evidence-set integrity

Each layer can veto.

Later layers cannot manufacture authority denied earlier.

## Important candidate boundary

A clean evidence set still does **not** mean:

- bullish;
- bearish;
- trade-worthy;
- recommended;
- contract selected;
- capital approved;
- ready for Manual Live.

It means only:

**the evidence packet is structurally admissible for this analytical candidate.**

## OBDATA085 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA081–085 tests pass;
2. OBDATA001–085 remains green;
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

- OBDATA081–085 focused regression: **GREEN**
- OBDATA001–085 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Candidate evidence admission remains analytical packet-integrity authority only.

It grants no recommendation, contract-selection, capital, broker, or execution authority.
