from pathlib import Path
import json

from web.ob_engine_account_authority import build_authority_registry
from web.ob_proof_demo_account import (
    SANITIZED_SCOREBOARD_AUTHORITY,
    activate_proof_demo_account,
    close_paper_position,
    event_count,
    get_account_state,
    open_paper_position,
)
from web.ob_proof_scoreboard import (
    CALCULATION_BASIS,
    PUBLIC_TRUTH_DISCLOSURE,
    SCHEMA_VERSION,
    build_sanitized_scoreboard,
    scoreboard_contract,
)


def db(tmp_path: Path) -> Path:
    return tmp_path / "proof_scoreboard.sqlite3"


def candidate(symbol="AAPL"):
    return {
        "symbol": symbol,
        "score": 930.25,
        "rank": 1,
        "signal": "CALL_BIAS",
        "nested": {
            "confidence": "HIGH",
        },
    }


def activate(path: Path, cash=2000):
    return activate_proof_demo_account(
        opening_demo_cash=cash,
        db_path=path,
    )


def open_stock(
    path: Path,
    *,
    symbol="AAPL",
    quantity=1,
    entry_price=10.0,
):
    return open_paper_position(
        candidate=candidate(symbol),
        owner_fit_bucket="NOW",
        owner_fit_fingerprint="fit_private_secret",
        owner_selected=True,
        instrument_type="STOCK",
        symbol=symbol,
        instrument_id=symbol,
        quantity=quantity,
        entry_price=entry_price,
        db_path=path,
    )


def collect_keys(value):
    found = set()

    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key))
            found |= collect_keys(child)

    elif isinstance(value, list):
        for child in value:
            found |= collect_keys(child)

    return found


def test_scoreboard_authority_is_now_active():
    assert SCHEMA_VERSION == "OB_PROOF_SANITIZED_SCOREBOARD_V1"
    assert (
        SANITIZED_SCOREBOARD_AUTHORITY
        ==
        "OB_PROOF_SANITIZED_SCOREBOARD_V1"
    )


def test_contract_is_projection_only_public_safe_and_locked():
    contract = scoreboard_contract()

    assert contract["authority"] == SCHEMA_VERSION
    assert contract["source_authority"] == "OB_PROOF_DEMO_ACCOUNT_V1"
    assert contract["source_account_key"] == "proof_demo"
    assert contract["source_capital_class"] == "SIMULATED_ONLY"

    assert contract["projection_only"] is True
    assert contract["durable_write"] is False
    assert contract["source_state_mutation"] is False

    assert contract["public_safe"] is True
    assert contract["aggregate_only"] is True
    assert contract["closed_samples_only"] is True

    assert contract["broker_submission"] is False
    assert contract["capital_movement"] is False
    assert contract["automatic_contract_selection"] is False
    assert contract["hybrid_execution"] is False
    assert contract["automatic_execution"] is False
    assert contract["live_auto_locked"] is True


def test_unactivated_scoreboard_fabricates_no_performance(tmp_path):
    projection = build_sanitized_scoreboard(
        db_path=db(tmp_path)
    )

    board = projection["scoreboard"]

    assert board["scoreboard_status"] == "NOT_ACTIVATED"
    assert board["completed_sample_count"] == 0
    assert board["wins"] == 0
    assert board["losses"] == 0
    assert board["flat"] == 0

    assert board["win_rate_pct"] is None
    assert board["net_realized_paper_pnl"] is None
    assert board["average_realized_paper_pnl"] is None
    assert board["gross_positive_paper_pnl"] is None
    assert board["gross_negative_paper_pnl"] is None
    assert board["profit_factor"] is None


def test_active_without_closed_samples_does_not_invent_results(tmp_path):
    path = db(tmp_path)

    activate(path)

    projection = build_sanitized_scoreboard(
        db_path=path
    )

    board = projection["scoreboard"]

    assert board["scoreboard_status"] == "READY_NO_COMPLETED_SAMPLES"
    assert board["completed_sample_count"] == 0
    assert board["win_rate_pct"] is None
    assert board["net_realized_paper_pnl"] == 0.0
    assert board["average_realized_paper_pnl"] is None
    assert board["profit_factor"] is None


def test_completed_paper_samples_project_aggregate_metrics(tmp_path):
    path = db(tmp_path)

    activate(path, 2000)

    first = open_stock(
        path,
        symbol="AAPL",
        quantity=10,
        entry_price=10.0,
    )

    close_paper_position(
        first["lifecycle_id"],
        exit_price=12.0,
        owner_closed=True,
        db_path=path,
    )

    second = open_stock(
        path,
        symbol="MSFT",
        quantity=5,
        entry_price=20.0,
    )

    close_paper_position(
        second["lifecycle_id"],
        exit_price=18.0,
        owner_closed=True,
        db_path=path,
    )

    projection = build_sanitized_scoreboard(
        db_path=path
    )

    board = projection["scoreboard"]

    assert board["scoreboard_status"] == "HAS_COMPLETED_SAMPLES"
    assert board["completed_sample_count"] == 2
    assert board["sample_size_band"] == "1_4"

    assert board["wins"] == 1
    assert board["losses"] == 1
    assert board["flat"] == 0

    assert board["win_rate_pct"] == 50.0

    assert board["net_realized_paper_pnl"] == 10.0
    assert board["average_realized_paper_pnl"] == 5.0
    assert board["gross_positive_paper_pnl"] == 20.0
    assert board["gross_negative_paper_pnl"] == 10.0
    assert board["profit_factor"] == 2.0


