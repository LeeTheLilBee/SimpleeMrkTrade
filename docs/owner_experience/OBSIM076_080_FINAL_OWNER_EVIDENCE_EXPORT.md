# OBSIM076–080 — owner-finalized synthetic evidence download and offline verification

**Scope:** opt-in, existing Tower-protected owner hosted rehearsal only. No new storage provider, service, secret, account entitlement, market source, broker, order API, real capital or trading mode. The hosted beta remains default **OFF** unless its separately reviewed exact HTTPS origin and feature flag are configured. A local 127.0.0.1 rehearsal and any canonical Tower owner session/receipt remain separate.

## Why this is needed

OBSIM056–065 deliberately store synthetic Proof/Demo reports only in the single running Python worker's volatile memory. A process restart, redeploy, workspace expiration, or clicking New may destroy those results. A visible final hash alone is not an owner-held record. This pack lets the already-authorized owner deliberately copy a **completed and stopped** synthetic report-only chain to their device without pretending the free hosted instance acquired durable recovery.

## Exact protected workflow

Open Tower → successfully authenticate and step up → use the canonical Tower→OB owner launch → enter the explicitly enabled Owner Rehearsal. Submit your own SYNTHETIC three-lane steps at due intervals. Click **Stop & finalize volatile report**, then **Save finalized Proof/Demo evidence**. Check that the browser actually saved the JSON before New/redeployment.

The read-only `GET /ob/owner-rehearsal/evidence.json` is an exact new path in Tower's default-deny allowlist. It passes the same every-request owner/session/step-up/operational-OB-receipt, exact Host, active workspace and per-workspace token controls. It is not callable without a finalized terminal record; requests before Stop are denied. No anonymous, wrong-token, expired Tower, different-host, superseded-token or reset session can export another workspace.

The service independently rehashes the complete source-only report chain, exact sequence, session binding, three lane scope, source classification and final terminal link. It refuses mismatches rather than trusting `report_hash` fields as permission. The owner copy carries a locally recomputable packet hash and an explicit source label; no CSRF token, Tower credential/session, production key, authenticated balances, provider attestation or account-access grant is serialized. It is marked `durable_server_archive: false`, `source_provider_authenticated: false`, `manual_live_authorized: false`, `this_is_a_third_party_attestation: false`.

## Offline check (on the owner's device)

From the repository root with existing Python dependencies:

```bash
python -m scripts.ob_verify_owner_evidence --file "/path/to/ob-proof-demo-OB-WEB-....json"
```

This rejects duplicate/nonfinite JSON, oversized/symlinked/malformed files, changed nested ticks, sequence or final-link mismatch, and forbidden live/authentication claims. A `VALID LOCAL INTEGRITY ONLY` result means the packet's contents and links match their included non-secret hashes. **Anyone able to modify the file can recompute an ordinary SHA-256. This is not a signature or proof that Tower, a broker, market provider or financial institution authenticated the contents.** Never present the packet as a real filled order, account profit, spendable acquisition money or Manual Live clearance.

## Acceptance

- New exact protected endpoint and browser action remain disabled until the existing hosted rehearsal itself is approved/enabled.
- Final-only export; even zero-tick finalizations stay explicitly report-only.
- Wrong Host, missing/wrong token, lost owner/Tower receipt, old token after New, active/paused session and new Python worker cannot export prior results.
- Browser downloads only after server envelope checks, uses a memory-only Blob without localStorage, and displays an explicit device-save warning.
- No paid Render resources, durable server storage, deployment setting or production mode flags are modified by this pack.

**Still OPEN:** owner verification of the official hosted Tower URL and deployed revision, feature flag/origin review, actual on-device walkthrough, certified durable server storage if required, and all separate real Manual Live/Hybrid/Auto external permission gates.
