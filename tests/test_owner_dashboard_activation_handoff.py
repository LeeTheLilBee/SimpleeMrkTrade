from pathlib import Path
import re

from tower.app_registry import (
    route_by_path,
    temporary_placeholder_routes,
)


ROOT = Path(__file__).resolve().parents[1]

APP = (
    ROOT / "web/app.py"
).read_text(
    encoding="utf-8",
    errors="replace",
)

TEMPLATE = (
    ROOT / "web/templates/owner_dashboard.html"
).read_text(
    encoding="utf-8",
    errors="replace",
)

OWNER_CONSOLE_TEMPLATE = (
    ROOT / "web/templates/owner_console.html"
).read_text(
    encoding="utf-8",
    errors="replace",
)

OWNER_CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

SOULAANA = (
    ROOT / "web/static/ob/ob_owner_dashboard_soulaana.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

TOWER_OWNER_WEB = (
    ROOT / "tower/owner_dashboard_web.py"
).read_text(
    encoding="utf-8",
    errors="replace",
)


def compact(value):
    return re.sub(
        r"\s+",
        "",
        value,
    )


def test_owner_dashboard_activation_uses_only_canonical_ob_route():
    assert '@app.route("/ob/owner-dashboard")' in APP

    assert '@app.route("/owner-dashboard")' not in APP

    assert (
        'def ob_owner_dashboard_v17():\n'
        '    return render_template("owner_dashboard.html")'
    ) in APP


def test_owner_dashboard_activation_reports_active_lifecycle():
    assert "OWNER_DASHBOARD_ACTIVATION_HANDOFF" in TEMPLATE

    assert (
        'data-ob-owner-dashboard-role="owner-only-active"'
        in TEMPLATE
    )

    assert (
        'data-ob-owner-dashboard-route-state="tower-protected-active"'
        in TEMPLATE
    )

    assert (
        'data-ob-owner-dashboard-design-activated="true"'
        in TEMPLATE
    )

    assert (
        'data-ob-owner-capital-lanes="true"'
        in TEMPLATE
    )

    assert "Tower Protected" in TEMPLATE

    assert "Live Auto Locked" in TEMPLATE


def test_ob_owner_dashboard_remains_tower_protected():
    route = route_by_path(
        "/ob/owner-dashboard"
    )

    assert route is not None

    assert route["owner_only"] is True

    assert route["requires_owner_session"] is True

    assert route["requires_step_up"] is False

    assert route["default_denied_when_unknown"] is True

    assert route["temporary_placeholder"] is False

    assert (
        route["lock_state"]
        == "owner_only_protected"
    )

    assert (
        "/ob/owner-dashboard"
        not in temporary_placeholder_routes()
    )


def test_ob_owner_dashboard_and_owner_console_remain_separate():
    assert (
        'return render_template("owner_dashboard.html")'
        in APP
    )

    assert (
        'return render_template("owner_console.html")'
        in APP
    )

    assert "ownerDashboardMount" in TEMPLATE

    assert "ownerConsoleMount" in OWNER_CONSOLE_TEMPLATE

    for marker in [
        "ob_owner_console.js",
        "ob_owner_source_audit.js",
        "ob_private_beta_launch_control.js",
        "ob_manual_live_operator_confidence_readiness_checkpoint.js",
    ]:
        assert marker not in TEMPLATE


def test_tower_and_ob_owner_dashboards_are_distinct_namespaces():
    assert "/tower/owner-dashboard" in TOWER_OWNER_WEB

    assert "/tower/owner-dashboard.json" in TOWER_OWNER_WEB

    assert "/ob/owner-dashboard" in APP


def test_soulaana_owner_intelligence_is_preserved_after_capital_lane_redesign():
    for marker in [
        "SOULAANA · OWNER BRIEFING",
        "what_i_see",
        "capital_read",
        "what_needs_you",
        "next_best_move",
        "no_action_needed",
        "owner_altitude",
        "evidence_rule",
    ]:
        assert marker in SOULAANA


def test_owner_truth_and_execution_boundaries_remain_fail_closed():
    source = compact(
        OWNER_CONTRACT
    )

    assert "sourceLooksVerified" in OWNER_CONTRACT

    assert (
        'credentials:"same-origin"'
        in source
    )

    for marker in [
        "actual_capital_known:false",
        "capital_progress_known:false",
        "verified_snapshot:false",
        "capital_lanes_owner_dashboard_only:true",
        "non_owner_capital_lane_delivery:false",
        "lane_selection_changes_context_only:true",
        "broker_api_enabled:false",
        "broker_order_submission_enabled:false",
        "real_capital_movement_enabled:false",
        "automatic_contract_selection_enabled:false",
        "auto_execution_enabled:false",
        "live_auto_locked:true",
    ]:
        assert marker in source
