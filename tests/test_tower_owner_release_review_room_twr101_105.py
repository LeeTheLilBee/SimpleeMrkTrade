
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

import tower.hosted_owner_release_review_web as release_web
from tower.hosted_candidate_release_gate import build_hosted_candidate_release_packet
from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
    SAFETY_FALSE_FIELDS,
)
from tower.hosted_release_packet_provider import (
    NO_REVIEWABLE_CANDIDATE,
    load_canonical_release_packet,
)
from tower.tower_human_login_ob_launch import (
    OWNER_ROLE,
    SESSION_AUTHENTICATED,
    SESSION_AUTH_TIME,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
)


REVISION = "abc123"
ORIGIN = {"Origin": "http://localhost"}


def parity(*, passing: bool = True) -> dict:
    return {
        "status": "tower_hosted_candidate_parity_pass" if passing else "tower_hosted_candidate_parity_fail",
        "parity_pass": passing,
        "expected_revision": REVISION,
        "actual_revision": REVISION,
        "entrypoint": "web.managed_staging:app",
        "critical_route_count": 11,
        "checks": {
            "expected_revision_valid": True,
            "health_http_200": passing,
            "manifest_http_200": True,
            "exact_candidate_revision_match": True,
            "all_critical_routes_present": True,
        },
        "failures": [] if passing else ["Hosted health check failed."],
        "deployment_authorized": False,
        "production_promotion_authorized": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "staging_ready_changed": False,
    }


def build_app(monkeypatch, tmp_path, *, owner=True, elevated=True, passing=True, source=True, age_seconds=0):
    app = Flask(__name__)
    app.secret_key = "tower-owner-release-review-test-only"
    packet_path = tmp_path / "canonical-release-packet.json"
    ledger_path = tmp_path / "owner-decision-receipts.jsonl"

    monkeypatch.setenv("TOWER_OWNER_USERNAME", "owner")
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    monkeypatch.setenv("TOWER_LOCAL_OWNER_PASSWORD", "test-owner-password")
    monkeypatch.setenv("TOWER_RELEASE_RECEIPT_LEDGER_PATH", str(ledger_path))
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)

    app.config["TOWER_HOSTED_RELEASE_PACKET_PATH"] = str(packet_path)
    app.config["TOWER_HOSTED_RELEASE_EXPECTED_REVISION"] = REVISION
    app.config["TOWER_HOSTED_RELEASE_MAX_PACKET_AGE_SECONDS"] = 3600

    if source:
        created_at = (
            datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
        ).isoformat().replace("+00:00", "Z")
        packet = build_hosted_candidate_release_packet(
            parity(passing=passing),
            created_at_utc=created_at,
        )
        packet_path.write_text(json.dumps(packet), encoding="utf-8")

    release_web.register_tower_owner_release_review_routes(app)
    client = app.test_client()

    if owner:
        with client.session_transaction() as owner_session:
            now = datetime.now(timezone.utc)
            owner_session[SESSION_AUTHENTICATED] = True
            owner_session[SESSION_ROLE] = OWNER_ROLE
            owner_session[SESSION_OWNER_ID] = "simplee_owner"
            owner_session[SESSION_USERNAME] = "owner"
            owner_session[SESSION_AUTH_TIME] = now.isoformat()
            if elevated:
                owner_session[SESSION_STEP_UP_UNTIL] = (
                    now + timedelta(minutes=10)
                ).isoformat()

    return app, client, packet_path, ledger_path


def review_form(client, packet_path, *, decision=APPROVE_RELEASE, reason="Owner reviewed exact hosted candidate."):
    client.get(release_web.RELEASE_REVIEW_PATH)
    with client.session_transaction() as owner_session:
        token = owner_session[release_web.RELEASE_CSRF_SESSION_KEY]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))["packet"]
    return {
        "csrf_token": token,
        "packet_integrity_hash": packet["packet_integrity_hash"],
        "expected_revision": packet["expected_revision"],
        "decision": decision,
        "reason": reason,
    }


