# Simplee World Ecosystem Integration Fabric

## Locked boundary

**Clouds knows where. Tower controls every protected crossing. The receiving app controls what happens after entry.**

Clouds never receives authority merely because it can see a status or recommend a destination.

## Canonical crossing

Clouds emits structured navigation intent:

- app
- destination
- optional item
- return context

Tower validates the intent against `tower/ecosystem_destination_registry.py`.

Canonical route:

`/tower/ecosystem/launch/<app_id>`

Tower owns:

- owner session
- owner permission
- step-up
- destination allowlist
- item validation
- handoff receipt
- return context
- default deny

## Current line truth

### Open

- The Tower
- The Clouds
- The Observatory

### Summary-only

- Archive Vault

Vault has a real safe status bridge. Tower does not treat that as equivalent to an unrestricted operational Vault owner room.

### Contract-ready, receiving runtime not operational in this branch

- The Teller
- The Grounds
- ATM Operations

The UI must not render these as live or operational.

## Observatory adapter

The Observatory adapter reuses the existing protected-room integration and real six-room route map. It does not create a second OB security model.

## Return context

A Tower session remembers the Clouds origin context during an app visit. HTML app surfaces receive a compact **Return to Clouds** control. Returning restores the owner command with the source context preserved.

## ADHD-friendly owner experience

Clouds leads with:

1. Needs You
2. Keep Watching
3. Can Wait

Meaning comes before evidence. Technical details stay behind disclosure drawers. The Ecosystem Lines view is a card grid, not a proof-page list.

## Runtime identity

The active hosted WSGI entrypoint is:

`web.runtime:app`

The active deploy lane is:

`deploy/runtime/`

Historical pre-release evidence can remain in Git history. Active runtime identity must not depend on `web.managed_staging:app`.

## Security invariants

- unknown app → deny
- unknown destination → deny
- invalid item → deny
- required step-up missing → step-up / deny
- receiving runtime unavailable → explain, never fake launch
- Clouds direct protected-app bypass → forbidden
- navigation handoff ≠ business-action authority
- navigation handoff ≠ capital movement
- navigation handoff ≠ downstream execution
