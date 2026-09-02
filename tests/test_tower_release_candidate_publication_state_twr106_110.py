
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

import tower.hosted_owner_release_candidate_state as candidate_state
import tower.hosted_owner_release_review_web as release_web
import tower.hosted_release_candidate_publication as publication
from tower.hosted_candidate_release_gate import (
    build_hosted_candidate_release_packet,
    verify_hosted_candidate_release_packet,
)
from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
    SAFETY_FALSE_FIELDS,
    record_owner_release_decision,
)
from tower.hosted_release_packet_provider import load_canonical_release_packet
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
    "owner_session_reference": "owner-session-twr106",
    "owner_role": "owner",
    "owner_verified": True,
    "session_active": True,
    "session_fresh": True,
    "step_up_verified": True,
}


def parity(*, passing=True, revision=REVISION):
    return {
        "status": "tower_hosted_candidate_parity_pass" if passing else "tower_hosted_candidate_parity_fail",
        "parity_pass": passing,
        "expected_revision": revision,
        "actual_revision": revision,
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


def build_app(monkeypatch, tmp_path, *, source=False, owner=True, elevated=True, age_seconds=0):
    app = Flask(__name__)
    app.secret_key = "tower-candidate-publication-tests-only"
    packet_path = tmp_path / "hosted-candidate.json"
    ledger_path = tmp_path / "owner-receipts.jsonl"
    app.config["TOWER_HOSTED_RELEASE_PACKET_PATH"] = str(packet_path)
    app.config["TOWER_HOSTED_RELEASE_EXPECTED_REVISION"] = REVISION
    app.config["TOWER_HOSTED_RELEASE_MAX_PACKET_AGE_SECONDS"] = 3600
    app.config["TOWER_HOSTED_RELEASE_BASE_URL"] = "https://tower.example"

    monkeypatch.setenv("TOWER_OWNER_USERNAME", "owner")
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    monkeypatch.setenv("TOWER_LOCAL_OWNER_PASSWORD", "test-owner-password")
    monkeypatch.setenv("TOWER_RELEASE_RECEIPT_LEDGER_PATH", str(ledger_path))
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    monkeypatch.delenv(publication.PACKET_STORE_DURABLE_CONFIG, raising=False)

    if source:
        created = (datetime.now(timezone.utc) - timedelta(seconds=age_seconds)).isoformat()
        packet = build_hosted_candidate_release_packet(parity(), created_at_utc=created)
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
                owner_session[SESSION_STEP_UP_UNTIL] = (now + timedelta(minutes=10)).isoformat()
    return app, client, packet_path, ledger_path


def csrf_token(client):
    client.get(release_web.RELEASE_REVIEW_PATH)
    with client.session_transaction() as owner_session:
        return owner_session[release_web.RELEASE_CSRF_SESSION_KEY]


def decision_form(client, packet_path, decision=APPROVE_RELEASE):
    token = csrf_token(client)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))["packet"]
    return {
        "csrf_token": token,
        "packet_integrity_hash": packet["packet_integrity_hash"],
        "expected_revision": packet["expected_revision"],
        "decision": decision,
        "reason": "Owner reviewed the genuine hosted release candidate.",
    }