def test_twr101_missing_server_packet_fails_closed(monkeypatch, tmp_path):
    app, client, _, _ = build_app(monkeypatch, tmp_path, source=False)
    with app.app_context():
        result = load_canonical_release_packet()
    assert result["reviewable"] is False
    assert result["candidate_state"] == NO_REVIEWABLE_CANDIDATE
    assert result["reason"] == "packet_source_missing"


def test_twr101_stale_packet_fails_closed(monkeypatch, tmp_path):
    app, client, _, _ = build_app(monkeypatch, tmp_path, age_seconds=7200)
    with app.app_context():
        result = load_canonical_release_packet()
    assert result["reviewable"] is False
    assert result["reason"] == "packet_stale_or_future_dated"


def test_twr101_tampered_server_packet_fails_closed(monkeypatch, tmp_path):
    app, client, path, _ = build_app(monkeypatch, tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["packet"]["actual_revision"] = "tampered"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with app.app_context():
        result = load_canonical_release_packet()
    assert result["reason"] == "packet_integrity_invalid"


def test_twr101_wrong_candidate_revision_fails_closed(monkeypatch, tmp_path):
    app, client, _, _ = build_app(monkeypatch, tmp_path)
    app.config["TOWER_HOSTED_RELEASE_EXPECTED_REVISION"] = "other-candidate"
    with app.app_context():
        result = load_canonical_release_packet()
    assert result["reason"] == "packet_candidate_revision_mismatch"


def test_twr102_nonowner_cannot_open_review_room(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, owner=False)
    response = client.get(release_web.RELEASE_REVIEW_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == "/tower/login"


def test_twr102_owner_without_step_up_stays_in_tower(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, elevated=False)
    response = client.get(release_web.RELEASE_REVIEW_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == release_web.RELEASE_STEP_UP_PATH
    assert "observatory" not in response.headers["Location"].lower()


def test_twr102_owner_review_room_uses_focused_product_ui(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path)
    response = client.get(release_web.RELEASE_REVIEW_PATH)
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Release Review" in body
    assert "Approve candidate" in body
    assert "Candidate evidence" in body
    assert "Execution" in body
    assert "Still locked" in body
    assert release_web.RELEASE_ROOM_MARKER in body


def test_twr102_missing_packet_room_has_no_decision_form(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, source=False)
    response = client.get(release_web.RELEASE_REVIEW_PATH)
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "NO REVIEWABLE CANDIDATE" in body
    assert "Approve candidate" not in body


def test_twr103_dashboard_contains_owner_release_entry(monkeypatch, tmp_path):
    import tower.owner_dashboard_web as dashboard

    monkeypatch.setattr(dashboard, "owner_session_active", lambda: True)
    app = Flask(__name__)
    app.secret_key = "tower-release-dashboard-test"
    dashboard.register_tower_owner_dashboard_routes(app)
    response = app.test_client().get("/tower/owner-dashboard")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "data-tower-release-review-entry" in body
    assert 'href="/tower/owner/release-review"' in body
    assert sum(
        1
        for rule in app.url_map.iter_rules()
        if rule.rule == release_web.RELEASE_REVIEW_PATH
    ) == 1


def test_twr103_dashboard_registration_is_idempotent(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    release_web.register_tower_owner_release_review_routes(app)
    assert sum(
        1
        for rule in app.url_map.iter_rules()
        if rule.rule == release_web.RELEASE_REVIEW_PATH
    ) == 1


def test_twr104_release_step_up_returns_to_tower_review(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, elevated=False)
    page = client.get(release_web.RELEASE_STEP_UP_PATH)
    assert "remain in Tower" in page.get_data(as_text=True)
    with client.session_transaction() as owner_session:
        token = owner_session[release_web.RELEASE_CSRF_SESSION_KEY]
    response = client.post(
        release_web.RELEASE_STEP_UP_PATH,
        data={"csrf_token": token, "password": "test-owner-password"},
        headers=ORIGIN,
    )
    assert response.status_code == 303
    assert response.headers["Location"] == release_web.RELEASE_REVIEW_PATH
    assert "observatory" not in response.headers["Location"].lower()


def test_twr104_wrong_owner_password_is_denied(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, elevated=False)
    client.get(release_web.RELEASE_STEP_UP_PATH)
    with client.session_transaction() as owner_session:
        token = owner_session[release_web.RELEASE_CSRF_SESSION_KEY]
    response = client.post(
        release_web.RELEASE_STEP_UP_PATH,
        data={"csrf_token": token, "password": "wrong-password"},
        headers=ORIGIN,
    )
    assert response.status_code == 403


def test_twr104_missing_csrf_is_denied(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    form = review_form(client, path)
    form.pop("csrf_token")
    response = client.post(release_web.RELEASE_DECISION_PATH, data=form, headers=ORIGIN)
    assert response.status_code == 403


def test_twr104_cross_origin_decision_is_denied(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=review_form(client, path),
        headers={"Origin": "https://attacker.invalid"},
    )
    assert response.status_code == 403


def test_twr104_stale_candidate_submission_is_denied(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    form = review_form(client, path)
    form["packet_integrity_hash"] = "0" * 64
    response = client.post(release_web.RELEASE_DECISION_PATH, data=form, headers=ORIGIN)
    assert response.status_code == 409
    assert response.get_json()["status"] == "tower_owner_release_candidate_stale"


def test_twr104_failed_parity_cannot_be_approved(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path, passing=False)
    body = client.get(release_web.RELEASE_REVIEW_PATH).get_data(as_text=True)
    assert "Approve candidate" not in body
    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=review_form(client, path, decision=APPROVE_RELEASE),
        headers=ORIGIN,
    )
    assert response.status_code == 422
    assert response.get_json()["recorded"] is False


@pytest.mark.parametrize("decision", (APPROVE_RELEASE, HOLD_RELEASE, REJECT_RELEASE))
def test_twr104_owner_can_record_explicit_decision(monkeypatch, tmp_path, decision):
    _, client, path, ledger = build_app(monkeypatch, tmp_path)
    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=review_form(client, path, decision=decision),
        headers=ORIGIN,
    )
    assert response.status_code == 303
    assert response.headers["Location"].startswith(release_web.RELEASE_REVIEW_PATH + "/receipt/")
    assert ledger.is_file()


def test_twr104_duplicate_decision_is_rejected(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    first = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=review_form(client, path),
        headers=ORIGIN,
    )
    assert first.status_code == 303
    second = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=review_form(client, path),
        headers=ORIGIN,
    )
    assert second.status_code == 409
    assert second.get_json()["duplicate"] is True


def test_twr105_receipt_confirmation_is_owner_only(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    decision = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=review_form(client, path),
        headers=ORIGIN,
    )
    receipt_path = decision.headers["Location"]
    body = client.get(receipt_path).get_data(as_text=True)
    assert "Decision recorded" in body
    assert "Verified" in body
    assert "Still locked" in body

    with client.session_transaction() as owner_session:
        owner_session.clear()
    denied = client.get(receipt_path)
    assert denied.status_code == 302
    assert denied.headers["Location"] == "/tower/login"


def test_twr105_json_decision_keeps_every_execution_boundary_closed(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        json=review_form(client, path),
        headers=ORIGIN,
    )
    result = response.get_json()
    assert response.status_code == 201
    assert result["recorded"] is True
    assert result["separate_release_execution_gate_required"] is True
    for field in SAFETY_FALSE_FIELDS:
        assert result[field] is False
        assert result["receipt"][field] is False


def test_twr105_server_source_wins_over_client_supplied_packet(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    form = review_form(client, path)
    form["packet"] = {"expected_revision": "attacker-controlled"}
    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        json=form,
        headers=ORIGIN,
    )
    assert response.status_code == 201
    assert response.get_json()["receipt"]["expected_revision"] == REVISION
