# TWR-TEST001–005 — repair the full Tower diagnostic without changing runtime authority

Base: dedicated Tower branch `20defb4406fd4dbaf65a022cb5ab7e64a19290d7`.
Source-only diagnostic repair. No hosted Manual Live grant, brokerage operation,
capital policy, new service, secrets or paid resource.

## Previous observed baseline

The optional full `pytest tests` step in the historical source-compatibility
workflow logged **42 failed / 1,005 passed** at [run 36335585651](https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36335585651). Because it used
`continue-on-error`, the overall workflow was green even though the diagnostic
was not. The failures included:
- 24+ parametrized OB account-source verifier failures from missing independently
  pinned `obai-source` checkout;
- one missing independently pinned PR #68 request fixture and one missing
  Grounds role source fixture;
- historical Colab-only `/content/SimpleeMrkTrade` paths in four tests;
- owner-home assertions written before the now-real, protected Teller launch;
- stale `skyField` market-map selector, currently `marketMapSky`.

This pack adds exact fixed-SHA source checkouts to the diagnostic workflow
without pretending fixture assertions can be removed; updates the historical
test assertions to describe the actual two protected product entries (OB and
Teller), retains default-deny for Vault/Clouds/Grounds/BuyBox and all execution
capabilities; changes Colab-only tests to repository-relative paths; and
reconciles the expected Market Map mounted element with the actual template.

The full suite remains explicitly diagnostic until its real run and failures
are inspected. A green workflow with a `continue-on-error` step MUST NOT be
cited as clean. If exact-current-head full tests pass, a later commit will
remove `continue-on-error` and make the full suite blocking. No existing
auth/launch/runtime code is modified by the repair. Synthetic pinned source
fixtures are not owner or provider acceptance.

Manual Live L1 remains HOLD per issue #115. Tower's operational OB entry
receipt is not an account/purpose-bound Manual Live grant. Remaining
authentic owner, broker permission, money/protected floors and durable
cross-redeploy replay proof cannot be fabricated from CI.

## First exact-head repair result
[Run 36374278377](https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36374278377): the historical optional full suite improved to **4 failed, 1,179 passed**. Remaining issues identified by actual failure logs: two more independently pinned missing producer/phase fixtures; stale Symbol Page expected mount (`symbolRoomMount` versus actual `obSymbolRoom`); and the product truth audit correctly flagged a literal legacy `draft` comment in `tower/app_registry.py`. This follow-up adds the exact independent checkouts, refreshes only the test selector, and changes the misleading source comment without changing registry behavior. The full suite is still nonblocking until its exact-head rerun proves zero failures.

## Exact-head suite repaired, promote to blocking
[Run 36374477992](https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36374477992) logged **1,183 passed in 23.77s**, zero failures, alongside 51 canonical focused rehearsal/Tower guard passes. Historical 42 failures are now resolved using independent pinned source fixtures, the current actual product-card expectations, portable paths and nonfunctional registry comment/OB template test corrections. The workflow is therefore promoted from `continue-on-error` to a genuinely blocking `pytest -q tests` run. This statement describes source tests, not real Manual Live readiness, owner acceptance or provider-backed durability. The next commit must independently pass with the blocking configuration before merge.
