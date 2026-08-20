from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "web/static/ob/ob_options_research_contract.js"
)

ADAPTER = (
    ROOT
    / "web/static/ob/ob_engine_feed_adapter.js"
)

SYMBOL = (
    ROOT
    / "web/static/ob/ob_symbol_page.js"
)

TEMPLATE = (
    ROOT
    / "web/templates/symbol_page.html"
)

OPTIONS_INTELLIGENCE = (
    ROOT
    / "engine/options_intelligence.py"
)

OPTIONS_LIFECYCLE = (
    ROOT
    / "engine/options_lifecycle.py"
)

VEHICLE_SELECTOR = (
    ROOT
    / "engine/vehicle_selector.py"
)

OPTION_REPRICING = (
    ROOT
    / "engine/option_repricing.py"
)


def read(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_existing_options_engine_is_preserved():
    intelligence = read(
        OPTIONS_INTELLIGENCE
    )

    lifecycle = read(
        OPTIONS_LIFECYCLE
    )

    selector = read(
        VEHICLE_SELECTOR
    )

    repricing = read(
        OPTION_REPRICING
    )

    assert "def choose_best_option(" in intelligence
    assert "def contract_quality_score(" in intelligence
    assert "def option_is_executable(" in intelligence

    assert "def build_options_lifecycle(" in lifecycle

    assert "LIFECYCLE_SELECTED" in lifecycle
    assert "LIFECYCLE_ENTERED" in lifecycle
    assert "LIFECYCLE_MANAGING" in lifecycle
    assert "LIFECYCLE_CLOSED" in lifecycle

    assert (
        "def choose_best_option_contract("
        in selector
    )

    assert "ranked_contracts" in selector

    assert "OPTION_PREMIUM" in repricing


def test_actual_adapter_function_is_project_payload():
    body = read(
        ADAPTER
    )

    assert (
        "function projectPayload(payload)"
        in body
    )

    assert (
        "OBDATA007_OPTIONS_RESEARCH_PROJECTION"
        in body
    )


def test_options_research_contract_exists():
    body = read(
        CONTRACT
    )

    assert "OB_OPTIONS_RESEARCH_V1" in body

    assert (
        "ENGINE_OPTIONS_INTELLIGENCE"
        in body
    )


def test_contract_preserves_research_fields():
    body = read(
        CONTRACT
    )

    required = [
        "contract_symbol",
        "contractSymbol",
        "right",
        "strike",
        "expiration",
        "dte",
        "bid",
        "ask",
        "last",
        "mark",
        "spread_pct",
        "volume",
        "open_interest",
        "implied_volatility",
        "contract_score",
        "contract_notes",
        "quote_quality",
        "quote_flags",
        "is_executable",
        "execution_reason",
    ]

    for marker in required:
        assert marker in body


def test_contract_reuses_ranked_engine_shapes():
    body = read(
        CONTRACT
    )

    for marker in [
        '"ranked_contracts"',
        '"top_ranked_contracts"',
        '"research_contracts"',
        '"option_chain"',
        '"options_chain"',
        '"options"',
        '"contracts"',
    ]:
        assert marker in body


def test_contract_has_no_fake_fallback():
    body = read(
        CONTRACT
    )

    assert "no_fake_fallback" in body
    assert "direct_market_fetch" in body
    assert "browser_yfinance" in body

    assert "Math.random(" not in body

    assert (
        'fetch("https://'
        not in body
    )

    assert (
        "fetch('https://"
        not in body
    )


def test_contract_never_marks_ob_as_selector():
    body = read(
        CONTRACT
    )

    assert re.search(
        r"ob_selected_contract\s*:\s*false",
        body,
    )

    assert re.search(
        r"automatic_contract_selection\s*:\s*false",
        body,
    )

    assert re.search(
        r"brokerage_execution\s*:\s*false",
        body,
    )

    assert re.search(
        r"automatic_execution\s*:\s*false",
        body,
    )


def test_project_payload_exposes_option_collections():
    body = read(
        ADAPTER
    )

    project = body[
        body.index(
            "function projectPayload(payload)"
        ):
    ]

    for marker in [
        "options:",
        "research_contracts:",
        "ranked_contracts:",
        "options_by_symbol:",
        "option_chains:",
        "options_chains:",
        "options_projection:",
    ]:
        assert marker in project


def test_options_use_existing_market_truth_gate():
    body = read(
        ADAPTER
    )

    project = body[
        body.index(
            "function projectPayload(payload)"
        ):
    ]

    assert re.search(
        r"research_contracts\s*:\s*displayEligible",
        project,
    )

    assert re.search(
        r"ranked_contracts\s*:\s*displayEligible",
        project,
    )

    assert re.search(
        r"options_by_symbol\s*:\s*displayEligible",
        project,
    )

    assert re.search(
        r"option_chains\s*:\s*displayEligible",
        project,
    )


def test_empty_projection_has_stable_empty_options_shape():
    body = read(
        ADAPTER
    )

    empty = body[
        body.index(
            "function emptyProjection("
        ):
        body.index(
            "function projectPayload(payload)"
        )
    ]

    for marker in [
        "options:",
        "research_contracts:",
        "ranked_contracts:",
        "options_by_symbol:",
        "option_chains:",
        "options_projection:",
    ]:
        assert marker in empty


def test_symbol_room_already_consumes_canonical_options():
    body = read(
        SYMBOL
    )

    assert "function optionsContainers(" in body

    assert "projection.options" in body

    assert (
        "projection.options_by_symbol"
        in body
    )

    assert (
        "projection.option_chains"
        in body
    )


def test_symbol_room_does_not_need_new_selector():
    body = read(
        SYMBOL
    )

    assert "choose_best_option(" not in body

    assert (
        "choose_best_option_contract("
        not in body
    )


def test_contract_loads_before_engine_adapter():
    body = read(
        TEMPLATE
    )

    contract_idx = body.index(
        "ob_options_research_contract.js"
    )

    adapter_idx = body.index(
        "ob_engine_feed_adapter.js"
    )

    symbol_idx = body.index(
        "ob_symbol_page.js"
    )

    assert (
        contract_idx
        <
        adapter_idx
        <
        symbol_idx
    )


def test_browser_does_not_import_yfinance():
    combined = (
        read(CONTRACT)
        +
        read(ADAPTER)
        +
        read(SYMBOL)
    ).lower()

    assert "import yfinance" not in combined
    assert "from yfinance" not in combined


def test_web_boundary_keeps_execution_disabled():
    combined = (
        read(CONTRACT)
        +
        read(SYMBOL)
    )

    assert re.search(
        r"brokerage_execution\s*:\s*false",
        combined,
    )

    assert re.search(
        r"automatic_execution\s*:\s*false",
        combined,
    )

    assert re.search(
        r"automatic_contract_selection\s*:\s*false",
        combined,
    )
