# Observatory Owner Dashboard — Activation Handoff

## Purpose

Activate the already-built Observatory Owner Dashboard behind its existing
Tower-protected owner-only doorway.

This handoff does not consume OBUX031–035. Those packs remain reserved for
the Market Map Experience Rebuild.

## Canonical route

- Active: `/ob/owner-dashboard`
- Removed legacy alias: `/owner-dashboard`

## Surface separation

The two owner dashboards are different systems:

- `/tower/owner-dashboard` — Tower people/access desk.
- `/ob/owner-dashboard` — Observatory strategic owner intelligence.

Owner Console also remains separate:

- `/ob/owner-console` — deep administration, diagnostics, and controls.

## Activation

The Observatory Owner Dashboard now renders:

- `web/templates/owner_dashboard.html`

Its already-accepted CSS, JavaScript, Soulaana layer, and guarded owner
intelligence contract are not redesigned by this handoff.

## Tower

Tower remains the permission authority.

The Observatory Owner Dashboard remains:

- owner-only
- owner-session protected
- default-denied when unknown
- separate from normal step-up room behavior

The temporary placeholder state is retired.

## Safety

- Live Auto remains locked.
- Broker API remains disabled.
- Broker order submission remains disabled.
- Real capital movement remains disabled.
- Auto execution remains disabled.
- No real Tower account creation is enabled here.
- No real invite sending is enabled here.
- No real access grants are enabled here.

## Preservation

This handoff does not modify:

- OBDATA001–005
- canonical market projection
- Owner Dashboard CSS/JS/contracts
- Observatory atmosphere
- normal Dashboard composition
- Market Map experience
- engine
- canonical runtime data
