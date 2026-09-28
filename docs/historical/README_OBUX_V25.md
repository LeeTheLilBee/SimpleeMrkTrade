# Pre-replacement OBUX021–025 Owner Dashboard — frozen historical evidence

Exact snapshots copied unchanged from the parent Dashboard repair branch (`tower-ob-modern-dashboard-retirement-0928`, baseline `f61567764e96a07f036b651a5713f35273e3f7ee`) before the OBUX091–095 owner cockpit replaced them in stacked Tower all-room PR #177. Files prefixed `obux_v25_` in this folder are source archives only, **never served by an OB route**.

Historical OBUX021–025 design/unit tests and original approval handoff's historical Soulaana/contract assertions refer to this archive; they do not certify the active owner cockpit. Current active owner route is separately tested for owner-only identity, independent source guard, unknown capital fields, broker/order/capital restrictions, and Live Auto lock in `tests/test_tower_ob_all_room_visual_integration_0928.py`. The full Tower suite still blocks merges; these tests are neither deleted nor skipped.

Active integrations import only the specific modern room template/CSS/JS artifacts from #166. Tower auth, existing data adapter, deployment settings, permissions and protected launch remain unchanged. Actual owner visual acceptance after a successful deployment is a separate unresolved gate.