def test_twr106_publication_uses_genuine_hosted_probe(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    observed = {}

    def genuine_probe(*, base_url, expected_revision):
        observed.update(base_url=base_url, expected_revision=expected_revision)
        return parity()

    monkeypatch.setattr(publication, "probe_hosted_runtime", genuine_probe)
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
        loaded = load_canonical_release_packet()

    assert result["published"] is True
    assert observed == {"base_url": "https://tower.example", "expected_revision": REVISION}
    assert path.is_file()
    assert loaded["reviewable"] is True
    assert verify_hosted_candidate_release_packet(loaded["packet"])["valid"] is True


@pytest.mark.parametrize("invalid_url", ("http://tower.example", "https://secret@tower.example", "https://tower.example/path"))
def test_twr106_noncanonical_or_insecure_host_is_rejected(monkeypatch, tmp_path, invalid_url):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    app.config["TOWER_HOSTED_RELEASE_BASE_URL"] = invalid_url
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["published"] is False
    assert result["reason"] == "hosted_release_base_url_invalid"
    assert not path.exists()


def test_twr106_missing_server_host_fails_closed(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    app.config["TOWER_HOSTED_RELEASE_BASE_URL"] = ""
    monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["reason"] == "hosted_release_base_url_not_configured"
    assert not path.exists()


def test_twr106_failed_parity_never_creates_candidate(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity(passing=False))
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["published"] is False
    assert result["reason"] == "hosted_runtime_parity_failed"
    assert not path.exists()


def test_twr106_wrong_revision_never_replaces_existing_packet(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path, source=True)
    before = path.read_bytes()
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity(revision="other-revision"))
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["reason"] == "hosted_runtime_parity_failed"
    assert path.read_bytes() == before


def test_twr106_open_safety_boundary_blocks_publication(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    unsafe = parity()
    unsafe["capital_movement_authorized"] = True
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: unsafe)
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["reason"] == "hosted_runtime_parity_failed"
    assert not path.exists()


def test_twr107_publication_is_atomic_and_sealed(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert result["published"] is True
    assert envelope["publication"]["genuine_hosted_probe_required"] is True
    assert envelope["publication"]["source_host"] == "tower.example"
    assert envelope["publication"]["expected_revision"] == REVISION
    assert verify_hosted_candidate_release_packet(envelope["packet"])["valid"] is True
    assert not list(tmp_path.glob(".tower-release-candidate-*.tmp"))


def test_twr107_same_revision_cannot_replace_published_candidate(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())
    with app.app_context():
        first = publication.publish_hosted_release_candidate()
        before = path.read_bytes()
        second = publication.publish_hosted_release_candidate()
    assert first["published"] is True
    assert second["published"] is False
    assert second["reason"] == "candidate_revision_already_published"
    assert path.read_bytes() == before


def test_twr107_failed_atomic_replace_preserves_prior_packet(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path, source=True)
    before = path.read_bytes()
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())

    def reject_replace(*args, **kwargs):
        raise OSError("simulated atomic replacement failure")

    monkeypatch.setattr(publication.os, "replace", reject_replace)
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["reason"] == "candidate_publication_persistence_failed"
    assert path.read_bytes() == before
    assert not list(tmp_path.glob(".tower-release-candidate-*.tmp"))


def test_twr107_symlink_destination_is_rejected(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    target = tmp_path / "protected-target.json"
    target.write_text("do not touch", encoding="utf-8")
    path.symlink_to(target)
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["reason"] == "packet_publication_symlink_rejected"
    assert target.read_text(encoding="utf-8") == "do not touch"


def test_twr107_hosted_runtime_requires_confirmed_durable_store(monkeypatch, tmp_path):
    app, _, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setenv("RENDER", "true")
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["reason"] == "packet_durable_storage_not_configured"
    assert not path.exists()


def test_twr108_owner_context_required_for_candidate_state(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context={})
    assert result["candidate_state"] == candidate_state.OWNER_VERIFICATION_REQUIRED
    assert "expected_revision" not in result


def test_twr108_missing_candidate_projects_no_candidate(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context=OWNER_CONTEXT)
    assert result["candidate_state"] == candidate_state.NO_CANDIDATE


def test_twr108_expired_candidate_projects_stale(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path, source=True, age_seconds=7200)
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context=OWNER_CONTEXT)
    assert result["candidate_state"] == candidate_state.STALE_CANDIDATE


def test_twr108_changed_revision_projects_candidate_changed(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path, source=True)
    app.config["TOWER_HOSTED_RELEASE_EXPECTED_REVISION"] = "changed"
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context=OWNER_CONTEXT)
    assert result["candidate_state"] == candidate_state.CANDIDATE_CHANGED


def test_twr108_sealed_candidate_projects_ready(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path, source=True)
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context=OWNER_CONTEXT)
    assert result["candidate_state"] == candidate_state.READY_FOR_OWNER_REVIEW
    assert result["owner_decision_recorded"] is False


@pytest.mark.parametrize(
    "decision_state",
    (
        (APPROVE_RELEASE, candidate_state.OWNER_APPROVED),
        (HOLD_RELEASE, candidate_state.OWNER_HELD),
        (REJECT_RELEASE, candidate_state.OWNER_REJECTED),
    ),
)
def test_twr108_exact_verified_receipt_projects_owner_decision(monkeypatch, tmp_path, decision_state):
    decision, expected_state = decision_state
    app, _, path, _ = build_app(monkeypatch, tmp_path, source=True)
    packet = json.loads(path.read_text(encoding="utf-8"))["packet"]
    saved = record_owner_release_decision(
        packet,
        owner_context=OWNER_CONTEXT,
        decision=decision,
        reason="Owner explicitly reviewed this exact candidate.",
    )
    assert saved["recorded"] is True
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context=OWNER_CONTEXT)
    assert result["candidate_state"] == expected_state
    assert result["owner_decision_recorded"] is True
    assert result["receipt_integrity_verified"] is True
    assert result["receipt_id"] == saved["receipt"]["receipt_id"]


def test_twr108_corrupt_receipt_ledger_blocks_decision_state(monkeypatch, tmp_path):
    app, _, _, ledger = build_app(monkeypatch, tmp_path, source=True)
    ledger.write_text("not-valid-json\n", encoding="utf-8")
    with app.app_context():
        result = candidate_state.project_owner_release_candidate_state(owner_context=OWNER_CONTEXT)
    assert result["candidate_state"] == candidate_state.DECISION_STATE_UNAVAILABLE


