from flask import Flask

import tower.ob_web_route_enforcement as enforcement


def build_app(monkeypatch, *, owner, step_up):
    app = Flask(__name__)
    app.secret_key = "tower-ob-route-enforcement-test"

    monkeypatch.setattr(
        enforcement,
        "owner_session_active",
        lambda: owner,
    )

    monkeypatch.setattr(
        enforcement,
        "step_up_active",
        lambda: step_up,
    )

    monkeypatch.setattr(
        enforcement,
        "operational_ob_access_active",
        lambda: True,
    )

    @app.route("/ob/dashboard")
    def dashboard():
        return "DASHBOARD"

    @app.route("/ob/market-map")
    def market_map():
        return "MARKET MAP"

    @app.route("/ob/symbol/<symbol>")
    def symbol(symbol):
        return f"SYMBOL {symbol}"

    @app.route("/ob/trade-center")
    def trade_center():
        return "TRADE CENTER"

    @app.route("/ob/review-center")
    def review_center():
        return "REVIEW CENTER"

    @app.route("/ob/owner-console")
    def owner_console():
        return "OWNER CONSOLE"

    @app.route("/ob/owner-dashboard")
    def owner_dashboard():
        return "OWNER DASHBOARD"

    @app.route("/tower/login")
    def tower_login():
        return "LOGIN"

    @app.route("/tower/access-home")
    def tower_access_home():
        return "ACCESS HOME"

    enforcement.register_ob_protected_route_enforcement(
        app
    )

    return app


ROOMS = [
    "/ob/dashboard",
    "/ob/market-map",
    "/ob/symbol/AMD",
    "/ob/trade-center",
    "/ob/review-center",
    "/ob/owner-console",
    "/ob/owner-dashboard",
]


NORMAL_ROOMS = [
    "/ob/dashboard",
    "/ob/market-map",
    "/ob/symbol/AMD",
    "/ob/trade-center",
    "/ob/review-center",
]


OWNER_ONLY_ROOMS = [
    "/ob/owner-console",
    "/ob/owner-dashboard",
]


def test_anonymous_direct_ob_rooms_redirect_to_tower_login(monkeypatch):
    app = build_app(
        monkeypatch,
        owner=False,
        step_up=False,
    )

    client = app.test_client()

    for route in ROOMS:
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
        }

        assert response.headers["Location"].endswith(
            "/tower/login"
        )


def test_owner_without_step_up_cannot_enter_normal_rooms(monkeypatch):
    app = build_app(
        monkeypatch,
        owner=True,
        step_up=False,
    )

    client = app.test_client()

    for route in NORMAL_ROOMS:
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
        }

        assert response.headers["Location"].endswith(
            "/tower/access-home"
        )


def test_owner_only_rooms_remain_owner_session_only(monkeypatch):
    app = build_app(
        monkeypatch,
        owner=True,
        step_up=False,
    )

    client = app.test_client()

    for route in OWNER_ONLY_ROOMS:
        response = client.get(
            route,
            follow_redirects=False,
        )

        assert response.status_code == 200


def test_owner_with_step_up_can_enter_all_rooms(monkeypatch):
    app = build_app(
        monkeypatch,
        owner=True,
        step_up=True,
    )

    client = app.test_client()

    for route in ROOMS:
        response = client.get(
            route,
            follow_redirects=False,
        )

        assert response.status_code == 200


def test_unknown_ob_route_is_default_denied_even_for_valid_owner(monkeypatch):
    app = build_app(
        monkeypatch,
        owner=True,
        step_up=True,
    )

    response = app.test_client().get(
        "/ob/not-an-approved-room",
        follow_redirects=False,
    )

    assert response.status_code == 403
