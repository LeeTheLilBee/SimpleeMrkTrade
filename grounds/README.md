# The Grounds — private development package

The Grounds is a role-specific resident and property operations app for Simplee World. The resident enters through Tower, sees a lease/unit context, starts rent checkout through Teller, submits and follows maintenance, and reads notices. Technicians, leasing, management and the owner get scoped workspaces.

This branch now contains two intentionally distinct UI experiences: **`ui/preview.html` is a fictional local walkthrough**, whereas **`ui/app.html`, `ui/app.css`, `ui/app.js` and `web.py` are a real-data browser and server API** that only operate after a trusted server injects an authenticated TowerScope. The WSGI application accepts SQLite **only** in explicit `local_fixture_only=True` tests and can accept a separately provisioned PostgreSQL store only after its real schema preflight. `production_entry.py` is an explicit future deployment factory which refuses to initialize without an exact certified `tower.grounds_runtime_receiver` implementation, its three independent current identity/staff callbacks, a private PostgreSQL URL and high-entropy shared session-CSRF/idempotency configuration. Tower has **not implemented/certified that receiver yet**, and Grounds is **not hosted** or connected to real resident accounts. Never put personal data into previews, fixtures, or the disposable SQLite store. Private PostgreSQL and current/revocable Tower identity remain separate release dependencies.

### Local no-cost checks

From repository root with Python 3.11+:

```bash
python -m compileall -q grounds
python -m unittest discover -s grounds -p 'test_*.py' -v
python -m grounds.dev_demo --fictional-only
```

GitHub also runs the **actual non-skipped PostgreSQL integration suite** on a
separate ephemeral Postgres 16 container via
`.github/workflows/grounds-postgres-integration.yml`. The source suite alone
skips actual PostgreSQL tests if no disposable test DB is supplied. Both exact
latest-head workflow results must pass. No live user database or paid Render
resources are involved.

The explicit demo command exercises actual isolated Grounds domain services with fixed
fictional property/resident/staff fixtures: resident membership, notice read, work
request, urgent human-triage and no-entry checks, staff material/time logging,
appointment negotiation, Soulaana, a fake Teller projection, and owner counts.
It outputs JSON, makes **no network requests**, requires no credentials and removes
the synthetic SQLite file on exit. Do not adapt the demo's fixture verifier
lambdas or fake Teller result for a hosted entrypoint.

To inspect the visual prototype, open `grounds/ui/preview.html` locally in a browser. It contains only fictional sample data and in-memory demo actions. Rent checkout is visibly disabled. Opening a static preview does **not** create a credential/session or authorize any real operation.

### Domain map

