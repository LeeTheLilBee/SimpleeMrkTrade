# The Grounds — private development package

The Grounds is a role-specific resident and property operations app for Simplee World. The resident enters through Tower, sees a lease/unit context, starts rent checkout through Teller, submits and follows maintenance, and reads notices. Technicians, leasing, management and the owner get scoped workspaces.

Current branch is **local development/source-only**: not hosted, not a Tower receiver and not connected to actual tenants, payment methods or permanent evidence. Never feed real personal data into the preview or unit tests.

### Local no-cost checks

From repository root with Python 3.11+:

```bash
python -m compileall -q grounds
python -m unittest discover -s grounds -p 'test_*.py' -v
python -m grounds.dev_demo --fictional-only
```

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
- `teller.py` — exact-unit, exact-lease verified Teller rent display, no checkout.
- `evidence.py` — only verified opaque Vault/Tower proof references.
- `capital.py` — five-lane apartment reserve/readiness snapshot sourced through Teller, no money movement.
- `soulaana.py` — read-only source-bound explanations for work, verified rent/readiness, leases, appointments, stewardship, leasing, owner pulse, physical materials and preventive due dates.
- `stewardship.py` — property assets, certified preventive-plan completion, inspection findings/remediation and unit turnovers. No real dispatch, inspector self-service or automatic notifications.
- `residency.py` — externally certified lease-member grant/revocation, co-tenant/occupant records and history, separately from Tower sessions.
- `communications.py` — scoped in-app notice-read and appointment proposal/acceptance; not legal delivery or permission to enter.
- `safety.py` — human-only urgent triage, resident entry preferences and metadata-only pending notification intents; no provider/dispatch.
- `work_resources.py` — property/job-scoped append-only material counts and labor minutes, no costs, payroll, bills or inventory purchase.
- `dev_integrity.py` — synthetic local SQLite invariant counts and opt-in unencrypted, no-overwrite developer-only fixture backup; not production recovery.
- `owner_status.py` — owner-only, minimized physical-operating counts for future Tower-mediated Clouds review; no resident identifiers or live publisher.
- `workspaces.py` — protected read-only room projections for seven supported roles; six assignment-specific rooms remain locked pending Tower grants.
- `dev_demo.py` — deliberate offline fictional end-to-end scenario, never a real authentication or service layer.
- `release.py` — truthful source walkthrough status and immutable no-auto-unlock tenant release review.

A fake verifier appears only in unit-test fixtures and the explicit `dev_demo.py` fictional runner. No real public route may trust a caller-supplied role, identity, proof verifier or payment projection.

See `docs/THE_GROUNDS_RECOVERED_PLAN_GRD001_005.md`, `docs/THE_GROUNDS_IMPLEMENTATION_GRD006_019.md`, `docs/THE_GROUNDS_STEWARDSHIP_GRD024_033.md`, `docs/THE_GROUNDS_RESIDENT_SERVICES_GRD037_055.md`, `docs/THE_GROUNDS_PRE_TOWER_GRD056_065.md`, and `docs/THE_GROUNDS_OWNER_STATUS_GRD066_070.md` for scope, delivered code, explicit non-effects and launch gates.
