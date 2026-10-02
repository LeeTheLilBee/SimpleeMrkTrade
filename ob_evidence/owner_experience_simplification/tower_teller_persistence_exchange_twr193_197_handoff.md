# TWR193–TWR197 — Teller Persistence Exchange v2

Source parent:

`0508f941684b3a81a29b7a08c98bd201b6df8dd0`

Sealed Teller receiver:

`fd430134295167c6ee10e8c2d27a59592fa5d353`

## Boundary

Historical `tower-teller-exchange.v1` remains supported.

Persistence-capable hosted startup uses:

`tower-teller-exchange.v2`

on the existing:

`POST /tower/teller/exchange`

## Tower authority

The v2 response derives:

- `tower_session_id` from Tower-generated authenticated-session state
- `receipt_id` from the consumed Tower one-time handoff receipt
- `actor_id` from Tower's verified hosted owner identity
- `role` from Tower's verified owner role
- `business_key` from Tower's verified organization ID

Browser request values do not create or override these claims.

## Token

Tower issues:

`tpt1.<base64url-json-payload>.<HMAC-SHA256-signature>`

using environment-only:

`TELLER_TOWER_TOKEN_SECRET`

The token uses:

- issuer `tower`
- audience `teller-persistence`
- maximum lifetime 600 seconds
- default lifetime 300 seconds
- fresh cryptographic `jti`

The token is returned only in the exact-origin successful v2 response.

It is not added to Tower URLs, receipts, logs, or persistent storage.

## Not activated here

This source pack does not:

- deploy Tower
- mutate Render
- modify Teller
- activate Teller static hosted persistence
- add employee/manager hosted launch authority
- add team delegation
- add direct Teller → Vault access
- add payroll/payment execution
- add bank or broker execution
- add Manual Live or Live Auto authority
