# OBDATA003 — Canonical Web Projection

The existing V25 engine adapter remains the web bridge.

It now performs one job:

**project the existing engine snapshot without inventing missing information.**

## Required for a current claim

- source
- as-of timestamp
- acceptable provenance
- timestamp within freshness window

## States

- fresh
- stale
- provenance_required
- quarantined
- rehearsal
- guarded
- unavailable

## Updating

The adapter refreshes:

- on boot
- every 60 seconds while visible
- when the page regains focus
- when the page becomes visible again

## No second engine

No engine/canonical module is replaced or duplicated.
