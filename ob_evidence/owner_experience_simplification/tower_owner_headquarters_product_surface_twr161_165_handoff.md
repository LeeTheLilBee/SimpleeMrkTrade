# THE TOWER — TWR161–TWR165

## Owner Headquarters Product Surface

Owner Headquarters is now an owner workspace instead of a proof-first
or giant-status-list surface.

## TWR161 — Owner Headquarters hierarchy

`/tower/owner-dashboard` now answers three owner questions first:

1. What state matters?
2. What can I do now?
3. What remains locked?

The normal navigation is:

- Access Home
- Owner Headquarters
- Release Review
- Logout

Evidence is intentionally absent from the primary navigation rail.

## TWR162 — Owner state snapshot

The primary surface summarizes:

- people authority
- invitation authority
- access authority
- relevant counts

A missing authority count stays unavailable and renders as `—`.

`None` is never converted into fake `0`.

Detailed people/access records and supporting status cards remain available
under progressive disclosure.

## TWR163 — Operational next moves

Release Review is the primary operational owner action:

`/tower/owner/release-review`

Owner Headquarters does not add release execution, broker submission,
capital movement, Manual Live, or Live Auto actions.

## TWR164 — Backstage evidence boundary

Evidence and certification remain available behind progressive disclosure:

`/tower/owner/evidence`

Walkthrough and prerequisite proof do not return to primary owner navigation.

Historical TWR119/TWR127 prerequisite-route compatibility remains preserved
as inert HTML metadata only. It is not a clickable owner action.

## TWR165 — anti-regression

The following danger boundaries remain visible and closed:

- Live Auto
- broker execution
- capital movement
- release execution

This pack does not modify the authority engines that produce those states.

## Pack scope

Modified:

- `tower/owner_dashboard_web.py`

New:

- `tests/test_tower_owner_headquarters_product_surface_twr161_165.py`
- `ob_evidence/owner_experience_simplification/tower_owner_headquarters_product_surface_twr161_165.json`
- `ob_evidence/owner_experience_simplification/tower_owner_headquarters_product_surface_twr161_165_handoff.md`

Exactly four files.

## Safety

Nothing in this pack authorizes:

- release execution
- broker submission
- capital movement
- Manual Live
- Live Auto
- direct Vault writes

Observatory remains untouched.

## If green

Seal TWR161–TWR165.
