# Tower Grounds + BuyBox owner launch gates — 2026-10-01

## What this changes

Tower now owns exact authenticated launch-gate routes for two ecosystem products that previously had only source contracts:

- `GET /tower/launch/grounds`
- `GET /tower/launch/buybox`
- shared owner step-up: `GET/POST /tower/step-up/ecosystem?app=<grounds|buybox>`
- owner-only read status: `/tower/launch/grounds.json`, `/tower/launch/buybox.json`

The canonical registry points Grounds and BuyBox at those Tower gates. They intentionally remain `registered_future_room`; route registration is not product release.

## Grounds

The Grounds launch may redirect to same-origin `/grounds` only when all are independently true:

1. current Tower owner session,
2. fresh Tower step-up,
3. current app publication/environment/health/owner-entitlement truth is launchable,
4. a real same-origin Grounds route is mounted,
5. the independently installed `tower.grounds_runtime_receiver` is certified/healthy,
6. the independent `tower.grounds_operational_release` authority is approved/healthy.

Only then does Tower write the existing short-lived `tower.ecosystem.access-receipt.v1` bound to the current owner/session. The generic direct-route guard remains authoritative. No tenant access, payments, capital, or legal/property release is manufactured by this route.

## BuyBox

Tower can inspect the existing signed `tower.buybox.owner.handoff.v1` issuer preflight, but **does not issue or transmit a handoff token yet**. BuyBox's receiver accepts an exact same-origin form POST at `POST /tower/owner-exchange`; a cross-origin Tower form would be rejected, and putting the signed bearer in a query/localStorage/cookie would weaken the reviewed contract.

Therefore the Tower launch gate reports `BUYBOX_BROWSER_BOOTSTRAP_NOT_IMPLEMENTED` even if the signed issuer preflight becomes otherwise ready. A separate reviewed BuyBox-side same-origin browser bootstrap must be implemented before the Tower gate may mint and deliver the 60-second token.

## Integration Desk and Vault

The Integration Desk can show **Check Tower launch gate** for Grounds/BuyBox while still reporting the product runtime as blocked. This is deliberately distinct from **Open through Tower**, which remains reserved for independently verified hosted launchability.

Archive Vault remains protocol/evidence/recovery gated; this change does not add a generic `/tower/launch/vault` doorway. Teller and Clouds preserve their existing reviewed launch contracts.

No paid resources, provider credentials, broker execution, capital movement, payment execution, closing authority, live tenant release, or Vault raw-content access are enabled.
