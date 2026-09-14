# OBDATA021–025 — Cross-Source Corroboration + Disagreement Authority

Status: **SEALED**

Parent:

`fe9f93ea33babfd6d10d956f0b92c8260ca244ae`

## Purpose

OBDATA011–015 established source identity and provenance.

OBDATA016–020 established freshness and staleness authority.

OBDATA021–025 establishes what OB does when multiple fresh, valid sources
describe the same thing but do not perfectly agree.

## Authority chain

`Source → Provenance → Source Authority → Freshness Evaluation → Cross-Source Corroboration → Effective Observation State`

## OBDATA021 — Corroboration identity

Canonical states:

- `SINGLE_SOURCE`
- `CORROBORATED`
- `MINOR_DISAGREEMENT`
- `MATERIAL_DISAGREEMENT`
- `CONFLICTED`
- `UNKNOWN`

## OBDATA022 — Cross-source agreement measurement

Independent, fresh-enough observations may be compared.

Agreement and disagreement are explicit and measurable.

A repeated value from the same source does not count as independent corroboration.

## OBDATA023 — Disagreement authority

OB may not silently choose whichever source value is more convenient.

Material disagreement must remain visible.

A source being marked authoritative does not erase disagreement from other valid sources.

## OBDATA024 — Effective observation confidence boundary

Corroboration may strengthen analytical confidence.

Disagreement may reduce analytical confidence.

Neither grants:

- broker submission
- capital movement
- contract auto-selection
- Manual Live unlock
- Hybrid unlock
- Automated unlock
- MODE_POLICY override
- source-authority override
- freshness override

## OBDATA025 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface is not part of this Observatory seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA021–025 regression passes;
2. OBDATA001–025 remains green;
3. OBMODE remains green;
4. OBUX091–095 remains green;
5. full Observatory `tests/` remains green;
6. generated OB residue is restored;
7. Tower remains untouched;
8. exact pack is committed;
9. feature branch is pushed;
10. main is fast-forwarded without force.


## Final validation

- OBDATA021–025 focused regression: **GREEN**
- OBDATA001–025 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Cross-source corroboration remains analytical authority only.
It grants no execution or capital authority.
