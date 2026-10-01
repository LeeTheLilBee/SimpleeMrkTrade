from datetime import datetime, timezone

from engine.market_intake.alpaca_personal_bridge import (
    SOURCE_ID, installed_gateway, snapshot_to_gateway_raw,
)
from engine.market_intake.contracts import ScanContext


def test_alpaca_bridge_ingests_into_universal_gateway_without_execution_authority():
    gateway, _rights = installed_gateway(
        verified_at=datetime(2026, 9, 30, 18, 59, tzinfo=timezone.utc)
    )
    snap = {
        "symbol": "AAPL",
        "as_of": "2026-09-30T19:00:00+00:00",
        "quote": {
            "bid": 100.0, "ask": 100.2, "midpoint": 100.1,
            "timestamp": "2026-09-30T19:00:00+00:00",
        },
        "bar": {
            "close": 100.1, "volume": 12345,
            "timestamp": "2026-09-30T19:00:00+00:00",
        },
    }
    now = datetime(2026, 9, 30, 19, 0, 1, tzinfo=timezone.utc)
    decision = gateway.ingest(
        SOURCE_ID,
        snapshot_to_gateway_raw(snap),
        received_at=now,
        context=ScanContext(now=now, market_session="REGULAR", verified_market_time=True),
    )
    assert decision.state == "CURRENT_RESEARCH"
    assert decision.stored is True
    assert decision.owner_visible is True
    assert decision.invitee_visible is False
    assert decision.broker_execution_authorized is False
