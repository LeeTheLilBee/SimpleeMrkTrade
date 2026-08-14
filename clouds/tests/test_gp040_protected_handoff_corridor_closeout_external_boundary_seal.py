from clouds.protected_handoff_corridor_closeout_service import (
    get_clouds_gp040_status_payload,
    get_protected_handoff_corridor_closeout,
    get_protected_handoff_corridor_closeout_payload,
)


def test_gp040_clouds_side_complete():
    closeout = (
        get_protected_handoff_corridor_closeout()
    )

    assert (
        closeout.clouds_side_corridor_complete
        is True
    )

    assert (
        closeout
        .ready_for_external_tower_integration
        is True
    )


def test_gp040_does_not_claim_external_delivery():
    closeout = (
        get_protected_handoff_corridor_closeout()
    )

    assert (
        closeout.external_transport_invoked
        is False
    )

    assert (
        closeout.tower_contacted
        is False
    )

    assert (
        closeout.external_delivery_attempted
        is False
    )

    assert (
        closeout.external_receipt_verified
        is False
    )

    assert (
        closeout.handoff_delivered
        is False
    )


def test_gp040_requires_real_external_adapter_later():
    closeout = (
        get_protected_handoff_corridor_closeout()
    )

    assert (
        closeout
        .external_delivery_adapter_required
        is True
    )


def test_gp040_conclusion():
    closeout = (
        get_protected_handoff_corridor_closeout()
    )

    assert closeout.conclusion == (
        "CLOUDS_PHASE_II_HANDOFF_CORRIDOR_READY_FOR_"
        "EXTERNAL_TOWER_INTEGRATION"
    )


def test_gp040_payload_serializes():
    payload = (
        get_protected_handoff_corridor_closeout_payload()
    )

    assert (
        payload["clouds_side_corridor_complete"]
        is True
    )


def test_gp040_status_ready():
    status = (
        get_clouds_gp040_status_payload()
    )

    assert status["pack"] == "GP040"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert (
        status["clouds_side_corridor_complete"]
        is True
    )

    assert (
        status[
            "ready_for_external_tower_integration"
        ]
        is True
    )

    assert (
        status["external_receipt_verified"]
        is False
    )

    assert (
        status["tower_receipt_verified"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )

    assert status["next_pack"] == (
        "GP041 — TOWER + OBSERVATORY REAL "
        "SUMMARY FEED ADAPTER CONTRACTS"
    )
