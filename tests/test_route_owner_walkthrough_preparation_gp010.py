from ob_owner_experience.route_owner_walkthrough_preparation import (
    ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED,
    ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY,
    ROUTE_OWNER_WALKTHROUGH_REQUIRED_CHECKS,
    ROUTE_OWNER_WALKTHROUGH_REQUIRED_FALSE_FLAGS,
    ROUTE_OWNER_WALKTHROUGH_REQUIRED_TRUE_FLAGS,
    build_route_owner_walkthrough_preparation_bundle,
    build_route_owner_walkthrough_preparation_handoff,
    build_route_owner_walkthrough_preparation_status,
    build_route_owner_walkthrough_route_matrix,
    build_route_owner_walkthrough_script,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp010_identity():
    assert ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY["package"] == (
        "ob_route_owner_walkthrough_preparation_gp010"
    )
    assert ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY["decision"] == (
        "READY_FOR_ROUTE_AND_OWNER_WALKTHROUGH_PREPARATION_WITH_SAFETY_LOCKS_HELD"
    )


def test_gp010_route_matrix_prepares_all_six_rooms():
    matrix = build_route_owner_walkthrough_route_matrix()

    assert len(matrix) == 6
    assert [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    expected_routes = {
        "dashboard": "/ob/dashboard",
        "market_map": "/ob/market-map",
        "symbol_page": "/ob/symbol/<symbol>",
        "trade_center": "/ob/trade-center",
        "review_center": "/ob/review-center",
        "owner_console": "/ob/owner-console",
    }

    for item in matrix:
        assert item["accepted_by_gp008"] is True
        assert item["ready_for_walkthrough_preparation"] is True
        assert item["route_hint"] == expected_routes[item["room"]]
        assert item["component_hint"]
        assert item["data_adapter_hint"]
        assert item["owner_goal"]

        for key in ROUTE_OWNER_WALKTHROUGH_REQUIRED_CHECKS:
            assert item["checks"][key] is True


def test_gp010_walkthrough_script_is_prepared_but_not_executed():
    script = build_route_owner_walkthrough_script()

    assert len(script) == 6
    assert [item["room"] for item in script] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in script:
        assert item["prepared"] is True
        assert item["route_hint"]
        assert item["owner_prompt"]
        assert "Owner session is required." in item["must_confirm"]
        assert "Anonymous access is denied." in item["must_confirm"]
        assert "Dangerous actions are not available." in item["must_confirm"]
        assert "No staging readiness is claimed." in item["must_confirm"]
        assert "Do not accept the owner walkthrough in this package." in item["must_not_do"]
        assert "Do not redeploy Render." in item["must_not_do"]


def test_gp010_status_is_prepared_and_safety_locked():
    status = build_route_owner_walkthrough_preparation_status()

    assert status["gp009_closeout_closed"] is True
    assert status["gp008_six_room_acceptance_ready"] is True
    assert status["all_six_rooms_present"] is True
    assert status["all_routes_ready_for_walkthrough_preparation"] is True
    assert status["walkthrough_script_prepared"] is True
    assert status["route_owner_walkthrough_preparation_ready"] is True

    for key in ROUTE_OWNER_WALKTHROUGH_REQUIRED_FALSE_FLAGS:
        assert status[key] is False

    for key in ROUTE_OWNER_WALKTHROUGH_REQUIRED_TRUE_FLAGS:
        assert status[key] is True


def test_gp010_bundle_prepared_without_release_or_walkthrough_acceptance():
    bundle = build_route_owner_walkthrough_preparation_bundle()

    assert bundle["package"] == "ob_route_owner_walkthrough_preparation_gp010"
    assert bundle["prepared"] is True
    assert bundle["closed_dependency"] == "GP009"
    assert len(bundle["route_matrix"]) == 6
    assert len(bundle["walkthrough_script"]) == 6
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert "owner walkthrough accepted" in bundle["not_authorized"]
    assert "Tower return/session continuity repaired" in bundle["not_authorized"]
    assert "Render redeploy" in bundle["not_authorized"]
    assert "Live Auto unlock" in bundle["not_authorized"]

    boundary = bundle["release_boundary"]

    assert boundary["staging_ready"] is False
    assert boundary["owner_walkthrough_started"] is False
    assert boundary["owner_walkthrough_accepted"] is False
    assert boundary["tower_return_repaired"] is False
    assert boundary["render_redeployed"] is False
    assert boundary["production_deploy_enabled"] is False
    assert boundary["broker_submission_enabled"] is False
    assert boundary["real_capital_movement_enabled"] is False
    assert boundary["direct_execution_enabled"] is False
    assert boundary["automated_execution_enabled"] is False
    assert boundary["permission_mutation_enabled"] is False
    assert boundary["secret_reveal_enabled"] is False
    assert boundary["live_auto_locked"] is True


def test_gp010_not_authorized_terms_are_declared():
    assert "STAGING_READY" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "owner walkthrough started" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "owner walkthrough accepted" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "Tower return/session continuity repaired" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "Render redeploy" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "production deployment" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "broker submission" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "real capital movement" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED
    assert "Live Auto unlock" in ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED


def test_gp010_handoff_has_next_builder_notes():
    handoff = build_route_owner_walkthrough_preparation_handoff()

    assert handoff["package"] == "ob_route_owner_walkthrough_preparation_gp010"
    assert handoff["prepared"] is True
    assert handoff["closed_dependency"] == "GP009"
    assert len(handoff["route_matrix"]) == 6
    assert len(handoff["walkthrough_script"]) == 6
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
    assert "Do not start the owner walkthrough from this package." in handoff["next_builder_notes"]
    assert "Do not mark owner walkthrough accepted from this package." in handoff["next_builder_notes"]
    assert "Do not claim Tower return/session continuity repaired from this package." in handoff["next_builder_notes"]
    assert "Do not redeploy Render from this package." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
