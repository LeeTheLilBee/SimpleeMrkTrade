# BBX017–BBX021 — protected Tower owner crossing (source checkpoint)

**Status: implemented and regression-tested in source; NOT live, NOT deployed and
not independently certified by Tower or Render.** This pack develops BuyBox's
half of the genuine front-door crossing. All saved-record workspace features
remain unchanged in development mode. No sample product data or fake external
readiness is inserted.

## Consumed exact predecessor contracts

- Tower TWR201 registry: BuyBox is a registered future room; not launchable.
- Tower TWR202–206 `tower.buybox.action.v1` and blocked owner preflight:
  merged Tower commit `db57752b9fd7402265dceb7a35cf93ea16015218`.
- BuyBox BBX011–015 `tower.buybox.owner.handoff.v1`: HMAC-SHA256 `tbh1`
  exact-claims verifier, 60-second TTL and SQLite single-use replay ledger.
- BuyBox BBX016: exact persisted opportunity revision/digest untrusted draft.
- Vault PR #35: separate, metadata-only; no direct BuyBox–Vault call.

## Implemented receiver and protection

`buybox/app.py` has an owner exchange route
`POST /tower/owner-exchange` only in `BUYBOX_AUTH_MODE=tower`. It accepts a
form-encoded signed token in the POST **body**, not a URL query, only from the
configured exact HTTPS BuyBox Origin/Host/path. It bounds Content-Length,
rejects duplicate/extra fields and validates actual signature/issuer/audience,
short lifetime, exact destination and claimed references via the pre-existing
receiver primitive. It separately asks the injected **live, authenticated**
Tower introspection adapter whether that exact session, actor, entity,
entitlement and active step-up are still valid. An arbitrary bool is rejected.

The one-use handoff is consumed in the private SQLite ledger, and a separate
revocable, expiring server-side owner session is written before redirect to the
ordinary app. Flask's client-visible *signed but unencrypted* session cookie
holds only an unpredictable local handle, CSRF token and owner flag. It **does
not contain Tower principal, session, entity, entitlement or the handoff token**.
Every protected route reloads the private binding and revalidates current Tower
truth. A Tower outage, revocation, expiry or mismatched identity clears the
session and fails closed. Owner signout revokes the local binding and returns to
the fixed `/tower/access-home`; there is a safe Return to Tower navigation
link. In hosted mode the local password route is disabled. No financial,
contract, archival or acquisition protection gate is unlocked by login alone.

## Why this code cannot be turned on by environment flags alone

The factory `create_app` requires the existing private-hosted config inspection,
actual filesystem mount checks, Secure cookies, **no local password**, separate
secrets and approved exact HTTPS origins. It also requires **two trusted Python
adapter callables not supplied by this repository**: (1) independently
authenticated, revocation-aware Tower session introspection, and (2) storage
and backup/restore attestation from the approved provisioning integration
against the exact chosen workspace/mount. The format of a callback's response
is checked; this code alone cannot establish that a provider attestor or Tower
adapter is genuinely authoritative. Test injections are explicitly synthetic
and are not release evidence.

A running production WSGI deployment, real Tower issuer, managed disk/DB and
original-object storage, secure secret injection, malware scanner, verified
backup+restore drill, callback attestation and monitored protected owner
walkthrough are **not provided**. The current `python -m buybox.app` remains
localhost development and cannot enter Tower mode from environment flags
alone. Do not set source/test flags as a substitute for independent proof.

## Test matrix

- Local development login still works, with zero fake product listings.
- Hosted mode rejects missing adapters, local password, weak/insecure config
  and an unmounted/private-storage failure.
- Direct GET/POST password entrance cannot authenticate a hosted owner.
- Exact-origin signed single-use exchange succeeds under injected test-only
  Tower and provider fakes; wrong origin/scheme/query/extra or duplicate fields,
  expired or wrong-audience token, replay, and invalid source fail closed.
- Signed cookie excludes readable Tower IDs and raw signed handoff token.
- Cross-request active session revalidation and Tower revocation invalidate
  access and revoke the private session; returning to Tower is fixed.
- Existing complete BuyBox suite and pinned exact Tower/Vault cross-contract
  CI remain required. **Tests here do not assert a live hosted owner crossing.**

## Next coordination — Tower issue #42

Tower team must implement a real issuer bound to its actual owner session,
step-up and verified BuyBox entitlement, with exact approved Origin and this
receiver's `tower.buybox.owner.handoff.v1` wire contract. A genuine live
introspection/revocation adapter must be shared with BuyBox. Hosting must
select/provider-certify a durable private original-document/database
architecture and perform real backup/restore, with owner's price approval
before paid provisioning. Only then can private hosted owner walkthrough and
publication/health certification be executed; keep Tower's launch gate blocked
until verified. Teller, Vault and operational handoff remain separate gates.
