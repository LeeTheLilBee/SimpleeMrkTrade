# OBUX076–080 — Tower Product Doorway / Walkthrough Decoupling

## Purpose

The owner-facing Observatory launch must land in the real product rather than the historical proof walkthrough.

Tower remains involved only where Observatory access requires identity, owner session, step-up, clearance, receipt compatibility, and return continuity.

The walkthrough remains available as proof/evidence infrastructure but is not required for normal product entry.

## OBUX076 — Product handoff

The canonical product-entry handoff records `/ob/dashboard` as both requested path and destination.

## OBUX077 — Walkthrough compatibility

The legacy walkthrough handoff producer remains available for compatibility with the existing Tower/OB receipt chain.

The owner-facing launch wraps that state into a product handoff and redirects to `/ob/dashboard`.

## OBUX078 — Proof separation

The historical walkthrough is retained only as `proof_walkthrough_path`.

`walkthrough_required_for_product_entry` is false.

## OBUX079 — Product layout independence

Snapshot, candidate, Manual Live receipt, private-beta QA, and engine-expansion panels no longer use hidden mission bars, route bars, V27 room-polish panels, or proof status bars as layout anchors.

## OBUX080 — Safety

This pack adds no broker submission, capital movement, automatic contract selection, or automatic execution capability.

Manual Live is not authorized by the doorway handoff.

Live Auto remains locked.

## Legacy compatibility regression migration

The historical `tower/test_tower_human_login_ob_launch.py` suite still contained
a pre-product assertion requiring the normal owner launch to terminate at
`/tower/observatory-walkthrough`.

That assertion contradicted the canonical OBUX066+ product doorway.

OBUX080 migrates only that destination expectation to `/ob/dashboard`.
The test continues verifying owner login, step-up, launch receipt creation,
and locked safety fields.

The walkthrough itself remains available and separately tested as protected
proof/evidence infrastructure.
