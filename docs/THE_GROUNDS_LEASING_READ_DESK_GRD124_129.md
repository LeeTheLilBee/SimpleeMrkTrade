# Grounds GRD124–129 — actual leasing read desk, source-only

The domain already records property/unit availability, opaque prospects, stage transitions and tours. This increment makes those **existing real domain records** visible to authorized leasing staff, managers and owner in the non-demo Grounds browser. It does not fabricate a lease offer, rent amount, applicant identity, application approval or tour delivery.

## Scope and minimization

- New `GroundsLeasing.list_prospects` projects only opaque prospect reference, desired unit reference, stage, revision and timestamps; it **does not** include `contact_vault_ref` or applicant PII. Tour index returns preexisting opaque references/unit/time only. Both listings are bounded to 100 rows per property.
- `GET /grounds/api/leasing?property_ref=...` requires the same independently verified per-request Tower scope as every private API. Each domain read separately requires owner/property_manager/leasing_agent and exact property. Resident, technician or unrelated property scopes fail closed. Queries cannot specify source, contact, role or other foreign access.
- Browser renders a leasing desk for only those authorized roles: recorded ready units, opaque stages and tours, truthful disconnected private-contact status. A stage or planned tour is **not** a communicated appointment, screening result, lease approval or verified advertised rent.
- Registration/mutation remains absent from the browser until independently certified Tower/Vault contact intake and lawful housing/applicant-flow requirements exist. The older source-only domain fixtures are NOT permission to collect or store real application PII in source or a disposable SQLite DB.

## Verification

Source tests assert no Vault contact reference in the domain/API payload, denial of resident/technician/cross-property/unknown/extra-query requests and explicit no-application/no-notification status. Real PostgreSQL integration verifies the same projection through actual WSGI → private-style SQL adapter against **synthetic CI data only**. Exact-current-head source and disposable PG workflows must both pass.

Live blockers are unchanged: current certified Tower Grounds receiver; private approved Postgres with restore proof; actual Tower/Vault scoped contact retrieval; verified owner-reviewed applicable fair-housing/privacy/accessibility workflows; Teller-routed real rent offers/checkout if later approved; real notice/tour provider receipts and owner activation. No new public route, managed resource, live applicant or paid service is authorized.
