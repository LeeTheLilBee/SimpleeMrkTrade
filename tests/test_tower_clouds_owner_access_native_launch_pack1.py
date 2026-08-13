
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Flask

from tower.tower_clouds_intake_contract import (
    APP_ID,
    CANONICAL_BOUNDARY_STATE,
    CANONICAL_DELIVERY_STATE,
    CANONICAL_OWNER_ROUTE,
    CANONICAL_OWNER_SERVICE_GETTER,
    CANONICAL_OWNER_SURFACE,
    TOWER_INTAKE_PACKAGE_VERSION,
    build_canonical_clouds_boundary_record,
    build_canonical_tower_intake_package,
    validate_clouds_handoff_boundary_record,
    validate_tower_clouds_intake_package,
)

from tower.tower_clouds_native_launch import (
    CANONICAL_VISIBLE_LABELS,
    CANONICAL_WALKTHROUGH_LABELS,
    CLOUDS_ACCESS_PATH,
    CLOUDS_CONTRACT_JSON_PATH,
    CLOUDS_HOME_PATH,
    CLOUDS_RETURN_JSON_PATH,
    CLOUDS_RETURN_PATH,
    CLOUDS_STEP_UP_PATH,
    OWNER_ROLE,
    SESSION_AUTHENTICATED,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_TOWER_CLOUDS_BOUNDARY_RECORD,
    SESSION_TOWER_CLOUDS_INTAKE_PACKAGE,
    SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF,
    SESSION_TOWER_CLOUDS_LAUNCH_RECEIPT,
    SESSION_TOWER_CLOUDS_RETURN_RECEIPT,
    SESSION_USERNAME,
    TOWER_ACCESS_HOME_PATH,
    register_tower_clouds_native_launch,
)


def _app():
    app = Flask(__name__)
    app.secret_key = "test-secret"

    @app.get(TOWER_ACCESS_HOME_PATH)
    def access_home():
        return """
        <html>
          <body>
            <main>
              <h1>Tower Access Home</h1>
            </main>
          </body>
        </html>
        """

    @app.get("/tower/login")
    def login():
        return "login", 200

    register_tower_clouds_native_launch(app)
    return app


def _owner_session(client, *, step_up: bool = False):
    with client.session_transaction() as data:
        data[SESSION_AUTHENTICATED] = True
        data[SESSION_ROLE] = OWNER_ROLE
        data[SESSION_OWNER_ID] = "owner_solice"
        data[SESSION_USERNAME] = "solice"

        if step_up:
            data[SESSION_STEP_UP_UNTIL] = (
                datetime.now(timezone.utc) + timedelta(minutes=15)
            ).isoformat()


def test_gp016_canonical_tower_intake_package_validates():
    package = build_canonical_tower_intake_package(submission_id="abc123")
    validation = validate_tower_clouds_intake_package(package)

    assert validation.valid is True
    assert package["package_id"] == "tower-intake-abc123"
    assert package["package_version"] == TOWER_INTAKE_PACKAGE_VERSION
    assert package["destination_id"] == APP_ID
    assert package["open_route"] == CANONICAL_OWNER_ROUTE
    assert package["requires_owner_permission"] is True
    assert package["requires_step_up"] is True
    assert package["downstream_execution_performed"] is False


def test_gp016_rejects_noncanonical_guessed_fields_shape():
    package = {
        "package_id": "clouds-gp016-gp017-owner-intake",
        "source_app": "clouds",
        "source_packs": ["GP016", "GP017"],
        "clouds_surface": "owner_command_today_surface",
    }

    validation = validate_tower_clouds_intake_package(package)

    assert validation.valid is False
    assert "package_version_must_be_clouds_gp016_v1" in validation.errors
    assert "open_route_must_be_clouds" in validation.errors


def test_gp017_canonical_boundary_record_validates():
    package = build_canonical_tower_intake_package()
    boundary = build_canonical_clouds_boundary_record(package=package)
    validation = validate_clouds_handoff_boundary_record(boundary)

    assert validation.valid is True
    assert boundary["boundary_state"] == CANONICAL_BOUNDARY_STATE
    assert boundary["delivery_state"] == CANONICAL_DELIVERY_STATE
    assert boundary["tower_authority_required"] is True
    assert boundary["handoff_executed"] is False
    assert boundary["downstream_execution_performed"] is False


