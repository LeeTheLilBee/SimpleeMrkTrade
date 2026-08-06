# 🌙 OB Dashboard Simplification Handoff

## Build name

**OB Dashboard Simplification — Today’s Command Nest**

## Primary room

`dashboard`

## Primary owner question

**What needs my attention today?**

## Why this exists

Hosted staging proved The Observatory could technically load, but the owner
experience was too cluttered. The Dashboard especially needs to become a
calm first-glance command surface instead of a wall of cards, metrics,
warnings, owner controls, and unexplained technical labels.

## New Dashboard identity

- Display title: **Today’s Command Nest**
- Plain title: **Today**
- Main feeling: cute, calm, useful, owner-first
- Soulaana role: page-level interpreter
- Owner controls: collapsed by default
- Global settings: moved out to Owner Console
- Dangerous actions: separately gated

## First-glance order

1. 🌙 **Today’s Command Nest**
   - The main hero summary.
   - This should be visually dominant.

2. 🧭 **Soulaana Says**
   - Soulaana explains what the owner is looking at.
   - She tells the owner what matters, what can wait, and what to do next.

3. 🔥 **Needs Your Eyes**
   - Highest-priority attention queue.
   - Limit default display to three items.

4. ✨ **Tiny Signals**
   - Critical indicators only.
   - Limit default display to four indicators.

5. 👑 **Owner Next Move**
   - One recommended next action.
   - Dangerous actions still require step-up and separate authorization.

6. 🗂️ **Details When Needed**
   - Secondary information goes into collapsed drawers.

7. 🔐 **Owner Drawer**
   - Room-specific owner controls only.
   - Global controls belong in Owner Console.

## Detail drawers

- `market_context`
- `account_context`
- `watchlist_context`
- `risk_context`
- `receipt_context`
- `owner_notes`

## Files created or updated

- `ob_owner_experience/dashboard.py`
- `ob_owner_experience/__init__.py`
- `tests/test_dashboard_simplification.py`
- `ob_evidence/owner_experience_simplification/dashboard_simplification.json`
- `ob_evidence/owner_experience_simplification/dashboard_simplification_handoff.md`

## Next builder notes

- Do not turn the Dashboard back into a metric wall.
- Keep the hero summary visually dominant.
- Keep Soulaana near the top.
- Keep attention items limited.
- Keep critical indicators limited.
- Keep details behind drawers.
- Keep owner controls collapsed.
- Do not scatter global owner settings on the Dashboard.
- Do not expose dangerous actions without step-up.
- Wire actual UI components to the data contract in `dashboard.py`.

## Next build

**Market Map simplification and deep-dive rooms**
