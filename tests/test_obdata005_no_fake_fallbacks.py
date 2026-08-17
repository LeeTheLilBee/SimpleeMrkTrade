
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ADAPTER = (
    ROOT
    / "web/static/ob/ob_engine_feed_adapter.js"
).read_text(
    encoding="utf-8"
)

CONTRACTS = (
    ROOT
    / "web/static/ob/ob_data_contracts.js"
).read_text(
    encoding="utf-8"
)

MARKET = (
    ROOT
    / "web/static/ob/ob_market_data.js"
).read_text(
    encoding="utf-8"
)

ACCEPTANCE = json.loads(
    (
        ROOT
        / "evidence/market_truth/obdata005_acceptance.json"
    ).read_text(
        encoding="utf-8"
    )
)


def test_obdata005_fake_live_paths_are_closed():
    combined = ADAPTER + "\n" + CONTRACTS

    assert "v22_preview_contract_fallback" not in combined
    assert "Fallback Sector" not in combined
    assert '["MU", "AMD", "INTC"]' not in combined
    assert "next monthly call" not in combined

    assert "live_eligible: false" in MARKET


def test_obdata005_did_not_replace_existing_engine():
    assert ACCEPTANCE["engine_files_modified"] is False
    assert ACCEPTANCE["data_json_modified"] is False
    assert ACCEPTANCE["web_app_modified"] is False
    assert ACCEPTANCE["tower_modified"] is False


def test_obdata005_execution_boundaries_remain_closed():
    assert ACCEPTANCE["broker_api_enabled"] is False
    assert ACCEPTANCE["order_submission_enabled"] is False
    assert ACCEPTANCE["capital_movement_enabled"] is False
    assert ACCEPTANCE["auto_execution_enabled"] is False
    assert ACCEPTANCE["live_auto_locked"] is True
    assert ACCEPTANCE["gp066_advanced"] is False
