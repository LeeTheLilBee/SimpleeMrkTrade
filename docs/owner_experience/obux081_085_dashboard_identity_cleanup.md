# OBUX081–085 — Dashboard Mission Residue Final Retirement + Observatory Color Identity

Parent: `28efa5043b4c0553f7755cf2e283662f61fa816b`

## Owner feedback driving this pack

Hosted owner walkthrough confirmed that the new Observatory product structure looked good, but two presentation defects remained:

1. mission-account residue was still visible/represented at the top of the normal Dashboard experience;
2. Observatory color identity was still too close to Tower's plum/gold identity and the intended newer colors were not reliably appearing on the hosted surface.

## OBUX081 — Mission residue final retirement

Normal `/ob/dashboard` does not load the mission-account renderer.

This pack strengthens that boundary by:

- removing `data-ob-mission-layout` from non-owner mission surfaces;
- preventing normal Dashboard Settings from presenting a Mission bar preference;
- retaining the mission preference only when the exact path is `/ob/owner-dashboard`;
- preserving the underlying mission-account implementation rather than deleting the system.

## OBUX082 — Early theme authority

Dashboard now selects the Observatory theme before first stylesheet paint.

The new storage key is:

`ob.appearance.theme.v2`

Old theme selections from the previous plum/gold family do not silently win during hosted arrival.

## OBUX083 — Observatory identity

Tower remains visually separate and untouched.

Observatory now uses:

- space black;
- telescope teal;
- aurora mint;
- moon-silver;
- guarded red.

Default theme:

`aurora-ink`

Alternates:

- `deep-field`
- `lunar-sage`

Historical CSS variable names such as `--ob-gold` and `--ob-purple` remain only as compatibility aliases for older room styles. Their values are no longer Tower-style gold/plum.

## OBUX084 — Hosted cache identity

Canonical OB templates now request the changed theme and cleanup assets using:

`?v=obux081085`

This prevents stale OBUX061/071 URLs from remaining authoritative in hosted browser caches.

## OBUX085 — Safety

This pack changes owner-facing presentation only.

It does not add:

- broker submission;
- capital movement;
- automatic contract selection;
- automatic execution;
- Manual Live authorization;
- Live Auto authorization.

Tower source files are outside the pack scope.
