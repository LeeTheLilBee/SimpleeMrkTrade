from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP_SOURCE = ROOT / "web/app.py"
MARKET = ROOT / "web/templates/market_map.html"
ADAPTER = ROOT / "web/static/ob/ob_engine_feed_adapter.js"
MAP_JS = ROOT / "web/static/ob/ob_market_map.js"
TOWER_GUARD = ROOT / "tower/ob_web_route_enforcement.py"


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def owner_step_up(client):
    expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    ).isoformat()

    with client.session_transaction() as session:
        session["tower_authenticated"] = True
        session["tower_role"] = "owner"
        session["owner_id"] = "simplee_owner"
        session["tower_username"] = "owner"
        session["tower_authenticated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )
        session["tower_step_up_until"] = expires


def test_obfix006_market_map_route_carries_room_scoped_feed():
    source = text(APP_SOURCE)

    assert '@app.route("/ob/market-map")' in source
    assert "def ob_market_map_alias_v11():" in source
    assert 'request.args.get("engine_feed") == "1"' in source
    assert "return ob_engine_feed_snapshot_v25()" in source
    assert 'return render_template("market_map.html")' in source


def test_obfix007_market_map_sets_override_before_adapter_load():
    source = text(MARKET)

    endpoint = "window.OB_ENGINE_FEED_ENDPOINT"
    adapter = "ob_engine_feed_adapter.js"

    assert endpoint in source
    assert "?engine_feed=1" in source
    assert 'data-ob-market-map-open-repair="OBFIX006-010"' in source

    assert source.index(endpoint) < source.index(adapter)


def test_obfix008_adapter_override_is_same_origin_relative_only():
    source = text(ADAPTER)

    assert "DEFAULT_ENDPOINT" in source
    assert '"/ob/engine-feed-snapshot.json"' in source
    assert "window.OB_ENGINE_FEED_ENDPOINT" in source
    assert 'REQUESTED_ENDPOINT.startsWith("/")' in source
    assert '!REQUESTED_ENDPOINT.startsWith("//")' in source


def test_obfix009_tower_default_deny_is_not_weakened():
    source = text(TOWER_GUARD)

    assert '"/ob/market-map"' in source

    # We deliberately did NOT modify Tower to expose the old data URL.
    assert '"/ob/engine-feed-snapshot.json"' not in source

    assert 'if not path.startswith("/ob/"):' in source
    assert "if not is_approved_ob_web_room(path):" in source
    assert "abort(403)" in source


def test_obfix009_authenticated_market_map_final_response_is_real_room():
    from web.app import app

    app.config.update(TESTING=True)

    client = app.test_client()
    owner_step_up(client)

    response = client.get(
        "/ob/market-map",
        follow_redirects=False,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert 'data-ob-room="market-map"' in body
    assert 'data-ob-market-map-version="OBUX031-OBUX035"' in body
    assert 'data-ob-market-map-open-repair="OBFIX006-010"' in body
    assert "THE OBSERVATORY · MARKET SKY" in body
    assert "ob_market_map.js" in body
    assert "window.OB_ENGINE_FEED_ENDPOINT" in body


def test_obfix009_authenticated_room_scoped_feed_returns_engine_projection():
    from web.app import app

    app.config.update(TESTING=True)

    client = app.test_client()
    owner_step_up(client)

    response = client.get(
        "/ob/market-map?engine_feed=1",
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert response.is_json

    payload = response.get_json()

    assert isinstance(payload, dict)


def test_obfix009_old_unapproved_feed_path_remains_fail_closed():
    from web.app import app

    app.config.update(TESTING=True)

    client = app.test_client()
    owner_step_up(client)

    response = client.get(
        "/ob/engine-feed-snapshot.json",
        follow_redirects=False,
    )

    # Even a valid owner + step-up does not bypass the approved-room list.
    assert response.status_code == 403


def test_obfix010_market_map_symbol_handoff_is_preserved():
    source = text(MAP_JS)

    assert '"/ob/symbol/"' in source
    assert "window.location.assign" in source


def test_obfix010_no_execution_authority_added():
    combined = "\n".join([
        text(MARKET),
        text(ADAPTER),
        text(MAP_JS),
    ])

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ]:
        assert forbidden not in combined
