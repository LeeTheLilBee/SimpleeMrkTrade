from tower.ecosystem_destination_registry import (
    RUNTIME_CONTRACT_READY,
    RUNTIME_OPEN,
    RUNTIME_SUMMARY_ONLY,
    build_launch_reference,
    build_line_matrix,
    get_destination_contract,
    validate_launch_intent,
)


def test_all_ecosystem_lines_have_explicit_contracts():
    rows = build_line_matrix()

    assert {
        row["app_id"]
        for row
        in rows
    } == {
        "tower",
        "clouds",
        "observatory",
        "archive_vault",
        "teller",
        "grounds",
        "atm_operations",
    }


def test_line_states_are_truthful():
    rows = {
        row["app_id"]: row
        for row
        in build_line_matrix()
    }

    assert (
        rows["tower"]["launch_state"]
        == RUNTIME_OPEN
    )

    assert (
        rows["clouds"]["launch_state"]
        == RUNTIME_OPEN
    )

    assert (
        rows["observatory"]["launch_state"]
        == RUNTIME_OPEN
    )

    assert (
        rows["archive_vault"]["launch_state"]
        == RUNTIME_SUMMARY_ONLY
    )

    for app_id in (
        "teller",
        "grounds",
        "atm_operations",
    ):
        assert (
            rows[app_id]["launch_state"]
            == RUNTIME_CONTRACT_READY
        )

        assert (
            rows[app_id]["deep_link_state"]
            == "not_operational"
        )


def test_atm_is_not_a_clouds_security_exception():
    row = {
        item["app_id"]: item
        for item
        in build_line_matrix()
    }["atm_operations"]

    assert row["requires_tower"] is True
    assert row["requires_step_up"] is True
    assert row["direct_clouds_bypass_allowed"] is False


def test_observatory_symbol_validation_is_narrow():
    good = validate_launch_intent(
        app_id="observatory",
        destination="symbol",
        item="AMD",
        return_context="clouds-observatory",
    )

    assert good["valid"] is True
    assert good["target_route"] == "/ob/symbol/AMD"

    bad = validate_launch_intent(
        app_id="observatory",
        destination="symbol",
        item="../../secrets",
    )

    assert bad["valid"] is False
    assert (
        bad["reason_code"]
        == "symbol_item_invalid"
    )


def test_unknown_destination_fails_closed():
    payload = validate_launch_intent(
        app_id="teller",
        destination="root_admin",
    )

    assert payload["valid"] is False

    assert (
        payload["reason_code"]
        == "ecosystem_destination_unknown"
    )


def test_launch_reference_points_to_tower_fabric():
    route = build_launch_reference(
        "grounds",
        destination="portfolio",
        return_context="clouds-grounds",
    )

    assert route.startswith(
        "/tower/ecosystem/launch/grounds?"
    )

    assert (
        "destination=portfolio"
        in route
    )

    assert (
        "return_context=clouds-grounds"
        in route
    )


def test_registry_preserves_authority_requirements():
    destination = get_destination_contract(
        "observatory",
        "review_center",
    )

    assert destination is not None
    assert destination["requires_owner_permission"] is True
    assert destination["requires_step_up"] is True
