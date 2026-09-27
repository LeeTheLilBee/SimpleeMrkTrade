# The Grounds — private development package

The Grounds is a role-specific resident and property operations app for Simplee World. The resident enters through Tower, sees a lease/unit context, starts rent checkout through Teller, submits and follows maintenance, and reads notices. Technicians, leasing, management and the owner get scoped workspaces.

Current branch is **local development/source-only**: not hosted, not a Tower receiver and not connected to actual tenants, payment methods or permanent evidence. Never feed real personal data into the preview or unit tests.

### Local no-cost checks

From repository root with Python 3.11+:

```bash
python -m compileall -q grounds
python -m unittest discover -s grounds -p 'test_*.py' -v
```

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
- `soulaana.py` — read-only, source- and revision-bound explanations for work orders and readiness.
- `stewardship.py` — property assets, certified preventive-plan completion, inspection findings/remediation and unit turnovers. No real dispatch, inspector self-service or automatic notifications.
- `residency.py` — externally certified lease-member grant/revocation, co-tenant/occupant records and history, separately from Tower sessions.
- `communications.py` — scoped in-app notice-read and appointment proposal/acceptance; not legal delivery or permission to enter.
- `safety.py` — human-only urgent triage, resident entry preferences and metadata-only pending notification intents; no provider/dispatch.
- `soulaana.py` — also explains exact-scope resident rent/lease, appointments, inspections, turnovers, leasing, and owner pulse, in read-only form.

A fake verifier appears only in unit-test fixtures. No real public route may trust a caller-supplied role, identity, proof verifier or payment projection.

See `docs/THE_GROUNDS_RECOVERED_PLAN_GRD001_005.md`, `docs/THE_GROUNDS_IMPLEMENTATION_GRD006_019.md`, `docs/THE_GROUNDS_STEWARDSHIP_GRD024_033.md`, and `docs/THE_GROUNDS_RESIDENT_SERVICES_GRD037_055.md` for scope, delivered code, explicit non-effects and launch gates.
