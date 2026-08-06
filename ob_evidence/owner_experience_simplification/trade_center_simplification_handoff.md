# 🌸 OB Trade Center Simplification Handoff

## Build name

**OB Trade Center Simplification — Decision Garden**

## Primary room

`trade_center`

## Primary owner question

**What decisions or actions are waiting?**

## Why this exists

Hosted staging showed that owner-facing rooms must be understandable at
first glance. Trade Center especially must not look like a broker terminal
or imply that OB can submit orders, move money, or unlock Live Auto.

This build turns Trade Center into **Decision Garden**: a calm review room
for pending decisions, risk, readiness checklists, receipt context, and
Soulaana's guidance.

## New Trade Center identity

- Display title: **Decision Garden**
- Plain title: **Decisions**
- Main feeling: cute, calm, review-first, safety-aware
- Soulaana role: decision guide
- Review rule: review before action
- Safety rule: broker submission and money movement remain locked
- Owner controls: collapsed by default
- Global settings: moved out to Owner Console
- Dangerous actions: separately gated

## First-glance order

1. 🌸 **Decision Garden**
   - The top-level waiting decision summary.
   - This must not look like a broker terminal.

2. 🧭 **Soulaana Guides**
   - Soulaana explains what decision is waiting and what is safe to do next.

3. 📬 **Waiting Decisions**
   - Short queue only.
   - Limit default display to three waiting decisions.

4. 🛡️ **Risk Gate**
   - Risk and lock state appear before action language.

5. ✅ **Readiness Checklist**
   - A short owner-visible checklist before a decision moves forward.

6. 👑 **Owner Next Move**
   - One safe next step.
   - This does not submit broker orders or move money.

7. 🗂️ **Decision Detail Drawers**
   - Heavy decision detail goes here.

8. 🔐 **Owner Drawer**
   - Room-specific owner controls only.
   - Global controls belong in Owner Console.

## Detail drawers

- `candidate_context`
- `thesis_context`
- `risk_context`
- `broker_checklist_context`
- `manual_live_context`
- `receipt_context`
- `owner_notes`

## Safety locks

- `production_manual_live_authorized = False`
- `broker_submission_enabled = False`
- `real_capital_movement_enabled = False`
- `direct_vault_upload_enabled = False`
- `live_auto_locked = True`

## Files created or updated

- `ob_owner_experience/trade_center.py`
- `ob_owner_experience/__init__.py`
- `tests/test_trade_center_simplification.py`
- `ob_evidence/owner_experience_simplification/trade_center_simplification.json`
- `ob_evidence/owner_experience_simplification/trade_center_simplification_handoff.md`

## Next builder notes

- Do not turn Trade Center into a broker terminal.
- Keep **Decision Garden** visually dominant.
- Keep Soulaana near the top.
- Show risk and lock state before action language.
- Keep waiting decisions limited.
- Put candidate, thesis, risk, checklist, manual-live, receipt, and owner
  notes inside drawers.
- Do not scatter global owner settings on Trade Center.
- Do not expose broker submission or money movement controls.
- Wire actual UI components to the data contract in `trade_center.py`.

## Next build

**Review Center simplification using the same doctrine**
