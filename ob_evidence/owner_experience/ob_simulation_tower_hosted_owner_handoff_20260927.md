# TOWER ↔ OBSERVATORY — Owner Simulation: Source-to-Hosted Boundary Handoff
**Date:** September 27, 2026  
**Tower base:** `tower-hosted-runtime-identity-twr081-085@f6f0b26e60cb4681e07faf5846ddeb87a58124e9`  
**Accepted OB source:** `main@334a0d6203cd6a05674316d3b4418c99bbc75cc6`, [OBSIM016–055 PR #50](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/50).

## Purpose

OB completed a safe source-only, explicit owner-started Proof/Demo simulation with existing canonical three-lane replay, 30-second due guards, owner-authored historical/synthetic inputs, a private local archive and a runnable dark-glass browser **only on 127.0.0.1**. This PR is a Tower handoff and review request, **not** a route registration, deployment, production Manual Live clearance, permission issuance or paid-resource authorization.

Do not copy the local Flask factory `web.ob_local_owner_rehearsal_ui.create_local_owner_rehearsal_app` straight into hosted Tower. Its exact Host/remote/Origin/token assumptions intentionally reject remote access. Mounting it in a public process, weakening those checks or proxying a loopback endpoint would change its reviewed threat model. Do not expose `/ob/owner-rehearsal` by relaxing default deny.

## Authoritative OB source that Tower needs to inspect

- `web/ob_on_demand_simulation_session.py`: accepted OBSIM016–035 interval guard, capped replay, labelled source and report-only archive.
- `web/ob_explicit_owner_rehearsal_input.py`: accepted OBSIM036–040 exact Proof/Demo account-scoped owner input and canonical OBTIME/OBSIM delegation; SYNTHETIC/HISTORICAL user payload only, no fake live feed.
- `scripts/ob_local_owner_rehearsal.py` and `scripts/ob_local_owner_rehearsal_web.py`: **local-only** reference owner exercise, no hosted entrypoint.
- `web/ob_local_owner_rehearsal_ui.py`, `web/templates/local_owner_rehearsal.html`, local JS/CSS, static `examples/obsim_owner_synthetic_hold_example.json`: real local browser and fictional example, NOT Tower-authenticated.
- Tests `tests/test_obsim016_020_*` through `tests/test_obsim051_055_*`. Exact [#94 run](https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36331522210) passed 20 focused and **1,571 full** tests at the accepted final source tree.
- [OBBETA011–015 #92](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/92) fixed generic owner dashboard "verified" wording: an HTTP 200 or self-declared `verified:true` is only source observation, never independent Tower/provider provenance.

## Distinct Tower work / acceptance contract

**Owner beta Survey/Paper integration, not production Manual Live:** design a dedicated Tower-protected *new* owner rehearsal room, routed only through the existing owner session and canonical Tower→OB launch authority, without changing the six existing OB protected-room behavior. Explicit owner identity, purpose/access scope, current entitlements and verified current hosted revision must be server-derived. Choose/approve a real session/store lifecycle before accepting hosted reports. Existing local files are single-host, owner-private; an ephemeral Render filesystem is **not** certified durable recovery. If durable store and owner path are not verified, show HOLD/source-only, not a fake live browser endpoint. Do not provision paid resources.

Required negative acceptance before any hosted owner UI flag or route is enabled: anonymous/direct URL, invited tester, expired/lost session, owner logout, wrong account, unregistered `/ob/` path, wrong CSRF/Origin, duplicate/replayed source/receipt, stale/future observed frame, fabricated provider authenticity, synthetic sample represented as live, and a paused/closed session all deny or stay report-only. Confirm the actual deployed revision/route rendering by owner walkthrough; source CI is not hosted evidence. Report recovery does not resume a live harness.

The local prototype stays Proof/Demo only, 10,000 **fictional** units. BuyBox must consume deal-specific readiness through Teller/Tower, never direct OB balances. ATM Set 1/Set 2 protected floors are untouched.

## Separate Manual Live permission boundary (do not conflate)

[Draft Tower PR #68](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/68) still requests a real server-owned current owner session, exact mission-account entitlement, fresh account/purpose-bound step-up, revocation and one-time Tower-issued review-only handoff to an independently protected OB receiver. This is **not** supplied by a signed account namespace, local simulation, generic Tower step-up or the owner beta product UI. Distinct broker account/options/settlement/protected capital, Review Center human decision, independent provider order/fill and operating approval remain pending. Manual Live/Hybrid/Automated HOLD. No broker API or capital movement.

**Verifier deduplication alert:** Tower's dedicated branch currently contains `tower/obml_account_identity_source_verifier.py` from its TWR-OBML011–020 source work. Main already accepted canonical `tower/obml_account_namespace_source.py` [#82](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/82) and bounded local source nonce callback `tower/obml_local_source_nonce_ledger.py` [#84](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/84). Both source verifiers inspect the same amount-free `obai1` account-namespace class; **do not silently mount two independent full verifiers as separate permissions or assume the source token grants Manual Live**. Reconcile the negative cases and choose one explicit authoritative production-adapter contract. The local SQLite callback on a free/ephemeral host is not shared multi-host production proof. Do not merge Tower draft #81 as a competing duplicate into main without deliberate reconciliation.

## Done criteria for Tower

A protected and revision-verified owner Survey/Paper rehearsal product page can be entered from Tower; server-controlled current owner/route/session checks pass negative tests, explicit historical/synthetic source receipt remains properly classified, actual browser and storage walkthrough is observed and documented, all deployment/storage dependencies disclosed/approved, and no route/permission or broker/capital boundary is weakened. **Until then: local OB source accepted, hosted feature HOLD, real Manual Live HOLD.**
