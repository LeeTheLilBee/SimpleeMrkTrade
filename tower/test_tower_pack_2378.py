from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)
from tower.tower_ir_cert_p2378 import (
    create_room_access_receipt,
)


def test_pack_2378_access_receipt():
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
        issued_at="2026-07-13T12:00:00+00:00",
    )

    receipt = create_room_access_receipt(
        handoff=handoff,
        bridge_decision="ob_room_contract_allow",
        clearance_value="ob_owner_command",
        clearance_rank=900,
        step_up_state="not_required",
        launch_time="2026-07-13T12:00:01+00:00",
    )

    assert receipt["receipt_id"].startswith("obaccess_")
    assert receipt["handoff_id"] == handoff["handoff_id"]
    assert receipt["clearance_value"] == (
        "ob_owner_command"
    )
    assert receipt["completion_state"] == (
        "room_accessed_preview"
    )
