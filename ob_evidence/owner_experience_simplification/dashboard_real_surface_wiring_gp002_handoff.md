# 🌙 OB Dashboard Real Surface Wiring Handoff / GP002

## Build name

**OB — Dashboard Real Surface Wiring / GP002**

## Primary package

`ob_dashboard_real_surface_wiring_gp002`

## Primary acceptance question

**Can the real OB app wire Dashboard as Today’s Command Nest safely?**

## Decision

**READY_FOR_DASHBOARD_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD**

## Repair note

GP002 now derives the Dashboard section order from the actual Dashboard
contract. The existing contract uses canonical keys such as:

- `indicators` for the Tiny Signals section
- `drawers` for Details When Needed

The UI adapter maps those canonical keys to friendly component names:

- `DashboardTinySignalsStrip`
- `DashboardDetailsDrawerGroup`

## Dashboard identity

- Room: `dashboard`
- Display title: **Today’s Command Nest**
- Question: **What needs my attention today?**
- Route hint: `/ob/dashboard`
- Component hint: `DashboardTodayCommandNest`

## First-glance components

- `DashboardHeroCard`
- `DashboardSoulaanaCard`
- `DashboardNeedsYourEyesList`
- `DashboardTinySignalsStrip`
- `DashboardOwnerNextMoveCard`

## Collapsed components

- `DashboardDetailsDrawerGroup`
- `DashboardOwnerDrawer`

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

## Next build

**OB — Market Map Real Surface Wiring / GP003**
