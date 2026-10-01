# Grounds GRD136–141 — independent operational launch gate, source only

**Problem addressed:** A private PostgreSQL preflight and a certified Tower identity receiver only demonstrate infrastructure/authentication readiness, not safe service operation or owner authorization to admit real residents. A future operator must not accidentally expose tenant operations just because both become configured. Existing `grounds/release.py` checklist stays advisory, **not** an authorization grant.

## Additional independent contract

The opt-in production factory `grounds.production_entry.create_wsgi_application()` now requires both the current certified Tower identity/staff module **and** the exact separately Tower-owned module `tower.grounds_operational_release` with factory `create_certified_grounds_operational_release_guard()`. A missing, malformed, throwing or non-health-checked factory refuses startup with a generic operator message; private DSN and provider messages remain suppressed. There is no environment toggle, self-report Boolean, browser header, fixture callback, or source checklist that can satisfy the exact factory import.

The independent returned guard must have:
- `health_check() -> bool` — strict literal True **only** while independently authenticated, non-revoked operational/owner release evidence remains current; must validate real provider/on-call/delivery/recovery/legal/privacy/accessibility acceptance, not a developer fixture or persisted checkbox.
- `__call__(environ) -> bool` — strict literal True for each independently admitted protected request. It must not substitute for the separately mandatory Tower human session/current lease/staff/resource verifier; it is a global/operational release decision, **not a user entitlement**. It must fail shut on loss of approval, receipt, freshness or issuer, and report neither secrets nor tenant details in public errors.

`GroundsOperationalReleaseGate` wraps the existing real WSGI app. It allows only metadata-only `GET /grounds/health/live` when the release authority is unavailable. Its `GET /grounds/health/ready` checks independent release health **and** the underlying Tower/DB readiness; every other URL (including HTML, JS, CSS and API) requires the independent guard's current health and strict literal per-request admission before reaching existing Tower+lease+CSRF checks. Errors and denial are generic 503 with no-store. Revocation after an earlier successful request closes subsequent requests. No approval or provider authenticity is fabricated by this wrapper; the external certified authority itself remains **not implemented**.

## Verification

`grounds/test_grounds_operational_release.py` tests disabled health, missing guard, denied static/API, exact True, exception non-leakage, liveness-only while closed and per-request revocation with synthetic functions. Existing `test_grounds_production_entry.py` and `test_grounds_production_preflight.py` now also exercise missing independent release authority and the existing private adapter error containment through fiction-only local factories. Run exact-head Grounds source plus disposable PostgreSQL CI before source merge. These synthetic tests do NOT independently certify a real Tower release issuer, external provider, or any legal/owner review.

**Status:** PR #51 remains DRAFT. No paid Render service, production secrets, private DB, real tenants/applicants, messages, legal notice, money or public route added. This source makes the real startup path more restrictive until Tower implements and the owner explicitly accepts authentic provider-backed release evidence. A healthy load-balancer endpoint is not permission to expose Grounds.
