# Tower Grounds real owner runtime provider — October 1, 2026

## Purpose

This is the first non-fixture implementation behind the already-reviewed
`tower.grounds_runtime_receiver` adapter.

`simplee_integrations.grounds_owner_runtime_provider` is intentionally
**owner-only**. It enables a real owner beta identity path without pretending
Tower has resident/staff account lifecycle or staff-directory authority.

## Identity truth

A Grounds owner request is accepted only when all are current:

1. Tower's signed Flask session is authenticated with role `owner`;
2. the current Tower session has a server-created, current
   `tower.ecosystem.access-receipt.v1` for exactly `grounds`;
3. Tower's hosted owner identity authority is VERIFIED and has exact
   session-subject alignment from an explicit `TOWER_OWNER_ID`;
4. the hosted owner identity policy contains a VERIFIED/GRANTED Grounds
   owner-corridor entitlement;
5. the request being verified is the current same-origin `/grounds...` WSGI
   request.

Browser headers, query/body values, requested role, property lists and unit
lists are ignored as identity/grant sources.

## Resource grant truth

Owner property grants are read on every verified request from the actual private
Grounds PostgreSQL `properties` table through the reviewed
`grounds.postgres.PostgresGroundsStore` adapter and its schema preflight.

The provider does **not** read property grants from an environment allowlist.
It rejects an empty, malformed, duplicate or >500-property grant set.

The resulting short-lived Tower→Grounds claim contains:
- issuer `tower`;
- audience `grounds`;
- exact Tower owner subject/session;
- role `owner`;
- current real Grounds property refs;
- no unit grants;
- no assigned-work grants;
- at most 60 seconds lifetime and never beyond the current Tower Grounds access
  receipt.

## Staff / resident boundary

The provider exposes the function names required by the Tower adapter, but it
returns an **empty technician directory** and rejects technician assignment
verification. Tower does not yet have a separately authoritative staff people
and assignment source, so deriving staff identities from `work_orders` would
be unsafe.

Resident and staff browser sessions are not created by this provider. They
remain closed pending separately reviewed Tower account/session lifecycle and
current Grounds membership/assignment providers.

## Owner entitlement

Tower's hosted owner identity authority now includes a Grounds owner-corridor
policy entitlement alongside Observatory and Teller when the exact canonical
Grounds owner launch route is registered. This entitlement is intentionally
separate from runtime publication, provider health, property grants and
operational release.

## PostgreSQL-backed CI

`.github/workflows/tower-grounds-owner-runtime-provider.yml` starts PostgreSQL
16, applies the **current Grounds branch's exact baseline schema**, inserts one
synthetic property, configures a real hosted-owner identity in process, creates
a real Tower server-side Grounds access receipt, and passes the request through:

**signed Tower session → exact Grounds access receipt → real owner provider →
Tower runtime adapter → current Grounds `TowerScope`.**

It proves browser-supplied role/property headers cannot widen the grant and
that removing the Tower access receipt immediately closes the receiver.

No real person, property, credential, hosted database or paid resource is used
by CI.

## Required runtime configuration later

The reviewed adapter can load this provider only when the server sets:

`TOWER_GROUNDS_RUNTIME_PROVIDER_MODULE=simplee_integrations.grounds_owner_runtime_provider`

The provider also requires the existing:
- `GROUNDS_PRIVATE_POSTGRES_URL`;
- hosted Tower owner identity configuration including explicit
  `TOWER_OWNER_ID`;
- same-origin Grounds source/runtime;
- Tower owner launch/access receipt.

Setting the provider module environment variable does **not** bypass any of
those checks.

## Still blocked

This provider does not satisfy the independent operational-release provider,
private DB backup/restore approval, resident/staff Tower accounts, Teller
checkout/reconciliation, Vault evidence, delivery/on-call operations,
legal/privacy/accessibility review or owner hosted release acceptance.

No real live release is authorized by source merge alone.