def test_twr109_dashboard_displays_dynamic_candidate_status(monkeypatch, tmp_path):
    import tower.owner_dashboard_web as dashboard

    app, client, _, _ = build_app(monkeypatch, tmp_path, source=True)
    dashboard.register_tower_owner_dashboard_routes(app)
    body = client.get("/tower/owner-dashboard").get_data(as_text=True)
    assert "Ready for your review" in body
    assert 'data-tower-release-state="READY_FOR_OWNER_REVIEW"' in body


def test_twr109_decided_review_room_shows_receipt_without_decision_buttons(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path, source=True)
    submitted = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(client, path),
        headers=ORIGIN,
    )
    assert submitted.status_code == 303
    body = client.get(release_web.RELEASE_REVIEW_PATH).get_data(as_text=True)
    assert "Decision recorded" in body
    assert "View verified receipt" in body
    assert "Approve candidate" not in body
    assert "Still locked" in body


def test_twr109_republishing_decided_revision_cannot_create_new_decision(monkeypatch, tmp_path):
    app, client, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())
    with app.app_context():
        assert publication.publish_hosted_release_candidate()["published"] is True
    submitted = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(client, path),
        headers=ORIGIN,
    )
    assert submitted.status_code == 303
    token = csrf_token(client)
    repeated = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        json={"csrf_token": token},
        headers=ORIGIN,
    )
    assert repeated.status_code == 422
    assert repeated.get_json()["reason"] == "candidate_revision_already_published"
    state = client.get(release_web.RELEASE_STATE_PATH).get_json()
    assert state["candidate_state"] == candidate_state.OWNER_APPROVED


def test_twr109_publication_route_requires_owner_step_up(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, elevated=False)
    response = client.post(release_web.RELEASE_PUBLICATION_PATH, data={}, headers=ORIGIN)
    assert response.status_code == 302
    assert response.headers["Location"] == release_web.RELEASE_STEP_UP_PATH


def test_twr109_publication_route_rejects_missing_csrf(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path)
    response = client.post(release_web.RELEASE_PUBLICATION_PATH, data={}, headers=ORIGIN)
    assert response.status_code == 403


def test_twr109_publication_route_rejects_cross_origin(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path)
    token = csrf_token(client)
    response = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        data={"csrf_token": token},
        headers={"Origin": "https://attacker.invalid"},
    )
    assert response.status_code == 403


def test_twr109_browser_cannot_override_server_host_or_revision(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    observed = {}

    def genuine_probe(*, base_url, expected_revision):
        observed.update(base_url=base_url, expected_revision=expected_revision)
        return parity()

    monkeypatch.setattr(publication, "probe_hosted_runtime", genuine_probe)
    response = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        json={
            "csrf_token": csrf_token(client),
            "base_url": "https://attacker.invalid",
            "expected_revision": "attacker-controlled",
            "parity": {"parity_pass": True},
        },
        headers=ORIGIN,
    )
    assert response.status_code == 201
    assert observed == {"base_url": "https://tower.example", "expected_revision": REVISION}
    assert json.loads(path.read_text(encoding="utf-8"))["packet"]["expected_revision"] == REVISION


def test_twr110_end_to_end_genuine_candidate_owner_decision_and_receipt(monkeypatch, tmp_path):
    _, client, path, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())

    waiting = client.get(release_web.RELEASE_REVIEW_PATH).get_data(as_text=True)
    assert "NO REVIEWABLE CANDIDATE" in waiting
    assert "Check hosted candidate" in waiting

    published = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        data={"csrf_token": csrf_token(client)},
        headers=ORIGIN,
    )
    assert published.status_code == 303
    assert published.headers["Location"] == release_web.RELEASE_REVIEW_PATH

    review = client.get(release_web.RELEASE_REVIEW_PATH).get_data(as_text=True)
    assert "Approve candidate" in review

    decision = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(client, path),
        headers=ORIGIN,
    )
    assert decision.status_code == 303

    state = client.get(release_web.RELEASE_STATE_PATH).get_json()
    assert state["candidate_state"] == candidate_state.OWNER_APPROVED
    assert state["receipt_integrity_verified"] is True
    for field in SAFETY_FALSE_FIELDS:
        assert state[field] is False

    receipt = client.get(decision.headers["Location"]).get_data(as_text=True)
    assert "Decision recorded" in receipt
    assert "Verified" in receipt
    assert "Still locked" in receipt


def test_twr110_state_endpoint_is_owner_only(monkeypatch, tmp_path):
    _, client, _, _ = build_app(monkeypatch, tmp_path, owner=False)
    response = client.get(release_web.RELEASE_STATE_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == "/tower/login"


def test_twr110_publication_never_opens_execution_boundaries(monkeypatch, tmp_path):
    app, _, _, _ = build_app(monkeypatch, tmp_path)
    monkeypatch.setattr(publication, "probe_hosted_runtime", lambda **_: parity())
    with app.app_context():
        result = publication.publish_hosted_release_candidate()
    assert result["published"] is True
    assert result["separate_release_execution_gate_required"] is True
    for field in SAFETY_FALSE_FIELDS:
        assert result[field] is False
