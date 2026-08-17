# OBDATA002 — Seed / Demo / Rehearsal Contamination Boundary

## Rule

Seed, demo, preview, fixture, bootstrap, synthetic, and rehearsal material
may remain useful inside development and QA.

They may not silently become current market truth.

## Preserved

The old visual/static market fixture was preserved at:

`web/static/ob/demo/ob_market_data_demo.js`

## Live compatibility path

`web/static/ob/ob_market_data.js`

now contains an empty quarantined compatibility object.

No old visual work was destroyed.

## Important

`market_universe.py` static equity/diversity seeds remain in the engine
because they are useful for discovery/universe membership.

Universe membership is not a quote, signal, candidate, or position.
