# OBDATA091–095 — Candidate Evidence Sufficiency

Status: **SEALED**

Parent: `3c00ba23ab8024112af832e740d1d8bbdba2d4c6`

## Purpose

OBDATA081–085 answers:

> May this evidence enter the candidate?

OBDATA086–090 answers:

> How much genuinely independent confirmation does that evidence represent?

OBDATA091–095 answers:

> Does the candidate have enough of the required evidence categories and independent support to justify analytical reasoning?

These are separate authorities.

## OBDATA091 — Evidence requirement authority

Adds explicit category requirements with:

- evidence category
- minimum observation count
- minimum independent-confirmation count
- required vs optional status

A requirement cannot have zero minimum support.

Independent-confirmation requirements cannot exceed the required observation count.

## OBDATA092 — Category coverage

Each category is assessed independently.

The assessment records:

- raw observation count
- independent-family count
- unresolved dependency count
- required minimums
- whether the category is satisfied

Evidence from another category cannot silently satisfy the requirement.

## OBDATA093 — Independent-support sufficiency

Raw observation count cannot substitute for independent support.

Example:

Three PRICE observations from one independence family remain three observations,
but provide only one independent confirmation.

If policy requires two independent confirmations, the category is insufficient.

Evidence with unresolved dependency provenance receives no independent-support credit.

## OBDATA094 — Candidate-level sufficiency

Candidate sufficiency fails closed when:

- required categories are missing
- independent support is below requirement
- independence integrity is BLOCKED
- independence integrity is UNKNOWN
- requirements are absent
- requirement categories are duplicated
- required evidence contains unresolved dependency provenance

`REVIEW_REQUIRED` upstream independence cannot become `SUFFICIENT`.

Only explicit satisfaction of every required category under VALID independence
integrity may produce `SUFFICIENT`.

## OBDATA095 — Regression wall

Protects:

- explicit requirement validation
- category isolation
- raw-count vs independent-count separation
- missing required categories
- missing independent support
- unknown dependency handling
- blocked independence integrity
- review-required independence integrity
- unknown integrity
- empty requirements
- empty evidence
- duplicate requirement categories
- optional-category behavior
- authority boundary

## Authority boundary

`SUFFICIENT` means:

> The candidate has enough structurally valid evidence, under the supplied
> requirements, to participate in analytical reasoning.

It does **not** mean:

- bullish
- bearish
- buy
- sell
- hold
- recommended trade
- recommended option contract
- broker permission
- capital permission
- Manual Live permission
- Hybrid permission
- Automated permission

## Known integration boundary

This pack deliberately does not pretend that caller-supplied requirement categories
or independence states are already cryptographically bound to the prior authority chain.

The later foundation integration audit must inspect and harden:

- category identity
- observation-kind binding
- requirement-policy binding
- actual OBDATA086–090 receipt consumption
- actual OBDATA076–080 receipt consumption
- current-version / lifecycle / revocation revalidation
- exact instrument / option-contract binding

## Next intended authority

**OBDATA096–100 — Analytical Conclusion Integrity**

That layer should separate:

- what the evidence directly establishes
- what OB infers
- confidence / uncertainty
- unresolved conflict
- unsupported claims
- conclusion eligibility

It must consume sufficiency without turning `SUFFICIENT` into a trade recommendation.
