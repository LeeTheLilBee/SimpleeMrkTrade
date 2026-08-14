from pathlib import Path
import ast

from clouds.contracts import (
    AppConnectionState,
    AttentionPriority,
    HealthState,
)
from clouds.owner_command_service import (
    get_clouds_gp001_status_payload,
    get_owner_command_dashboard,
    get_owner_command_payload,
)
from clouds.registry import (
    get_app,
    get_mission_lane,
    list_apps,
    list_mission_lanes,
)


def test_gp001_app_registry_contains_core_ecosystem():
    apps = list_apps()

    assert [
        app.app_id
        for app in apps
    ] == [
        "tower",
        "observatory",
        "archive_vault",
        "teller",
        "grounds",
        "clouds",
    ]

    assert get_app("tower") is not None
    assert get_app("clouds") is not None
    assert get_app("missing") is None


def test_gp001_clouds_is_connected_and_other_apps_are_safe():
    clouds = get_app("clouds")
    teller = get_app("teller")
    grounds = get_app("grounds")

    assert clouds is not None
    assert teller is not None
    assert grounds is not None

    assert (
        clouds.connection_state
        == AppConnectionState.CONNECTED.value
    )

    assert (
        teller.connection_state
        == AppConnectionState.RESERVED.value
    )

    assert (
        grounds.connection_state
        == AppConnectionState.RESERVED.value
    )


def test_gp001_mission_lane_registry_is_canonical():
    lanes = list_mission_lanes()

    assert [
        lane.lane_id
        for lane in lanes
    ] == [
        "owner_command",
        "investment_engine",
        "trust_stewardship",
        "atm_operations",
        "real_estate",
        "people_and_payments",
    ]

    assert (
        get_mission_lane("investment_engine")
        .owning_app_id
        == "observatory"
    )

    assert get_mission_lane("missing") is None


def test_gp001_dashboard_is_json_ready_and_owner_focused():
    payload = get_owner_command_payload()

    assert payload["summary"]["title"] == (
        "The Clouds"
    )

    assert (
        payload["summary"]["execution_performed"]
        is False
    )

    assert payload["summary"]["active_app_count"] == 4
    assert payload["summary"]["reserved_app_count"] == 2
    assert payload["summary"]["active_lane_count"] == 5

    assert len(payload["apps"]) == 6
    assert len(payload["app_statuses"]) == 6
    assert len(payload["mission_lanes"]) == 6
    assert len(payload["mission_lane_statuses"]) == 6
    assert len(payload["owner_attention"]) == 2


def test_gp001_attention_is_deterministically_prioritized():
    dashboard = get_owner_command_dashboard()

    attention = dashboard.owner_attention

    assert attention[0].priority == (
        AttentionPriority.HIGH.value
    )

    assert attention[0].source_app_id == (
        "observatory"
    )

    assert attention[1].priority == (
        AttentionPriority.ELEVATED.value
    )


def test_gp001_overall_health_reflects_owner_attention():
    dashboard = get_owner_command_dashboard()

    assert dashboard.summary.overall_health == (
        HealthState.WATCH.value
    )

    assert (
        dashboard.summary.high_attention_count
        == 1
    )

    assert (
        dashboard.summary.critical_attention_count
        == 0
    )


def test_gp001_boundaries_block_operational_execution():
    payload = get_owner_command_payload()

    boundaries = " ".join(
        payload["boundaries"]
    ).lower()

    assert "does not authenticate" in boundaries
    assert "does not grant permissions" in boundaries
    assert "does not execute trades" in boundaries
    assert "does not move money" in boundaries
    assert "does not retrieve raw vault" in boundaries
    assert "does not operate properties" in boundaries


def test_gp001_status_is_ready_and_safe_to_continue():
    status = get_clouds_gp001_status_payload()

    assert status["pack"] == "GP001"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert (
        status["direct_operational_execution"]
        is False
    )
    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP002 — OWNER COMMAND APP REGISTRY SURFACE"
    )


def test_gp001_has_no_cross_app_python_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    forbidden_roots = {
        "vault",
        "tower",
        "observatory",
        "teller",
        "grounds",
    }

    production_files = [
        clouds_root / "contracts.py",
        clouds_root / "registry.py",
        clouds_root / "owner_command_service.py",
    ]

    for path in production_files:
        tree = ast.parse(
            path.read_text(encoding="utf-8")
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]

                    assert root not in forbidden_roots, (
                        f"{path.name} imports forbidden "
                        f"app root {root!r}"
                    )

            if isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue

                root = node.module.split(".")[0]

                assert root not in forbidden_roots, (
                    f"{path.name} imports forbidden "
                    f"app root {root!r}"
                )
