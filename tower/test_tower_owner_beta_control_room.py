from __future__ import annotations

from tower.tower_owner_beta_control_room import (
    CURRENT_STAGING_READY_DECISION,
    FINAL_STAGING_DECISION_COMMIT,
    HOSTED_OWNER_WALKTHROUGH_COMMIT,
    OWNER_BETA_CONTROL_ROOM_READY,
    OWNER_BETA_JSON_ROUTE,
    OWNER_BETA_ROUTE,
    STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH,
    app_readiness_matrix,
    beta_blockers,
    dangerous_controls,
    hosted_staging_readiness_card,
    ob_beta_gate_summary,
    owner_beta_cert,
    owner_beta_payload,
    owner_issue_intake_schema,
    owner_next_action_panel,
    render_owner_beta_html,
    tester_access_statuses as build_tester_access_statuses,
    walkthrough_receipts,
)


def test_owner_beta_routes_are_defined():
    assert OWNER_BETA_ROUTE == "/tower/owner-beta"
    assert OWNER_BETA_JSON_ROUTE == "/tower/owner-beta.json"


def test_owner_beta_decision_is_ready_but_safety_locked():
    assert CURRENT_STAGING_READY_DECISION == "STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH"
    assert STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH is True
    assert OWNER_BETA_CONTROL_ROOM_READY is True

    controls = dangerous_controls()
    assert controls
    assert all(value is False for value in controls.values())


def test_hosted_staging_readiness_card():
    card = hosted_staging_readiness_card()
    assert card.card_id == "hosted_staging_readiness"
    assert card.status == "ready_for_owner_beta_walkthrough"
    assert "Owner Console" in card.summary
    assert "Tower return" in card.summary


def test_walkthrough_receipts_include_final_and_hosted_proof():
    receipts = walkthrough_receipts()
    commits = {receipt.commit for receipt in receipts}

    assert FINAL_STAGING_DECISION_COMMIT in commits
    assert HOSTED_OWNER_WALKTHROUGH_COMMIT in commits

    titles = {receipt.title for receipt in receipts}
    assert "Final Tower–OB Staging Readiness Decision" in titles
    assert "Hosted Owner Walkthrough Verification" in titles


def test_owner_issue_intake_schema_is_safe_contract():
    schema = owner_issue_intake_schema()

    assert schema["schema_id"] == "tower_owner_beta_issue_intake_v1"
    assert "soulaana_interpretation_gap" in schema["accepted_issue_types"]
    assert "market_map_too_cluttered" in schema["accepted_issue_types"]
    assert schema["dangerous_actions_allowed"] is False


def test_beta_blockers_keep_manual_live_and_capital_locked():
    blockers = beta_blockers()
    blocker_ids = {blocker.blocker_id for blocker in blockers}

    assert "manual_live_not_authorized" in blocker_ids
    assert "production_not_authorized" in blocker_ids
    assert "broker_capital_locked" in blocker_ids

    assert all(blocker.status == "locked" for blocker in blockers)


def test_app_readiness_matrix_has_ecosystem_apps():
    rows = app_readiness_matrix()
    ids = {row.app_id for row in rows}

    assert {"tower", "observatory", "vault", "teller", "clouds", "grounds"} <= ids
    assert all(row.dangerous_controls_locked is True for row in rows)


def test_ob_beta_gate_summary_keeps_ob_survey_paper_only():
    cards = ob_beta_gate_summary()
    card_ids = {card.card_id for card in cards}

    assert "ob_mode_scope" in card_ids
    assert "ob_six_rooms" in card_ids
    assert "soulaana_interpretation" in card_ids
    assert "market_map_deep_dives" in card_ids

    mode_card = next(card for card in cards if card.card_id == "ob_mode_scope")
    assert mode_card.status == "survey_paper_only"
    assert mode_card.locked is True


def test_tester_access_statuses_default_deny_non_owner():
    statuses = build_tester_access_statuses()
    groups = {status.tester_group: status for status in statuses}

    assert groups["owner"].access_status == "allowed"
    assert groups["private_beta_testers"].owner_approval_required is True
    assert groups["anonymous_users"].access_status == "denied"
    assert groups["non_owner_users"].access_status == "denied_until_invited"


def test_owner_next_action_panel_holds_manual_live():
    cards = owner_next_action_panel()
    card_ids = {card.card_id for card in cards}

    assert "review_hosted_owner_beta" in card_ids
    assert "open_issue_intake" in card_ids
    assert "prepare_ob_manual_live_later" in card_ids

    manual = next(card for card in cards if card.card_id == "prepare_ob_manual_live_later")
    assert manual.locked is True
    assert manual.status == "hold"


def test_owner_beta_payload_shape_and_safety():
    payload = owner_beta_payload()

    assert payload["version"] == "tower_owner_beta_control_room_v1"
    assert payload["routes"]["html"] == "/tower/owner-beta"
    assert payload["routes"]["json"] == "/tower/owner-beta.json"
    assert payload["staging_ready_for_owner_beta_walkthrough"] is True
    assert payload["owner_beta_control_room_ready"] is True

    assert payload["dangerous_controls"]
    assert all(value is False for value in payload["dangerous_controls"].values())

    assert len(payload["cards"]) >= 8
    assert len(payload["walkthrough_receipts"]) == 2
    assert len(payload["beta_blockers"]) == 3
    assert len(payload["app_readiness_matrix"]) >= 6
    assert len(payload["tester_access_statuses"]) == 4


def test_owner_beta_html_contains_owner_beta_control_room():
    html = render_owner_beta_html()

    assert "Tower Owner-Beta Control Room" in html
    assert "Owner beta is ready for walkthrough" in html
    assert "Manual Live locked" in html
    assert "Production locked" in html
    assert FINAL_STAGING_DECISION_COMMIT in html


def test_owner_beta_certs_2553_to_2562():
    for pack in range(2553, 2563):
        cert = owner_beta_cert(pack)

        assert cert["pack"] == pack
        assert cert["status"] == "passed"
        assert cert["owner_beta_control_room_ready"] is True
        assert cert["staging_ready_for_owner_beta_walkthrough"] is True
        assert cert["dangerous_controls_locked"] is True
        assert cert["route"] == "/tower/owner-beta"
        assert cert["json_route"] == "/tower/owner-beta.json"
