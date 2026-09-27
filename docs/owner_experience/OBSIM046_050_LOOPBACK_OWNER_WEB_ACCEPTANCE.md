# OBSIM046–050 — active local owner browser rehearsal

**Status: source-only standalone loopback application, not hosted Observatory/Tower deployment.** Stacked on [draft #50](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/50), after OBSIM016–045; includes accepted OBBETA011–015 source-trust wording from main. No paid service, external market feed, broker connection, trading, trust-bank balance or capital movement.

## What is now interactive

An actual local dark-glass, mobile-responsive browser surface starts in a separate Python process bound **only** to `127.0.0.1`. It shows three simulation-lane cards, accepted report count, read-only due/countdown hints and historical/synthetic input classification. The owner can explicitly load the labelled fictional example, inspect/edit complete three-lane replay JSON, click **Submit one simulated tick** (only when at least 30 seconds due), pause, resume, stop and inspect final report-only status. The visible status timer requests a read-only snapshot; it **never submits a tick**, downloads prices or invents decisions. If the browser/process closes before Stop, previously saved ticks remain partial/report-only and no session is silently restored.

This is safer than adding a new unapproved `/ob/*` endpoint to a live hosted application or weakening Tower's default-deny route registry. The separate local app exports only a factory and does not register itself with `web.app`, managed staging or hosted Tower. It does **not** authenticate the Tower user. Real owner-hosted acceptance must still use the existing Tower identity/step-up/launch authorities.

## Local use (Python 3.11, existing repository dependencies)

From the project root on the owner's own device:

```bash
mkdir -p "$HOME/ob-private"
chmod 700 "$HOME/ob-private"
python -m scripts.ob_local_owner_rehearsal_web --archive "$HOME/ob-private/reports" --port 8765 --source-kind SYNTHETIC
```

Open **http://127.0.0.1:8765/** on that **same device**. The sample uses a historical-looking **fictional 2026-09-24** frame with declared synthetic source and three explicit HOLD decisions. Selecting SYNTHETIC classifies it honestly; it is not a market-data or calendar vendor. Further ticks require a strictly later observation, distinct frame/decision IDs and human-authored input. Choosing `--source-kind HISTORICAL` requires the pasted envelope's source_kind to match; the synthetic example itself is not relabelled automatically. Only `PROOF-DEMO` receives 10,000 simulated units in this local flow.

## Browser/transport boundary

- Fixed nonprivileged port and exact local host check, local client address required; runner binds only `127.0.0.1`, no debug/reloader, one application process, single-threaded local runner.
- Random process-local token embedded in the same-origin document; all API calls need the token, and every mutation needs an exact local Origin and application/json. No cross-origin permission or cookies.
- No-store, no-referrer, nosniff, deny framing and restrictive CSP. DOM displays dynamic evidence using text nodes, not HTML injection. No browser localStorage of input.
- Content is bounded at 64 KiB. All source envelope fields and three explicit decisions go through the strict OBSIM036–040 adapter and accepted session/OBTIME/CAPSIM replay; no LIVE_OBSERVED from a user JSON, Experimental policy bypass, real accounts, broker orders or modes.
- Report saves remain owner-private single-host; HTTP failures never imply a successful tick. Client requests must be checked against local status/report archive before retry.
- **Not** a remote-user/hosted/multi-process authentication or storage service. The local loopback boundary does not substitute for Tower owner identity, account entitlement, purpose-bound step-up, revocation, provider provenance or hosted acceptance.

## Acceptance

`tests/test_obsim046_050_loopback_owner_rehearsal_ui.py` tests actual Flask GET/POST route behavior: spoofed Host, non-loopback client, missing token/Origin, wrong content type, 29-second early rejection, first explicit tick, pause/resume, second later frame, stop and verified final archive, wrong account/source/provider declarations, CSP and absence of hosted registration or automatic tick. CI checks the browser script, CSS/sample/source syntax, upstream OBSIM and full repo tests at the exact PR head.

**Still required before closing draft #50 or claiming hosted owner beta:** actual Tower-protected product UI integration at a verified revision, an on-device private storage owner walkthrough, and separate source/operator acceptance. Actual Manual Live external gates stay HOLD. No automatic production merge, paid Render or live-mode activation is authorized here.
