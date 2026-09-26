# OBSIM006–010 — Deterministic three-lane replay

This is a **new bounded implementation** on the September 24 main checkpoint, not a claim that all OB is finished.

Inputs: a fresh OBSIM harness and explicitly authored historical steps. Each frame carries a verified, matching OBTIME receipt; the frame timestamps strictly increase; each step gives one decision for CONTROL, INTEGRATED, and EXPERIMENTAL. Existing OBSIM owns fills, cash, positions, P&L and receipt chains. The orchestrator does not select trades or strategies.

Experimental OPEN must use the CAPSIM006–010 admission wrapper with the canonical policy/time/session-loss path; REJECTED admission does not open a position and is visible in the replay events. The two other lanes retain their independent state and fixed build references. Reports carry a deterministic hash and do not rank a winner.

The caller's harness stays unchanged on failure because each OBSIM operation returns immutable replacement state. This is a historical replay interface; it does not implement live data ingestion, unattended scheduling, persistence or trading authority. Run the focused test and the full `python -m pytest -q tests` in the OB checkout before merging. No Tower files touched.
