
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

import tower.hosted_owner_release_review_web as release_web
import tower.hosted_owner_release_walkthrough_web as walkthrough
import tower.hosted_release_candidate_publication as publication
import tower.hosted_release_prerequisite_certification as certification
import tower.hosted_release_prerequisite_certification_web as certification_web

from tower.hosted_candidate_release_gate import (
    build_hosted_candidate_release_packet,
)

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
    "owner_session_reference": "owner-session-twr116",
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
        "critical_route_count": 14,
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
):

    app = Flask(__name__)

    app.secret_key = (
        "tower-prerequisite-certification-tests-only"
    )

    packet_path = tmp_path / "hosted-candidate.json"
    ledger_path = tmp_path / "hosted-owner-receipts.jsonl"

    app.config[
        "TOWER_HOSTED_RELEASE_PACKET_PATH"
    ] = str(packet_path)

    app.config[
        "TOWER_HOSTED_RELEASE_EXPECTED_REVISION"
    ] = REVISION

    app.config[
        "TOWER_HOSTED_RELEASE_MAX_PACKET_AGE_SECONDS"
    ] = 3600

    app.config[
        "TOWER_HOSTED_RELEASE_BASE_URL"
    ] = "https://tower.example"

    app.config[
        publication.PACKET_STORE_DURABLE_CONFIG
    ] = "true"

    monkeypatch.setenv(
        "RENDER",
        "true",
    )

    monkeypatch.setenv(
        "RENDER_GIT_COMMIT",
        REVISION,
    )

    monkeypatch.setenv(
        "TOWER_OWNER_USERNAME",
        "owner",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_PASSWORD_HASH",
        "scrypt:16384:8:1$test$hashed-owner-password",
    )

    monkeypatch.setenv(
        "TOWER_RELEASE_RECEIPT_LEDGER_PATH",
        str(ledger_path),
    )

    monkeypatch.setenv(
        "TOWER_RELEASE_RECEIPT_STORE_DURABLE",
        "true",
    )

    monkeypatch.setenv(
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        "false",
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        "test-session-secret",
    )

    @app.get("/tower/healthz")
    def tower_health():
        return "ok"

    @app.get("/tower/runtime-manifest.json")
    def tower_manifest():
        return "{}"

    @app.get("/tower/login")
    def tower_login():
        return "login"

    release_web.register_tower_owner_release_review_routes(
        app
    )

    if source:
        envelope = build_hosted_candidate_release_packet(
            parity(),
            created_at_utc=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        packet_path.write_text(
            json.dumps(envelope),
            encoding="utf-8",
        )

    client = app.test_client()

    if owner:
        with client.session_transaction() as owner_session:

            now = datetime.now(timezone.utc)

            owner_session[
                SESSION_AUTHENTICATED
            ] = True

            owner_session[
                SESSION_ROLE
            ] = OWNER_ROLE

            owner_session[
                SESSION_OWNER_ID
            ] = "simplee_owner"

            owner_session[
                SESSION_USERNAME
            ] = "owner"

            owner_session[
                SESSION_AUTH_TIME
            ] = now.isoformat()

            if elevated:
                owner_session[
                    SESSION_STEP_UP_UNTIL
                ] = (
                    now
                    + timedelta(minutes=10)
                ).isoformat()

    return (
        app,
        client,
        packet_path,
        ledger_path,
    )


def csrf_token(client):

    client.get(
        release_web.RELEASE_REVIEW_PATH
    )

    with client.session_transaction() as owner_session:
        return owner_session[
            release_web.RELEASE_CSRF_SESSION_KEY
        ]


def decision_form(
    client,
    packet_path,
    decision=APPROVE_RELEASE,
):

    packet = json.loads(
        packet_path.read_text(
            encoding="utf-8"
        )
    )["packet"]

    return {
        "csrf_token": csrf_token(client),
        "packet_integrity_hash": packet[
            "packet_integrity_hash"
        ],
        "expected_revision": packet[
            "expected_revision"
        ],
        "decision": decision,
        "reason": (
            "Owner explicitly verified the hosted "
            "release prerequisite chain."
        ),
    }


def record_decision(
    client,
    packet_path,
    decision=APPROVE_RELEASE,
):

    response = client.post(
        release_web.RELEASE_DECISION_PATH,
        data=decision_form(
            client,
            packet_path,
            decision,
        ),
        headers=ORIGIN,
    )

    assert response.status_code == 303

    return response


def inspect_verification(app):

    with app.app_context():
        return (
            certification.project_hosted_owner_verification(
                owner_context=OWNER_CONTEXT
            )
        )


def inspect_certificate(app):

    with app.app_context():
        return (
            certification.build_release_prerequisite_certificate(
                owner_context=OWNER_CONTEXT
            )
        )


def test_twr116_owner_verification_requires_fresh_verified_owner(
    monkeypatch,
    tmp_path,
):

    app, _, _, _ = build_app(
        monkeypatch,
        tmp_path,
    )

    with app.app_context():
        result = (
            certification.project_hosted_owner_verification(
                owner_context={}
            )
        )

    assert (
        result["verification_state"]
        == certification.OWNER_VERIFICATION_REQUIRED
    )

    assert result["owner_verified_for_release"] is False
    assert result["release_prerequisites_certified"] is False
    assert "checks" not in result


def test_twr116_hosted_chain_without_owner_approval_is_not_verified(
    monkeypatch,
    tmp_path,
):

    app, _, _, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    result = inspect_verification(app)

    assert (
        result["verification_state"]
        == certification.RELEASE_PREREQUISITES_NOT_CERTIFIED
    )

    assert result["owner_verified_for_release"] is False
    assert result["release_prerequisites_certified"] is False


@pytest.mark.parametrize(
    "decision",
    (
        HOLD_RELEASE,
        REJECT_RELEASE,
    ),
)
def test_twr116_hold_or_rejection_never_verifies_release_prerequisites(
    monkeypatch,
    tmp_path,
    decision,
):

    app, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
        decision,
    )

    result = inspect_verification(app)

    assert result[
        "release_prerequisites_certified"
    ] is False

    assert (
        result["verification_state"]
        == certification.RELEASE_PREREQUISITES_NOT_CERTIFIED
    )


