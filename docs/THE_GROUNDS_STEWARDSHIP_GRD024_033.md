# The Grounds — physical stewardship / GRD024–033

Status: **source-only local implementation** on draft Grounds PR #51, without active tenant/staff routes, live Vault/Teller/Tower receiver, external notifications, hosted database or paid deployment. The Tower handoff for separate resident/staff/owner identities is [draft PR #52](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/52) and must be reviewed in Tower's authoritative work path before any activation.

## Implemented

- Owned-property physical asset inventory: property/ref, optional same-property unit, label/category, active/retired lifecycle. Cross-property asset creation and inventory reads fail closed. A unit reference is not accepted without a matching property relation.
- Preventive plans: explicit asset+property binding, cadence, due date, revision and due-list view. No timer, technician dispatch or unattended job creation. Completion requires a **closed same-property work order** and an externally certified sealed attestation bound to exact plan, asset, job and completed date. Immutable completion history and proof reference; overdue scheduling is advisory only.
- Inspection workflow: planned → in_progress → review → closed, explicit finding records/severity. Closure requires recorded findings, and major/urgent findings require a separate certified, sealed, finding-specific resolution proof before closure. Self-service inspector assignment remains locked until Tower specifies job-specific inspection entitlements; managers/supervisors/owner use verified property scopes in this local service.
- Unit turnovers: can begin only after an active lease has explicitly ended and the unit is marked make-ready. The sequence planned → inspection → work → final_review → complete requires a closed turnover-specific inspection, no open unit work orders and exact-turnover final sealed proof. Completion transactionally marks the unit ready and records an append-only turnover event. It does **not** send a resident notice or automatically relist a unit.
- Negative tests exercise mismatched properties/units, unfinished work, missing/stale revision, invalid proof, duplicate proof, absent severe-item resolution, ungranted inspector role and inability to complete while blockers exist. All sample properties/tenants are fictional fixtures.

## Proof boundary

Fixture-only lambda verifiers in the tests are explicitly not production identity or proof verification. A real Tower/Vault receiver must validate signature, issuer, audience, exact property/unit/asset/job or turnover claims, replay, expiry, revocation, subject and audit before this domain code may be connected to any public request.

The original 130-feature scope is still the overall Grounds backlog, not a claim that all workflows are now complete. Remaining work includes certified identity receiver, role-specific app API/UI, private hosted storage and migrations, integration with Teller hosted rent checkout, real Vault upload/lease sealing, consent/entry permission rules, assigned inspectors/vendors, notices and resident communications, real emergency escalation procedures, accessibility/compliance review, repair materials/labor records, and backup/restore drills. No route, payment, capital deployment or Render resource is authorized by source-only tests.
