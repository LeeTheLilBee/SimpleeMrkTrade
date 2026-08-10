from ob_owner_experience.six_room_real_surface_acceptance import (
    SIX_ROOM_DANGEROUS_FALSE_KEYS,
    SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY,
    SIX_ROOM_REAL_SURFACE_ORDER,
    SIX_ROOM_REQUIRED_LOCKED_TRUE_KEYS,
    build_six_room_real_surface_acceptance_bundle,
    build_six_room_real_surface_acceptance_handoff,
    build_six_room_real_surface_acceptance_matrix,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp008_identity_and_room_order():
    assert SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY["package"] == "ob_six_room_real_surface_acceptance_gp008"
    assert SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY["decision"] == (
        "READY_FOR_SIX_ROOM_REAL_SURFACE_ACCEPTANCE_WITH_SAFETY_LOCKS_HELD"
    )
    assert SIX_ROOM_REAL_SURFACE_ORDER == [
        "dashboard",
        "market_map",
        "symbol_page",
        "trade_center",
        "review_center",
        "owner_console",
    ]


def test_gp008_acceptance_matrix_accepts_all_six_rooms():
    matrix = build_six_room_real_surface_acceptance_matrix()

    assert len(matrix) == 6
    assert [record["room"] for record in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for record in matrix:
        assert record["accepted"] is True
        assert record["missing_required_keys"] == []
        assert "action_locks" not in record["missing_required_keys"]
        assert record["route_matches_registry"] is True
        assert record["component_matches_registry"] is True
        assert record["data_adapter_matches_registry"] is True
        assert record["protected_route_policy_matches"] is True
        assert record["anonymous_access_denied"] is True
        assert record["owner_session_required"] is True
        assert record["has_any_components"] is True
        assert record["loading_empty_error_states_ready"] is True
        assert record["unsafe_false_flags"] == {}
        assert record["unsafe_true_flags"] == {}
        assert "STAGING_READY" in record["must_not_claim"]


def test_gp008_bundle_closes_acceptance_without_staging_ready():
    bundle = build_six_room_real_surface_acceptance_bundle()

    assert bundle["package"] == "ob_six_room_real_surface_acceptance_gp008"
    assert bundle["accepted"] is True
    assert bundle["accepted_rooms"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert bundle["blocked_rooms"] == []
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert bundle["surface_status"]["six_room_real_surface_acceptance_ready"] is True
    assert bundle["surface_status"]["all_six_rooms_present"] is True
    assert bundle["surface_status"]["all_registry_routes_match"] is True
    assert bundle["surface_status"]["all_registry_components_match"] is True
    assert bundle["surface_status"]["all_data_adapters_match"] is True
    assert bundle["surface_status"]["all_routes_protected"] is True
    assert bundle["surface_status"]["anonymous_access_allowed"] is False
    assert bundle["surface_status"]["owner_session_required"] is True
    assert bundle["surface_status"]["staging_ready"] is False
    assert bundle["surface_status"]["production_deploy_enabled"] is False
    assert bundle["surface_status"]["broker_submission_enabled"] is False
    assert bundle["surface_status"]["real_capital_movement_enabled"] is False
    assert bundle["surface_status"]["direct_execution_enabled"] is False
    assert bundle["surface_status"]["automated_execution_enabled"] is False
    assert bundle["surface_status"]["permission_mutation_enabled"] is False
    assert bundle["surface_status"]["secret_reveal_enabled"] is False
    assert bundle["surface_status"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]


def test_gp008_dangerous_keys_are_declared():
    assert "broker_submission_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "real_capital_movement_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "direct_execution_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "automated_execution_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "permission_mutation_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "secret_reveal_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "production_deploy_enabled" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "staging_ready" in SIX_ROOM_DANGEROUS_FALSE_KEYS
    assert "live_auto_locked" in SIX_ROOM_REQUIRED_LOCKED_TRUE_KEYS


def test_gp008_handoff_contains_registry_and_safety_notes():
    handoff = build_six_room_real_surface_acceptance_handoff()

    assert handoff["package"] == "ob_six_room_real_surface_acceptance_gp008"
    assert handoff["accepted"] is True
    assert handoff["accepted_rooms"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert handoff["blocked_rooms"] == []
    assert len(handoff["registry_summary"]) == 6

    for item in handoff["registry_summary"]:
        assert item["accepted"] is True
        assert item["route_hint"]
        assert item["component_hint"]
        assert item["data_adapter_hint"]

    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
    assert "Do not redeploy Render from this package." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
