from web.app import app


PROTECTED_ROUTES = [
    "/ob/dashboard",
    "/ob/market-map",
    "/ob/symbol/AMD",
    "/ob/trade-center",
    "/ob/review-center",
    "/ob/owner-console",
    "/ob/owner-dashboard",
]


REAL_ROOM_BODY_MARKERS = [
    b"SOULAANA \\xc2\\xb7 RIGHT NOW",
    b"ob-command-stage",
    b"NORMAL_OB_DASHBOARD_ONLY",
    b"OWNER DASHBOARD",
    b"OWNER CONSOLE",
]


def test_real_app_anonymous_ob_rooms_do_not_render_protected_content():
    app.config.update(
        TESTING=True,
    )

    client = app.test_client()

    for route in PROTECTED_ROUTES:
        response = client.get(
            route,
            follow_redirects=False,
        )

        assert response.status_code in {
            301,
            302,
            303,
            307,
            308,
            401,
            403,
        }, (
            route,
            response.status_code,
        )

        upper_body = response.data.upper()

        for marker in REAL_ROOM_BODY_MARKERS:
            assert marker.upper() not in upper_body


def test_real_app_direct_owner_dashboard_redirects_to_tower_login():
    app.config.update(
        TESTING=True,
    )

    response = app.test_client().get(
        "/ob/owner-dashboard",
        follow_redirects=False,
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert response.headers["Location"].endswith(
        "/tower/login"
    )


def test_real_app_direct_owner_console_redirects_to_tower_login():
    app.config.update(
        TESTING=True,
    )

    response = app.test_client().get(
        "/ob/owner-console",
        follow_redirects=False,
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert response.headers["Location"].endswith(
        "/tower/login"
    )


def test_real_app_unknown_ob_route_fails_closed():
    app.config.update(
        TESTING=True,
    )

    response = app.test_client().get(
        "/ob/absolutely-not-a-real-room",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_real_app_tower_login_still_responds():
    app.config.update(
        TESTING=True,
    )

    response = app.test_client().get(
        "/tower/login",
        follow_redirects=False,
    )

    assert response.status_code == 200
