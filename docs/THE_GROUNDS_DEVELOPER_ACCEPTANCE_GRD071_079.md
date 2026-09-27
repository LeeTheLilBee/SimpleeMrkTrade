# The Grounds — developer walkthrough completion and Tower acceptance packet (GRD071–079)

Status: **usable source-only developer walkthrough with fictional records; NOT a live resident/staff app.** Source of truth is [draft Grounds PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51). Separate Tower review is [draft PR #52](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/52). Do not merge, activate protected doors, host private tenant data or provision paid resources on the strength of this packet.

## Changes completed

- **GRD071** — resident Home, list and individual job read require **both** current Tower-granted unit and exact active Grounds `lease_ref`. Renewing/re-leasing the same unit to the same subject does not expose old lease maintenance records. Regression uses synthetic fixture-only reset to represent a completed turnover.
- **GRD072–073** — `python -m grounds.dev_demo --fictional-only` is a genuine one-command, offline end-to-end domain walkthrough. It creates a disposable synthetic DB, validates failed urgency transition before human review, failed job start on an explicit no-entry preference, approved resident/staff domain state changes, fictional notice read, appointment proposal/accept, nonfinancial resources, Soulaana, a clearly fake fresh Teller projection, owner aggregate and database consistency. Its fake verifiers are isolated to this deliberately named development runner; **never install it as an API or security adapter**. Missing the explicit option fails before running.
- **GRD074–075** — `grounds/workspaces.py` projects authorized, field-whitelisted read-only room state from actual Grounds domain data. Resident, maintenance technician, supervisor, property manager, leasing, regional manager and owner have current scoped surfaces. Inspector, turnover crew, grounds/janitorial, renovation coordinator, compliance and vendor remain explicitly **locked** until exact task-specific Tower assignments are certified. A maintenance supervisor is not silently promoted to manager financial/portfolio status.
- **GRD076** — normalized sealed stewardship proof must be independently certified for Vault `source`, Grounds `audience`, correct kind and all preexisting exact property/plan/inspection/finding/turnover bindings. Wrong source or audience is rejected, consistent with work-order proof normalization.
- **GRD077–078** — `grounds/release.py` exposes truthful fictional-demo status and a fixed external release checklist; even every self-reported checkbox marked true cannot authorize live traffic, real payments, provider provisioning or a resident session.
- **GRD079** — CI now executes the fictional end-to-end demo after compilation and all unit tests; README includes exact no-cost command.

## Usability boundary

**Developer-usable without Tower:** inspect dark-glass fictional `grounds/ui/preview.html` in a browser, exercise its in-memory role switching/work/notice/appointment/Soulaana interactions; run the actual isolated domain scenario via `python -m grounds.dev_demo --fictional-only`; run the complete source tests; call `build_workspace` in an offline test using *fixture-only* Tower scopes to view real SQLite-sourced projections. There is no real login, file upload, checkout, messaging transport, hosted database or actual external AI.

**Not yet resident-usable:** no true Tower receiver or authenticated role/lease/job/inspection grants, no private hosted storage/recovery, no Teller checkout/settlement/partial/returned-payment reconciliation, no real Vault upload/document services, no actual notification delivery, after-hours dispatch or legally reviewed entry/notice process, and no authorized live Soulaana model. We must not create unsecured routes or let fake validators impersonate the missing systems.

## Tower reviewer — concrete interface decisions

1. Certify canonical branch, exact signed/audience-bound Tower → Grounds receiver, replay/nonce/session/expiry/revocation, separate resident/staff/owner identity, owner step-up, active member/property/unit and per-job/vendor/inspection delegated claims. The Grounds internal `TowerScope` is **not** a wire protocol; `dev_demo.py` is not authentication.
2. Resolve audience and evidence envelopes with Vault. Grounds now checks `source=vault`, `audience=grounds`, `status=verified_sealed`, exact proof kind and resource-specific fields for work, preventive, severe findings and turnover. Actual signer/uploader/approver claims, storage scan, retention, document viewing and legal evidence remain Tower/Vault decisions.
3. Define certified service-owned adapter patterns. A public caller must never supply an arbitrary `verifier=lambda x:x`, actor role or finance projection. `workspaces.py` has no API/network routes; Tower provides the real entry and tenancy proof.
4. Keep Teller invoices/checkout/refunds/receipts and the five protected apartment capital lanes authoritative. Grounds/BuyBox cannot interpret OB balances as spendable. No rent value appears on the owner/Clouds physical operating snapshot.
5. Certify delivery provider, idempotent receipts, actual on-call emergency routing, resident preferences, consent/accessibility and legally compliant property-specific notices before calling any local `event_outbox` row a delivered communication.
6. Once integration proof is independently available, owner accepts a deliberately separate live-release decision. `grounds/release.py` can **never** lift the gate based on self-reported flags.

## Developer acceptance

From repo root with Python 3.11+:

```bash
python -m compileall -q grounds
python -m unittest discover -s grounds -p 'test_*.py' -v
python -m grounds.dev_demo --fictional-only
```

A source-only CI pass is a pre-integration quality gate, not a deployment certificate. The demo deliberately emits only fictional data, deletes its SQLite directory on exit and makes no network requests. The GitHub Actions run for the exact latest PR head must be checked after every change, not inferred from an earlier green commit.

**Do not silently expand the claimed historical inventory:** planning previously mentioned 80 + 50 feature entries; the complete verbatim numbered version has not been retrieved, so this checkpoint describes only verified implemented modules and explicit remaining dependencies.
