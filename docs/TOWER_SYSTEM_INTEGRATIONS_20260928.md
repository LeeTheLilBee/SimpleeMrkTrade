# Tower ecosystem integrations — September 28, 2026

This packet reconciles current Tower-side integration work without turning source completion into live authorization.

## Grounds

The Grounds product branch is source-complete for external integration and explicitly imports two Tower modules that were previously missing. Tower now supplies those exact boundaries:

- `tower.grounds_runtime_receiver` — independently provided, current/revocable resident/staff/owner request verification plus exact staff directory/assignment adapters.
- `tower.grounds_operational_release` — separate short-lived owner/operations/storage/privacy release authority checked independently from user identity.

Both remain fail-closed unless separately installed server-owned provider modules return current attestations. No environment Boolean, browser role, local fixture, registry entry or passing test can release tenants. Tower does not provision the private PostgreSQL store, approve recovery, certify legal/housing requirements, activate Teller checkout, Vault documents, notification delivery, or real resident accounts in this packet.

## BuyBox

BuyBox already consumes `tower.buybox.owner.handoff.v1`. Tower now has the matching exact short-lived HMAC issuer in `tower.buybox_owner_handoff_issuer`. Issuance requires, independently, current owner authentication, owner role/id, exact Tower session binding, active step-up, verified hosted owner identity, explicit verified BuyBox entitlement, launchable app publication truth and a separate signing secret.

There is deliberately still no `/tower/launch/buybox`. The canonical registry remains `registered_future_room`; current Tower identity does not manufacture a BuyBox entitlement; BuyBox private hosted storage/restore and runtime publication remain separate evidence. Therefore the new issuer source is not presently able to open BuyBox.

## Teller

Teller already has the active protected Tower owner launch, step-up and one-time handoff/exchange implementation on the canonical hosted branch. This packet adds a reciprocal owner-session-preserving `/tower/return/teller` corridor so Teller can return to Access Home without issuing a new grant. Teller product UI still needs to use that route and the actual hosted Teller crossing must be browser-accepted on the selected Tower environment.

## Vault and Clouds

Both products have source routes in the repository, but registry/source presence is not permission. A new hosted Tower direct-route guard covers `/vault`, `/archive-vault`, `/clouds` and `/the-clouds` (plus future Grounds/BuyBox product paths). Authenticated owners still receive a fail-closed response unless an app-specific, short-lived access receipt is bound to the exact current Tower owner/session. No current route mints such receipts for Vault, Clouds, Grounds or BuyBox.

Reciprocal owner return corridors are registered for Vault, Clouds, Grounds and BuyBox now so future protected products share the same Tower-in/Tower-out model as Observatory. Return receipts are navigation evidence only; they grant no app access, tenant permission, storage permission, payment, capital, closing, broker or trading authority.

## Direct-route doctrine

Future application launch code must perform its app-specific entitlement, step-up, publication, provider, receiver and release checks first. Only then may it create a short-lived `tower.ecosystem.access-receipt.v1` bound to the exact current `owner_id` and `tower_session_id`. The generic direct-route guard is not itself a launch authority.

Unknown, stale, cross-session, malformed or absent receipts fail closed. Tower internal `/tower/*` protocol and evidence routes remain separate and are not swallowed by the product-path guard.

## Remaining external gates

- Grounds: actual independently operated identity/grant provider, owner operational-release provider, approved private PostgreSQL + restore evidence, Teller/Vault/delivery/legal/owner acceptance.
- BuyBox: durable approved private hosting/storage + restore, actual publication/health evidence, owner entitlement activation only after those facts, live Tower introspection and owner walkthrough.
- Teller: hosted browser crossing/return acceptance and real financial-provider paths as they are approved.
- Vault: real sealed storage/scanner/recovery/retention authorization and a protected owner launch; no raw-file shortcut.
- Clouds: authenticated freshness-limited source publishers and protected owner launch/return acceptance.
- No direct BuyBox→OB integration. Teller remains the money/readiness boundary.

No paid resources, live tenant traffic, broker submission, Manual Live, Live Auto, capital movement, payroll execution, closing or external Vault file access is activated by this source integration.
