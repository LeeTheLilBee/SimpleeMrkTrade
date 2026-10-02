from __future__ import annotations

from urllib.parse import urlsplit

from web.hosted_tower import app


def path_of(response):

    return urlsplit(
        response.headers.get(
            "Location",
            "",
        )
    ).path


def test_twr192_root_redirects_to_tower_start():

    with app.test_client() as client:

        response = client.get(
            "/",
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert path_of(response) == "/tower/start"


def test_twr192_legacy_tower_redirects_to_tower_start():

    with app.test_client() as client:

        response = client.get(
            "/tower",
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert path_of(response) == "/tower/start"


def test_twr192_legacy_tower_slash_redirects_to_tower_start():

    with app.test_client() as client:

        response = client.get(
            "/tower/",
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert path_of(response) == "/tower/start"


def test_twr192_start_without_owner_session_redirects_to_login():

    with app.test_client() as client:

        response = client.get(
            "/tower/start",
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert path_of(response) == "/tower/login"


def test_twr192_access_home_without_session_redirects_to_login():

    with app.test_client() as client:

        response = client.get(
            "/tower/access-home",
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert path_of(response) == "/tower/login"


def test_twr192_teller_launch_without_session_redirects_to_login():

    with app.test_client() as client:

        response = client.get(
            "/tower/launch/teller",
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert path_of(response) == "/tower/login"


def test_twr192_health_is_not_redirected():

    with app.test_client() as client:

        response = client.get(
            "/tower/healthz",
            follow_redirects=False,
        )

    assert response.status_code == 200


def test_twr192_front_door_grants_no_authority():

    contract = (
        app.extensions[
            "tower_canonical_hosted_front_door_twr192"
        ]
    )

    assert (
        contract[
            "canonical_destination"
        ]
        == "/tower/start"
    )

    assert contract["authentication_bypass"] is False
    assert contract["step_up_bypass"] is False
    assert contract["broker_authority"] is False
    assert contract["capital_authority"] is False
    assert contract["payroll_execution_authority"] is False
    assert contract["manual_live_authorized"] is False
    assert contract["live_auto_authorized"] is False
