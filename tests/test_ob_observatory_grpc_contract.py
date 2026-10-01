from pathlib import Path
import json

import pytest

from engine.market_intake.observatory_event_stream import ObservatoryEventHub
from engine.market_intake.observatory_grpc_contract import (
    grpc_event_projection,
    grpc_lifecycle_projection,
    grpc_runtime_status,
)
from tower.ob_alpaca_iex_stream import AlpacaIEXStreamManager


ROOT = Path(__file__).resolve().parents[1]


def test_market_event_lifecycle_is_content_free_and_truthful():
    hub = ObservatoryEventHub(history=8)
    event = hub.publish_invalidation(
        event_type="market_snapshot_changed",
        source="synthetic_provider",
        snapshot_path="/ob/engine-feed-snapshot.json",
        symbol="AAPL",
        producer_stages=("RECEIVED", "VALIDATED", "NORMALIZED"),
    )
    assert event["trace_available"] is True
    assert event["event_id"] == f"{hub.epoch}.1"

    trace = hub.trace_snapshot(event_id=event["event_id"])["traces"][0]
    assert trace["stages"]["RECEIVED"] is True
    assert trace["stages"]["VALIDATED"] is True
    assert trace["stages"]["NORMALIZED"] is True
    assert trace["stages"]["PUBLISHED"] is True
    assert trace["stages"]["SCANNER_CONSUMED"] is False
    assert trace["stages"]["SIMULATION_CONSUMED"] is False
    assert trace["stages"]["SOULAANA_CONSUMED"] is False
    assert trace["stages"]["SOULAANA_INTERPRETED"] is False
    assert trace["soulaana_complete"] is False

    with pytest.raises(ValueError, match="TRACE_ORDER_HOLD"):
        hub.record_lifecycle(
            event_id=event["event_id"],
            stage="SOULAANA_INTERPRETED",
            consumer="soulaana",
        )

    hub.record_lifecycle(
        event_id=event["event_id"],
        stage="SCANNER_CONSUMED",
        consumer="scanner",
    )
    hub.record_lifecycle(
        event_id=event["event_id"],
        stage="SIMULATION_CONSUMED",
        consumer="simulation_engine",
    )
    hub.record_lifecycle(
        event_id=event["event_id"],
        stage="SOULAANA_CONSUMED",
        consumer="soulaana",
    )
    final = hub.record_lifecycle(
        event_id=event["event_id"],
        stage="SOULAANA_INTERPRETED",
        consumer="soulaana",
    )
    assert final["soulaana_complete"] is True
    assert all(final["stages"].values())
    encoded = json.dumps(final)
    assert "api_secret" not in encoded
    assert "place_order" not in encoded
    assert "100.25" not in encoded


def test_producer_stage_order_fails_closed():
    hub = ObservatoryEventHub()
    with pytest.raises(ValueError, match="TRACE_ORDER_HOLD"):
        hub.publish_invalidation(
            event_type="market_snapshot_changed",
            source="provider",
            snapshot_path="/ob/engine-feed-snapshot.json",
            symbol="AAPL",
            producer_stages=("NORMALIZED",),
        )
    with pytest.raises(ValueError, match="TRACE_STAGE_HOLD"):
        hub.record_lifecycle(
            event_id="not-an-event",
            stage="PUBLISHED",
            consumer="scanner",
        )


def test_grpc_projection_matches_content_free_event_contract():
    hub = ObservatoryEventHub()
    event = hub.publish_invalidation(
        event_type="market_snapshot_changed",
        source="alpaca_iex_stream",
        snapshot_path="/ob/engine-feed-snapshot.json",
        symbol="MSFT",
        producer_stages=("RECEIVED", "VALIDATED", "NORMALIZED"),
    )
    grpc = grpc_event_projection(event)
    assert grpc["schema"] == "SIMPLEE_OBSERVATORY_GRPC_EVENT_V1"
    assert grpc["event_id"] == event["event_id"]
    assert grpc["has_symbol"] is True
    assert grpc["symbol"] == "MSFT"
    assert grpc["needs_authenticated_snapshot"] is True
    assert grpc["content_attached"] is False
    assert grpc["provider_payload_attached"] is False
    assert grpc["execution_authorized"] is False

    trace = hub.trace_snapshot(event_id=event["event_id"])["traces"][0]
    published = next(row for row in trace["receipts"] if row["stage"] == "PUBLISHED")
    receipt = grpc_lifecycle_projection(
        event_id=event["event_id"],
        stage=published["stage"],
        consumer=published["consumer"],
        observed_at=published["observed_at"],
    )
    assert receipt["stage"] == "PUBLISHED"

    status = grpc_runtime_status()
    assert status["contract_installed"] is True
    assert status["network_server_started"] is False
    assert status["provider_payload_transport_enabled"] is False
    assert status["broker_execution_authorized"] is False


def test_alpaca_stream_marks_received_validated_normalized_and_published():
    hub = ObservatoryEventHub()
    manager = AlpacaIEXStreamManager()
    manager._hub = hub
    manager._ingest(json.dumps([{
        "T": "q",
        "S": "AAPL",
        "bp": 100.0,
        "bs": 2,
        "ap": 100.2,
        "as": 3,
        "t": "2026-10-01T14:31:00Z",
    }]))
    snapshot = hub.trace_snapshot()
    assert len(snapshot["traces"]) == 1
    trace = snapshot["traces"][0]
    assert trace["source"] == "alpaca_iex_stream"
    assert trace["symbol"] == "AAPL"
    assert trace["stages"]["RECEIVED"] is True
    assert trace["stages"]["VALIDATED"] is True
    assert trace["stages"]["NORMALIZED"] is True
    assert trace["stages"]["PUBLISHED"] is True
    assert trace["stages"]["SOULAANA_CONSUMED"] is False


def test_proto_declares_stream_and_lifecycle_rpc_without_execution_payloads():
    proto = (ROOT / "proto/observatory_event_v1.proto").read_text()
    assert 'package simplee.observatory.v1;' in proto
    assert "rpc StreamEvents" in proto
    assert "rpc RecordLifecycle" in proto
    for stage in (
        "RECEIVED", "VALIDATED", "NORMALIZED", "PUBLISHED",
        "SCANNER_CONSUMED", "SIMULATION_CONSUMED",
        "SOULAANA_CONSUMED", "SOULAANA_INTERPRETED",
    ):
        assert stage in proto
    assert "order_payload" not in proto
    assert "string credential" not in proto
    assert "capital_amount" not in proto
