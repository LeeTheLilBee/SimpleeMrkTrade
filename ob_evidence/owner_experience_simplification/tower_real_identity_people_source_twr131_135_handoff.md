# THE TOWER — TWR131–TWR135
## Real Identity + People Source

Parent:

`1a64f1a523f86f1b9c26ea4d4900ad76fc23fddd`

TWR131–TWR135 moves Tower from:

`identity authority NOT_CONFIGURED`

to a real secret-free projection over the same hosted owner configuration used
by the existing Tower authentication layer.

## TWR131 — Hosted owner identity

Product identity uses the hosted configuration contract:

- `TOWER_OWNER_USERNAME`
- `TOWER_OWNER_PASSWORD_HASH`
- optional `TOWER_OWNER_ID`

The product projection never returns:

- the password hash value
- plaintext password
- Tower session secret

Explicit local walkthrough configuration is excluded from product people truth.

If the hosted username and credential hash are absent, Owner People remains:

`NOT_CONFIGURED`

No person is fabricated.

## TWR132 — Role + organization

The current owner login policy supports a verified derived role:

`owner`

Organization membership is shown only when both optional values are explicitly
configured:

- `TOWER_ORGANIZATION_ID`
- `TOWER_ORGANIZATION_NAME`

Otherwise organization membership remains unconfigured or unverified.

## TWR133 — Account-state honesty

Tower may truthfully state:

`AUTHENTICATION_CONFIGURED`

when hosted hashed credentials are configured.

This pack does NOT claim:

`ACTIVE`

as an account lifecycle state.

Suspend / disable / restore authority does not exist yet, so:

`account_lifecycle_state = NOT_CONFIGURED`

## TWR134 — Observatory access policy

The current owner role may project:

`Observatory access policy = GRANTED`

from the current Tower owner-role/application registry contract.

That does NOT mean:

- Observatory runtime is reachable
- Observatory runtime is healthy
- Observatory deployment is current
- broker execution is enabled
- capital movement is enabled
- Manual Live is enabled
- Live Auto is enabled

Runtime availability remains:

`UNKNOWN`

Future registered products receive no people-authority grant.

## TWR135 — Owner People + Owner Headquarters

When hosted owner identity is configured:

- Owner People contains one real configured identity
- people count may truthfully be `1`
- owner role count may truthfully be `1`
- Observatory owner access policy may be shown as `GRANTED`

Still unconfigured:

- invitation lifecycle
- invitation count
- account/access mutation lifecycle
- pending access count
- suspension lifecycle

Missing values remain null / NOT_CONFIGURED rather than fake zero.

## Preserved boundaries

The following files are byte-identical to the sealed parent:

- `tower/app_registry.py`
- `tower/hosted_owner_release_walkthrough_web.py`
- `tower/tower_human_login_ob_launch.py`

No Tower→OB launch behavior changes occur in this pack.

No Observatory checkout is modified.

## Next

**TWR136–TWR140 — Real Invitations + Access Lifecycle**

That pack may introduce actual invitation/access lifecycle state, but it must
continue the same rule:

> Tower presents verified reality, explicit uncertainty, or explicit unavailability.

This build does not stage, commit, or push.
