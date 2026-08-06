# 🔎 OB Symbol Page Real Surface Wiring Handoff / GP004

## Build name

**OB — Symbol Page Real Surface Wiring / GP004**

## Primary package

`ob_symbol_page_real_surface_wiring_gp004`

## Primary acceptance question

**Can the real OB app wire Symbol Page as Asset Storybook safely?**

## Decision

**READY_FOR_SYMBOL_PAGE_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD**

## What this builds

This build turns the simplified Symbol Page contract into a route-ready
real surface adapter for the OB app.

It does not render final production HTML yet. It creates the component,
state, route, symbol-context, and data wiring contract the actual Symbol
Page UI should use.

## Symbol Page identity

- Room: `symbol_page`
- Display title: **Asset Storybook**
- Question: **What do I need to understand about this asset?**
- Component hint: `AssetStorybookSurface`
- Symbol context: required
- Destination-only fallback: `/ob/market-map`

## First-glance components

- `AssetStorybookHeroCard`
- `AssetStorybookSoulaanaCard`
- `AssetStorybookNarrativeCard`
- `AssetStorybookRiskBeforeShineCard`
- `AssetStorybookDecisionPostureCard`
- `AssetStorybookTinySignalsStrip`

## Collapsed components

- `AssetStorybookDetailDrawerGroup`
- `AssetStorybookOwnerDrawer`

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

- `ob_owner_experience/symbol_page_real_surface.py`
- `ob_owner_experience/__init__.py`
- `tests/test_symbol_page_real_surface_wiring.py`
- `ob_evidence/owner_experience_simplification/symbol_page_real_surface_wiring_gp004.json`
- `ob_evidence/owner_experience_simplification/symbol_page_real_surface_wiring_gp004_handoff.md`

## Next builder notes

- Use `AssetStorybookHeroCard` for the first card.
- Keep Soulaana near the top.
- Show story, risk, and decision posture before raw chart/news detail.
- Keep symbol context required and destination-only.
- Keep detail drawers collapsed by default.
- Keep broker submission locked.
- Keep real capital movement locked.
- Keep Live Auto locked.
- Do not claim `STAGING_READY`.

## Next build

**OB — Trade Center Real Surface Wiring / GP005**

## Repair note

GP004 now maps the canonical Symbol Page `thesis` section to:

- `AssetStorybookNarrativeCard`

This keeps the real surface adapter aligned with the actual Asset Storybook
contract while preserving the owner-facing first-glance story card.

