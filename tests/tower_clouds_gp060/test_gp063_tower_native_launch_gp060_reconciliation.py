from tower.tower_clouds_gp060_launch_reconciliation_service import (
    get_clouds_gp063_status_payload,
)


def test_gp063():

    p = (
        get_clouds_gp063_status_payload()
    )

    assert p["status"] == "ready"

    assert (
        p[
            "owner_route_compatible"
        ]
        is True
    )

    assert (
        p[
            "owner_surface_compatible"
        ]
        is True
    )

    assert (
        p[
            "owner_session_gate_present"
        ]
        is True
    )

    assert (
        p[
            "step_up_gate_present"
        ]
        is True
    )

    assert (
        p[
            "handoff_gate_present"
        ]
        is True
    )

    assert (
        p[
            "default_deny_preserved"
        ]
        is True
    )

    assert (
        p[
            "existing_native_launch_modified"
        ]
        is False
    )
