# 🧩 OB Six-Room Real Surface Registry + UI Contract Adapter Handoff

## Build name

**OB — Six-Room Real Surface Registry + UI Contract Adapter / GP001**

## Primary package

`ob_six_room_real_surface_registry`

## Primary acceptance question

**Can the real OB app discover the six simplified owner rooms safely?**

## Decision

**READY_FOR_OB_UI_WIRING_WITH_SAFETY_LOCKS_HELD**

## What this builds

This build starts the real OB UI wiring lane without touching Tower,
Render, production, broker submission, money movement, or Live Auto.

It creates the adapter that lets the actual OB app discover:

1. 🌙 **Dashboard** → **Today’s Command Nest**
2. 🌦️ **Market Map** → **Market Weather**
3. 🔎 **Symbol Page** → **Asset Storybook**
4. 🌸 **Trade Center** → **Decision Garden**
5. 📚 **Review Center** → **Reflection Library**
6. 👑 **Owner Console** → **Owner Crown Room**

## Files created or updated

- `ob_owner_experience/ui_surface_registry.py`
- `ob_owner_experience/__init__.py`
- `tests/test_ui_surface_registry_adapter.py`
- `ob_evidence/owner_experience_simplification/ui_surface_registry_adapter.json`
- `ob_evidence/owner_experience_simplification/ui_surface_registry_adapter_handoff.md`

## Registry gives the next builder

- Six-room order
- Display titles
- Primary questions
- Route hints
- Component hints
- Data adapter hints
- Empty-state hints
- Owner walkthrough hooks
- Protected-route policy
- Safety-lock summary
- Must-not-claim list

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

## Next OB schedule

1. **GP002 Dashboard real surface wiring**
2. **GP003 Market Map real surface wiring**
3. **GP004 Symbol Page real surface wiring**
4. **GP005 Trade Center real surface wiring**
5. **GP006 Review Center real surface wiring**
6. **GP007 Owner Console real surface wiring**
7. **GP008 Visual polish pass**
8. **GP009 Tower handoff adapter**
9. **GP010 OB pre-integration closeout**

## Next builder notes

- Use the registry instead of hard-coding scattered room metadata.
- Keep Soulaana visible near the top of each room.
- Keep global controls in Owner Console.
- Keep protected routes owner-session-only.
- Do not claim `STAGING_READY`.
- Do not unlock broker submission.
- Do not enable real capital movement.
- Do not unlock Live Auto.

## Next build

**OB — Dashboard Real Surface Wiring / GP002**
