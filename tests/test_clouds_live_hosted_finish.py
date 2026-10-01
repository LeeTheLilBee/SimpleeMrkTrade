from __future__ import annotations

from datetime import datetime, timedelta, timezone

from web.hosted_tower import app

from tower.tower_clouds_native_launch import (
    CLOUDS_ACCESS_PATH,
    CLOUDS_HOME_PATH,
    OWNER_ROLE,
    SESSION_AUTHENTICATED,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
)


def _owner_session(client):
    with client.session_transaction() as data:
        data[SESSION_AUTHENTICATED] = True
        data[SESSION_ROLE] = OWNER_ROLE
        data[SESSION_OWNER_ID] = "owner_clouds_acceptance"
        data[SESSION_USERNAME] = "clouds_acceptance"
        data[SESSION_STEP_UP_UNTIL] = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        ).isoformat()


def test_hosted_clouds_launch_renders_finished_owner_command():
    client = app.test_client()
    _owner_session(client)

    launch = client.get(
        CLOUDS_ACCESS_PATH,
        follow_redirects=False,
    )

    assert launch.status_code == 302
    assert launch.headers["Location"] == CLOUDS_HOME_PATH

    response = client.get(
        CLOUDS_HOME_PATH,
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert (
        response.headers.get(
            "x-clouds-live-owner-command"
        )
        == "20261001"
    )

    html = response.get_data(
        as_text=True
    )

    for label in (
        "Needs You",
        "Keep Watching",
        "Ecosystem Lines",
        "Can Wait",
        "Technical Truth",
        "Soulaana explains",
        "Feed status and Door status are separate",
    ):
        assert label in html

    assert 'href="/ob/dashboard"' not in html
    assert 'href="/teller"' not in html
    assert 'href="/grounds"' not in html
    assert "/tower/clouds/open/" not in html

    assert "/tower/launch/observatory" in html
    assert "/tower/launch/teller" in html
    assert "/tower/launch/grounds" in html
    assert "/tower/launch/buybox" in html

    assert "No broker order" in html
    assert "capital movement" in html


def test_hosted_clouds_remains_closed_without_tower_launch():
    client = app.test_client()

    response = client.get(
        CLOUDS_HOME_PATH,
        follow_redirects=False,
    )

    assert response.status_code != 200
    assert (
        response.headers.get(
            "x-clouds-live-owner-command"
        )
        != "20261001"
    )
