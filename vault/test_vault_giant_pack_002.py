"""Vault Giant Pack 002 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_room_service import (
    get_document_drawer_payload,
    get_owner_action_queue_payload,
    get_packet_board_payload,
    get_vault_gp002_status_payload,
    get_vault_room_payload,
)


def test_gp002_room_payload_is_ready_and_json_serializable():
    room = get_vault_room_payload()
    json.dumps(room)

    assert room["app_id"] == "archive_vault"
    assert room["room_status"] == "ready"
    assert room["readiness_score"] == 100
    assert room["public_access"] is False
    assert room["private_invite_only"] is True
    assert room["tower_guard"]["tower_required"] is True
    assert room["tower_guard"]["vault_owns_permissions"] is False


def test_gp002_packet_board_has_aggressive_growth_lanes():
    board = get_packet_board_payload()
    lanes = {card["business_lane"] for card in board["cards"]}

    assert board["card_count"] >= 6
    assert {"atm", "property", "trust", "observatory", "soulaana", "beta"}.issubset(lanes)

    atm = next(card for card in board["cards"] if card["business_lane"] == "atm")
    property_card = next(card for card in board["cards"] if card["business_lane"] == "property")

    assert atm["setup_status"] == "ready_for_target"
    assert property_card["setup_status"] == "ready_for_target"
    assert atm["direct_upload_allowed"] is False
    assert property_card["tower_guard_required"] is True


def test_gp002_document_drawer_is_redacted_and_upload_locked():
    drawer = get_document_drawer_payload()

    assert drawer["record_count"] >= 4
    assert drawer["redaction_default"] == "redacted"
    assert drawer["direct_upload_allowed"] is False

    for record in drawer["records"]:
        assert "Overview" in record["drawer_tabs"]
        assert "Redaction" in record["drawer_tabs"]
        assert record["redaction_required"] is True
        assert record["direct_upload_allowed"] is False
        assert "bank_account_details" in record["sensitive_fields_hidden"]
        assert record["clouds_safe_summary"]["title"] == record["title"]


def test_gp002_owner_action_queue_has_ready_and_locked_items():
    queue = get_owner_action_queue_payload()

    assert queue["action_count"] >= 6
    assert queue["critical_count"] >= 1
    assert queue["high_count"] >= 4
    assert queue["ready_count"] >= 4

    action_ids = {action["action_id"] for action in queue["actions"]}
    assert "vault_action_storage_clearance" in action_ids
    assert "vault_action_atm_packet_ready" in action_ids
    assert "vault_action_property_packet_ready" in action_ids
    assert "vault_action_clouds_preview_ready" in action_ids

    storage = next(action for action in queue["actions"] if action["action_id"] == "vault_action_storage_clearance")
    assert storage["status"] == "blocked_until_tower_clearance"
    assert "direct_upload_locked" in storage["blocked_by"]


def test_gp002_clouds_preview_is_summary_only_redacted():
    room = get_vault_room_payload()
    preview = room["clouds_preview"]

    assert preview["safe_for_clouds"] is True
    assert preview["view"] == "summary_only_redacted"
    assert preview["packet_card_count"] >= 6
    assert preview["document_record_count"] >= 4
    assert "broker_details" in preview["sensitive_fields_hidden"]
    assert "raw_direct_file_upload" in preview["blocked_reasons"]


def test_gp002_status_payload_marks_safe_to_continue():
    status = get_vault_gp002_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 002"
    assert status["safe_to_continue_to_gp003"] is True
    assert status["packet_card_count"] >= 6
    assert status["document_record_count"] >= 4
    assert status["owner_action_count"] >= 6


def test_gp002_template_css_and_js_exist_and_use_dark_vault_room():
    template = Path("templates/vault_home.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault.css").read_text(encoding="utf-8")
    js = Path("static/vault/vault_room.js").read_text(encoding="utf-8")

    assert "VAULT_ROOM_BOOTSTRAP" in template
    assert "packet-board" in template
    assert "document-drawer" in template
    assert "owner-queue" in template
    assert "clouds-preview" in template

    assert "vault-body" in css
    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()

    assert "setupDocumentDrawer" in js
    assert "setupPacketFilters" in js


def test_gp002_routes_include_new_json_endpoints():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")

    assert "/vault/room.json" in routes
    assert "/vault/packet-board.json" in routes
    assert "/vault/document-drawer.json" in routes
    assert "/vault/owner-action-queue.json" in routes
    assert "/vault/gp002-status.json" in routes
