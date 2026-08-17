# OBDATA004 — Canonical Room Data Contracts

All room contracts now consume the same canonical web projection.

Rooms:

- Dashboard
- Market Map
- Symbol Page
- Trade Center
- Review Center
- Owner Console

## Removed synthesis

Room contracts no longer:

- create a fallback market sector
- default missing symbols to MU
- force MU / AMD / INTC into open positions
- derive a fake market-health score from card tiers
- generate candidates from visual tiers
- generate a Manual Live queue from those candidates
- manufacture current notifications
- patch preview sectors into the live market object

Missing information remains missing.