def test_open_positions_are_not_included_in_public_scoreboard(tmp_path):
    path = db(tmp_path)

    activate(path)

    open_stock(
        path,
        symbol="NVDA",
        quantity=3,
        entry_price=25.0,
    )

    projection = build_sanitized_scoreboard(
        db_path=path
    )

    board = projection["scoreboard"]

    assert board["completed_sample_count"] == 0
    assert board["open_samples_included"] is False

    dumped = json.dumps(
        projection,
        sort_keys=True,
    )

    assert "NVDA" not in dumped


def test_projection_suppresses_private_trade_and_account_fields(tmp_path):
    path = db(tmp_path)

    activate(path, 2500)

    opened = open_stock(
        path,
        symbol="SECRET_SYMBOL",
        quantity=2,
        entry_price=15.0,
    )

    close_paper_position(
        opened["lifecycle_id"],
        exit_price=17.0,
        owner_closed=True,
        db_path=path,
    )

    projection = build_sanitized_scoreboard(
        db_path=path
    )

    keys = collect_keys(
        projection
    )

    forbidden_keys = {
        "symbol",
        "instrument_id",
        "lifecycle_id",
        "candidate_fingerprint",
        "candidate_authority",
        "owner_fit_fingerprint",
        "owner_fit_bucket",
        "position_fingerprint",
        "entry_price",
        "exit_price",
        "entry_cost",
        "exit_proceeds",
        "quantity",
        "multiplier",
        "opened_at",
        "closed_at",
        "source_payload_json",
        "activation_fingerprint",
        "opening_demo_cash",
        "demo_cash",
        "demo_buying_power",
        "committed_demo_capital_at_cost",
        "recorded_demo_equity_at_cost",
        "unrealized_pnl",
        "activated_at",
        "updated_at",
    }

    assert not (
        keys
        &
        forbidden_keys
    )

    dumped = json.dumps(
        projection,
        sort_keys=True,
    )

    assert "SECRET_SYMBOL" not in dumped
    assert "fit_private_secret" not in dumped
    assert opened["lifecycle_id"] not in dumped


def test_projection_does_not_mutate_demo_ledger(tmp_path):
    path = db(tmp_path)

    activate(path)

    opened = open_stock(path)

    close_paper_position(
        opened["lifecycle_id"],
        exit_price=11.0,
        owner_closed=True,
        db_path=path,
    )

    before_state = get_account_state(
        db_path=path
    )

    before_events = event_count(
        db_path=path
    )

    build_sanitized_scoreboard(
        db_path=path
    )

    after_state = get_account_state(
        db_path=path
    )

    after_events = event_count(
        db_path=path
    )

    assert before_state == after_state
    assert before_events == after_events


def test_projection_is_deterministic_for_same_durable_state(tmp_path):
    path = db(tmp_path)

    activate(path)

    opened = open_stock(path)

    close_paper_position(
        opened["lifecycle_id"],
        exit_price=11.5,
        owner_closed=True,
        db_path=path,
    )

    first = build_sanitized_scoreboard(
        db_path=path
    )

    second = build_sanitized_scoreboard(
        db_path=path
    )

    assert first == second
    assert (
        first["projection_fingerprint"]
        ==
        second["projection_fingerprint"]
    )


def test_projection_has_explicit_simulated_truth_disclosure(tmp_path):
    path = db(tmp_path)

    activate(path)

    projection = build_sanitized_scoreboard(
        db_path=path
    )

    board = projection["scoreboard"]

    assert (
        board["truth_disclosure"]
        ==
        PUBLIC_TRUTH_DISCLOSURE
    )

    assert (
        board["calculation_basis"]
        ==
        CALCULATION_BASIS
    )

    assert board["truth_class"] == "SIMULATED_ONLY"
    assert board["live_marks_included"] is False
    assert board["real_broker_data_included"] is False


def test_account_authority_registry_converges_on_scoreboard():
    registry = build_authority_registry({
        "canonical_engine_adapter":
            "This is NOT another engine",

        "options_research_contract":
            "OB_OPTIONS_RESEARCH_V1",

        "owner_fit_eligibility":
            "OB_OWNER_FIT_ELIGIBILITY_V1",
    })

    proof = registry[
        "proof_demo_account"
    ]

    scoreboard = registry[
        "proof_sanitized_scoreboard"
    ]

    assert (
        proof["sanitized_scoreboard_authority"]
        ==
        SCHEMA_VERSION
    )

    assert scoreboard["authority"] == SCHEMA_VERSION
    assert scoreboard["service_present"] is True
    assert scoreboard["source_authority"] == "OB_PROOF_DEMO_ACCOUNT_V1"

    assert scoreboard["projection_only"] is True
    assert scoreboard["durable_write"] is False
    assert scoreboard["source_state_mutation"] is False

    assert scoreboard["symbols_exposed"] is False
    assert scoreboard["instrument_ids_exposed"] is False
    assert scoreboard["source_payload_exposed"] is False

    assert scoreboard["broker_submission"] is False
    assert scoreboard["capital_movement"] is False
    assert scoreboard["automatic_execution"] is False
    assert scoreboard["live_auto_locked"] is True


def test_scoreboard_service_has_no_flask_broker_or_execution_surface():
    source = Path(
        "web/ob_proof_scoreboard.py"
    ).read_text(
        encoding="utf-8"
    ).lower()

    forbidden = (
        "@app.route",
        "@bp.route",
        "from flask import",
        "import flask",
        "requests.post(",
        "ib_insync",
        "alpaca_trade_api",
        "place_order(",
        "submit_order(",
    )

    for token in forbidden:
        assert token not in source
