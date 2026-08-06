# 👑 OB Owner Console Simplification Handoff

## Build name

**OB Owner Console Simplification — Owner Crown Room**

## Primary room

`owner_console`

## Primary owner question

**What controls need owner attention?**

## Why this exists

Hosted staging showed that owner-facing rooms must be understandable at
first glance. The other protected rooms should not be cluttered with
global owner settings, scattered approval controls, safety overrides,
mode gates, deployment controls, access controls, or raw evidence walls.

This build turns Owner Console into **Owner Crown Room**: the global
owner control room for approvals, mode gates, access, sessions, safety
locks, evidence, and Soulaana's guidance.

## New Owner Console identity

- Display title: **Owner Crown Room**
- Plain title: **Owner Controls**
- Main feeling: cute, calm, global-control-first, safety-aware
- Soulaana role: owner-control guide
- Global control rule: global controls live here
- Room rule: room-specific drawers stay inside each room
- Safety rule: broker submission and money movement remain locked
- Live Auto rule: Live Auto remains locked
- Dangerous actions: separately gated

## First-glance order

1. 👑 **Owner Crown Room**
   - The top-level global owner-control summary.

2. 🧭 **Soulaana Advises**
   - Soulaana explains approvals, gates, sessions, locks, and next owner step.

3. 🪄 **Approval Basket**
   - Short list of owner approvals waiting for review.

4. 🚦 **Mode Gates**
   - Survey, Paper, Manual Live, Hybrid, and Live Auto state.

5. 🗝️ **Access Watch**
   - Access, permissions, onboarding, and protected-room visibility notes.

6. 🕯️ **Session Lanterns**
   - Owner session continuity, login health, timeout, and step-up notes.

7. 🔒 **Safety Locks**
   - Production Manual Live, broker submission, money movement,
     Vault upload, and Live Auto locks.

8. 📎 **Proof Shelf**
   - Evidence and receipts without making the first screen a raw evidence wall.

9. 👣 **Owner Next Step**
   - One safe next owner step.
   - This does not deploy, submit broker orders, move money, or bypass gates.

10. 🗂️ **Control Detail Drawers**
    - Heavy owner-control detail goes here.

## Detail drawers

- `approval_context`
- `mode_gate_context`
- `access_context`
- `session_context`
- `deployment_context`
- `safety_lock_context`
- `evidence_context`
- `owner_notes`

## Global control policy

- `global_controls_live_here = True`
- `room_specific_drawers_live_in_rooms = True`
- `dashboard_global_controls_allowed = False`
- `market_map_global_controls_allowed = False`
- `symbol_page_global_controls_allowed = False`
- `trade_center_global_controls_allowed = False`
- `review_center_global_controls_allowed = False`
- `owner_console_is_control_center = True`

## Safety locks

- `production_manual_live_authorized = False`
- `broker_submission_enabled = False`
- `real_capital_movement_enabled = False`
- `direct_vault_upload_enabled = False`
- `live_auto_locked = True`

## Files created or updated

- `ob_owner_experience/owner_console.py`
- `ob_owner_experience/__init__.py`
- `tests/test_owner_console_simplification.py`
- `ob_evidence/owner_experience_simplification/owner_console_simplification.json`
- `ob_evidence/owner_experience_simplification/owner_console_simplification_handoff.md`

## Next builder notes

- Do not scatter global owner settings across protected rooms.
- Keep **Owner Crown Room** visually dominant.
- Keep Soulaana near the top.
- Show approvals, mode gates, access, sessions, and locks at first glance.
- Keep broker submission locked.
- Keep real capital movement locked.
- Keep Live Auto locked.
- Put approval, mode, access, session, deployment, safety, evidence, and
  owner notes inside drawers.
- Do not expose dangerous actions without step-up.
- Wire actual UI components to the data contract in `owner_console.py`.

## Next build

**Six-room owner experience consolidation and acceptance contract**
