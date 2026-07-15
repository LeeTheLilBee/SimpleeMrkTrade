from tower.tower_ob_gp046_native_contract import (
    GP046_CONTRACT_VERSION,
    run_owner_rehearsal,
)


def test_native_gp046_rehearsal_handoff():
    result = run_owner_rehearsal(
        owner_id="owner_solice",
        session_id="tower_test_session_native_gp046",
        requested_path="/trade-center",
        mode="paper",
        step_up_reference="tower_test_step_up_native_gp046",
        mission_account_id="proof_demo",
        symbol="AMD",
    )

    assert result["status"] == "passed"
    assert result["gp046_native_contract"] is True

    assert (
        result[
            "runtime_contract_adapter_required"
        ]
        is False
    )

    packet = result["launch_handoff"]

    required_fields = {
        "contract_version",
        "issuer",
        "app_id",
        "handoff_id",
        "owner_id",
        "subject_role",
        "session_id",
        "room_id",
        "canonical_route",
        "room_parameters",
        "mode",
        "clearance_decision_ref",
        "step_up_ref",
        "step_up_verified",
        "issued_at",
        "expires_at",
        "nonce",
        "single_use",
        "safety",
        "integrity_hash",
    }

    assert required_fields.issubset(
        packet
    )

    assert (
        packet["contract_version"]
        == GP046_CONTRACT_VERSION
    )

    assert packet["issuer"] == "tower"
    assert packet["app_id"] == "observatory"
    assert packet["subject_role"] == "owner"
    assert packet["room_id"] == "trade_center"
    assert packet["canonical_route"] == "/trade-center"
    assert packet["mode"] == "paper"
    assert packet["step_up_verified"] is True
    assert packet["single_use"] is True

    assert (
        packet[
            "room_parameters"
        ][
            "mission_account_id"
        ]
        == "proof_demo"
    )

    assert (
        packet[
            "room_parameters"
        ][
            "symbol"
        ]
        == "AMD"
    )

    assert len(
        packet[
            "integrity_hash"
        ]
    ) == 64

    assert (
        packet[
            "safety"
        ][
            "dry_run_only"
        ]
        is True
    )

    assert (
        packet[
            "safety"
        ][
            "production_manual_live_authorized"
        ]
        is False
    )

    assert (
        packet[
            "safety"
        ][
            "broker_submission_enabled"
        ]
        is False
    )

    assert (
        packet[
            "safety"
        ][
            "real_capital_movement_enabled"
        ]
        is False
    )

    assert (
        packet[
            "safety"
        ][
            "direct_vault_upload_enabled"
        ]
        is False
    )

    assert (
        packet[
            "safety"
        ][
            "live_auto_locked"
        ]
        is True
    )


if __name__ == "__main__":
    test_native_gp046_rehearsal_handoff()
    print(
        "✅ Tower native GP046 regression test passed."
    )
