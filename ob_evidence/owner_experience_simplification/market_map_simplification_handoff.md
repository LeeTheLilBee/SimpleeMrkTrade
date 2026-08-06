# 🌦️ OB Market Map Simplification Handoff

## Build name

**OB Market Map Simplification — Market Weather + Deep-Dive Rooms**

## Primary room

`market_map`

## Primary owner question

**What is happening in the market?**

## Why this exists

Hosted staging proved The Observatory could technically load, but the
Market Map was too confusing at first glance. It had too many panels,
signals, warnings, metrics, headings, and details competing at once.

This build turns Market Map into a calm first-glance market read called
**Market Weather**. The heavy details still exist, but they move into
named deep-dive rooms.

## New Market Map identity

- Display title: **Market Weather**
- Plain title: **Market**
- Main feeling: cute, calm, readable, risk-aware
- Soulaana role: market interpreter
- Risk rule: risk appears before opportunity
- Owner controls: collapsed by default
- Global settings: moved out to Owner Console
- Dangerous actions: separately gated

## First-glance order

1. 🌦️ **Market Weather**
   - The top-level market read.
   - Shows whether the market is calm, mixed, risky, or constructive.

2. 🧭 **Soulaana Reads the Room**
   - Soulaana explains the market read in plain language.
   - She tells the owner what matters most and what can wait.

3. 🛡️ **Risk First**
   - Current risk level.
   - Risk must be understood before opportunity.

4. 🌊 **Biggest Movement**
   - The single most important market movement.

5. 🌱 **Strongest Opportunities**
   - Short list only.
   - Limit default display to three opportunities.

6. ⚠️ **Watch Your Step**
   - Short list of warnings.
   - Limit default display to three warnings.

7. 🗺️ **Deep-Dive Rooms**
   - Heavy details go here.

8. 🔐 **Owner Drawer**
   - Room-specific owner controls only.
   - Global controls belong in Owner Console.

## Deep-dive rooms

- 🌿 `sector_details` — **Sector Garden**
- 🫧 `market_breadth` — **Breadth Check**
- 🧲 `correlations` — **Together Map**
- ⛈️ `volatility` — **Storm Meter**
- 💧 `flows` — **Money River**
- 🏮 `technical_signals` — **Signal Lanterns**
- 🪺 `symbol_level_data` — **Symbol Nest**
- 📎 `evidence` — **Receipts Table**
- 📚 `research_detail` — **Research Library**
- 🪞 `historical_comparisons` — **Time Mirror**

## Files created or updated

- `ob_owner_experience/market_map.py`
- `ob_owner_experience/__init__.py`
- `tests/test_market_map_simplification.py`
- `ob_evidence/owner_experience_simplification/market_map_simplification_and_deep_dives.json`
- `ob_evidence/owner_experience_simplification/market_map_simplification_handoff.md`

## Next builder notes

- Do not turn Market Map back into a metric wall.
- Keep **Market Weather** visually dominant.
- Keep Soulaana near the top.
- Show risk before opportunity.
- Keep opportunities limited.
- Keep warnings limited.
- Put sectors, breadth, volatility, flows, technicals, symbols, evidence,
  research, and history inside deep-dive rooms.
- Do not scatter global owner settings on Market Map.
- Do not expose dangerous actions without step-up.
- Wire actual UI components to the data contract in `market_map.py`.

## Next build

**Symbol Page simplification using the same doctrine**
