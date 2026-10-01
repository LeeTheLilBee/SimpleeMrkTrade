# The Grounds — real-user operational handoff (GRD104–111)

**Checkpoint:** real-data browser + API + PostgreSQL source, with repeatable disposable database tests and a locked production factory. **Not an activated tenant product.** [Grounds PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51) remains draft. No managed database, paid infrastructure, real tenant credentials, rent collections, document uploader, provider notifications or public Grounds route was created.

## What was made operationally testable

1. **GRD104: Actual PostgreSQL in CI.** `.github/workflows/grounds-postgres-integration.yml` starts an ephemeral PostgreSQL 16 container and installs psycopg 3. The same schema and transaction adapter run against real SQL, with fixture-only records. It is isolated GitHub Actions infrastructure, not Render or a production tenant DB. A passwordless CI-only container is used solely inside the short-lived job; NEVER reuse its settings for any deployed or network-reachable PostgreSQL instance.
2. **GRD105–106: Create-command retry safety.** New maintenance and appointment requests require browser-generated UUIDv4 `X-Grounds-Idempotency-Key`. A keyed HMAC-derived resource reference is bound to authenticated subject, stable Tower session, operation and target. Exact uncertain-response retries return the current original record with `replayed=true`; a changed payload with the same key conflicts. Current property/unit/lease authorization is rechecked before any earlier data can be returned. JS preserves the key until confirmation, rather than creating duplicates on a network failure. CSRF now binds to the stable Tower session (not a rotating handoff ticket's expiry), while the real Tower receiver still authenticates and revalidates every request. Do not substitute idempotency or CSRF for Tower authentication.
3. **GRD107: Full HTTP → PostgreSQL synthetic integration.** New integration test invokes the actual WSGI API against real PostgreSQL, verifies durable work and appointment rows and only one event each, exact replay, owner vs resident scope and current lease replacement denying old records. The fake Tower identity exists in the isolated CI test only.
4. **GRD108–110: Actual staff assignment crossing prepared.** `GET /grounds/api/technicians` obtains a minimal authorized property-scoped staff roster from a trusted server-owned Tower directory adapter, never from a user's claimed role. `POST /grounds/api/work/assign` can act only after independently resolving a current technician scope for this property/work and checking the manager/supervisor's authorization and expected revision. Browser presents a technician picker only with a certified connected roster; otherwise explains why assignment is not available, and never fakes it. The future Tower runtime must supply three separately certified callables: `create_certified_grounds_receiver()`, `create_certified_grounds_staff_directory()`, `create_certified_grounds_staff_resolver()`. Production factory refuses missing roles. Scope reviewer files in Tower are **not** these runtime implementations.
5. **GRD111: Infrastructure health semantics.** `GET /grounds/health/live` returns only nonpersonal liveness without authentication. `GET /grounds/health/ready` is 503 for every disposable SQLite fixture or unverified Tower receiver, and requires both an actual receiver health check and a private PostgreSQL query to return 200. Neither route permits login, declares legal/product readiness, leaks private provider detail or overrides the owner release gate. Every other page, asset and API request still demands a currently authorized Tower scope.

## Consistent verification

At the repository root, the source suite continues to be checked by `.github/workflows/grounds-source-contract.yml`; the independent `grounds-postgres-integration.yml` now runs all non-skipped actual PostgreSQL tests on every relevant Grounds PR/branch update. Inspect **both exact latest-head workflow checks**, not historic green badges. CI is free of real credentials, property information and paid Render resources.

Manual developer commands, with only fictional fixtures:

```bash
python -m compileall -q grounds
python -m unittest discover -s grounds -p 'test_*.py' -v
python -m grounds.dev_demo --fictional-only
```

To run actual PG tests outside GitHub Actions, separately provision a disposable isolated CI/test PostgreSQL database, install `grounds/requirements-production.txt` or psycopg3, then provide test-only `GROUNDS_POSTGRES_TEST_ONLY=true` and `GROUNDS_TEST_POSTGRES_URL`; never point it to any production/shared database, as the integration suite creates schema and inserts fixture rows.

## Exact live release gates and responsible systems

| Gate | Required evidence / owner decision | Authority |
|---|---|---|
| Tower user identity | Real separate resident/staff/owner sessions, actual session/auth revocation, audience/issuer/nonce/replay binding, grants derived from current human, property, exact lease/co-tenant and staff job assignments. All three runtime callbacks must exist and be certified, with health check. | Tower; no local fixture callback |
| Private datastore | Owner-approved private PostgreSQL provider/cost, limited network access, secrets/TLS, reviewed migration `grounds/sql/0001_initial_postgres.sql`, schema marker, encrypted backup **and successful restore drill** plus logging retention and rollback. | Grounds/infrastructure, not CI container |
| Real property onboarding | Independently verified owned/closed property, correctly recorded units/buildings and certified leases and household membership; no real tenancy is created from a listing or fixture validator. | BuyBox post-close → Tower/Vault → Grounds |
| Rent | Actual authenticated lease-specific Teller invoice, payments, partial/failed/returned/refund handling and receipt/reconciliation; never OB direct cash. | Teller/Tower |
| Documents | Signed Vault source/audience/actor/kind/current-resource proofs; protected scan/upload/revocation/retention/view. | Tower/Vault |
| Delivery and emergencies | Real provider acknowledgment and on-call incident process, delivery retry/dead-letter, human owner escalation and legal notice/entry review. Local event outbox is only pending intent. | Grounds + Tower + provider |
| Real owner acceptance | Source revision and hosted revision verified, exact-head CI, hosted resident/staff/owner privacy/permissions tests, accessibility and jurisdiction-specific housing/legal review, recovery rehearsal, actual security/incident contacts and separate owner release authorization. | Owner/Tower/Grounds |

**Nothing here opens a public route or bills the owner.** The product can now be exercised end-to-end against real SQL in GitHub without spending money, while the outside-provider, source-of-authority and owner-specific live-data gates remain visible rather than papered over.

## Future Tower receiver method signatures (interface request, NOT a real verifier)

- `create_certified_grounds_receiver() -> callable(environ) -> TowerScope`: authenticates original hosted session on every request and derives active current scope independently. Has a real `health_check() -> bool` method (no tenant data in result).
- `create_certified_grounds_staff_directory() -> callable(actor, property_ref) -> list[{"staff_ref": str, "label": str}]`: minimal current roster, property-filtered and manager/supervisor/owner-authorized.
- `create_certified_grounds_staff_resolver() -> callable(actor, property_ref, work_ref, technician_ref) -> TowerScope`: independently verifies the current staff identity/property assignment and returns only a current technician scope, or denies; never trusts a user-submitted technician role or job grant. Grounds rechecks the exact resource and optimistic revision.

The production factory imports **exactly** `tower.grounds_runtime_receiver`. Existing `tower/grounds_handoff_requirements_v1.py` and `tower/grounds_scope_review_v1.py` are descriptive/untrusted review only, not substitutes. The external Tower team must implement on its authoritative branch; keep Grounds PR draft until integration and owner acceptance.
