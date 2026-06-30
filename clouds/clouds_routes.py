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