def test_twr116_exact_approved_receipt_completes_hosted_owner_verification(
    monkeypatch,
    tmp_path,
):

    app, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    result = inspect_verification(app)

    assert result["owner_verified_for_release"] is True

    assert result[
        "release_prerequisites_certified"
    ] is True

    assert (
        result["verification_state"]
        == certification.RELEASE_PREREQUISITES_CERTIFIED_EXECUTION_LOCKED
    )

    assert result["decision"] == APPROVE_RELEASE

    assert (
        result["receipt_integrity_verified"]
        is True
    )

    assert (
        result["checks"][
            "exact_approval_receipt_verified"
        ]
        is True
    )


def test_twr116_corrupt_receipt_chain_blocks_verification(
    monkeypatch,
    tmp_path,
):

    app, client, packet_path, ledger_path = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    ledger_path.write_text(
        "corrupt\n",
        encoding="utf-8",
    )

    result = inspect_verification(app)

    assert result[
        "release_prerequisites_certified"
    ] is False


def test_twr117_certificate_is_not_issued_before_verified_approval(
    monkeypatch,
    tmp_path,
):

    app, _, _, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    result = inspect_certificate(app)

    assert result["certificate_issued"] is False
    assert result["release_execution_authorized"] is False
    assert result["staging_ready"] is False


def test_twr117_verified_approval_issues_integrity_sealed_prerequisite_certificate(
    monkeypatch,
    tmp_path,
):

    app, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    first = inspect_certificate(app)
    second = inspect_certificate(app)

    assert first["certificate_issued"] is True
    assert second["certificate_issued"] is True
    assert first["certificate"] == second["certificate"]

    certificate = first["certificate"]

    assert (
        certificate["certificate_status"]
        == "CERTIFIED_PREREQUISITES_ONLY"
    )

    assert certificate["owner_decision"] == APPROVE_RELEASE
    assert certificate["expected_revision"] == REVISION

    assert certificate["certificate_id"].startswith(
        "tower-release-prerequisite-"
    )

    assert len(
        certificate["certificate_integrity_hash"]
    ) == 64


def test_twr117_certificate_verifier_rejects_tampering(
    monkeypatch,
    tmp_path,
):

    app, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    with app.app_context():

        result = (
            certification.build_release_prerequisite_certificate(
                owner_context=OWNER_CONTEXT
            )
        )

        certificate = dict(
            result["certificate"]
        )

        certificate[
            "expected_revision"
        ] = "tampered"

        verification = (
            certification.verify_release_prerequisite_certificate(
                certificate,
                owner_context=OWNER_CONTEXT,
            )
        )

    assert verification["valid"] is False

    assert (
        "certificate_integrity_hash_mismatch"
        in verification["errors"]
    )


def test_twr117_certificate_never_opens_execution_boundaries(
    monkeypatch,
    tmp_path,
):

    app, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    result = inspect_certificate(app)

    certificate = result["certificate"]

    assert (
        certificate[
            "separate_release_execution_gate_required"
        ]
        is True
    )

    assert (
        certificate[
            "release_execution_authorized"
        ]
        is False
    )

    assert certificate["staging_ready"] is False

    for field in SAFETY_FALSE_FIELDS:
        assert certificate[field] is False


def test_twr118_prerequisite_page_requires_owner_session(
    monkeypatch,
    tmp_path,
):

    _, client, _, _ = build_app(
        monkeypatch,
        tmp_path,
        owner=False,
    )

    response = client.get(
        certification_web.PREREQUISITE_PAGE_PATH
    )

    assert response.status_code == 302

    assert (
        response.headers["Location"]
        == "/tower/login"
    )


