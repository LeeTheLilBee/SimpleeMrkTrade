# Tower ↔ Observatory integration audit — September 28, 2026

**Scope:** current canonical Tower branch and already accepted Observatory simulation. This is an auditable source/runtime inventory, not an authenticated owner acceptance record. No owner credentials or secret environment values were requested, inspected, copied, or added. No deployment, Render setting, paid plan or trading mode is modified by this audit branch.

## Evidence and correction of the previous checkpoint

- [PR #103](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/103), the selective OBSIM016–055 source import, **merged September 27**, merge `6b3351647fe39a2bf180c9b3a5e76b0aad0d4e23`. Do not repeat that import. [PR #95](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/95) also merged as an integration handoff.
- Canonical Tower target examined: `tower-hosted-runtime-identity-twr081-085@306ec81fea24d6d5c14df0434d0c284539040214` (September 28). Source now includes OBSIM056–100: exact hosted synthetic route, in-process isolated workspace, explicit owner JSON tick, Tower session/step-up/operational receipt checks, exact configured HTTPS Origin/Host, CSRF, token rotation on new session, old-token read/mutation race checks, private final evidence export and offline proof inspection, redacted manifest and anonymous two-host probes. The separate local loopback app remains local-only and is not mounted into hosted Tower.
- Current exact-head Python 3.11 syntax gate [run 36408093450](https://github.com/LeeTheLilBee/SimpleeMrkTrade/actions/runs/36408093450) is green. The original #103 diagnostic full suite was **not** green (42 failed/1005 passed); later Tower source repairs and the now-blocking full suite superseded that earlier diagnostic. However the full-suite workflow, until this audit, did **not run for pushes to the canonical Tower branch**, so current-head full-suite success cannot be inferred from the syntax gate.
- This branch adds `tower-hosted-runtime-identity-twr081-085` to the full suite workflow push trigger, keeps the full `python -m pytest -q tests` step blocking without `continue-on-error`, and adds a source audit regression for that trigger and the default-off owner/trading/restart claims. After merge, validate the full gate at the exact canonical head; report any failure, do not count a green unrelated job as a full test result.

## Render service inventory — read-only connected account inspection

| Candidate | Service | Configured source | Latest observed deploy |
| --- | --- | --- | --- |
| Staging workspace owner candidate A | `simplee-tower-ob.onrender.com` | dedicated Tower branch, autoDeploy OFF | `5a4e7f49b121f71b978729357d5f767a3b8ab284` LIVE, published September 27; older than audited Tower source |
| Other Simplee World owner candidate B | `simplee-tower-ob-tunv.onrender.com` | same dedicated Tower branch, autoDeploy ON | `306ec81fea24d6d5c14df0434d0c284539040214` LIVE, September 28 |
| Separate main-based OB service | `simpleemrktrade.onrender.com` | `main`, autoDeploy ON | `cced86992fabdb6a91de3fb3e48a1f1f4aaf0478` BUILD_FAILED; service requests missing root `requirements.txt` and hosted start script is absent from that branch |

**These are account configuration and Render deployment records, not owner-verified HTTP route or authenticated browser evidence.** Neither A nor B is selected as the official owner destination by source freshness alone. The failed main-based service is separate and must not be used as a covert replacement for Tower's front door.

## Source boundary audited

The hosted rehearsal is default OFF unless `OB_OWNER_REHEARSAL_HOSTED_ENABLED=1` **and** a valid exact `OB_OWNER_REHEARSAL_ORIGIN` is provided. Its fixed `/ob/owner-rehearsal` and enumerated JSON subroutes sit behind Tower's current session, step-up, and consumed operational OB launch, with explicit source/owner scope and CSRF/Origin checks. It uses a fake Proof/Demo 10,000-unit harness and owner-declared SYNTHETIC frames. Reports are volatile process memory; even final read/export cannot claim server restart durability. Actual Manual Live, Hybrid, Automated, broker order submission, real capital movement and protected-floor release are not authorized by this route. Source-level manifest booleans explicitly never assert the owner/device walkthrough.

The old Tower branch alternative `obai1` source verifier and accepted main namespace source verifier still require deliberate reconciliation before any distinct real Manual Live clearance wiring. [Draft #68](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/68) is **not** merged and remains a separate owner/account/purpose-specific review authorization request.

## Acceptance sequence / owner boundary

1. Verify canonical owner-used URL and intended workspace/service; do not elect a different destination from deployment dates.
2. Observe a real anonymous fixed-path revision + source-activation tri-state probe against **that exact URL**; public evidence is preflight only, not owner clearance.
3. For enabled hosted beta, require observed current owner Tower login, fresh step-up and actual `/tower/launch/observatory` operational receipt before opening the protected owner rehearsal. An invited tester, anonymous browser, old token, expired session, or wrong host/origin must never receive data.
4. On owner's own device: explicit synthetic sample, due at 30 seconds, one input for each of Control/Integrated/Experimental, pause/resume, stop, private final evidence download and offline chain verification. Show a restart/session-loss test and clear volatile-retention explanation. Do not use real broker credentials or balances.
5. Record exact deployed revision, actual HTTP outcomes, owner-accepted URL, and source/runtime flags without secrets. Mark **HOSTED_OWNER_ACCEPTED** only after separately observed owner walkthrough. Even then production Manual Live remains HOLD.

No paid Render resources, service reconfiguration, feature flag enablement, deployment trigger or real-money API is authorized by this source audit.
