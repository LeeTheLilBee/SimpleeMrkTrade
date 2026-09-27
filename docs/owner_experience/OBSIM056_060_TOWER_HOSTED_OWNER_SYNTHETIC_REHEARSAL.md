# OBSIM056–060 — Tower-protected hosted synthetic owner rehearsal (opt-in)

**Status:** Stacked over selective Tower source integration #103; source implemented but default-disabled. It is NOT an authenticated live market data product, real account, bank balance, Manual Live/Hybrid/Automated grant, or permanent Archive Vault storage.

## Why this is a distinct hosted adapter

`web.ob_local_owner_rehearsal_ui` is intentionally bound to `127.0.0.1` and explicitly denies reverse-proxy/public traffic. The hosted Tower interface is instead `tower.ob_hosted_owner_rehearsal`, whose exact routes are enumerated in existing fail-closed `tower.ob_web_route_enforcement`, which requires current Tower owner session, step-up and current operational OB launch receipt. The adapter revalidates all three on every request, binds the in-process workspace to the Tower-issued session identifier and owner identity with per-process random HMAC, and never accepts caller-declared owner proof.

### Routes

`GET /ob/owner-rehearsal`; GET `/ob/owner-rehearsal/status.json`, `sample.json`; POST `tick.json`, `pause.json`, `resume.json`, `stop.json`, `new.json`. All other `/ob/*` paths continue to default-deny. The dashboard card appears only when the feature is enabled. No separate local listener is imported into hosted Tower.

### Fail-closed hosted activation

The module is registered by `web/hosted_tower.py` with the feature **OFF by default**. It can only activate with BOTH exact server-controlled environment values, after Tower/source review and accepted deployment choice:

- `OB_OWNER_REHEARSAL_HOSTED_ENABLED=1`
- `OB_OWNER_REHEARSAL_ORIGIN=https://<actual approved HTTPS host>`

The adapter validates exact canonical Host and Origin, current signed Tower session, fresh step-up, operational OB receipt, random per-workspace CSRF token on all API calls, strict no-duplicate/nonfinite JSON, maximum 64KiB mutation, no-store/no-referrer/frame-deny/CSP. Browser uses same-origin Tower session cookie and text-only dynamic rendering, not the standalone loopback assumptions. No GET tick, background job, generated prices, automatic decisions or restored trading session. Client countdown requests read-only status every five seconds.

### Volatile storage doctrine / free-host limit

The sole authorized account is `PROOF-DEMO` with 10,000 **simulated** units; source kind is fixed `SYNTHETIC`. A separate `EphemeralOwnerReportStore` holds copied/hashes-checked reports in Python process memory only, and exposes `VOLATILE_PROCESS_MEMORY_ONLY`, `durable_archive:false`, `restart_recovery:false`. Owner must explicitly stop before starting another session, and New requires the existing session to be stopped. On process restart, deploy, one-hour idle pruning, or worker routing mismatch, earlier reports are lost and no future state can be reconstructed from the page. This intentionally does not pretend that a free Render filesystem is an Archive Vault. The existing hosted startup requires one worker until shared stores are tested; a multi-host topology is not certified.

**This does not meet permanent beta-evidence retention.** Independently approved Tower/Archive Vault/Simplee Cloud storage and auth contracts would be separate work. No paid Render resources or environment settings are changed by source merge. Exact live site/revision, owner device walkthrough, and enabled deployment still require separate acceptance.

### Security and product boundaries

Tester beta remains Survey/Paper under separately authorized accounts; this room is owner-only. This is not an OBML purpose-bound trading review grant (#68), which still needs separate exact account entitlement, revocation and a one-time Tower issuer+OB receiver. Signed mission-account export remains namespace source only, not a Tower owner credential or broker proof. No orders, provider-authenticated prices/fills, live capital, protected floor release, direct BuyBox balance path, or Manual Live/Hybrid/Automated mode unlock.

### Tests

`tests/test_obsim056_060_hosted_owner_rehearsal.py` exercises disabled-by-default, exact approved paths, forbidden anonymous/step-up/access, wrong Host/Origin/CSRF, duplicate/nonfinite JSON, forbidden account/provider claims, 29s early tick, actual 3-lane strict synthetic input after 30s, pause/resume/second unique frame, stop/final, owner-reset token continuity, session rotation and process restart, no-store/CSP and no import of local Flask factory. Existing original OBSIM tests continue. Legacy unrelated Tower whole-suite failures are kept visible as non-release diagnostic, not misreported as a green full suite.

**Before turning the flag on:** select exact active owner URL and workspace/service, verify matching source revision, stable no-paid deployment/build/start, working current Tower owner credentials and operational OB receipt, run an actual browser/device acceptance, and approve volatile-report limitation. Leave flag off if any evidence missing.
