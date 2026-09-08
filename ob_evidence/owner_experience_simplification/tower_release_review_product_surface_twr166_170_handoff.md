# THE TOWER — TWR166–TWR170

## Release Review Product Surface

`/tower/owner/release-review` is now designed as an owner decision room.

It is not an evidence page and it is not a release-execution room.

## TWR166 — Release Review hierarchy

The room now answers four questions first:

1. What exact candidate am I reviewing?
2. What does Tower currently know about readiness?
3. What owner decision can I record?
4. What remains locked?

If there is no sealed current candidate, the room fails closed and presents
no owner decision form.

## TWR167 — Candidate decision surface

The exact candidate identity is visible on the primary surface.

The existing decision semantics remain:

- `APPROVE_RELEASE` → Approve candidate
- `HOLD_RELEASE` → Place on hold
- `REJECT_RELEASE` → Reject candidate

Candidate evidence remains available through progressive disclosure rather
than dominating the owner experience.

## TWR168 — Readiness + prerequisite summary

The primary room shows only operational meaning for:

- hosted readiness
- prerequisite certification state

Detailed walkthrough proof, readiness evidence, certificate records, and
verification material stay backstage in:

`/tower/owner/evidence`

Historical TWR154 wording remains preserved:

`Evidence & readiness details`

## TWR169 — Owner decision boundaries

Approval is owner decision recording only.

Hold is owner decision recording only.

Rejection is owner decision recording only.

No decision performs:

- deployment
- promotion
- release execution
- broker submission
- capital movement
- Manual Live authorization
- Live Auto activation

A separate release-execution gate remains required.

## TWR170 — anti-regression

The primary Release Review source may not add direct navigation to:

- `/tower/owner/release-review/walkthrough`
- `/tower/owner/release-review/prerequisites`

It may not add an execution, deployment, promotion, broker, capital,
Manual Live, or Live Auto action.

Historical TWR101–TWR105 focused-room contracts remain preserved:

- Release Review
- Approve candidate
- Candidate evidence
- Execution
- Still locked
- NO REVIEWABLE CANDIDATE

## Pack scope

Modified:

- `tower/hosted_owner_release_review_web.py`

New:

- `tests/test_tower_release_review_product_surface_twr166_170.py`
- `ob_evidence/owner_experience_simplification/tower_release_review_product_surface_twr166_170.json`
- `ob_evidence/owner_experience_simplification/tower_release_review_product_surface_twr166_170_handoff.md`

Exactly four files.

## If green

Seal TWR166–TWR170.
