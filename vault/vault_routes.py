"""Flask routes for Archive Vault.

Vault Giant Pack 006 adds the Unified Vault Command Center while preserving
GP001-GP005 routes.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .vault_acquisition_service import (
    get_acquisition_builders_payload,
    get_acquisition_owner_queue_payload,
    get_apartment_lender_builder_payload,
    get_atm_route_builder_payload,
    get_vault_gp003_status_payload,
)
from .vault_command_center_service import (
    get_unified_vault_command_center_payload,
    get_vault_gp006_status_payload,
)
from .vault_room_service import (
    get_document_drawer_payload,
    get_owner_action_queue_payload,
    get_packet_board_payload,
    get_vault_gp002_status_payload,
    get_vault_room_payload,
)
from .vault_service import (
    get_clouds_source_payload,
    get_document_registry_payload,
    get_no_direct_upload_payload,
    get_open_app_handoff_payload,
    get_owner_console_payload,
    get_packet_templates_payload,
    get_readiness_payload,
    get_receipt_chain_payload,
    get_redacted_view_policy_payload,
    get_vault_status,
)
from .vault_soulaana_beta_service import (
    get_private_beta_onboarding_vault_payload,
    get_soulaana_artist_ip_vault_payload,
    get_soulaana_beta_owner_queue_payload,
    get_soulaana_beta_vault_payload,
    get_vault_gp005_status_payload,
)
from .vault_trust_ob_service import (
    get_ob_manual_live_proof_vault_payload,
    get_trust_entity_vault_payload,
    get_trust_ob_owner_queue_payload,
    get_trust_ob_vault_payload,
    get_vault_gp004_status_payload,
)


vault_bp = Blueprint("vault", __name__)


@vault_bp.route("/vault")
@vault_bp.route("/archive-vault")
def vault_home():
    room = get_vault_room_payload()
    return render_template(
        "vault_home.html",
        status=get_vault_status(),
        owner_console=get_owner_console_payload(),
        room=room,
    )


@vault_bp.route("/vault/command-center")
@vault_bp.route("/archive-vault/command-center")
def vault_command_center_room():
    return render_template(
        "vault_command_center.html",
        payload=get_unified_vault_command_center_payload(),
    )


@vault_bp.route("/vault/acquisition-builders")
@vault_bp.route("/archive-vault/acquisition-builders")
def vault_acquisition_builders_room():
    return render_template(
        "vault_acquisition_builders.html",
        payload=get_acquisition_builders_payload(),
    )


@vault_bp.route("/vault/trust-ob")
@vault_bp.route("/archive-vault/trust-ob")
def vault_trust_ob_room():
    return render_template(
        "vault_trust_ob.html",
        payload=get_trust_ob_vault_payload(),
    )


@vault_bp.route("/vault/soulaana-beta")
@vault_bp.route("/archive-vault/soulaana-beta")
def vault_soulaana_beta_room():
    return render_template(
        "vault_soulaana_beta.html",
        payload=get_soulaana_beta_vault_payload(),
    )


@vault_bp.route("/vault/status.json")
@vault_bp.route("/archive-vault/status.json")
def vault_status_json():
    return jsonify(get_vault_status())


@vault_bp.route("/vault/room.json")
@vault_bp.route("/archive-vault/room.json")
def vault_room_json():
    return jsonify(get_vault_room_payload())


@vault_bp.route("/vault/command-center.json")
@vault_bp.route("/archive-vault/command-center.json")
def vault_command_center_json():
    return jsonify(get_unified_vault_command_center_payload())


@vault_bp.route("/vault/packet-board.json")
def vault_packet_board_json():
    return jsonify(get_packet_board_payload())


@vault_bp.route("/vault/document-drawer.json")
def vault_document_drawer_json():
    return jsonify(get_document_drawer_payload())


@vault_bp.route("/vault/owner-action-queue.json")
def vault_owner_action_queue_json():
    return jsonify(get_owner_action_queue_payload())


@vault_bp.route("/vault/gp002-status.json")
def vault_gp002_status_json():
    return jsonify(get_vault_gp002_status_payload())


@vault_bp.route("/vault/acquisition-builders.json")
def vault_acquisition_builders_json():
    return jsonify(get_acquisition_builders_payload())


@vault_bp.route("/vault/atm-route-builder.json")
def vault_atm_route_builder_json():
    return jsonify(get_atm_route_builder_payload())


@vault_bp.route("/vault/apartment-lender-builder.json")
def vault_apartment_lender_builder_json():
    return jsonify(get_apartment_lender_builder_payload())


@vault_bp.route("/vault/acquisition-owner-queue.json")
def vault_acquisition_owner_queue_json():
    return jsonify(get_acquisition_owner_queue_payload())


@vault_bp.route("/vault/gp003-status.json")
def vault_gp003_status_json():
    return jsonify(get_vault_gp003_status_payload())


@vault_bp.route("/vault/trust-ob-vault.json")
def vault_trust_ob_vault_json():
    return jsonify(get_trust_ob_vault_payload())


@vault_bp.route("/vault/trust-entity-vault.json")
def vault_trust_entity_vault_json():
    return jsonify(get_trust_entity_vault_payload())


@vault_bp.route("/vault/ob-manual-live-proof-vault.json")
def vault_ob_manual_live_proof_vault_json():
    return jsonify(get_ob_manual_live_proof_vault_payload())


@vault_bp.route("/vault/trust-ob-owner-queue.json")
def vault_trust_ob_owner_queue_json():
    return jsonify(get_trust_ob_owner_queue_payload())


@vault_bp.route("/vault/gp004-status.json")
def vault_gp004_status_json():
    return jsonify(get_vault_gp004_status_payload())


@vault_bp.route("/vault/soulaana-beta-vault.json")
def vault_soulaana_beta_vault_json():
    return jsonify(get_soulaana_beta_vault_payload())


@vault_bp.route("/vault/soulaana-artist-ip-vault.json")
def vault_soulaana_artist_ip_vault_json():
    return jsonify(get_soulaana_artist_ip_vault_payload())


@vault_bp.route("/vault/private-beta-onboarding-vault.json")
def vault_private_beta_onboarding_vault_json():
    return jsonify(get_private_beta_onboarding_vault_payload())


@vault_bp.route("/vault/soulaana-beta-owner-queue.json")
def vault_soulaana_beta_owner_queue_json():
    return jsonify(get_soulaana_beta_owner_queue_payload())


@vault_bp.route("/vault/gp005-status.json")
def vault_gp005_status_json():
    return jsonify(get_vault_gp005_status_payload())


@vault_bp.route("/vault/gp006-status.json")
def vault_gp006_status_json():
    return jsonify(get_vault_gp006_status_payload())


@vault_bp.route("/vault/document-registry.json")
def vault_document_registry_json():
    return jsonify(get_document_registry_payload())


@vault_bp.route("/vault/packet-templates.json")
def vault_packet_templates_json():
    return jsonify(get_packet_templates_payload())


@vault_bp.route("/vault/owner-console.json")
def vault_owner_console_json():
    return jsonify(get_owner_console_payload())


@vault_bp.route("/vault/readiness.json")
def vault_readiness_json():
    return jsonify(get_readiness_payload())


@vault_bp.route("/vault/no-direct-upload.json")
def vault_no_direct_upload_json():
    return jsonify(get_no_direct_upload_payload())


@vault_bp.route("/vault/redacted-view-policy.json")
def vault_redacted_view_policy_json():
    return jsonify(get_redacted_view_policy_payload())


@vault_bp.route("/vault/open-app-handoff.json")
def vault_open_app_handoff_json():
    return jsonify(get_open_app_handoff_payload())


@vault_bp.route("/vault/receipt-chain.json")
def vault_receipt_chain_json():
    return jsonify(get_receipt_chain_payload())


@vault_bp.route("/vault/clouds-source.json")
def vault_clouds_source_json():
    return jsonify(get_clouds_source_payload())

# === VAULT GIANT PACK 007 ROUTES START ===
@vault_bp.route("/vault/search-tracker")
@vault_bp.route("/archive-vault/search-tracker")
def vault_search_tracker_room():
    from .vault_tracking_service import get_vault_search_tracker_payload
    return render_template(
        "vault_search_tracker.html",
        payload=get_vault_search_tracker_payload(),
    )


@vault_bp.route("/vault/search-tracker.json")
def vault_search_tracker_json():
    from .vault_tracking_service import get_vault_search_tracker_payload
    return jsonify(get_vault_search_tracker_payload())


@vault_bp.route("/vault/search-index.json")
def vault_search_index_json():
    from .vault_tracking_service import get_vault_search_index_payload
    return jsonify(get_vault_search_index_payload())


@vault_bp.route("/vault/requirement-tracker.json")
def vault_requirement_tracker_json():
    from .vault_tracking_service import get_requirement_tracker_payload
    return jsonify(get_requirement_tracker_payload())


@vault_bp.route("/vault/expiration-renewal-wall.json")
def vault_expiration_renewal_wall_json():
    from .vault_tracking_service import get_expiration_renewal_wall_payload
    return jsonify(get_expiration_renewal_wall_payload())


@vault_bp.route("/vault/data-freshness-wall.json")
def vault_data_freshness_wall_json():
    from .vault_tracking_service import get_data_freshness_wall_payload
    return jsonify(get_data_freshness_wall_payload())


@vault_bp.route("/vault/gp007-status.json")
def vault_gp007_status_json():
    from .vault_tracking_service import get_vault_gp007_status_payload
    return jsonify(get_vault_gp007_status_payload())
# === VAULT GIANT PACK 007 ROUTES END ===
