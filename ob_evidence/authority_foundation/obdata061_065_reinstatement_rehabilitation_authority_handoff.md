# OBDATA061–065 — Reinstatement + Rehabilitation Authority

Status: **SEALED**

Parent:

`d30731fcee5692e1e8481d154fe5ae3c7b66c304`

## Purpose

OBDATA056–060 established revocation authority.

OBDATA061–065 establishes the only safe path by which new evidence may support a future observation after revocation.

The revoked record itself is never reinstated in place.

## Core doctrine

A revoked observation remains revoked.

Rehabilitation creates a new observation version.

Example:

`v2 — REVOKED / lineage-A`

New independent evidence arrives.

After explicit review:

`v3 — TRUSTED / lineage-B`

The system records:

`v3 rehabilitates revoked v2`

But v2 remains revoked.

## OBDATA061 — Rehabilitation identity

Canonical states:

- `NOT_APPLICABLE`
- `REVIEW_REQUIRED`
- `APPROVED_FOR_NEW_VERSION`
- `REJECTED`
- `UNKNOWN`

Canonical reasons:

- `SOURCE_RESTORED`
- `CORRECTED_DATA`
- `PROVENANCE_REESTABLISHED`
- `ERROR_CORRECTED`
- `NEW_INDEPENDENT_EVIDENCE`
- `OWNER_REVIEW`
- `OTHER`
- `UNKNOWN`

## OBDATA062 — Explicit rehabilitation review

A rehabilitation attempt begins with:

`REVIEW_REQUIRED`

Approval requires:

- explicit revoked predecessor;
- explicit known reason;
- explicit approval note;
- new evidence lineage.

A revoked lineage cannot be reused as the new lineage.

## OBDATA063 — New-version reinstatement

Approval does not clear revocation.

It authorizes creation of a new analytical version.

A rehabilitated version records:

- observation ID;
- new version number;
- revoked predecessor version;
- revoked predecessor lineage hash;
- new lineage hash;
- new effective state;
- new confidence;
- rehabilitation reason;
- review note.

The new version number must be greater than the revoked predecessor.

## OBDATA064 — Revoked-predecessor preservation

The old record remains:

`REVOKED`

The new record is separate.

No function in this authority may:

- clear revocation;
- delete revocation;
- rewrite the revoked version;
- reuse the revoked lineage;
- mutate the old effective state.

This preserves the exact historical truth:

**OB believed X, later revoked X, then later received enough new evidence to create Y.**

## Failure behavior

If rehabilitation is rejected:

- the revoked observation remains revoked;
- no new version may be created.

If rehabilitation remains under review:

- no new version may be created.

If new lineage is missing:

- no new version may be created.

If the proposed new lineage equals the revoked lineage:

- no new version may be created.

## Preserved boundaries

Rehabilitation cannot:

- submit broker orders;
- move capital;
- select contracts;
- unlock Manual Live;
- unlock Hybrid;
- unlock Automated;
- override MODE_POLICY;
- override upstream data authority.

## OBDATA065 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA061–065 tests pass;
2. OBDATA001–065 remains green;
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

- OBDATA061–065 focused regression: **GREEN**
- OBDATA001–065 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Rehabilitation creates new analytical history.

It never clears or rewrites revoked history and grants no execution authority.
