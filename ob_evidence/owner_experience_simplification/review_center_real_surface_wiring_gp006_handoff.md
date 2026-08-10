# 🧾 OB Review Center Real Surface Wiring Handoff / GP006

## Build name

**OB — Review Center Real Surface Wiring / GP006**

## Decision

**READY_FOR_REVIEW_CENTER_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD**

## What this builds

This build turns the simplified Review Center contract into a route-ready real
surface adapter for the OB app.

## Route and component

- Room: `review_center`
- Display title: **Review Center**
- Route hint: `/ob/review-center`
- Component hint: `ReviewCenterSurface`

## First-glance components

- `ReviewCenterHeroCard`
- `ReviewCenterSoulaanaCard`
- `ReviewCenterRecentReviewsList`
- `ReviewCenterDecisionReplayCard`
- `ReviewCenterLessonPatternCard`
- `ReviewCenterCorrectionQueueCard`

## Collapsed components

- `ReviewCenterDetailDrawerGroup`
- `ReviewCenterOwnerDrawer`

## Allowed review actions

- Review read
- Lesson capture
- Correction note

## Locked actions

- Broker submission remains locked.
- Real capital movement remains locked.
- Direct execution remains disabled.
- Automated execution remains disabled.
- Live Auto remains locked.

## Not staging ready

This package does not authorize production deployment, Render redeploy, owner
walkthrough acceptance, Tower return repair, or `STAGING_READY`.

## Next build

**OB — Owner Console Real Surface Wiring / GP007**
