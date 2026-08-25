
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

import tower.hosted_owner_release_readiness as readiness
import tower.hosted_owner_release_review_web as release_web
import tower.hosted_owner_release_walkthrough_web as walkthrough
import tower.hosted_release_candidate_publication as publication
from tower.hosted_candidate_release_gate import build_hosted_candidate_release_packet
from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
    SAFETY_FALSE_FIELDS,
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
OWNER_CONTEXT = {
    "owner_id": "simplee_owner",
    "owner_session_reference": "owner-session-twr111",
    "owner_role": "owner",
    "owner_verified": True,
    "session_active": True,
    "session_fresh": True,
    "step_up_verified": True,
}


def parity():
    return {
        "status": "tower_hosted_candidate_parity_pass",
        "parity_pass": True,
        "expected_revision": REVISION,
        "actual_revision": REVISION,
        "entrypoint": "web.managed_staging:app",
        "critical_route_count": 11,
        "checks": {
            "expected_revision_valid": True,
            "health_http_200": True,
            "manifest_http_200": True,
            "exact_candidate_revision_match": True,
            "all_critical_routes_present": True,
        },
        "failures": [],
        "deployment_authorized": False,
        "production_promotion_authorized": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "staging_ready_changed": False,
    }


def build_app(
    monkeypatch,
    tmp_path,
    *,
    source=False,
    owner=True,
    elevated=True,
    hosted=True,
    core_routes=True,
    age_seconds=0,
):
    app = Flask(__name__)
    app.secret_key = "tower-hosted-owner-readiness-tests-only"
    packet_path = tmp_path / "hosted-candidate.json"
    ledger_path = tmp_path / "hosted-owner-receipts.jsonl"
    app.config["TOWER_HOSTED_RELEASE_PACKET_PATH"] = str(packet_path)
    app.config["TOWER_HOSTED_RELEASE_EXPECTED_REVISION"] = REVISION
    app.config["TOWER_HOSTED_RELEASE_MAX_PACKET_AGE_SECONDS"] = 3600
    app.config["TOWER_HOSTED_RELEASE_BASE_URL"] = "https://tower.example"
    app.config[publication.PACKET_STORE_DURABLE_CONFIG] = "true"

    monkeypatch.setenv("TOWER_OWNER_USERNAME", "owner")
    monkeypatch.setenv("TOWER_OWNER_PASSWORD_HASH", "scrypt:16384:8:1$test$hashed-owner-password")
    monkeypatch.setenv("TOWER_RELEASE_RECEIPT_LEDGER_PATH", str(ledger_path))
    monkeypatch.setenv("TOWER_RELEASE_RECEIPT_STORE_DURABLE", "true")
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "false")
    if hosted:
        monkeypatch.setenv("RENDER", "true")
        monkeypatch.setenv("RENDER_GIT_COMMIT", REVISION)
    else:
        monkeypatch.delenv("RENDER", raising=False)
        monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)

    if core_routes:
        @app.get("/tower/healthz")
        def tower_health():
            return "ok"

        @app.get("/tower/runtime-manifest.json")
        def tower_manifest():
            return "{}"

        @app.get("/tower/login")
        def tower_login():
            return "login"

    release_web.register_tower_owner_release_review_routes(app)

    if source:
        created_at = (datetime.now(timezone.utc) - timedelta(seconds=age_seconds)).isoformat()
        envelope = build_hosted_candidate_release_packet(parity(), created_at_utc=created_at)
        packet_path.write_text(json.dumps(envelope), encoding="utf-8")

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
                owner_session[SESSION_STEP_UP_UNTIL] = (now + timedelta(minutes=10)).isoformat()

    return app, client, packet_path, ledger_path


def inspect_readiness(app):
    with app.app_context():
        return readiness.project_hosted_owner_release_readiness(owner_context=OWNER_CONTEXT)


def blocker_codes(result):
    return {item["code"] for item in result.get("blockers", [])}


def csrf_token(client):
    client.get(release_web.RELEASE_REVIEW_PATH)
    with client.session_transaction() as owner_session:
        return owner_session[release_web.RELEASE_CSRF_SESSION_KEY]


def decision_form(client, path, decision=APPROVE_RELEASE):
    packet = json.loads(path.read_text(encoding="utf-8"))["packet"]
    return {
        "csrf_token": csrf_token(client),
        "packet_integrity_hash": packet["packet_integrity_hash"],
        "expected_revision": packet["expected_revision"],
        "decision": decision,
        "reason": "Owner explicitly reviewed the genuine hosted candidate.",
    }


