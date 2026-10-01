# Grounds ↔ Tower integration reconciliation — GRD219–224
**October 1, 2026 | source integration advanced; live resident release still closed**

## Tower work now available

Grounds no longer needs to treat the Tower adapter modules themselves as missing.

The authoritative Tower development lane has merged these source boundaries:

- **Tower PR #181** — current Tower session + Grounds property/unit/job reconciliation source.
- **Tower PR #189** — the exact modules/factory names Grounds imports:
  - `tower.grounds_runtime_receiver.create_certified_grounds_receiver()`
  - `tower.grounds_runtime_receiver.create_certified_grounds_staff_directory()`
  - `tower.grounds_runtime_receiver.create_certified_grounds_staff_resolver()`
  - `tower.grounds_operational_release.create_certified_grounds_operational_release_guard()`
- **Tower PR #296** — authenticated owner + step-up Grounds launch gate.
- **Tower PR #326**, merged as `9c09e9ada6621ffa5a4256f0e343426dec0af895` — fail-closed same-origin Grounds runtime mount and current Tower↔Grounds cross-branch contract CI.

Tower’s integration CI now checks out the current Grounds development branch and proves that the real current Tower adapter factories normalize into the real current Grounds `TowerScope`, that the staff directory/resolver shapes agree, that the operational-release callable/health shape agrees, and that the actual Grounds production factory resolves the current Tower factory names. It also proves that a random `/grounds` route cannot satisfy the Tower launch gate; only the reviewed same-origin mount attestation can.

## What is no longer a blocker

The following old statements are retired:

- “Tower has not implemented `tower.grounds_runtime_receiver`.”
- “Tower has not implemented `tower.grounds_operational_release`.”
- “Tower has no authenticated owner launch route for Grounds.”
- “Tower has no reviewed same-origin mount source for the Grounds WSGI runtime.”

Those source pieces now exist and are cross-tested.

## What is still genuinely blocked

### 1. Actual runtime identity/grant provider
The Tower adapter intentionally loads a separately installed server-owned provider via `TOWER_GROUNDS_RUNTIME_PROVIDER_MODULE`. Source presence does not create that provider. The provider must produce a current Tower→Grounds attestation and independently verify the original request/session, revocation/logout, exact role, property, unit/lease membership and job grants. It must also supply the current technician directory and exact assignment verifier.

**Status: NOT CONNECTED / NOT CERTIFIED FOR LIVE PEOPLE.**

### 2. Actual independent operational-release provider
The Tower release adapter loads a separate provider via `TOWER_GROUNDS_RELEASE_PROVIDER_MODULE`. Its current decision must bind the exact environment/revision to owner acceptance, successful storage restore evidence, privacy/housing review and operations coverage, with revocation rechecked and a short lifetime.

**Status: NOT CONNECTED / NO LIVE APPROVAL DECISION.**

### 3. Private Grounds data environment
Grounds still requires an approved private PostgreSQL deployment, reviewed versioned migration, TLS/network/secret controls, retention, backup and an observed successful restore. The same-origin mount will not register if Grounds’ own production factory cannot complete this preflight.

**Status: NOT PROVISIONED OR RECOVERY-CERTIFIED BY THIS SOURCE WORK.**

### 4. Tower publication/entitlement truth
The owner launch gate also requires current authoritative application publication/environment/health truth and owner entitlement before it will issue the short-lived owner/session-bound access receipt.

**Status: MUST BE VERIFIED IN THE ACTUAL HOSTED ENVIRONMENT.**

### 5. Resident/staff Tower entry
The newly reviewed same-origin crossing is an **owner** launch corridor. It deliberately does not create resident/staff Tower launch or tenant entitlements. Real resident/staff entry needs a separately reviewed multi-role Tower session/entry path backed by the certified runtime provider.

**Status: NOT ACTIVATED.**

### 6. Teller, Vault, delivery/on-call and legal acceptance
No change: Teller remains authoritative for rent invoice/checkout/reconciliation; Vault for protected originals/contact/evidence; real providers for recipient delivery/retry/dead-letter and current human on-call escalation; qualified review remains required for housing, privacy, entry/notices and accessibility.

**Status: EXTERNAL / NOT CERTIFIED HERE.**

## Grounds production behavior

`grounds.production_entry.create_wsgi_application()` still fails closed. Its updated error language now distinguishes three separate facts:

1. Tower adapter modules are absent from the deployed revision;
2. the adapter modules exist but their independent providers fail certification/initialization;
3. the private Grounds database/runtime preflight fails.

None of those errors prints a DSN, credential, provider diagnostic or private tenant detail.

## Release decision

This reconciliation advances Grounds from **“waiting for Tower source modules”** to **“Tower/Grounds source contracts aligned; waiting for real provider/environment certification.”**

Grounds PR #51 remains DRAFT / NOT LIVE. No real tenant, resident/staff session, payment, notification, emergency call, legal notice, private file, paid resource or production migration is created by GRD219–224.
