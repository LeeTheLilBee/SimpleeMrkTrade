from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)
from tower.tower_ir_cert_p2391 import (
    build_active_launch_ledger,
)


def test_pack_2391_active_ledger():
    handoff = create_ob_launch_handoff(
        owner_id="owner_1",
        session_id="session_1",
        approved_room={
            "room_id": "ob_room_dashboard",
            "display_name": "Dashboard",
        },
        canonical_path="/dashboard",
        mode="paper",
        step_up_reference=None,
        clearance_decision_reference="obclr_1",
        issued_at="2026-07-14T12:00:00+00:00",
    )

    ledger = build_active_launch_ledger(
        issued_handoffs=[handoff],
        consumed_handoff_ids=[],
        revoked_handoff_ids=[],
        closed_handoff_ids=[],
    )

    assert ledger["active_count"] == 1
    assert ledger["entries"][0][
        "authorization_state"
    ] == "active_preview"
