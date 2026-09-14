# THE TOWER — TWR171–TWR175

## Owner Step-Up + Verification Product Surface

The Release Review verification checkpoint is now a deliberate
owner-facing Tower product surface instead of a bare password form.

## TWR171 — Owner verification hierarchy

The owner sees:

- the protected destination
- why fresh verification is required
- the identity checkpoint
- the exact return destination

Canonical route:

`/tower/owner/release-review/step-up`

## TWR172 — Verification purpose and authority

Verification confirms owner identity only.

It does not:

- approve a candidate
- execute a release
- deploy
- promote
- submit to a broker
- move capital
- authorize Manual Live
- activate Live Auto

## TWR173 — Return continuity

Historical TWR104 behavior remains exact:

- successful verification returns HTTP 303
- destination remains `/tower/owner/release-review`
- owner remains inside Tower
- no Observatory redirect is introduced

## TWR174 — Failure and expiry

Fail-closed behavior remains authoritative:

- non-owner -> Tower login
- expired/missing step-up -> verification checkpoint
- missing/invalid CSRF -> 403
- bad origin -> 403
- wrong owner password -> 403

Failed verification creates no step-up window.

## TWR175 — Anti-regression

Existing POST mechanics remain intact:

- owner session required
- same-origin required
- CSRF required
- existing credential verifier used
- existing step-up duration used
- existing step-up session key used
- exact 303 return retained

Password input never renders a password value back.

## Exact pack scope

Modified:

- `tower/hosted_owner_release_review_web.py`

New:

- `tests/test_tower_owner_step_up_verification_product_surface_twr171_175.py`
- `ob_evidence/owner_experience_simplification/tower_owner_step_up_verification_product_surface_twr171_175.json`
- `ob_evidence/owner_experience_simplification/tower_owner_step_up_verification_product_surface_twr171_175_handoff.md`

Exactly four files.

## If green

Seal TWR171–TWR175.
