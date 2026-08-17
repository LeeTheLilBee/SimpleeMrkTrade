
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONTRACTS = (
    ROOT
    / "web/static/ob/ob_data_contracts.js"
).read_text(
    encoding="utf-8"
)


def test_obdata004_all_rooms_use_canonical_projection():
    assert "OBDATA004_CANONICAL_ROOM_DATA_CONTRACTS" in CONTRACTS
    assert "OB_CANONICAL_WEB_PROJECTION_OBDATA003_API" in CONTRACTS
    assert "OB_CANONICAL_ROOM_CONTRACTS_OBDATA004_API" in CONTRACTS

    for name in [
        "dashboardContract",
        "marketMapContract",
        "symbolPageContract",
        "tradeCenterContract",
        "reviewCenterContract",
        "ownerConsoleContract",
    ]:
        assert f"function {name}" in CONTRACTS


def test_obdata004_no_fake_fallback_sector_or_default_mu():
    assert "Fallback Sector" not in CONTRACTS
    assert 'String(symbol || "MU")' not in CONTRACTS
    assert '["MU", "AMD", "INTC"]' not in CONTRACTS


def test_obdata004_no_generated_market_health_score():
    assert "score: hot >=" not in CONTRACTS
    assert "Healthy but guarded" not in CONTRACTS
    assert "Risk-on pockets" not in CONTRACTS


def test_obdata004_no_generated_manual_live_queue():
    assert "candidates().slice(0, 5).map" not in CONTRACTS
    assert "next monthly call" not in CONTRACTS
    assert "Needs owner review" not in CONTRACTS


def test_obdata004_no_preview_mode():
    assert 'return "canonical"' in CONTRACTS
    assert "localStorage.setItem" not in CONTRACTS
    assert "patchPreviewData" in CONTRACTS
    assert "return false;" in CONTRACTS
