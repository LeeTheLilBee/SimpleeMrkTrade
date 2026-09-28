# TWR-TEST006–010 — Python 3.11 source syntax seal

Scope: dormant historical Tower OB mode-clearance quote repair and CI syntax/behavior check. No trading-mode policy, entitlement, broker, execution, capital, owner-session, hosted feature toggle, payment or new service change.

Current Tower source full-suite gate passed 1,183 tests, but it did not import every historical module. Three Soulaana f-string expressions nested single quotes in Python 3.12 style; they are invalid under Python 3.11. This pack changes only the f-string delimiter to double quotes, retaining text, conditions and source policy exactly.

New Python 3.11 workflow compiles the entire tower/ and web/ source tree and exercises Survey text/default-deny behavior alongside existing Tower app-registry and OBML preflight tests. If additional dormant syntax failures surface, repair in minimal separately reviewed source changes.

Release unchanged: existing Tower simplee-tower-ob only, no paid infrastructure. Manual Live remains NO_GO_HOLD_OWNER_MANUAL_LIVE_L1 pending issue #115's independent owner, durable replay, exact account, broker/funds, market/safety and owner acceptance evidence. This is source quality, not a live grant.

Python 3.11 compileall at initial candidate caught two additional dormant modules, tower/ob_clearance_bridge.py (two quote repairs) and tower/ob_object_clearance.py (two quote repairs). They now use the same exact delimiter-only correction. The first rerun compiled the full tower/ and web/ tree successfully; the remaining focused test failure was an omitted exact pinned OBML PR68 fixture checkout in this new workflow, not a product failure. The checkout was added, and exact-head CI must pass before merge.
