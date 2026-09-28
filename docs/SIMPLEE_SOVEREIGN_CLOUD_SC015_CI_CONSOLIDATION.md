# SIMPLEE SOVEREIGN CLOUD — SC015 CI CONSOLIDATION

Date: September 28, 2026. Based on merged SC014 source head `ffd7586bdf7783adfd4f42051bfb338527857e1d`. Production **NO_GO**. This changes only repository testing triggers and adds a pure source topology regression; it does **not** deploy anything.

## Why

By SC014, changing one Cloud source file scheduled approximately twenty GitHub Actions jobs. Many historical SC001–SC014 specialist workflows re-ran the entire `simplee_cloud/tests/` suite, while the existing `vault-cloud-consolidated-source.yml` already tested all current Cloud tests **plus** actual merged Vault/Tower cross-contract corridors. Every GitHub runner startup can consume the repository's Actions capacity. Repeated full-suite copies are not equivalent to more independent security proof.

## What changes and what does not

The 18 historical specialist workflows remain in the repository, with their original steps and test commands unchanged. They still trigger for a change to their own workflow or historical handoff document and retain their explicitly named source branch push trigger. Their *broad* package-wide `pull_request.paths: simplee_cloud/**` entry is removed so ordinary Cloud code PRs do not schedule eighteen repeated runners. Nothing is deleted.

The **one routine full package PR gate** is now the existing combined [Vault and Cloud source workflow](../.github/workflows/vault-cloud-consolidated-source.yml), for PRs targeting `vault-dev` that change `simplee_cloud/**`, `vault/**`, related Tower/BuyBox evidence contracts or the workflow itself. It runs all Cloud tests, actual Vault crypto/storage/journal/registry/retention/integrity tests and Tower evidence-handoff source tests. The independent pinned older Cloud contract used by Vault interoperability tests is intentionally retained. This check also runs on matching source changes merged into `vault-dev`, and cancels only superseded checks from the **same** PR/ref. It always publishes the production HOLD owner-preflight card beside its test results.

`simplee_cloud/tests/test_sc015_ci_topology.py` checks that all historical specialists remain present and self-scoped, there is exactly one broad Cloud PR regression workflow, the full Vault/Cloud suites and owner HOLD still run, credentials are not persisted and no deployment/production hook has been introduced.

## Risk and release boundaries

This reduces redundant runner use but does **not** remove any source test case from routine Cloud PR acceptance. The initial SC015 transition PR itself will still exercise the historical specialist workflows because each workflow file was changed; following source PRs should normally run the consolidated gate rather than twenty repeats.

Repository rulesets returned an empty list in the authenticated source inspection. Branch protection configuration was not readable through the GitHub App (403), so no claim is made that every external required check is visible. Do not disable a specific required check out-of-band. If repository branch policy later requires a named historical check, reconcile its rule with the consolidated gate rather than force-merging or skipping a protected review.

No provider enrollment, paid Render resource, hosted route, real document access, secrets, Cloud production mode, live signer or owner release decision is affected. New paid infrastructure stays at $0 until explicit separate approval.
