# TWR181–TWR185 — Hosted Migration + Final Active-Staging Purge

Parent: `f96a1de2b83efa31b4c20bef9ff8066d5afec972`

## Canonical hosted Tower

- Service: `simplee-tower-ob`
- WSGI: `web.hosted_tower:app`
- Build: `pip install -r deploy/hosted_tower/requirements.txt`
- Start: `bash deploy/hosted_tower/start.sh`

The retired compatibility WSGI module and retired deployment bundle
are physically absent.

## Current hosted readiness contract

Current hosted release/parity surfaces use:

`hosted_ready_changed`

Historical beta-era STAGING_READY evidence remains historical.

## Observatory doorway

`/tower/launch/observatory`
→ `/tower/observatory/receive`
→ `/ob/dashboard`

The real product endpoint remains `ob_dashboard_v16`.

The Tower Observatory walkthrough remains a separate proof/backstage
surface.

## External host

This source build has not changed Render.

After seal:

1. Service name: `simplee-tower-ob`
2. Build:
   `pip install -r deploy/hosted_tower/requirements.txt`
3. Start:
   `bash deploy/hosted_tower/start.sh`
4. Deploy the exact sealed TWR181–TWR185 SHA.
5. Run the live hosted verifier against that revision.
6. Login through Tower and confirm Observatory opens `/ob/dashboard`.
