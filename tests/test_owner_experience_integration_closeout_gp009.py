from ob_owner_experience.owner_experience_integration_closeout import (
    OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_FALSE_FLAGS,
    OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_TRUE_FLAGS,
    OWNER_EXPERIENCE_CLOSED_PACKAGES,
    OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY,
    build_owner_experience_integration_closeout_bundle,
    build_owner_experience_integration_closeout_handoff,
    build_owner_experience_integration_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp009_identity_and_closed_packages():
    assert OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY["package"] == (
        "ob_owner_experience_integration_closeout_gp009"
    )
    assert OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_IDENTITY["decision"] == (
        "READY_FOR_OWNER_EXPERIENCE_INTEGRATION_CLOSEOUT_WITH_SAFETY_LOCKS_HELD"
    )

    gp_codes = [item["gp"] for item in OWNER_EXPERIENCE_CLOSED_PACKAGES]

    assert gp_codes == [
        "GP001",
        "GP002",
        "GP003",
        "GP004",
        "GP005",
        "GP006",
        "GP007",
        "GP008",
    ]

    for item in OWNER_EXPERIENCE_CLOSED_PACKAGES:
        assert item["status"] == "closed"


def test_gp009_integration_status_accepts_all_six_rooms_without_staging():
    status = build_owner_experience_integration_status()

    assert status["registry_adapter_closed"] is True
    assert status["dashboard_real_surface_closed"] is True
    assert status["market_map_real_surface_closed"] is True
    assert status["symbol_page_real_surface_closed"] is True
    assert status["trade_center_real_surface_closed"] is True
    assert status["review_center_real_surface_closed"] is True
    assert status["owner_console_real_surface_closed"] is True
    assert status["six_room_acceptance_closed"] is True
    assert status["owner_experience_integration_closeout_ready"] is True
    assert status["all_six_rooms_present"] is True
    assert status["all_registry_routes_match"] is True
    assert status["all_registry_components_match"] is True
    assert status["all_data_adapters_match"] is True
    assert status["all_routes_protected"] is True
    assert status["anonymous_access_allowed"] is False
    assert status["owner_session_required"] is True
    assert status["live_auto_locked"] is True

    for key in OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_FALSE_FLAGS:
        assert status[key] is False

    for key in OWNER_EXPERIENCE_CLOSEOUT_REQUIRED_TRUE_FLAGS:
        assert status[key] is True


def test_gp009_closeout_bundle_is_closed_and_safety_locked():
    bundle = build_owner_experience_integration_closeout_bundle()

    assert bundle["package"] == "ob_owner_experience_integration_closeout_gp009"
    assert bundle["closed"] is True
    assert bundle["closed_gp_codes"] == [
        "GP001",
        "GP002",
        "GP003",
        "GP004",
        "GP005",
        "GP006",
        "GP007",
        "GP008",
    ]
    assert bundle["room_order"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert bundle["accepted_rooms"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert bundle["blocked_rooms"] == []
    assert len(bundle["registry_summary"]) == 6
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert "production deployment" in bundle["not_authorized"]
    assert "broker submission" in bundle["not_authorized"]
    assert "real capital movement" in bundle["not_authorized"]
    assert "Live Auto unlock" in bundle["not_authorized"]

    boundary = bundle["release_boundary"]

    assert boundary["staging_ready"] is False
    assert boundary["production_deploy_enabled"] is False
    assert boundary["render_redeployed"] is False
    assert boundary["owner_walkthrough_accepted"] is False
    assert boundary["tower_return_repaired"] is False
    assert boundary["broker_submission_enabled"] is False
    assert boundary["real_capital_movement_enabled"] is False
    assert boundary["direct_execution_enabled"] is False
    assert boundary["automated_execution_enabled"] is False
    assert boundary["permission_mutation_enabled"] is False
    assert boundary["secret_reveal_enabled"] is False
    assert boundary["live_auto_locked"] is True


def test_gp009_registry_summary_has_all_six_routes():
    bundle = build_owner_experience_integration_closeout_bundle()
    summary = bundle["registry_summary"]

    assert [item["room"] for item in summary] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in summary:
        assert item["accepted"] is True
        assert item["route_hint"]
        assert item["component_hint"]
        assert item["data_adapter_hint"]


def test_gp009_handoff_has_closeout_notes_and_next_build():
    handoff = build_owner_experience_integration_closeout_handoff()

    assert handoff["package"] == "ob_owner_experience_integration_closeout_gp009"
    assert handoff["closed"] is True
    assert handoff["accepted_rooms"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert handoff["blocked_rooms"] == []
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
    assert "Do not redeploy Render from this package." in handoff["next_builder_notes"]
    assert "Keep production deploy disabled." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
    assert "Next build is GP010 route and owner walkthrough preparation." in handoff["next_builder_notes"]
