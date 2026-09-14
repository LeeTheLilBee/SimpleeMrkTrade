
# OBDATA011–015 — Canonical Source Provenance

Parent: `3ddef544f44275e63f7c58ea0ef6dbcb31ebcb26`

Status: **UNSEALED**

## Purpose

This pack introduces a canonical provenance contract for Observatory data and
derived observations.

Every provenanced observation can identify:

- the source identity;
- the source kind;
- the source's data-authority classification;
- when the observation occurred;
- when the observation was retrieved;
- the instrument, provider event ID, and sequence when available.

## Authority boundary

`SourceAuthority.AUTHORITATIVE` means authoritative **as a data source**.

It does **not** mean:

- trade authority;
- broker authority;
- capital authority;
- operating-mode authority;
- Manual Live authorization;
- Hybrid authorization;
- Automated authorization.

The existing chain remains:

`Account/Profile → Operating Mode → MODE_POLICY → Effective Policy → Owner Fit`

Provenance is descriptive evidence feeding Observatory reasoning. It is not an
execution grant.

## Tower boundary

No `tower/` source is part of this pack.

## Seal condition

Do not seal until:

1. focused OBDATA tests pass;
2. existing OBMODE wall passes;
3. broader Observatory tests pass;
4. no Tower paths are changed;
5. worktree contains only the intended OBDATA pack.


## Dashboard regression supersession

OBUX091–095 is the current dual-dashboard replacement authority.

Sixteen older dashboard regression modules were retired because they encoded superseded
pre-OBUX091 dashboard information-wall, atmosphere, hierarchy, and presentation expectations.
They are not restored as product behavior.

Replacement regression:

`tests/test_obdata011_015_superseded_dashboard_expectations.py`

Canonical dashboard authority:

`tests/test_ob_dual_dashboard_replacement_obux091_095.py`

Validation boundary:

- Observatory seal wall: `tests/`
- Tower's independent `tower/` pytest surface is not part of the OBDATA seal wall.
- Repository-root pytest is not used for this Observatory seal because Tower collection/execution
  writes tracked `tower/data/*` status artifacts.
- No Tower source or product behavior is modified by OBDATA011–015.