def test_twr118_prerequisite_page_requires_step_up(
    monkeypatch,
    tmp_path,
):

    _, client, _, _ = build_app(
        monkeypatch,
        tmp_path,
        elevated=False,
    )

    response = client.get(
        certification_web.PREREQUISITE_PAGE_PATH
    )

    assert response.status_code == 302

    assert (
        response.headers["Location"]
        == release_web.RELEASE_STEP_UP_PATH
    )


def test_twr118_owner_page_is_focused_and_execution_locked(
    monkeypatch,
    tmp_path,
):

    _, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    response = client.get(
        certification_web.PREREQUISITE_PAGE_PATH
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert (
        "Release Prerequisite Certificate"
        in body
    )

    assert "Owner verification" in body
    assert "Release prerequisites" in body
    assert "Execution authority" in body
    assert "Locked" in body
    assert "View source owner receipt" in body

    assert (
        certification_web.PREREQUISITE_PAGE_MARKER
        in body
    )


def test_twr118_json_surfaces_do_not_disclose_storage_paths_or_secrets(
    monkeypatch,
    tmp_path,
):

    _, client, packet_path, ledger_path = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    text = (
        client.get(
            certification_web.PREREQUISITE_VERIFICATION_JSON_PATH
        ).get_data(
            as_text=True
        )
        +
        client.get(
            certification_web.PREREQUISITE_CERTIFICATION_JSON_PATH
        ).get_data(
            as_text=True
        )
    )

    assert str(packet_path) not in text
    assert str(ledger_path) not in text
    assert "hashed-owner-password" not in text
    assert "test-session-secret" not in text


def test_twr119_walkthrough_hands_certified_owner_to_prerequisite_certificate(
    monkeypatch,
    tmp_path,
):

    _, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    record_decision(
        client,
        packet_path,
    )

    body = client.get(
        walkthrough.HOSTED_WALKTHROUGH_PATH
    ).get_data(
        as_text=True
    )

    assert (
        "Open prerequisite certificate"
        in body
    )

    assert (
        f'href="{certification_web.PREREQUISITE_PAGE_PATH}"'
        in body
    )


def test_twr119_owner_dashboard_shows_prerequisite_certificate_state(
    monkeypatch,
    tmp_path,
):

    import tower.owner_dashboard_web as dashboard

    app, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
        source=True,
    )

    dashboard.register_tower_owner_dashboard_routes(
        app
    )

    record_decision(
        client,
        packet_path,
    )

    dashboard_body = client.get(
        "/tower/owner-dashboard"
    )

    body = dashboard_body.get_data(
        as_text=True
    )

    assert dashboard_body.status_code == 200

    assert (
        "Release prerequisite certificate"
        in body
    )

    assert (
        f'href="{certification_web.PREREQUISITE_PAGE_PATH}"'
        in body
    )

    assert (
        'data-tower-prerequisite-certificate="'
        + certification.RELEASE_PREREQUISITES_CERTIFIED_EXECUTION_LOCKED
        + '"'
    ) in body


def test_twr120_prerequisite_routes_register_once(
    monkeypatch,
    tmp_path,
):

    app, _, _, _ = build_app(
        monkeypatch,
        tmp_path,
    )

    certification_web.register_tower_release_prerequisite_certification_routes(
        app
    )

    assert (
        sum(
            rule.rule
            == certification_web.PREREQUISITE_PAGE_PATH
            for rule in app.url_map.iter_rules()
        )
        == 1
    )


def test_twr120_full_hosted_owner_verification_certificate_remains_fail_closed(
    monkeypatch,
    tmp_path,
):

    _, client, packet_path, _ = build_app(
        monkeypatch,
        tmp_path,
    )

    monkeypatch.setattr(
        publication,
        "probe_hosted_runtime",
        lambda **_: parity(),
    )

    published = client.post(
        release_web.RELEASE_PUBLICATION_PATH,
        data={
            "csrf_token": csrf_token(
                client
            )
        },
        headers=ORIGIN,
    )

    assert published.status_code == 303
    assert packet_path.is_file()

    review = client.get(
        walkthrough.HOSTED_READINESS_JSON_PATH
    ).get_json()

    assert (
        review["readiness_state"]
        == "HOSTED_AWAITING_OWNER_DECISION"
    )

    record_decision(
        client,
        packet_path,
    )

    verification = client.get(
        certification_web.PREREQUISITE_VERIFICATION_JSON_PATH
    ).get_json()

    assert (
        verification[
            "release_prerequisites_certified"
        ]
        is True
    )

    result = client.get(
        certification_web.PREREQUISITE_CERTIFICATION_JSON_PATH
    ).get_json()

    assert result["certificate_issued"] is True

    assert (
        result["release_execution_authorized"]
        is False
    )

    assert result["staging_ready"] is False

    assert (
        result[
            "separate_release_execution_gate_required"
        ]
        is True
    )

    for field in SAFETY_FALSE_FIELDS:
        assert result[field] is False
        assert result["certificate"][field] is False
