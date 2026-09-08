# OBPOLICY001–010 — Policy Registry + Most-Restrictive Resolver

## Sealed parent

`7eb3eaab90c031f86ca187a8b9dab532d0009825`

## Canonical authority

`OB_EFFECTIVE_POLICY_V1`

Policy layer schema:

`OB_POLICY_LAYER_V1`

## Core architectural decision

OBPOLICY does not create new restriction math.

The sealed primitive remains:

`OB_OWNER_OPERATING_PROFILE_V1.most_restrictive_limits`

OBPOLICY wraps that primitive with source registration, account binding,
layer fingerprints, winning-layer provenance, and effective-policy fingerprints.

## Resolution rules

- Upper bounds: LOWER wins
- Minimum requirements: HIGHER wins
- Permissions: FALSE wins
- Missing execution/capital capability: DEFAULT DENY

## Active policy sources

- PRODUCT_PHASE_LOCK
- OWNER_OPERATING_PROFILE
- EXPLICIT_OWNER_RESTRICTION

Explicit restrictions are non-persistent in this pack.

OBEVENT will later own accepted policy-change events.

## Future policy layers

- PENDING_OBMODE
- PENDING_OBCAP
- PENDING_OBPORT
- PENDING_OBSAFE

None of those pending layers may run early.

## Owner Fit transition

Owner Fit no longer treats raw profile limits as the final effective policy.

It resolves:

OWNER OPERATING PROFILE
+ PRODUCT PHASE LOCK
+ future authorized restriction layers
→ OB_EFFECTIVE_POLICY_V1
→ Owner Fit

The original risk-envelope reference remains intact as source evidence.

## Hard rules

- effective policy cannot widen the owner profile
- mixed-account policy layers fail
- invalid layer fingerprints fail
- exactly one owner-profile baseline is required
- exactly one product-phase lock is required
- policy does not mutate its inputs
- policy does not persist itself
- policy does not authorize execution
- no broker submission
- no capital movement
- no automatic contract selection
- no Hybrid execution
- no automatic execution
- Live Auto remains locked

## Registry transition

`PENDING_OBPOLICY` → `OB_EFFECTIVE_POLICY_V1`

## Next

**OBEVENT001–010 — Canonical Commands + Events + Causal Invalidation**

## Authority graph correction

The first fresh-process OBPOLICY probe correctly exposed an authority dependency cycle:

`OB_OWNER_FIT_ELIGIBILITY_V1`
→ `OB_EFFECTIVE_POLICY_V1`
→ `OB_ACCOUNT_IDENTITY_TRUTH_V1`
→ `OB_PROOF_DEMO_ACCOUNT_V1`
→ `OB_OWNER_FIT_ELIGIBILITY_V1`

The invalid edge was:

`OB_ACCOUNT_IDENTITY_TRUTH_V1`
→ `OB_PROOF_DEMO_ACCOUNT_V1`

That edge was stronger than the implementation.

`web/ob_account_identity_truth.py` does not runtime-import or invoke the Proof/Demo
account service. It uses `OB_PROOF_DEMO_ACCOUNT_V1` as taxonomy/provenance for the
`proof_demo_account` simulated source role.

Therefore the canonical graph is:

`OB_OWNER_OPERATING_PROFILE_V1`
→ `OB_ACCOUNT_IDENTITY_TRUTH_V1`
→ `OB_EFFECTIVE_POLICY_V1`
→ `OB_OWNER_FIT_ELIGIBILITY_V1`
→ `OB_PROOF_DEMO_ACCOUNT_V1`

The Proof/Demo relationship remains preserved as:

- source role: `proof_demo_account`
- authority label: `OB_PROOF_DEMO_ACCOUNT_V1`
- origin class: `SIMULATED`

It is not a reverse runtime dependency.

An acceptance regression now explicitly prevents that false dependency edge from returning.

## Validation precedence

The focused acceptance wall exposed one validation-order issue.

Two copies of the same owner-profile layer violate both:

1. the structural rule requiring exactly one owner operating profile baseline; and
2. the generic duplicate `layer_id` rule.

The canonical resolver now evaluates structural policy invariants first:

1. validate each policy layer;
2. enforce the account boundary;
3. require exactly one `OWNER_OPERATING_PROFILE`;
4. require exactly one `PRODUCT_PHASE_LOCK`;
5. then reject duplicate `layer_id` values.

The duplicate-ID guard remains active.

A separate regression proves duplicate non-structural restriction layers with the same
`layer_id` still fail with `Duplicate policy layer_id`.