def test_contract_json_exposes_canonical_clouds_names():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    response = client.get(CLOUDS_CONTRACT_JSON_PATH)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["app_id"] == "clouds"
    assert payload["app_name"] == "The Clouds"
    assert payload["owner_route"] == "/clouds"
    assert payload["owner_surface"] == CANONICAL_OWNER_SURFACE
    assert payload["owner_service_getter"] == CANONICAL_OWNER_SERVICE_GETTER
    assert payload["clouds_gp024_preexisting_session_handoff_key"] is None
    assert payload["tower_integration_session_handoff_key"] == SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF
    assert payload["clouds_executes_navigation"] is False
    assert payload["downstream_execution_performed"] is False


def test_clouds_launch_requires_owner_session():
    app = _app()
    client = app.test_client()

    response = client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)

    assert response.status_code in {302, 401, 403}


def test_clouds_launch_requires_step_up_before_handoff():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=False)

    response = client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)

    assert response.status_code == 302
    assert CLOUDS_STEP_UP_PATH in response.headers["Location"]

    with client.session_transaction() as data:
        assert SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF not in data


def test_clouds_launch_persists_explicit_tower_integration_handoff():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    response = client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == CLOUDS_HOME_PATH

    with client.session_transaction() as data:
        assert data[SESSION_TOWER_CLOUDS_INTAKE_PACKAGE]["package_version"] == "clouds-gp016-v1"
        assert data[SESSION_TOWER_CLOUDS_BOUNDARY_RECORD]["boundary_state"] == "ready_for_external_tower_intake"
        assert data[SESSION_TOWER_CLOUDS_LAUNCH_RECEIPT]["downstream_execution_performed"] is False

        handoff = data[SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF]
        assert handoff["contract_owner"] == "tower"
        assert handoff["target_app_id"] == "clouds"
        assert handoff["target_route"] == "/clouds"
        assert handoff["owner_surface"] == "OwnerCommandExperience"
        assert handoff["clouds_session_key_preexisting_in_gp024"] is False
        assert handoff["clouds_executes_navigation"] is False
        assert handoff["downstream_execution_performed"] is False
        assert handoff["broker_submission_enabled"] is False
        assert handoff["real_capital_movement_enabled"] is False
        assert handoff["production_manual_live_authorized"] is False
        assert handoff["live_auto_locked"] is True


def test_clouds_route_requires_tower_integration_handoff():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    response = client.get(CLOUDS_HOME_PATH, follow_redirects=False)

    assert response.status_code == 403
    assert response.get_json()["reason_code"] == "tower_clouds_integration_handoff_required"


def test_clouds_route_renders_canonical_owner_command_labels_after_handoff():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)
    response = client.get(CLOUDS_HOME_PATH, follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.headers["x-tower-clouds-pack1"] == "canonical-owner-command"

    for label in CANONICAL_VISIBLE_LABELS:
        assert label in body

    for label in [
        "Soulaana explains first",
        "Needs You identifies top focus",
        "Keep Watching identifies ATM lane",
        "Quiet work remains collapsed",
        "Detail drawers are progressive",
        "Operating source boundary is explicit",
        "Protected handoff remains non-executing",
        "No raw downstream execution",
    ]:
        assert label in body

    assert "owner_command_today_surface" not in body
    assert "Soulaana has the room." not in body


def test_clouds_return_persists_receipt_and_preserves_session():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)

    response = client.get(CLOUDS_RETURN_PATH, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == TOWER_ACCESS_HOME_PATH

    with client.session_transaction() as data:
        receipt = data[SESSION_TOWER_CLOUDS_RETURN_RECEIPT]
        assert receipt["receipt_type"] == "tower_clouds_return_receipt"
        assert receipt["tower_session_preserved"] is True
        assert receipt["downstream_execution_performed"] is False


def test_clouds_return_json_reports_receipt():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)
    client.get(CLOUDS_RETURN_PATH, follow_redirects=False)

    response = client.get(CLOUDS_RETURN_JSON_PATH, follow_redirects=False)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["allowed"] is True
    assert payload["receipt"]["receipt_type"] == "tower_clouds_return_receipt"


def test_access_home_injects_canonical_clouds_launch_card():
    app = _app()
    client = app.test_client()
    _owner_session(client, step_up=True)

    response = client.get(TOWER_ACCESS_HOME_PATH, follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-clouds-canonical-owner-launch-card-pack1" in body
    assert "The Clouds" in body
    assert "Open The Clouds" in body
    assert "OwnerCommandExperience" in body
    assert response.headers["x-tower-clouds-card"] == "canonical-pack1"
