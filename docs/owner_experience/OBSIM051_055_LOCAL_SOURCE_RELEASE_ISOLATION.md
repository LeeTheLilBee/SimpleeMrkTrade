# OBSIM051–055 — local simulation source integration vs hosted release

This acceptance pack explicitly distinguishes three states:

1. **Source merged to the main codebase:** safe if code is dormant until explicitly launched on the owner's device; only a local Proof/Demo runner and source-only backend/test/docs/static files are added.
2. **Owner-local rehearsal:** available through an explicit separate `python -m scripts.ob_local_owner_rehearsal_web --archive ...` command, bound to `127.0.0.1`. It is not a remote service, hosted Observatory route, or Tower owner session.
3. **Hosted owner beta / real Manual Live:** **not authorized by this source merge**; these require independent Tower registration/guard/identity/step-up, runtime revision and actual owner walk-through, real provider proof and separate product/security/compliance decisions. Manual Live, Hybrid and Automated retain their distinct hold gates.

The owner has asked for an actionable app, and OBSIM016–050 now includes the existing three-lane replay engine, protected 30-second cadence, private report archive read/final verification, exact historical/synthetic owner-authored input, local terminal and dark-glass local browser. The parent PR was originally a source-only draft pending a real local interface. This pack verifies it can be accepted **as local-only source** without silently adding a hosted product entry.

## Enforced boundary

- The standalone web module exposes a factory, not a global `app`, and is not imported by `web.app` or `web.managed_staging`.
- Tower's existing fail-closed registry still rejects `/ob/owner-rehearsal`. The owner dashboard template does not load or present a live hosted rehearsal feature.
- The only explicit runner binds `127.0.0.1`, with no debug/reloader, one thread and an owner-initiated process.
- There is no independently authenticated Tower, broker or market source in the local view; Proof/Demo-only capital is simulated and unspendable. No broker submission, real capital movement or unattended tick.
- Existing dedicated Tower branch and draft [Tower actual owner clearance #68](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/68) remain separate. Do not merge competing account source verifiers or infer permission from a signed namespace token.
- Adding these source-only files may trigger ordinary repository CI or an existing host's redeploy configured for main. The local UI still has **no hosted route**; do not represent repository integration as verified live deployment.

## Evidence

`tests/test_obsim051_055_source_release_isolation.py` asserts dormant import/route behavior and explicit local runner policy. Complete upstream HTTP and archive tests plus full repository suite run at exact head. The actual hosted Tower→OB crossing, device walkthrough, paid-provider decisions, and all real-money gates still need independent acceptance.

**No paid Render, production key, broker-order API, capital transfer, Manual Live or Hybrid/Auto mode unlock is allowed by source integration.**
