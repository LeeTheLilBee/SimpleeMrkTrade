# OBDATA086–090 — Evidence Independence + Corroboration-Weight Integrity

Status: **SEALED**

Parent: `188ba92a96310c25f3fac64a04c211789006bd9c`

## Purpose

OBDATA081–085 determines whether evidence may enter a candidate evidence set.

OBDATA086–090 answers a separate question:

> How many genuinely independent confirmations does that evidence represent?

Raw observation count is not corroboration weight.

Three observations that resolve to one source family, one upstream origin family,
or one declared independence family cannot masquerade as three independent confirmations.

## OBDATA086 — Evidence origin identity

Adds explicit:

- observation identity/version
- lineage hash
- canonical source ID
- source-family ID
- upstream origin-family ID
- independence-family ID
- explicit dependency IDs
- dependency-known state

## OBDATA087 — Pairwise independence authority

Pairwise evidence is classified as:

- `INDEPENDENT`
- `DEPENDENT`
- `REVIEW_REQUIRED`
- `UNKNOWN`

Same source, source family, origin family, or explicit dependency cannot receive
separate independent-confirmation credit.

Unknown dependency fails closed for independence credit.

## OBDATA088 — Independence-family composition

Evidence observations are grouped by independence family.

A family is the maximum unit of one independent confirmation.

Multiple observations may remain visible without multiplying corroboration weight.

## OBDATA089 — Corroboration-weight integrity

Corroboration weight is based on independent evidence families rather than raw
observation quantity.

Cross-family declarations that contradict detected dependency relationships fail closed.

Unknown dependency produces `REVIEW_REQUIRED` and receives no additional independent credit.

## OBDATA090 — Regression wall

Protects:

- same-source dependency
- same-family dependency
- same-origin dependency
- explicit dependency
- unknown dependency
- deterministic grouping
- no raw-count inflation
- cross-family contradiction blocking
- exact duplicate blocking
- execution boundary

## Authority boundary

This pack grants **corroboration-counting authority only**.

It does **not** grant:

- trade recommendation authority
- trade ranking authority
- option-contract auto-selection
- broker submission
- capital movement
- Manual Live unlock
- Hybrid execution
- Automated execution

## Important future integration boundary

The source/dependency metadata introduced here is explicit canonical structure,
but this pack does not yet claim that every field is cryptographically or
receipt-bound to OBDATA011–015 provenance.

A later integration/hardening layer must bind these independence receipts to
canonical provenance/lineage/current-version receipts so callers cannot manufacture
independence merely by supplying different family strings.

## Next intended authority

**OBDATA091–095 — Candidate Evidence Sufficiency**

That layer should answer:

> Even after contamination and independence controls, does this candidate have
> enough of the required evidence categories and independent support to justify
> an analytical conclusion?

It must not treat corroboration count alone as sufficiency.
