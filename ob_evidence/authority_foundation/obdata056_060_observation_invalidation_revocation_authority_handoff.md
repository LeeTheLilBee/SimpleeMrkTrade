# OBDATA056–060 — Observation Invalidation + Revocation Authority

Status: **SEALED**

Parent:

`eb3225d5091e5ce892b06a39283c809ddaa55558`

## Purpose

OBDATA046–050 established supersession.

OBDATA051–055 established lifecycle and retention.

OBDATA056–060 establishes explicit invalidation and revocation.

The key distinction is:

**superseded does not mean revoked.**

A superseded observation may have been correct when it was produced.

A revoked observation is explicitly marked as no longer trustworthy as observation truth.

## OBDATA056 — Invalidation identity

Canonical invalidation states:

- `VALID`
- `REVOKED`
- `REVIEW_REQUIRED`
- `UNKNOWN`

## OBDATA057 — Revocation authority

Canonical reasons:

- `SOURCE_COMPROMISED`
- `DATA_CORRUPTION`
- `PROVENANCE_FAILURE`
- `MATERIAL_ERROR`
- `IMPOSSIBLE_OBSERVATION`
- `OWNER_REVIEW`
- `OTHER`
- `UNKNOWN`

Explicit revocation cannot use `UNKNOWN`.

Revocation requires a written note.

## OBDATA058 — Evidence preservation

Revocation preserves:

- observation identity;
- observation version;
- original effective observation state;
- evidence-lineage hash;
- explicit revocation reason;
- revocation explanation.

Revocation does not rewrite the original analytical state.

Instead:

`TRUSTED at time of assessment`

may later become:

`REVOKED because DATA_CORRUPTION was discovered`

Both facts remain visible.

## Review before revocation

If a revocation concern exists but is unresolved:

`REVIEW_REQUIRED`

Current analytical use is blocked.

OB does not prematurely label the observation revoked.

## OBDATA059 — Revoked-history boundary

A revoked observation may be retained for:

- audit;
- debugging;
- reconstruction;
- owner explanation;
- incident review;
- historical comparison.

But it must display a revocation warning.

It cannot be used as current observation truth.

## No automatic reinstatement

This pack provides no API for automatic reinstatement.

A future explicit authority would be required before a revoked observation could ever regain trusted status.

## Preserved boundaries

Revocation cannot:

- delete prior evidence;
- rewrite lineage;
- rewrite versions;
- override lifecycle authority;
- override MODE_POLICY;
- submit broker orders;
- move capital;
- select contracts;
- unlock Manual Live;
- unlock Hybrid;
- unlock Automated execution.

## OBDATA060 — Regression wall

Observatory validation remains scoped to:

`tests/`

Tower's independent pytest surface remains outside the OB seal.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA056–060 tests pass;
2. OBDATA001–060 remains green;
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

- OBDATA056–060 focused regression: **GREEN**
- OBDATA001–060 regression: **GREEN**
- OBMODE001–010: **GREEN**
- OBUX091–095: **GREEN**
- Full Observatory `tests/`: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Revocation remains observation-trust authority only.

It does not delete history and does not grant execution authority.
