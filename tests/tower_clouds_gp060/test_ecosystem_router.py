from datetime import timedelta

from flask import Flask

from tower.ecosystem_router import (
    SESSION_ECOSYSTEM_RETURN,
    register_tower_ecosystem_router,
)
from tower.tower_clouds_native_launch import (
    OWNER_ROLE,
    SESSION_AUTHENTICATED,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
    utc_now,
)


def _app():
    app = Flask(
        "ecosystem-router-test"
    )

    app.secret_key = (
        "ecosystem-router-test-only"
    )

    register_tower_ecosystem_router(
        app
    )

    return app


def _owner_session(
    client,
    *,
    step_up=True,
):
    with client.session_transaction() as sess:
        sess[SESSION_AUTHENTICATED] = True
        sess[SESSION_ROLE] = OWNER_ROLE
        sess[SESSION_OWNER_ID] = "owner-test"
        sess[SESSION_USERNAME] = "owner-test"

        if step_up:
            sess[SESSION_STEP_UP_UNTIL] = (
                utc_now()
                + timedelta(minutes=10)
            ).isoformat()


def test_line_matrix_requires_owner_session():
    app = _app()

    with app.test_client() as client:
        response = client.get(
            "/tower/ecosystem/lines.json",
            follow_redirects=False,
        )

        assert response.status_code == 401

        assert (
            response.get_json()["default_deny"]
            is True
        )


def test_line_matrix_is_compact_truth_surface():
    app = _app()

    with app.test_client() as client:
        _owner_session(client)

        response = client.get(
            "/tower/ecosystem/lines.json"
        )

        assert response.status_code == 200

        payload = response.get_json()

        assert payload["allowed"] is True
        assert payload["line_count"] == 7

        assert (
            payload["clouds_direct_bypass_allowed"]
            is False
        )

        assert (
            payload["downstream_execution_performed"]
            is False
        )


def test_contract_ready_app_does_not_fake_launch():
    app = _app()

    with app.test_client() as client:
        _owner_session(client)

        response = client.get(
            "/tower/ecosystem/launch/teller"
            "?destination=payroll_review"
            "&return_context=clouds-teller",
            follow_redirects=False,
        )

        assert response.status_code == 409

        assert (
            "Connection contract is ready"
            in response.get_data(
                as_text=True
            )
        )


def test_missing_step_up_routes_to_tower_step_up():
    app = _app()

    with app.test_client() as client:
        _owner_session(
            client,
            step_up=False,
        )

        response = client.get(
            "/tower/ecosystem/launch/observatory"
            "?destination=dashboard",
            follow_redirects=False,
        )

        assert response.status_code in {
            301,
            302,
            303,
            307,
            308,
        }

        assert (
            "/tower/ecosystem/step-up/observatory"
            in response.headers["Location"]
        )


def test_tower_destination_can_route_without_extra_step_up():
    app = _app()

    with app.test_client() as client:
        _owner_session(
            client,
            step_up=False,
        )

        response = client.get(
            "/tower/ecosystem/launch/tower"
            "?destination=access_home"
            "&return_context=clouds-tower",
            follow_redirects=False,
        )

        assert response.status_code in {
            301,
            302,
            303,
            307,
            308,
        }

        assert (
            response.headers["Location"]
            .endswith(
                "/tower/access-home"
            )
        )


def test_unknown_app_fails_closed():
    app = _app()

    with app.test_client() as client:
        _owner_session(client)

        response = client.get(
            "/tower/ecosystem/launch/not-real",
            follow_redirects=False,
        )

        assert response.status_code == 403
        assert response.get_json()["default_deny"] is True


def test_return_context_routes_back_to_clouds():
    app = _app()

    with app.test_client() as client:
        _owner_session(client)

        with client.session_transaction() as sess:
            sess[SESSION_ECOSYSTEM_RETURN] = {
                "origin_app": "clouds",
                "opened_app": "observatory",
                "opened_destination": "review_center",
                "item": "OB-1",
                "return_context": "clouds-observatory",
                "handoff_id": "eco-test",
                "created_at": utc_now().isoformat(),
                "return_to": "clouds",
            }

        response = client.get(
            "/tower/ecosystem/return",
            follow_redirects=False,
        )

        assert response.status_code in {
            301,
            302,
            303,
            307,
            308,
        }

        assert (
            response.headers["Location"]
            .startswith("/clouds?")
        )

        assert (
            "resume=clouds-observatory"
            in response.headers["Location"]
        )
