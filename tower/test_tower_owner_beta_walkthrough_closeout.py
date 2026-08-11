from __future__ import annotations

from tower.tower_owner_beta_walkthrough_closeout import (
    beta_scope_reminder,
    dangerous_controls_locked,
    hosted_proof_summary,
    issue_intake_receipt_summary,
    owner_decision_packet,
    tester_entry_prep_payload,
    tester_entry_readiness_gate,
    tester_invite_prep_record,
    walkthrough_checklist,
    walkthrough_closeout_cert,
    walkthrough_closeout_payload,
)


def test_walkthrough_closeout_payload_is_safe_and_ready():
    payload = walkthrough_closeout_payload()

    assert payload["version"] == "tower_owner_beta_walkthrough_closeout_v1"
    assert payload["status"] == "ready_for_owner_walkthrough_closeout"
    assert payload["all_required_walkthrough_steps_ready"] is True
    assert payload["tester_entry_open"] is False
    assert payload["dangerous_controls_locked"] is True
    assert all(value is False for value in payload["dangerous_controls"].values())


def test_walkthrough_checklist_routes_present():
    routes = {item["route"] for item in walkthrough_checklist()}

    assert "/tower/login" in routes
    assert "/tower/access-home" in routes
    assert "/tower/owner-beta" in routes
    assert "/tower/observatory-six-room-acceptance" in routes
    assert "/tower/owner-beta/issues.json" in routes
    assert "/tower/owner-beta/review-receipts.json" in routes


def test_hosted_proof_and_issue_receipt_summary():
    proof = hosted_proof_summary()
    issue_summary = issue_intake_receipt_summary()

    assert proof["hosted_owner_beta_owner_gated"] is True
    assert proof["hosted_issue_submit_verified"] is True
    assert issue_summary["anonymous_issue_routes_denied"] is True
    assert issue_summary["review_receipt_generated"] is True
    assert issue_summary["receipt_linkage_verified"] is True


def test_tester_entry_prep_is_not_open():
    gate = tester_entry_readiness_gate()
    invite = tester_invite_prep_record()
    prep = tester_entry_prep_payload()

    assert gate["status"] == "prepared_not_open"
    assert gate["ready_for_owner_decision"] is True
    assert gate["tester_invites_sent"] is False
    assert invite["status"] == "draft_prepared_not_sent"
    assert invite["tester_invites_sent"] is False
    assert prep["tester_entry_open"] is False
    assert prep["tester_invites_sent"] is False
    assert prep["external_accounts_created"] is False


def test_beta_scope_keeps_live_and_production_closed():
    scope = beta_scope_reminder()

    assert "Survey" in scope["allowed_modes"]
    assert "Paper" in scope["allowed_modes"]
    assert "Manual Live Level 1" in scope["owner_only_later"]
    assert "production deployment" in scope["not_allowed"]
    assert "broker submission" in scope["not_allowed"]
    assert "capital movement" in scope["not_allowed"]
    assert "Live Auto" in scope["not_allowed"]


def test_owner_decision_packet_does_not_open_live():
    packet = owner_decision_packet()

    assert packet["decision_required"] is True
    assert packet["dangerous_controls_locked"] is True

    for option in packet["decision_options"]:
        assert option["opens_live_or_production"] is False


def test_walkthrough_closeout_certs_2583_to_2592():
    for pack in range(2583, 2593):
        cert = walkthrough_closeout_cert(pack)

        assert cert["pack"] == pack
        assert cert["status"] == "passed"
        assert cert["requires_owner_session"] is True
        assert cert["tester_entry_open"] is False
        assert cert["tester_invites_sent"] is False
        assert cert["external_accounts_created"] is False
        assert cert["dangerous_controls_locked"] is True
        assert all(value is False for value in cert["dangerous_controls"].values())


def test_dangerous_controls_locked():
    assert dangerous_controls_locked() is True
