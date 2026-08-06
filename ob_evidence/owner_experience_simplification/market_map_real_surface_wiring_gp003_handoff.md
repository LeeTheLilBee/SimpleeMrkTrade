# 🌦️ OB Market Map Real Surface Wiring Handoff / GP003

## Build name

**OB — Market Map Real Surface Wiring / GP003**

## Primary package

`ob_market_map_real_surface_wiring_gp003`

## Primary acceptance question

**Can the real OB app wire Market Map as Market Weather safely?**

## Decision

**READY_FOR_MARKET_MAP_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD**

## What this builds

This build turns the simplified Market Map contract into a route-ready real
surface adapter for the OB app.

It does not render final production HTML yet. It creates the component,
state, route, deep-dive, and data wiring contract the actual Market Map UI
should use.

## Market Map identity

- Room: `market_map`
- Display title: **Market Weather**
- Question: **What is happening in the market?**
- Route hint: `/ob/market-map`
- Component hint: `MarketWeatherSurface`

## First-glance components

- `MarketWeatherHeroCard`
- `MarketWeatherSoulaanaCard`
- `MarketWeatherRiskFirstCard`
- `MarketWeatherBiggestMovementCard`
- `MarketWeatherOpportunityGarden`
- `MarketWeatherWatchYourStepCard`

## Collapsed / tab-ready components

- `MarketWeatherDeepDiveRoomTabs`
- `MarketWeatherOwnerDrawer`

## Required states

- Loading state
- Empty state
- Error state

## Protected-route policy

- Anonymous access: **not allowed**
- Owner session: **required**
- Tower handoff: **required**
- Dangerous actions: **step-up required**
- Broker submission: **not allowed**
- Money movement: **not allowed**
- Live Auto: **not allowed**

## This does not mean STAGING_READY

This package does **not** authorize:

- `STAGING_READY`
- Production deployment
- Broker submission
- Real capital movement
- Live Auto unlock
- Tower return/session continuity repaired
- Render redeploy
- Owner walkthrough accepted

## Files created or updated

- `ob_owner_experience/market_map_real_surface.py`
- `ob_owner_experience/__init__.py`
- `tests/test_market_map_real_surface_wiring.py`
- `ob_evidence/owner_experience_simplification/market_map_real_surface_wiring_gp003.json`
- `ob_evidence/owner_experience_simplification/market_map_real_surface_wiring_gp003_handoff.md`

## Next builder notes

- Use `MarketWeatherHeroCard` for the first card.
- Keep Soulaana near the top.
- Show risk before opportunity.
- Keep biggest movement and opportunities owner-readable.
- Keep Deep-Dive Rooms collapsed or tab-ready by default.
- Keep broker submission locked.
- Keep real capital movement locked.
- Keep Live Auto locked.
- Do not claim `STAGING_READY`.

## Next build

**OB — Symbol Page Real Surface Wiring / GP004**
