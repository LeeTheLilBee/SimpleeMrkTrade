# OBML011–015 — canonical mission-account identity export for Tower

**Source-only signed namespace contract, not Tower authentication or Manual Live.**
Parent Observatory main: dc2960c51266807acd309e46cc613b857d119858.
This pack reuses the existing web.ob_account_identity_truth resolver and
web.ob_owner_operating_profile namespace; it does not invent another account
registry or query any trading balance.

## Distinct source responsibility

OB owns the canonical identity fingerprint for an explicitly selected mission
account. Tower owns the actual person, active session/device, effective
entitlement, fresh purpose-specific step-up, revocation and request routing.
The broker owns real account/option permissions and fill truth. A valid
namespace fingerprint is **not** any of these independent credentials.

web.ob_tower_account_identity_export.py adds a dedicated short-lived HMAC
source export, intended only for a future authenticated private OB-to-Tower
transport. Format obai1.canonical_base64url(payload).HMAC-SHA256. Claims
contain only fixed issuer/audience/schema, exact account key, the existing
canonical identity fingerprint and namespace authority, mission-account and
UNKNOWN capital truth classifications, random nonce and issuance/expiry.
No balances, positions, P&L, broker credentials, owner/Tower session material,
broker permission, cap release or execution scope is exported. Proof/Demo
and unknown, nonexact or implicit-default accounts fail closed. Maximum
source export TTL is 60 seconds. Dedicated distinct 32+ byte signing key
is supplied by a future secure server caller; this pack reads or configures
no environment secret and exposes no HTTP endpoint.

Even a valid source-signed packet makes
owner_authentication_asserted=False, broker_account_verified=False,
real_capital_verified=False and manual_live_granted=False. Tower's next
versioned independent receiver must check the exact HMAC, audience/issuer,
time and nonce replay, and compare the current OB canonical account identity.
It must separately bind the current Tower owner session and OBML-purpose step-up,
source/effective policy, real broker evidence and Review Center receipt.
Do not copy OB's account resolver wholesale into a second active Tower owner
identity database or treat a browser-provided token as an authenticated
server-to-server exchange.

Tests cover all five non-demo mission account namespaces, source fingerprints,
non-reused nonces, no balance/secret leakage, proof-demo/unknown rejection,
invalid times, weak/wrong signing keys and permanent false execution flags.

## Remaining real work

1. Build separate Tower-side receiver with an explicit issuer-bound HMAC check
   and durable single-use nonce ledger; no receiver installed by this pack.
2. Verify a *server-provided* current OB account source, account change/revision
   and Tower's current owner/entitlement/step-up/session/revocation independently.
3. Consumer-side account matching and OB safety/effective policy do not attest
   live brokerage permission or fund availability. Human places any eventual
   allowed order manually in the broker app after separate real gates.
4. Live acceptance remains blocked; no new paid Render/cloud resource is
   authorized and PR #68 is still a Tower work request, not a live grant.
