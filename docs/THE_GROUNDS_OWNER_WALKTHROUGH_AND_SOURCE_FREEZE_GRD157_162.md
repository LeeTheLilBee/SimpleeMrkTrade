# The Grounds — source integration freeze and owner walkthrough acceptance plan
**GRD157–162 | September 28, 2026 | DRAFT / NO LIVE RESIDENT ACCESS**

## What is actually implemented in Grounds

The current Grounds development branch contains tested source paths for property/lease context and primary household membership, maintenance intake and state transitions, staff assignments, resident entry preference and appointments, notices/in-app read state, owner/staff/source-bound Soulaana views, authenticated read-only exact-lease Teller invoice projection, minimized leasing and physical operating workboards, human urgency review, transactional event intents and separately verified historical delivery/on-call receipts, post-close Tower/BuyBox property-acceptance lineage, private PostgreSQL adapter/baseline, and a separate future operational-release gate in front of the normal Tower per-request receiver. There is **no** standalone Grounds login, fake checkout, in-app emergency call, independent credit facility, OB trading access, real notifier, live provider or activated tenant service.

## GRD157–159: integrated refusal and recovery regression

`grounds/test_grounds_postgres.py::test_full_private_postgres_wsgi_operational_and_tower_gate_integration` runs the actual domain, WSGI, `GroundsOperationalReleaseGate` and disposable **real PostgreSQL** together under local fictional Tower/owner test objects. It verifies unavailable independent release denies resident GET/static/POST despite a healthy database; liveness is nonpersonal; readiness requires independent release plus Tower/DB health; release granted but unauthenticated or wrong-lease resident stays denied; exact authorized lease returns its own scoped view; no signed Teller adapter returns unknown rent, never zero or checkout; revocation prevents persistence; only later independently authorized action saves one real disposable SQL row; Tower receiver revocation denies again; operational release revocation shuts off all private access. Fake fixture receivers are in the test only, **not** the future provider implementation.

`grounds/test_grounds_browser_context.py` and `tests_js/context_switch.cjs` separately run the actual UI under a fake in-memory DOM and prove synchronous old-context clearing, wrong returned property/unit rejection and late response isolation.

## Exact acceptance packet required from external owners

A source test or local checklist cannot certify any of the following. The real, authorized integration team should attach a timestamped, environment-specific, signed/reviewed receipt to each gate. No actual receipt exists in this packet.

| Gate | External owner | Minimum independently verified evidence | Current status |
| --- | --- | --- | --- |
| Current human identity and assignments | Tower + independent runtime provider | Tower adapter source/factory now implemented and cross-tested against current Grounds; still requires actual provider attestation, original-session verification, expiry/logout/replay/revocation, resident/property/unit/lease/household and exact maintenance assignment; current staff directory/resolver; negative cross-tenant walkthrough | ADAPTER SOURCE IMPLEMENTED; LIVE PROVIDER NOT CERTIFIED |
| Independent operating authorization | Tower + owner/security + independent release provider | Tower operational-release adapter factory now implemented; still requires a real short-lived decision binding exact environment/revision to owner acceptance, successful restore, privacy/housing review and operations coverage, with current health/revocation | ADAPTER SOURCE IMPLEMENTED; LIVE DECISION NOT CERTIFIED |
| Tenant data custody | Approved hosting/operator | Private PostgreSQL, exact reviewed migration inventory, encryption/network/secret/retention access, backup, successfully observed restore, rollback/rotation and incident access evidence | NOT CERTIFIED |
| Rent and receipts | Teller through Tower | Original signed invoice per exact lease, payer authorization, real checkout in Teller, idempotency, partial/failed/returned/reversed/refunded paths and authoritative reconciliation; no card/bank details in Grounds | NOT CERTIFIED |
| Private evidence/contact | Tower + Vault | Actual sealed document/upload/scanning/authorization, private access and original issuer proof, retention/revocation/recovery; lease/work/inspection and prospect-contact scoping | NOT CERTIFIED |
| Notifications and urgent human coverage | Tower delivery gateway + operations | Current recipient grants, live delivery receipts/failures/retry/dead letter, after-hours contact roster, actual human acknowledgment, service recovery and escalation plan | NOT CERTIFIED |
| Housing and real-person acceptance | Owner + qualified local professionals | Applicable fair-housing, notices, entry, emergency procedures, lease/privacy/accessibility review; full owner and role-specific hosted walkthrough and final signed approval | NOT CERTIFIED |

## October 1 Tower reconciliation

Tower now also has an authenticated owner + step-up Grounds launch gate and a reviewed fail-closed same-origin mount source. The mount registers `/grounds` only if Grounds' own production factory succeeds; an arbitrary route cannot satisfy Tower's launch preflight. This retires the old **missing Tower module / missing owner doorway source** blockers, but does not create a resident/staff launch, live provider attestation, private database, release approval or tenant authorization. See `docs/THE_GROUNDS_TOWER_RECONCILIATION_GRD219_224.md`.

## Hosted owner walkthrough — future gated sequence (no real tenant until signed approval)

1. Confirm signed owner operating-release acceptance and the exact deploy/revision/build identity, private host and recovery evidence. Verify no walkthrough-only Tower mode, no self-reported env Boolean and that blocked status stays 503 before current release.
2. Open Grounds **through authenticated Tower** as owner; verify only assigned property summaries, operating dashboards and receipt lineage; switch between authorized properties to test synchronous erasure and stale-response isolation.
3. Use a deliberately authorized resident test account (created only in the approved live-like, non-customer test environment); verify exact current property/unit/household, lease and notices; assert another resident and ended lease get no data. Rent shows unknown if Teller not actually certified; otherwise only a fresh validated invoice and no Grounds checkout.
4. Submit a synthetic ordinary and urgent work order; check current real PostgreSQL persistence, retry/idempotency, consent preference, visible human review and accurate 'not externally dispatched' status until real provider receipts exist. Verify owner/manager/maintenance supervisor and assigned technician boundaries independently.
5. Test appointment request/propose/accept/cancel and current lease revocation, resident notice read versus actual provider/legal notice, staff safety desk and reviewed/undelivered/historical receipt distinctions.
6. Check leasing prospect stage/tour metadata cannot expose Vault contact records or make approvals; physical workboard supervisor cannot view owner-only turnover counts; inspect responsive controls, keyboard/focus paths and assistive-technology acceptance.
7. Expire/logout/revoke the Tower session, resident lease, technician assignment and owner operational release **between successive requests**; verify 401/404/503 as appropriate, no confidential HTML/JS/data from an old context and no unauthorized write.
8. Simulate permitted recovery/failover with operator controls, verify successful approved restore and safe return to service, preserve receipts and records, and obtain explicit owner release decision.

If any gate fails, remain DRAFT / NOT LIVE. Do not pay for hosted resources, turn on real payments, issue tenant credentials, publish notices, dispatch emergency calls or promote the parent PR solely because a source CI check passed. Source development is not equivalent to real service certification. The real Tower, Teller, Vault and operations teams must supply actual issuer-backed implementations rather than importing this file's test stubs.

## Source completion decision

The Grounds-owned implementation can be considered **ready for external integration review** after exact child and merged parent source/real-PostgreSQL CI pass and reviewer acceptance. This is not a declaration of hosted production readiness, financial settlement, legal service, provider delivery, data-recovery certification or owner-approved resident release. Parent PR #51 remains draft and should not be merged to `main` or exposed to real users automatically.
