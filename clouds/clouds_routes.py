"""Flask routes for The Clouds."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .clouds_service import (
    get_clouds_command_dashboard_payload,
    get_clouds_gp001_status_payload,
    get_clouds_source_map_payload,
    get_clouds_status_payload,
    get_clouds_vault_summary_payload,
)


clouds_bp = Blueprint("clouds", __name__)


@clouds_bp.route("/clouds")
@clouds_bp.route("/the-clouds")
def clouds_home():
    return render_template(
        "clouds_home.html",
        dashboard=get_clouds_command_dashboard_payload(),
        status=get_clouds_status_payload(),
    )


@clouds_bp.route("/clouds/status.json")
@clouds_bp.route("/the-clouds/status.json")
def clouds_status_json():
    return jsonify(get_clouds_status_payload())


@clouds_bp.route("/clouds/source-map.json")
def clouds_source_map_json():
    return jsonify(get_clouds_source_map_payload())


@clouds_bp.route("/clouds/vault-summary.json")
def clouds_vault_summary_json():
    return jsonify(get_clouds_vault_summary_payload())


@clouds_bp.route("/clouds/dashboard.json")
def clouds_dashboard_json():
    return jsonify(get_clouds_command_dashboard_payload())


@clouds_bp.route("/clouds/gp001-status.json")
def clouds_gp001_status_json():
    return jsonify(get_clouds_gp001_status_payload())

# === CLOUDS GIANT PACK 002 ROUTES START ===
@clouds_bp.route("/clouds/app-registry")
@clouds_bp.route("/the-clouds/app-registry")
def clouds_app_registry_room():
    from .clouds_app_registry_service import get_clouds_app_registry_dashboard_payload
    return render_template(
        "clouds_app_registry.html",
        payload=get_clouds_app_registry_dashboard_payload(),
    )


@clouds_bp.route("/clouds/app-registry.json")
def clouds_app_registry_json():
    from .clouds_app_registry_service import get_clouds_app_registry_payload
    return jsonify(get_clouds_app_registry_payload())


@clouds_bp.route("/clouds/placeholder-sources.json")
def clouds_placeholder_sources_json():
    from .clouds_app_registry_service import get_clouds_placeholder_sources_payload
    return jsonify(get_clouds_placeholder_sources_payload())


@clouds_bp.route("/clouds/authority-map.json")
def clouds_authority_map_json():
    from .clouds_app_registry_service import get_clouds_authority_map_payload
    return jsonify(get_clouds_authority_map_payload())


@clouds_bp.route("/clouds/app-registry-dashboard.json")
def clouds_app_registry_dashboard_json():
    from .clouds_app_registry_service import get_clouds_app_registry_dashboard_payload
    return jsonify(get_clouds_app_registry_dashboard_payload())


@clouds_bp.route("/clouds/gp002-status.json")
def clouds_gp002_status_json():
    from .clouds_app_registry_service import get_clouds_gp002_status_payload
    return jsonify(get_clouds_gp002_status_payload())
# === CLOUDS GIANT PACK 002 ROUTES END ===

# === CLOUDS GIANT PACK 003 ROUTES START ===
@clouds_bp.route("/clouds/owner-focus")
@clouds_bp.route("/the-clouds/owner-focus")
def clouds_owner_focus_room():
    from .clouds_owner_focus_service import get_clouds_owner_focus_dashboard_payload
    return render_template(
        "clouds_owner_focus.html",
        payload=get_clouds_owner_focus_dashboard_payload(),
    )


@clouds_bp.route("/clouds/owner-focus-queue.json")
def clouds_owner_focus_queue_json():
    from .clouds_owner_focus_service import get_clouds_owner_focus_queue_payload
    return jsonify(get_clouds_owner_focus_queue_payload())


@clouds_bp.route("/clouds/focus-lanes.json")
def clouds_focus_lanes_json():
    from .clouds_owner_focus_service import get_clouds_focus_lanes_payload
    return jsonify(get_clouds_focus_lanes_payload())


@clouds_bp.route("/clouds/blocked-watch.json")
def clouds_blocked_watch_json():
    from .clouds_owner_focus_service import get_clouds_blocked_watch_payload
    return jsonify(get_clouds_blocked_watch_payload())


@clouds_bp.route("/clouds/owner-focus-dashboard.json")
def clouds_owner_focus_dashboard_json():
    from .clouds_owner_focus_service import get_clouds_owner_focus_dashboard_payload
    return jsonify(get_clouds_owner_focus_dashboard_payload())


@clouds_bp.route("/clouds/gp003-status.json")
def clouds_gp003_status_json():
    from .clouds_owner_focus_service import get_clouds_gp003_status_payload
    return jsonify(get_clouds_gp003_status_payload())
# === CLOUDS GIANT PACK 003 ROUTES END ===

# === CLOUDS GIANT PACK 004 ROUTES START ===
@clouds_bp.route("/clouds/app-lane-status")
@clouds_bp.route("/the-clouds/app-lane-status")
def clouds_app_lane_status_room():
    from .clouds_app_lane_status_service import get_clouds_app_lane_status_dashboard_payload
    return render_template(
        "clouds_app_lane_status.html",
        payload=get_clouds_app_lane_status_dashboard_payload(),
    )


@clouds_bp.route("/clouds/app-status-board.json")
def clouds_app_status_board_json():
    from .clouds_app_lane_status_service import get_clouds_app_status_board_payload
    return jsonify(get_clouds_app_status_board_payload())


@clouds_bp.route("/clouds/lane-status-board.json")
def clouds_lane_status_board_json():
    from .clouds_app_lane_status_service import get_clouds_lane_status_board_payload
    return jsonify(get_clouds_lane_status_board_payload())


@clouds_bp.route("/clouds/placeholder-health.json")
def clouds_placeholder_health_json():
    from .clouds_app_lane_status_service import get_clouds_placeholder_health_payload
    return jsonify(get_clouds_placeholder_health_payload())


@clouds_bp.route("/clouds/vault-live-status.json")
def clouds_vault_live_status_json():
    from .clouds_app_lane_status_service import get_clouds_vault_live_status_payload
    return jsonify(get_clouds_vault_live_status_payload())


@clouds_bp.route("/clouds/app-lane-status-dashboard.json")
def clouds_app_lane_status_dashboard_json():
    from .clouds_app_lane_status_service import get_clouds_app_lane_status_dashboard_payload
    return jsonify(get_clouds_app_lane_status_dashboard_payload())


@clouds_bp.route("/clouds/gp004-status.json")
def clouds_gp004_status_json():
    from .clouds_app_lane_status_service import get_clouds_gp004_status_payload
    return jsonify(get_clouds_gp004_status_payload())
# === CLOUDS GIANT PACK 004 ROUTES END ===
