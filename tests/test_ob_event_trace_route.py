from flask import Flask

from engine.market_intake.observatory_event_stream import ObservatoryEventHub
from web.ob_event_trace_route import create_event_trace_blueprint


def app_with_trace(*, authorized=True):
    app = Flask(__name__)
    hub = ObservatoryEventHub()
    app.register_blueprint(create_event_trace_blueprint(
        owner_authorize=lambda: authorized,
        event_hub=hub,
    ))
    return app, hub


def test_trace_route_is_owner_only_and_status_only():
    app, hub = app_with_trace()
    event = hub.publish_invalidation(
        event_type="market_snapshot_changed",
        source="alpaca_iex_stream",
        snapshot_path="/ob/engine-feed-snapshot.json",
        symbol="AAPL",
        producer_stages=("RECEIVED", "VALIDATED", "NORMALIZED"),
    )

    response = app.test_client().get("/ob/data-desk/event-traces.json")
    assert response.status_code == 200
    data = response.get_json()
    assert data["schema"] == "OB_EVENT_TRACE_V1"
    assert data["content_attached"] is False
    assert data["provider_payload_attached"] is False
    assert data["credentials_attached"] is False
    assert data["positions_attached"] is False
    assert data["orders_attached"] is False
    assert data["execution_authorized"] is False

    row = data["traces"][0]
    assert row["event_id"] == event["event_id"]
    assert row["stages"]["PUBLISHED"] is True
    assert row["stages"]["SOULAANA_CONSUMED"] is False
    assert row["stages"]["SOULAANA_INTERPRETED"] is False
    assert row["soulaana_complete"] is False
    assert "private, no-store" in response.headers["Cache-Control"]


def test_trace_route_does_not_infer_soulaana_from_publication():
    app, hub = app_with_trace()
    event = hub.publish_invalidation(
        event_type="research_context_changed",
        source="official_catalyst_radar",
        snapshot_path="/ob/research/catalysts.json",
    )
    row = hub.trace_snapshot(event_id=event["event_id"])["traces"][0]
    assert row["stages"]["PUBLISHED"] is True
    assert row["soulaana_complete"] is False

    hub.record_lifecycle(
        event_id=event["event_id"],
        stage="SOULAANA_CONSUMED",
        consumer="soulaana",
    )
    row = hub.trace_snapshot(event_id=event["event_id"])["traces"][0]
    assert row["stages"]["SOULAANA_CONSUMED"] is True
    assert row["stages"]["SOULAANA_INTERPRETED"] is False
    assert row["soulaana_complete"] is False

    hub.record_lifecycle(
        event_id=event["event_id"],
        stage="SOULAANA_INTERPRETED",
        consumer="soulaana",
    )
    row = hub.trace_snapshot(event_id=event["event_id"])["traces"][0]
    assert row["soulaana_complete"] is True


def test_trace_route_denies_without_owner_authorization():
    app, _ = app_with_trace(authorized=False)
    assert app.test_client().get("/ob/data-desk/event-traces.json").status_code == 403
