from datetime import (
    datetime,
    timedelta,
    timezone,
)

from flask import Flask

from tower import (
    tower_clouds_native_launch
    as native
)


def test_gp081_probe_fails_closed_anonymous():

    app = Flask(
        "gp081-test"
    )

    app.secret_key = (
        "gp081-test-only"
    )

    app.register_blueprint(
        native.tower_clouds_native_bp
    )

    with app.test_client() as client:

        response = client.get(
            "/tower/clouds/gp081-hosted-probe"
        )

        assert (
            response.status_code
            == 401
        )

        payload = (
            response.get_json()
        )

        assert (
            payload[
                "default_deny"
            ]
            is True
        )

        assert (
            payload[
                "downstream_execution_performed"
            ]
            is False
        )


def test_gp081_current_clouds_and_source_truth():

    app = Flask(
        "gp081-test-current-clouds"
    )

    app.secret_key = (
        "gp081-test-current-clouds-only"
    )

    app.register_blueprint(
        native.tower_clouds_native_bp
    )

    with app.test_client() as client:

        with client.session_transaction() as sess:

            sess[
                native.SESSION_AUTHENTICATED
            ] = True

            sess[
                native.SESSION_ROLE
            ] = native.OWNER_ROLE

            sess[
                native.SESSION_OWNER_ID
            ] = "gp081-test-owner"

            sess[
                native.SESSION_USERNAME
            ] = "gp081-test-owner"

            sess[
                native.SESSION_STEP_UP_UNTIL
            ] = (
                datetime.now(
                    timezone.utc
                )
                + timedelta(
                    minutes=10
                )
            ).isoformat()


        launch = client.get(
            native.CLOUDS_ACCESS_PATH,
            follow_redirects=False,
        )

        assert (
            launch.status_code
            in {
                301,
                302,
                303,
                307,
                308,
            }
        )


        page = client.get(
            native.CLOUDS_HOME_PATH
        )

        assert (
            page.status_code
            == 200
        )

        text = (
            page.get_data(
                as_text=True
            )
        )

        assert (
            "The Clouds"
            in text
        )

        assert (
            "Soulaana"
            in text
        )


        truth = client.get(
            "/clouds/hosted-source-truth.json"
        )

        assert (
            truth.status_code
            == 200
        )

        payload = (
            truth.get_json()
        )

        assert (
            payload[
                "projection_only_source_count"
            ]
            == 3
        )

        assert (
            payload[
                "unavailable_source_count"
            ]
            == 3
        )

        assert (
            payload[
                "verified_live_source_count"
            ]
            == 0
        )

        assert (
            payload[
                "false_urgency_count"
            ]
            == 0
        )