def test_twr111_readiness_details_require_verified_owner(monkeypatch, tmp_path):
    app, _, packet_path, ledger_path = build_app(monkeypatch, tmp_path)
    with app.app_context():
        result = readiness.project_hosted_owner_release_readiness(owner_context={})
    assert result["readiness_state"] == readiness.OWNER_VERIFICATION_REQUIRED
    assert "checks" not in result
    assert "hosted_host" not in result
    assert str(packet_path) not in json.dumps(result)
    assert str(ledger_path) not in json.dumps(result)


def test_twr111_local_runtime_is_not_hosted_ready(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path, hosted=False)
    result = inspect_readiness(app)
    assert result["hosted_configuration_ready"] is False
    assert "hosted_runtime_detected" in blocker_codes(result)


@pytest.mark.parametrize("invalid_url", ("http://tower.example", "https://secret@tower.example", "https://tower.example/private"))
def test_twr111_invalid_hosted_endpoint_blocks_readiness(monkeypatch, tmp_path, invalid_url):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    app.config["TOWER_HOSTED_RELEASE_BASE_URL"] = invalid_url
    result = inspect_readiness(app)
    assert "hosted_https_endpoint_configured" in blocker_codes(result)
    assert result["hosted_configuration_ready"] is False


def test_twr111_wrong_deployed_revision_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setenv("RENDER_GIT_COMMIT", "wrong-revision")
    result = inspect_readiness(app)
    assert "exact_deployed_revision_confirmed" in blocker_codes(result)


def test_twr111_missing_packet_durability_confirmation_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    app.config[publication.PACKET_STORE_DURABLE_CONFIG] = "false"
    result = inspect_readiness(app)
    assert "durable_packet_store_configured" in blocker_codes(result)


def test_twr111_missing_packet_parent_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    app.config["TOWER_HOSTED_RELEASE_PACKET_PATH"] = str(tmp_path / "missing-parent" / "packet.json")
    result = inspect_readiness(app)
    assert "durable_packet_store_usable" in blocker_codes(result)


def test_twr111_packet_store_symlink_blocks_readiness(monkeypatch, tmp_path):
    app, _, packet_path, _ = build_app(monkeypatch, tmp_path)
    target = tmp_path / "protected.json"
    target.write_text("protected", encoding="utf-8")
    packet_path.symlink_to(target)
    result = inspect_readiness(app)
    assert "durable_packet_store_usable" in blocker_codes(result)
    assert target.read_text(encoding="utf-8") == "protected"


def test_twr111_missing_receipt_durability_confirmation_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setenv("TOWER_RELEASE_RECEIPT_STORE_DURABLE", "false")
    result = inspect_readiness(app)
    assert "durable_receipt_store_configured" in blocker_codes(result)


def test_twr111_missing_receipt_path_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.delenv("TOWER_RELEASE_RECEIPT_LEDGER_PATH")
    result = inspect_readiness(app)
    assert "durable_receipt_store_configured" in blocker_codes(result)
    assert "durable_receipt_store_usable" in blocker_codes(result)


def test_twr111_packet_and_receipt_store_must_be_distinct(monkeypatch, tmp_path):
    app, _, packet_path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setenv("TOWER_RELEASE_RECEIPT_LEDGER_PATH", str(packet_path))
    result = inspect_readiness(app)
    assert "packet_and_receipt_stores_distinct" in blocker_codes(result)


