# OBDATA016–020 — Observation Freshness + Staleness Authority

Status: **SEALED**

Parent:

`4a05b1e9bb4120adf0cd78f2efed7c796d8f349a`

## Purpose

OBDATA011–015 established canonical source identity, observation/retrieval provenance,
and source-authority boundaries.

OBDATA016–020 adds the next authority layer:

**Is this observation current enough for the context in which OB is trying to use it?**

An authoritative source can still contain an old observation.
Freshness therefore remains separate from source authority.

## Authority chain

### Operating mode

`Account/Profile → Operating Mode → MODE_POLICY → Effective Policy → Owner Fit`

### Source provenance

`Source → Provenance → Source Authority`

### Observation freshness

`Source Provenance → Freshness Evaluation → Effective Observation State`

## OBDATA016 — Freshness identity

Canonical states:

- `FRESH`
- `AGING`
- `STALE`
- `EXPIRED`
- `UNKNOWN`

## OBDATA017 — Context-specific policy

Freshness is not one universal timer.

A real-time quote, market snapshot, session datum, reference datum, user input,
and derived observation may have different freshness thresholds.

## OBDATA018 — Staleness propagation

Derived information cannot become fresher than its least-current input.

A calculation may preserve or worsen freshness.
It may never launder stale evidence into fresh evidence.

## OBDATA019 — Decision-use boundary

Freshness is descriptive / analytical authority.

It can reduce how confidently OB treats an observation as current.

It cannot:

- submit a broker order
- move capital
- auto-select a contract
- unlock Manual Live
- unlock Hybrid
- unlock Automated execution
- override `MODE_POLICY`
- override source authority
- fabricate missing observations

## OBDATA020 — Regression wall

Observatory validation is scoped to:

`tests/`

Repository-root pytest is intentionally not an Observatory seal wall because Tower
maintains its own independent executable test surface under `tower/`.

No Tower product behavior is changed by this pack.

## Seal rule

This handoff becomes **SEALED** only after:

1. focused OBDATA016–020 tests pass;
2. OBMODE001–010 remains green;
3. OBDATA001–015 remains green;
4. current OBUX091–095 dashboard authority remains green;
5. full Observatory `tests/` surface remains green;
6. generated OB data residue is restored;
7. no Tower mutation survives;
8. exact pack is committed and pushed;
9. `main` is fast-forwarded without force.


## Final validation

- OBDATA016–020 focused regression: **GREEN**
- OBDATA001–020 authority/data regression: **GREEN**
- OBMODE001–010 regression: **GREEN**
- OBUX091–095 dashboard authority: **GREEN**
- Full Observatory `tests/` surface: **GREEN**
- Generated OB data residue: **RESTORED**
- Tower mutation retained: **NO**

Freshness remains descriptive / analytical authority only.
It grants no broker, capital, contract-selection, or mode-unlock power.