- `contract.py` — supported rooms and system boundaries.
- `access.py` — normalized externally verified Tower-scoped identity placeholder; requires certified verifier.
- `storage.py` — local SQLite property/lease/work-order/leasing reference records.
- `operations.py` — owner/manager/resident/technician scoped property, lease, notice and maintenance actions.
- `maintenance.py` — state transition policy.
- `leasing.py` — availability, opaque prospect stages and tour plans.
- `GET /grounds/api/leasing` + resident/staff UI leasing desk — permission-filtered, read-only property inventory, PII-minimized prospect stages and tour records; applicant contact, screening and real tour delivery stay unconnected.
- `teller.py` — exact-unit, exact-lease verified Teller rent display, no checkout.
- `web.py` `/grounds/api/rent` — server-only optional paired Teller document source + independent verifier, exact current resident lease check, no-store read; disconnected is unknown balance, not $0. Browser displays a verified snapshot only and never renders a checkout control. This is source-only and production entry has no certified Teller adapter yet.
- `evidence.py` — only verified opaque Vault/Tower proof references.
- `capital.py` — five-lane apartment reserve/readiness snapshot sourced through Teller, no money movement.
- `soulaana.py` — read-only source-bound explanations for work, verified rent/readiness, leases, appointments, stewardship, leasing, owner pulse, physical materials and preventive due dates.
- `stewardship.py` — property assets, certified preventive-plan completion, inspection findings/remediation and unit turnovers. No real dispatch, inspector self-service or automatic notifications.
- `GET /grounds/api/physical-desk` — current Tower-scoped asset, due-preventive, inspection and owner/manager-only turnover read indices, bounded and minimized. No dispatch/entry/Vault/capital authority.
- `ui/app.js` / `test_grounds_browser_context.py` — immediate clearing of private DOM when property/unit changes, exact returned workspace context guard, deferred-response race denial and truthful unknown Teller balance; Node fake-DOM regression runs in source CI.
- `residency.py` — externally certified lease-member grant/revocation, co-tenant/occupant records and history, separately from Tower sessions.
- `communications.py` — scoped in-app notice-read and appointment proposal/acceptance; not legal delivery or permission to enter.
- `safety.py` — human-only urgent triage, resident entry preferences and metadata-only pending notification intents; no provider/dispatch.
- `safety.py::staff_safety_desk` + `GET /grounds/api/safety-desk` — exact-property manager/supervisor/owner urgency backlog, minimized metadata and pending local event count; staff UI offers explicit human review without claiming message delivery, on-call response or emergency dispatch.
- `work_resources.py` — property/job-scoped append-only material counts and labor minutes, no costs, payroll, bills or inventory purchase.
- `dev_integrity.py` — synthetic local SQLite invariant counts and opt-in unencrypted, no-overwrite developer-only fixture backup; not production recovery.
- `owner_status.py` — owner-only, minimized physical-operating counts for future Tower-mediated Clouds review; no resident identifiers or live publisher.
- `experience.py` + exact role-scoped private endpoints — resident My Home, manager/supervisor Daily Grounds, property Health and bounded owner Portfolio, grounded only in current Grounds operating records, no money or delivery assertions.
- `acquisition_handoff.py` — verified, idempotent multifamily post-close property acceptance with exact BuyBox/Tower/title/encumbrance lineage; no direct BuyBox acquisition claim or money movement.
- `delivery.py` — independently verified, append-only provider and human-on-call acknowledgment receipts bound to exact local outbox events; no transport, legal service or emergency dispatch. The safety desk distinguishes historical receipts from current provider status.
- `workspaces.py` — protected read-only room projections for seven supported roles; six assignment-specific rooms remain locked pending Tower grants.
- `dev_demo.py` — deliberate offline fictional end-to-end scenario, never a real authentication or service layer.
- `release.py` — truthful source walkthrough status and immutable no-auto-unlock tenant release review.
- `ui/app.html`, `ui/app.css`, `ui/app.js` — real-data responsive resident/staff interface; no sample people, forged payment buttons or role switcher.
- `web.py` — server-injected Tower authentication on every HTTP read/write, bounded WSGI API and session-scoped CSRF; SQLite forbidden in private production composition.
- `production_entry.py` — real deployment factory that fails closed without the missing certified Tower runtime receiver, private PostgreSQL schema and configured secrets; it does not start a service itself.
- `operational_release.py` + production factory — additional independent Tower-owned, current/revocable owner/operations release guard on **every** future protected WSGI request; no identity/DB health or self-reported checklist may launch tenants by itself. Actual certified factory is not yet implemented.
- `test_grounds_postgres.py` integrated synthetic service check — actual disposable PostgreSQL + real WSGI + separate fictional operating/Tower gates, proving denial, current lease, revoked access, unknown Teller amount and authorized durable write. No fixture issuer can be used for production.
- `storage.py::GroundsStoreBase` — common domain transaction contract; the old `GroundsStore` remains disposable SQLite.
- `postgres.py` — real psycopg3 PostgreSQL domain transaction adapter with serializable writes and read-only baseline compatibility; no implicit production migrations.
- `sql/0001_initial_postgres.sql` — reviewed fresh private PostgreSQL baseline schema with lease/notice/asset/appointment/turnover constraints.
- `requirements-production.txt` — future bounded Python WSGI/database dependencies, no host/secrets/deployment.
- `ui/app.js` and `web.py` — UUIDv4/HMAC-scoped retry-safe maintenance and appointment creation; the same pending browser action never duplicates on uncertain network responses.
- `web.py` — manager-only future Tower directory + independently resolved technician assignment, not an unsafe user-chosen staff grant.
- `web.py` — metadata-only liveness and fail-closed private DB + certified Tower receiver readiness checks.
- `.github/workflows/grounds-postgres-integration.yml` — actual synthetic Postgres 16 API → durable DB tests, not just static adapter checks.

A fake verifier appears only in unit-test fixtures and the explicit `dev_demo.py` fictional runner. No real public route may trust a caller-supplied role, identity, proof verifier or payment projection.

**New-schema warning:** New unit-targeted notices and notice read marks are bound to the exact current lease. `GroundsStore.initialize()` intentionally rejects known old local lease-unscoped notice schemas; `dev_integrity.py` reports missing tables/columns. There is **no production migration** and no permission to convert real tenant records. Recreate only disposable fictional fixtures; separately design a versioned, backed-up private-store migration before live use.

See `docs/THE_GROUNDS_RECOVERED_PLAN_GRD001_005.md`, `docs/THE_GROUNDS_IMPLEMENTATION_GRD006_019.md`, `docs/THE_GROUNDS_STEWARDSHIP_GRD024_033.md`, `docs/THE_GROUNDS_RESIDENT_SERVICES_GRD037_055.md`, `docs/THE_GROUNDS_PRE_TOWER_GRD056_065.md`, `docs/THE_GROUNDS_OWNER_STATUS_GRD066_070.md`, `docs/THE_GROUNDS_DEVELOPER_ACCEPTANCE_GRD071_079.md`, `docs/THE_GROUNDS_HARDENING_GRD080_087.md`, `docs/THE_GROUNDS_REAL_USER_RELEASE_GRD089_100.md`, and `docs/THE_GROUNDS_OPERATIONAL_HANDOFF_GRD104_111.md`, and `docs/THE_GROUNDS_VERIFIED_RENT_READ_GRD113_117.md`, and `docs/THE_GROUNDS_HUMAN_SAFETY_DESK_GRD118_123.md`, and `docs/THE_GROUNDS_LEASING_READ_DESK_GRD124_129.md`, and `docs/THE_GROUNDS_PHYSICAL_WORKBOARD_GRD130_135.md`, and `docs/THE_GROUNDS_INDEPENDENT_OPERATIONAL_RELEASE_GRD136_141.md`, and `docs/THE_GROUNDS_RECONCILED_CLOSE_DELIVERY_GRD142_150.md`, and `docs/THE_GROUNDS_CONTEXT_PRIVACY_GRD151_156.md`, and `docs/THE_GROUNDS_OWNER_WALKTHROUGH_AND_SOURCE_FREEZE_GRD157_162.md`, and `docs/THE_GROUNDS_ROLE_EXPERIENCE_GRD163_171.md` for scope, delivered code, real-data web/PostgreSQL architecture, privacy hardening, executable checks, external providers and live-release gates.
