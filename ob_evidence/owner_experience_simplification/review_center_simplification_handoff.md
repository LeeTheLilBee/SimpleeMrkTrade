# 📚 OB Review Center Simplification Handoff

## Build name

**OB Review Center Simplification — Reflection Library**

## Primary room

`review_center`

## Primary owner question

**What did we learn and what needs review?**

## Why this exists

Hosted staging showed that owner-facing rooms must be understandable at
first glance. Review Center especially must not become a wall of raw
receipts, trade history, performance tables, screenshots, and audit text.

This build turns Review Center into **Reflection Library**: a calm review
room for outcomes, lessons, receipt status, repeated patterns, mistakes,
improvements, and Soulaana's reflection.

## New Review Center identity

- Display title: **Reflection Library**
- Plain title: **Review**
- Main feeling: cute, calm, reflective, learning-first
- Soulaana role: outcome and lesson interpreter
- Receipt rule: receipt state appears early
- Lesson rule: lessons appear before raw evidence
- Owner controls: collapsed by default
- Global settings: moved out to Owner Console
- Dangerous actions: separately gated

## First-glance order

1. 📚 **Reflection Library**
   - The top-level review summary.
   - This must not look like a receipt wall.

2. 🧭 **Soulaana Reflects**
   - Soulaana explains what happened, what was learned, and what to review next.

3. 🪴 **What Happened**
   - Short outcome summary.
   - Not a full trade history table.

4. 🧾 **Receipt Check**
   - Shows verified, pending, missing, failed, or not-required receipt state.

5. 🧠 **Lesson Shelf**
   - Lessons learned and process improvements.

6. 🪞 **Pattern Mirror**
   - Repeated behaviors, mistakes, strengths, weaknesses, and risks.

7. 👑 **Owner Next Review**
   - One safe next review step.
   - This does not submit broker orders or move money.

8. 🗂️ **Review Detail Drawers**
   - Heavy review detail goes here.

9. 🔐 **Owner Drawer**
   - Room-specific owner controls only.
   - Global controls belong in Owner Console.

## Detail drawers

- `outcome_context`
- `receipt_context`
- `performance_context`
- `mistake_context`
- `pattern_context`
- `improvement_context`
- `owner_notes`

## Safety locks

- `production_manual_live_authorized = False`
- `broker_submission_enabled = False`
- `real_capital_movement_enabled = False`
- `direct_vault_upload_enabled = False`
- `live_auto_locked = True`

## Files created or updated

- `ob_owner_experience/review_center.py`
- `ob_owner_experience/__init__.py`
- `tests/test_review_center_simplification.py`
- `ob_evidence/owner_experience_simplification/review_center_simplification.json`
- `ob_evidence/owner_experience_simplification/review_center_simplification_handoff.md`

## Next builder notes

- Do not turn Review Center into a receipt wall.
- Keep **Reflection Library** visually dominant.
- Keep Soulaana near the top.
- Show receipt state early.
- Show lessons before raw evidence.
- Keep review items limited.
- Put outcome, receipt, performance, mistake, pattern, improvement, and
  owner notes inside drawers.
- Do not scatter global owner settings on Review Center.
- Do not expose broker submission or money movement controls.
- Wire actual UI components to the data contract in `review_center.py`.

## Next build

**Owner Console simplification using the same doctrine**
