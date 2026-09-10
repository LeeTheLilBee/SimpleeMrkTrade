# OBCTX001–005 — Canonical Decision Context

## Sealed parent

`7fdebbd02c2666c8db78132af0eba278dbdc4663`

## Canonical authority

`OB_DECISION_CONTEXT_V1`

## Core doctrine

A Decision Context is an immutable, hash-bound snapshot of what OB knew and what canonical
authority revisions were bound when a decision context was created.

It is not another decision engine.

It does not recalculate market truth, options research, account identity, owner profile,
Effective Policy, Owner Fit, or event history.

## Canonical bindings

OBCTX binds:

- canonical authority-registry fingerprint
- Trade Intent ID / hash / lifecycle state
- candidate snapshot / fingerprint
- options-research snapshot / fingerprint when available
- explicit account identity / identity fingerprint
- owner operating profile ID / revision / profile hash
- Effective Policy ID / fingerprint
- Owner Fit evaluation fingerprint
- optional causal event lineage
- optional causal invalidation-plan lineage

## Future authorities

OBCTX001–005 does not fabricate authorities that have not been built.

It preserves:

- `PENDING_OBMODE`
- `PENDING_OBDATA011_015`
- `PENDING_OBTIME`

These will be replaced by later canonical authority snapshots only after those authorities exist.

## Registry transition

`PENDING_OBCTX` is retired to `OB_DECISION_CONTEXT_V1`.

The obsolete `decision_context` deferred integration is removed from exactly:

1. market_candidate_truth
2. options_research
3. account_reconciliation
4. owner_operating_profile
5. trade_intent
6. owner_fit_eligibility
7. proof_demo_account
8. account_identity_truth_taxonomy
9. effective_policy
10. event_authority

OBCTX depends on the existing authorities.

The existing authorities are not given a reverse structural dependency on OBCTX.

## Validation correction

`validate_trade_intent()` returns a validation summary.

OBCTX therefore performs:

`validate_trade_intent(intent)`

and then deep-copies the original Trade Intent.

It never substitutes the validation summary for the Trade Intent.

## Immutability

Decision Context is hash-bound.

Mutation of a bound snapshot after construction invalidates the Decision Context fingerprint.

Historical context is replaced by creating a new context after relevant upstream change;
the old context is never rewritten into a different historical decision.

## Hard locks

- no market truth mutation
- no candidate recalculation
- no score or rank recalculation
- no options-research recalculation
- no owner-profile mutation
- no Effective Policy recalculation
- no Owner Fit recalculation
- no event-history mutation
- no automatic contract selection
- no broker submission
- no capital movement
- no Hybrid execution
- no automatic execution
- Live Auto remains locked
- `app.py` untouched
- Tower untouched

## Seal

The build cell performs focused testing, foundation regressions, exact-packet verification,
hash freezing, commit creation, and atomic remote verification.

The exact seal commit is the commit containing this handoff and is printed by the build cell.

## Next

`OBMODE001–010 — Canonical Operating Mode Authority`


## Regression recovery

The initial OBCTX001–005 implementation passed syntax validation, canonical authority
registry validation, real Decision Context construction, and focused OBCTX acceptance tests.

The full foundation regression wall identified one stale pre-OBCTX expectation in
`tests/test_obevent001_010_command_event_causal.py`.

That regression expected the owner operating profile's direct structural dependents to
exclude Decision Context because `OB_DECISION_CONTEXT_V1` did not exist when OBEVENT001–010
was sealed.

With OBCTX active, Decision Context intentionally binds the owner-profile revision used by
a decision. It is therefore correctly a direct structural dependent.

The regression expectation was updated to include `OB_DECISION_CONTEXT_V1`.

No OBEVENT production authority code was modified.
No dependency invalidation was weakened.
No commit, push, or seal occurred before this correction.

A separate continuation-tooling defect was also corrected: whitespace-stripping Git status
parsing truncated the first character of the first porcelain path. NUL-delimited porcelain
parsing is now used for the seal continuation.
