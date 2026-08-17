# OBDATA005 — Fake Fallback Removal + Truth Acceptance

## Closed

The engine adapter no longer substitutes V22 preview data when:

- the snapshot route is guarded
- the snapshot route redirects
- the snapshot route returns an error
- fetch fails

The web layer returns unavailable/guarded state instead.

## Preserved

- canonical engine
- pipeline
- stored data artifacts
- Main Dashboard composition
- Owner Dashboard
- Observatory atmosphere
- Tower
- routes

## Safety

- broker API disabled
- order submission disabled
- capital movement disabled
- automated execution disabled
- Live Auto locked
- GP066 parked

## Next

OBUX031–035 — Market Map Experience Rebuild.
