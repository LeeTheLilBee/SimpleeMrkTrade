
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ADAPTER = (
    ROOT
    / "web/static/ob/ob_engine_feed_adapter.js"
).read_text(
    encoding="utf-8"
)


def test_obdata003_reuses_existing_engine_snapshot_endpoint():
    assert "OBDATA003_CANONICAL_WEB_PROJECTION" in ADAPTER
    assert '"/ob/engine-feed-snapshot.json"' in ADAPTER
    assert "window.OB_ENGINE_FEED_ADAPTER_V25" in ADAPTER
    assert "window.OB_CANONICAL_WEB_PROJECTION_OBDATA003_API" in ADAPTER


def test_obdata003_requires_provenance_before_current():
    assert "source_identified:" in ADAPTER
    assert "timestamp_identified:" in ADAPTER
    assert "current_eligible:" in ADAPTER
    assert '"provenance_required"' in ADAPTER
    assert '"quarantined"' in ADAPTER
    assert '"rehearsal"' in ADAPTER
    assert '"stale"' in ADAPTER
    assert '"fresh"' in ADAPTER


def test_obdata003_updates_without_new_engine():
    assert "60 * 1000" in ADAPTER
    assert '"visibilitychange"' in ADAPTER
    assert '"focus"' in ADAPTER
    assert 'cache:' in ADAPTER
    assert '"no-store"' in ADAPTER


def test_obdata003_fallback_is_empty_not_preview():
    assert "v22_preview_contract_fallback" not in ADAPTER
    assert "guarded_route_preview_fallback" not in ADAPTER
    assert "http_fallback" not in ADAPTER
    assert "error_fallback" not in ADAPTER

    assert "Preview fallback is disabled" in ADAPTER
    assert "positions_preview:" in ADAPTER
    assert "candidates_preview:" in ADAPTER


def test_obdata003_safety_is_locked():
    assert "no_broker_api:" in ADAPTER
    assert "no_order_submission:" in ADAPTER
    assert "no_capital_movement:" in ADAPTER
    assert "no_auto_execution:" in ADAPTER
    assert "live_auto_locked:" in ADAPTER
    assert "gp066_advanced:" in ADAPTER
