from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

JS = (
    ROOT / "web/static/ob/ob_market_map.js"
).read_text(encoding="utf-8")


def test_obux034_symbol_handoff_uses_ob_symbol_route():
    assert '"/ob/symbol/"' in JS
    assert "encodeURIComponent" in JS
    assert "window.location.assign" in JS


def test_obux034_attention_states_are_contract_backed():
    assert "contract.open_positions" in JS
    assert "contract.signals" in JS
    assert "contract.candidates" in JS
    assert "contract.watchlist" in JS


def test_obux034_missing_market_truth_renders_empty_sky():
    assert "renderEmptySky" in JS

    assert (
        "OB will not invent stars, sectors, or opportunities."
        in JS
    )


def test_obux034_no_execution_actions():
    assert "submitOrder" not in JS
    assert "placeOrder" not in JS

    assert "order_submission_enabled:" in JS
    assert "capital_movement_enabled:" in JS
    assert "auto_execution_enabled:" in JS
    assert "live_auto_locked:" in JS
