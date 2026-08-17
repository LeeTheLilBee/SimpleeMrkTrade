
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LIVE = (
    ROOT
    / "web/static/ob/ob_market_data.js"
).read_text(
    encoding="utf-8"
)

DEMO = (
    ROOT
    / "web/static/ob/demo/ob_market_data_demo.js"
).read_text(
    encoding="utf-8"
)


def test_obdata002_live_market_fixture_is_empty():
    assert "live_eligible: false" in LIVE
    assert "current_market_truth: false" in LIVE
    assert "sectors: []" in LIVE
    assert "symbols: []" in LIVE
    assert "signals: []" in LIVE


def test_obdata002_old_market_fixture_is_preserved_but_demo_only():
    assert "QUARANTINED LEGACY MARKET FIXTURE" in DEMO
    assert "OB_MARKET_DATA_DEMO_ONLY = true" in DEMO
    assert "OB_MARKET_DATA_DEMO_LIVE_ELIGIBLE = false" in DEMO


def test_obdata002_demo_fixture_is_not_loaded_by_templates():
    for path in (ROOT / "web/templates").glob("*.html"):
        text = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        assert "demo/ob_market_data_demo.js" not in text
