# 🔎 OB Symbol Page Simplification Handoff

## Build name

**OB Symbol Page Simplification — Asset Storybook**

## Primary room

`symbol_page`

## Primary owner question

**What do I need to understand about this asset?**

## Why this exists

Hosted staging showed that The Observatory can technically display asset
surfaces, but the owner should not have to decode a pile of quote data,
chart signals, risk notes, evidence, and controls all at once.

This build turns the Symbol Page into **Asset Storybook**: a first-glance
page that explains one asset clearly before exposing deeper details.

## New Symbol Page identity

- Display title: **Asset Storybook**
- Plain title: **Asset**
- Main feeling: cute, clear, asset-focused, risk-aware
- Soulaana role: asset interpreter
- Thesis rule: thesis before chart noise
- Risk rule: risk before action
- Owner controls: collapsed by default
- Global settings: moved out to Owner Console
- Dangerous actions: separately gated

## First-glance order

1. 🔎 **Asset Storybook**
   - The top-level asset summary.
   - Shows which symbol this is and why the owner is looking at it.

2. 🧭 **Soulaana Explains**
   - Soulaana explains the asset in plain language.
   - She tells the owner what matters and what can wait.

3. 📖 **The Asset Story**
   - The short asset thesis.
   - This should appear before charts and raw quote detail.

4. 🛡️ **Risk Before Shine**
   - Current risk level.
   - Risk must be visible before any action language.

5. 👑 **Decision Posture**
   - Observe, review, wait, avoid, or ready for owner review.
   - This is not broker submission.

6. ✨ **Tiny Asset Signals**
   - Short list only.
   - Limit default display to four indicators.

7. 🗂️ **Asset Detail Drawers**
   - Heavy asset detail goes here.

8. 🔐 **Owner Drawer**
   - Room-specific owner controls only.
   - Global controls belong in Owner Console.

## Detail drawers

- `quote_context`
- `thesis_detail`
- `risk_detail`
- `technical_context`
- `news_context`
- `evidence_context`
- `history_context`
- `owner_notes`

## Files created or updated

- `ob_owner_experience/symbol_page.py`
- `ob_owner_experience/__init__.py`
- `tests/test_symbol_page_simplification.py`
- `ob_evidence/owner_experience_simplification/symbol_page_simplification.json`
- `ob_evidence/owner_experience_simplification/symbol_page_simplification_handoff.md`

## Next builder notes

- Do not turn Symbol Page back into a quote wall.
- Keep **Asset Storybook** visually dominant.
- Keep Soulaana near the top.
- Put thesis before chart noise.
- Show risk before any action language.
- Keep indicators limited.
- Put quote, technical, news, evidence, history, and owner notes inside drawers.
- Do not scatter global owner settings on Symbol Page.
- Do not expose broker submission or money movement controls.
- Wire actual UI components to the data contract in `symbol_page.py`.

## Next build

**Trade Center simplification using the same doctrine**
