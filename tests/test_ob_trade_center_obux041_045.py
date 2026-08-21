from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = ROOT / "web/templates/trade_center.html"
JS = ROOT / "web/static/ob/ob_trade_center.js"
CSS = ROOT / "web/static/ob/ob_trade_center.css"
MODES = ROOT / "web/static/ob/ob_trade_center_modes.js"

LIFECYCLE = ROOT / "engine/options_lifecycle.py"
INTELLIGENCE = ROOT / "engine/options_intelligence.py"
SELECTOR = ROOT / "engine/vehicle_selector.py"

OPTIONS_CONTRACT = (
    ROOT
    / "web/static/ob/ob_options_research_contract.js"
)

ADAPTER = (
    ROOT
    / "web/static/ob/ob_engine_feed_adapter.js"
)


def read(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_canonical_cockpit_exists():
    body = read(TEMPLATE)

    for marker in [
        'id="ob-trade-center"',
        'id="obtc-active-positions"',
        'id="obtc-decision-queue"',
        'id="obtc-workspace"',
        'id="obtc-contract-title"',
        'id="obtc-lifecycle-rail"',
        'id="obtc-mode-zone"',
        'id="obtc-soulaana-orb"',
    ]:
        assert marker in body


def test_active_money_precedes_new_decisions():
    body = read(TEMPLATE)

    assert (
        body.index(
            'id="obtc-active-positions"'
        )
        <
        body.index(
            'id="obtc-decision-queue"'
        )
    )


def test_trade_center_is_options_first():
    body = read(TEMPLATE)

    for marker in [
        'id="obtc-premium"',
        'id="obtc-bid-ask"',
        'id="obtc-iv"',
        'id="obtc-delta"',
        'id="obtc-liquidity"',
        'id="obtc-rank"',
    ]:
        assert marker in body


def test_visual_lifecycle_exists():
    body = read(TEMPLATE)

    for stage in [
        "research",
        "contract",
        "preflight",
        "entry",
        "manage",
        "exit",
        "review",
    ]:
        assert (
            f'data-stage="{stage}"'
            in body
        )


def test_existing_engine_lifecycle_preserved():
    body = read(LIFECYCLE)

    assert (
        "def build_options_lifecycle("
        in body
    )

    for marker in [
        "LIFECYCLE_SELECTED",
        "LIFECYCLE_ENTERED",
        "LIFECYCLE_MANAGING",
        "LIFECYCLE_CLOSED",
    ]:
        assert marker in body


def test_existing_option_intelligence_preserved():
    intelligence = read(INTELLIGENCE)
    selector = read(SELECTOR)

    assert (
        "def choose_best_option("
        in intelligence
    )

    assert (
        "def contract_quality_score("
        in intelligence
    )

    assert (
        "def choose_best_option_contract("
        in selector
    )

    assert "ranked_contracts" in selector


def test_canonical_options_projection_is_used():
    body = read(JS)

    for marker in [
        "safe.options_by_symbol",
        "safe.option_chains",
        "safe.ranked_contracts",
        "safe.research_contracts",
    ]:
        assert marker in body


def test_no_old_market_fixture_on_trade_center_page():
    body = read(TEMPLATE)

    assert (
        "ob_market_data.js"
        not in body
    )


def test_old_proof_mount_is_hidden_not_primary_ui():
    body = read(TEMPLATE)

    assert (
        'id="obtc-proof-compatibility"'
        in body
    )

    compatibility = body[
        body.index(
            'id="obtc-proof-compatibility"'
        )
        - 30:
        body.index(
            'id="obtc-proof-compatibility"'
        )
        + 150
    ]

    assert "hidden" in compatibility


def test_existing_manual_live_operating_layers_preserved():
    body = read(TEMPLATE)

    required = [
        "ob_manual_live_level1_operating_room.js",
        "ob_manual_live_safety_preflight_gate.js",
        "ob_manual_live_decision_packet.js",
        "ob_manual_broker_checklist_fill_capture.js",
        "ob_position_monitor_exit_close_capture.js",
        "ob_final_trade_review_performance_receipt.js",
        "ob_manual_live_candidate_decision_handoff.js",
    ]

    for marker in required:
        assert marker in body


def test_no_hardcoded_legacy_symbols():
    body = read(JS)

    for marker in [
        '"MU"',
        "'MU'",
        '"AMD"',
        "'AMD'",
        '"INTC"',
        "'INTC'",
    ]:
        assert marker not in body


def test_no_fake_confidence_values():
    body = read(JS)

    for marker in [
        "confidence: 82",
        "confidence: 61",
        "confidence: 38",
        '"confidence": 82',
        '"confidence": 61',
        '"confidence": 38',
    ]:
        assert marker not in body


def test_no_next_monthly_contract_fabrication():
    body = read(JS).lower()

    assert "next monthly call" not in body
    assert "next monthly put" not in body


def test_manual_live_owner_authority():
    body = read(MODES)

    section = body[
        body.index(
            "[MODE_MANUAL_LIVE_1]"
        ):
        body.index(
            "[MODE_HYBRID]"
        )
    ]

    assert (
        'contract_choice_authority: "OWNER"'
        in section
    )

    assert (
        "owner_external_execution: true"
        in section
    )

    assert (
        "broker_execution: false"
        in section
    )

    assert (
        "automatic_execution: false"
        in section
    )


def test_hybrid_user_authority():
    body = read(MODES)

    section = body[
        body.index(
            "[MODE_HYBRID]"
        ):
        body.index(
            "[MODE_AUTOMATED]"
        )
    ]

    assert (
        'contract_choice_authority: "USER"'
        in section
    )

    assert (
        "ranked_contract_set_visible: true"
        in section
    )

    assert (
        "broker_execution: false"
        in section
    )


def test_automated_locked():
    body = read(MODES)

    section = body[
        body.index(
            "[MODE_AUTOMATED]"
        ):
        body.index(
            "function normalizeMode"
        )
    ]

    assert "locked: true" in section

    assert (
        "automatic_execution: false"
        in section
    )


def test_rank_one_does_not_become_selection_automatically():
    body = read(JS)

    assert (
        "Ranked #1 is NOT silently promoted"
        in body
    )

    assert (
        "state.selectedContract =\n                contract;"
        in body
        or
        "state.selectedContract = contract;"
        in body
    )


def test_browser_does_not_call_engine_selector():
    body = read(JS)

    assert (
        "choose_best_option("
        not in body
    )

    assert (
        "choose_best_option_contract("
        not in body
    )


def test_no_direct_market_fetch():
    body = read(JS).lower()

    assert 'fetch("http' not in body
    assert "fetch('http" not in body
    assert "yfinance" not in body


def test_no_broker_execution():
    combined = (
        read(JS)
        +
        read(MODES)
    )

    assert re.search(
        r"broker_execution\s*:\s*false",
        combined,
    )

    assert re.search(
        r"automatic_execution\s*:\s*false",
        combined,
    )


def test_options_bridge_preserved():
    contract = read(OPTIONS_CONTRACT)
    adapter = read(ADAPTER)

    assert (
        "OB_OPTIONS_RESEARCH_V1"
        in contract
    )

    assert (
        "options_by_symbol:"
        in adapter
    )

    assert (
        "option_chains:"
        in adapter
    )


def test_soulaana_is_progressive_disclosure():
    body = read(TEMPLATE)

    location = body.index(
        'id="obtc-soulaana-drawer"'
    )

    window = body[
        location - 80:
        location + 180
    ]

    assert "hidden" in window


def test_dark_glass_visual_layer():
    body = read(CSS)

    assert "--obtc-bg: #06070c" in body
    assert "backdrop-filter" in body
    assert ".obtc-workspace" in body
