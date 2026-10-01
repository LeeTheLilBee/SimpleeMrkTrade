# Tower ↔ Grounds same-origin runtime integration — 2026-10-01

## What changed

Tower already provides the exact runtime boundary modules Grounds imports:

- `tower.grounds_runtime_receiver.create_certified_grounds_receiver()`
- `tower.grounds_runtime_receiver.create_certified_grounds_staff_directory()`
- `tower.grounds_runtime_receiver.create_certified_grounds_staff_resolver()`
- `tower.grounds_operational_release.create_certified_grounds_operational_release_guard()`

PR #296 also added the authenticated owner + step-up launch gate at `/tower/launch/grounds`, but it deliberately remains blocked unless a real same-origin `/grounds` runtime is mounted.

`tower/grounds_same_origin_mount.py` closes that source-composition gap without weakening any release gate.

## Mount contract

Hosted Tower calls `register_configured_grounds_same_origin_runtime(app)` before the generic direct-product route guard and owner launch gate.

The adapter registers **no** `/grounds` route unless all of these are true:

1. `TOWER_GROUNDS_SAME_ORIGIN_MOUNT=1` is explicitly configured;
2. the deployed Python environment actually contains `grounds.production_entry`;
3. `grounds.production_entry.create_wsgi_application()` exists and returns a callable;
4. Grounds' own production factory successfully initializes, which independently requires its private PostgreSQL/CSRF configuration, Tower receiver + staff factories, and Tower operational-release guard.

If any import, provider, release, database or Grounds preflight fails, Tower itself remains available but `/grounds` stays **unregistered**. The launch preflight therefore continues to return `GROUNDS_SAME_ORIGIN_RUNTIME_NOT_MOUNTED`. Private exception text, DSNs and provider diagnostics are not exposed in the mount status.

The mounted child gets the original `/grounds...` PATH_INFO unchanged because the Grounds router owns that prefix.

## Existing Tower gates still apply

The mount is not a launch authority.

The existing generic direct-route guard still denies direct `/grounds` access until Tower has created a current, exact owner/session-bound `tower.ecosystem.access-receipt.v1`. The existing owner launch route creates that receipt only after current owner authentication, step-up, app publication/health/entitlement truth, route presence, certified runtime receiver health and independent operational-release health are all verified.

This first crossing is an **owner** corridor. It does not create a resident/staff Tower launch route or tenant entitlement. Multi-role resident/staff access still requires the separately certified runtime provider and a reviewed Tower multi-role entry/session path before real residents are admitted.

## Cross-branch contract CI

The Tower systems integration workflow also checks out the current `grounds-resident-operations-grd001-005` branch into an isolated path. It imports the real Grounds `TowerScope` and production factory against the current Tower receiver/release modules, uses only synthetic independent provider modules, and proves:

- actual Tower receiver output is accepted by actual Grounds scope normalization;
- current owner/property and staff/job shapes agree;
- Grounds production factory can resolve the exact Tower factory names;
- operational-release callable/health shape agrees;
- the same-origin mount can register the actual Grounds production factory only after those test-only provider/preflight dependencies are injected.

No real database, person, property, provider credential, tenant session, payment, message or deployment is used by this CI.

## Still external / not certified by this source

- actual independently operated Tower Grounds runtime identity/grant provider;
- actual operational release decision provider with current owner acceptance, storage restore, privacy/housing review and operations coverage evidence;
- approved private PostgreSQL environment + migration/backup/restore/retention/security evidence;
- Teller invoice/payment/reconciliation;
- Vault protected originals and contact/evidence access;
- real delivery/on-call provider and retry/dead-letter coverage;
- qualified legal/privacy/accessibility/housing/entry review;
- explicit hosted owner acceptance and later reviewed resident/staff Tower entry corridor.

No paid resource or public Grounds service is provisioned by this source change.