def test_twr111_hosted_owner_requires_hashed_password(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.delenv("TOWER_OWNER_PASSWORD_HASH")
    result = inspect_readiness(app)
    assert "owner_password_hash_configured" in blocker_codes(result)


def test_twr111_hosted_owner_rejects_local_walkthrough_mode(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    result = inspect_readiness(app)
    assert "local_walkthrough_mode_disabled" in blocker_codes(result)


def test_twr111_missing_owner_username_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.delenv("TOWER_OWNER_USERNAME")
    result = inspect_readiness(app)
    assert "owner_username_configured" in blocker_codes(result)


def test_twr111_missing_critical_identity_routes_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path, core_routes=False)
    result = inspect_readiness(app)
    assert "critical_owner_routes_present" in blocker_codes(result)


def test_twr111_open_managed_safety_boundary_blocks_readiness(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(readiness, "_managed_safety_closed", lambda: False)
    result = inspect_readiness(app)
    assert "execution_boundaries_closed" in blocker_codes(result)


def test_twr111_readiness_never_exposes_paths_hashes_or_secrets(monkeypatch, tmp_path):
    app, _, packet_path, ledger_path = build_app(monkeypatch, tmp_path)
    monkeypatch.setenv("TOWER_SESSION_SECRET", "ultra-private-owner-session-secret")
    result = inspect_readiness(app)
    text = json.dumps(result, sort_keys=True)
    assert str(packet_path) not in text
    assert str(ledger_path) not in text
    assert "hashed-owner-password" not in text
    assert "ultra-private-owner-session-secret" not in text


def test_twr112_owner_walkthrough_requires_owner_session(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, owner=False)
    response = client.get(walkthrough.HOSTED_WALKTHROUGH_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == "/tower/login"


def test_twr112_owner_walkthrough_requires_tower_step_up(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, elevated=False)
    response = client.get(walkthrough.HOSTED_WALKTHROUGH_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == release_web.RELEASE_STEP_UP_PATH
    assert "observatory" not in response.headers["Location"].lower()


def test_twr112_owner_walkthrough_uses_focused_cards_and_next_action(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path)
    response = client.get(walkthrough.HOSTED_WALKTHROUGH_PATH)
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Hosted Release Readiness" in body
    assert "Hosted identity" in body
    assert "Durable owner storage" in body
    assert "Your next move" in body
    assert "Run genuine hosted candidate check" in body
    assert "remain locked" in body
    assert walkthrough.HOSTED_WALKTHROUGH_MARKER in body


def test_twr112_blocked_walkthrough_shows_real_owner_action(monkeypatch, tmp_path):
    app, client, _, _ = build_app(monkeypatch, tmp_path)
    app.config[publication.PACKET_STORE_DURABLE_CONFIG] = "false"
    body = client.get(walkthrough.HOSTED_WALKTHROUGH_PATH).get_data(as_text=True)
    assert "Needs attention" in body
    assert "durable hosted candidate-packet storage" in body
    assert "Run genuine hosted candidate check" not in body


def test_twr112_existing_owner_dashboard_links_to_hosted_readiness(monkeypatch, tmp_path):
    import tower.owner_dashboard_web as dashboard

    app, client, _, _ = build_app(monkeypatch, tmp_path)
    dashboard.register_tower_owner_dashboard_routes(app)
    body = client.get("/tower/owner-dashboard").get_data(as_text=True)
    assert "Hosted readiness" in body
    assert 'href="/tower/owner/release-review/walkthrough"' in body
    assert 'data-tower-hosted-readiness="HOSTED_AWAITING_CANDIDATE"' in body


def test_twr112_readiness_routes_register_once(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    walkthrough.register_tower_hosted_owner_walkthrough_routes(app)
    assert sum(rule.rule == walkthrough.HOSTED_WALKTHROUGH_PATH for rule in app.url_map.iter_rules()) == 1


def test_twr113_valid_hosted_configuration_waits_for_real_candidate(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    result = inspect_readiness(app)
    assert result["hosted_configuration_ready"] is True
    assert result["readiness_state"] == readiness.HOSTED_AWAITING_CANDIDATE
    assert result["staging_prerequisites_certified"] is False


def test_twr113_genuine_publication_advances_to_owner_review(monkeypatch, tmp_path):
    _, client, packet_path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())
    published = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        data={"csrf_token": csrf_token(client)},
        headers=ORIGIN,
    )
    assert published.status_code == 303
    assert packet_path.is_file()
    result = client.get(walkthrough.HOSTED_READINESS_JSON_PATH).get_json()
    assert result["readiness_state"] == readiness.HOSTED_AWAITING_OWNER_DECISION
    assert result["owner_walkthrough_complete"] is False


def test_twr113_expired_same_revision_does_not_promise_impossible_republication(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path, source=True, age_seconds=7200)
    result = inspect_readiness(app)
    assert result["readiness_state"] == readiness.HOSTED_READINESS_BLOCKED
    assert "candidate_expired_same_revision_replay_blocked" in blocker_codes(result)
    assert "distinct deployed revision" in result["owner_next_action"]


def test_twr113_readiness_endpoint_requires_owner(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, owner=False)
    response = client.get(walkthrough.HOSTED_READINESS_JSON_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == "/tower/login"


def test_twr113_readiness_endpoint_never_leaks_durable_paths(monkeypatch, tmp_path):
    _, client, packet_path, ledger_path = build_app(monkeypatch, tmp_path)
    text = client.get(walkthrough.HOSTED_READINESS_JSON_PATH).get_data(as_text=True)
    assert str(packet_path) not in text
    assert str(ledger_path) not in text


def test_twr114_review_without_owner_decision_is_not_certified(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, source=True)
    result = client.get(walkthrough.HOSTED_CERTIFICATION_JSON_PATH).get_json()
    assert result["certified"] is False
    assert result["readiness_state"] == readiness.HOSTED_AWAITING_OWNER_DECISION
    assert result["receipt_id"] is None


@pytest.mark.parametrize(
    "decision_result",
    (
        (APPROVE_RELEASE, readiness.HOSTED_OWNER_APPROVED_CERTIFIED, True),
        (HOLD_RELEASE, readiness.HOSTED_OWNER_HOLD_RECORDED, False),
        (REJECT_RELEASE, readiness.HOSTED_OWNER_REJECTION_RECORDED, False),
    ),
)
def test_twr114_owner_decisions_project_exact_hosted_outcome(monkeypatch, tmp_path, decision_result):
    decision, expected_state, expected_certified = decision_result
    _, client, path, _ = build_app(monkeypatch, tmp_path, source=True)
    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(client, path, decision),
        headers=ORIGIN,
    )
    assert response.status_code == 303
    result = client.get(walkthrough.HOSTED_READINESS_JSON_PATH).get_json()
    assert result["readiness_state"] == expected_state
    assert result["owner_walkthrough_complete"] is True
    assert result["staging_prerequisites_certified"] is expected_certified
    assert result["receipt_id"]


def test_twr114_corrupt_receipt_chain_blocks_hosted_readiness(monkeypatch, tmp_path):
    app, _, _, ledger = build_app(monkeypatch, tmp_path, source=True)
    ledger.write_text("invalid-receipt-chain\n", encoding="utf-8")
    result = inspect_readiness(app)
    assert result["hosted_configuration_ready"] is False
    assert "candidate_or_receipt_integrity_unavailable" in blocker_codes(result)


def test_twr114_approved_walkthrough_links_to_verified_receipt(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path, source=True)
    client.post(release_web.RELEASE_DECISION_PATH, data=decision_form(client, path), headers=ORIGIN)
    body = client.get(walkthrough.HOSTED_WALKTHROUGH_PATH).get_data(as_text=True)
    assert "View verified owner receipt" in body
    assert "Verified" in body
    assert "Run genuine hosted candidate check" not in body


def test_twr115_verified_owner_approval_certifies_prerequisites_only(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path, source=True)
    client.post(release_web.RELEASE_DECISION_PATH, data=decision_form(client, path), headers=ORIGIN)
    result = client.get(walkthrough.HOSTED_CERTIFICATION_JSON_PATH).get_json()
    assert result["certified"] is True
    assert result["staging_prerequisites_certified"] is True
    assert result["separate_release_execution_gate_required"] is True
    assert result["staging_ready"] is False
    for field in SAFETY_FALSE_FIELDS:
        assert result[field] is False


@pytest.mark.parametrize("decision", (HOLD_RELEASE, REJECT_RELEASE))
def test_twr115_hold_or_reject_never_certifies_staging(monkeypatch, tmp_path, decision):
    _, client, path, _ = build_app(monkeypatch, tmp_path, source=True)
    client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(client, path, decision),
        headers=ORIGIN,
    )
    result = client.get(walkthrough.HOSTED_CERTIFICATION_JSON_PATH).get_json()
    assert result["certified"] is False
    assert result["staging_prerequisites_certified"] is False
    assert result["staging_ready"] is False


def test_twr115_certification_endpoint_is_owner_only(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, owner=False)
    response = client.get(walkthrough.HOSTED_CERTIFICATION_JSON_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == "/tower/login"


def test_twr115_full_hosted_owner_walkthrough_remains_execution_locked(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())

    before = client.get(walkthrough.HOSTED_READINESS_JSON_PATH).get_json()
    assert before["readiness_state"] == readiness.HOSTED_AWAITING_CANDIDATE

    published = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        data={"csrf_token": csrf_token(client)},
        headers=ORIGIN,
    )
    assert published.status_code == 303

    review = client.get(walkthrough.HOSTED_READINESS_JSON_PATH).get_json()
    assert review["readiness_state"] == readiness.HOSTED_AWAITING_OWNER_DECISION

    decision = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(client, path),
        headers=ORIGIN,
    )
    assert decision.status_code == 303

    certified = client.get(walkthrough.HOSTED_CERTIFICATION_JSON_PATH).get_json()
    assert certified["certified"] is True
    assert certified["owner_walkthrough_complete"] is True
    assert certified["staging_ready"] is False
    for field in SAFETY_FALSE_FIELDS:
        assert certified[field] is False
