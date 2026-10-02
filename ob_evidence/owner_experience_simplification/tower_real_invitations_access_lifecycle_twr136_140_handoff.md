# THE TOWER — TWR136–TWR140
## Real Invitations + Access Lifecycle

Parent:

`6d901c71019db50c4f66b6066caec29aaa698afe`

This pack introduces a real durable invitation/onboarding state authority.

## Canonical states

- CREATED
- DELIVERY_PENDING
- SENT
- OPENED
- ACCEPTED
- IDENTITY_PENDING
- ACTIVE
- EXPIRED
- REVOKED
- FAILED

## TWR136 — Creation

A durable invitation provider exists only when:

`TOWER_INVITATION_STORE_PATH`

is explicitly configured.

A created invitation receives a cryptographically random one-time token.

Tower persists only the token hash.

The raw token is returned once at invitation creation and is never written to
the invitation store or product projection.

Requested apps begin with:

`granted_apps = []`

Requested access does not equal granted access.

## TWR137 — Delivery

Delivery support is explicit.

Without a configured delivery handoff Tower reports:

> Invitation delivery not configured.

and the invitation remains:

`CREATED`

When external-receipt delivery handoff is explicitly configured, requesting
delivery may move the record to:

`DELIVERY_PENDING`

This is still not SENT.

`SENT` requires provider message and delivery receipt identifiers.

## TWR138 — Open / acceptance / exceptions

`OPENED` requires an explicit provider event.

`ACCEPTED` requires verification of the actual one-time invitation token.

Expiry is derived from real timestamps.

Revocation and failure require explicit transitions.

No state is inferred from elapsed UI behavior.

## TWR139 — Identity and activation boundary

After ACCEPTED, an identity binding request may move the invitation to:

`IDENTITY_PENDING`

The pending binding is not called verified.

`ACTIVE` exists in the canonical state vocabulary, but this pack deliberately
does not permit transition to ACTIVE.

Tower still lacks a general invited-user identity authority plus entitlement
mutation authority.

Therefore:

`Access activation authority not configured.`

Acceptance does not create an account.

Acceptance does not grant Observatory or any other app.

## TWR140 — Owner Headquarters

When a durable invitation store is configured, Owner Headquarters may show
authoritative invitation counts and states.

A configured empty provider may truthfully show:

`0 invitations`

An unconfigured provider still reports:

`None / NOT_CONFIGURED`

The UI is read-only in this pack. Consequential owner action surfaces remain
for the later canonical owner-action framework.

## Preserved

Unmodified:

- `tower/identity_authority.py`
- `tower/app_registry.py`
- `tower/tower_human_login_ob_launch.py`
- `tower/hosted_owner_release_walkthrough_web.py`

Observatory remains untouched.

## Next

**TWR141–TWR145 — Authoritative App Publication + Availability**

This build does not stage, commit, or push.
