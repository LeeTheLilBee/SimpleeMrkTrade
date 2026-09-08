# THE TOWER — TWR146–TWR150

## Real Owner Tower → Observatory Cutover

This pack cuts the owner’s operational Observatory launch path away from the
historical GP046 rehearsal bridge.

The GP046 module remains preserved backstage for historical proof and
compatibility testing. It is no longer the public operational launch path.

## Operational chain

Tower owner session

→ current hosted owner identity verification

→ current Observatory entitlement

→ TWR141–TWR145 launchability verification

→ active step-up

→ signed short-lived opaque handoff code

→ durable one-time replay ledger

→ receiving boundary re-verifies current authority

→ signed session-bound Observatory access receipt

→ `/ob/dashboard`

## One-time handoff

The raw handoff code is returned transiently once and is never persisted.

The durable ledger stores only:

- SHA-256 code hash
- handoff ID
- canonical signed payload
- HMAC signature
- issuance / expiry
- consumption state
- safe receipt ID

Replay is rejected atomically.

## Protected Observatory entry

Owner session + step-up alone are no longer sufficient for normal OB rooms.

Normal protected rooms also require the signed access receipt created by a
successfully consumed real Tower→OB handoff.

Owner-only administrative OB rooms retain their existing owner-session boundary.

## No walkthrough fallback

If:

- owner identity is unavailable,
- entitlement is unavailable,
- publication/availability/health is unavailable or stale,
- session secret is not configured,
- durable handoff ledger is not configured,
- step-up is absent,

the real owner launch fails closed.

It does not redirect into a walkthrough and it does not manufacture a
successful rehearsal.

## Safety

This pack grants application entry only.

It does not authorize:

- broker submission
- capital movement
- Manual Live trading authority
- Live Auto
- release execution

## Next

TWR151–TWR155 — Evidence Basement Cutover.
