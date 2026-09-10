from copy import deepcopy
from pathlib import Path
import pytest

from web.ob_engine_account_authority import build_authority_registry
from web.ob_owner_operating_profile import ACCOUNT_REGISTRY
from web.ob_proof_demo_account import (
    ACCOUNT_KEY,
    DEFAULT_DB_PATH,
    MODE_AUTHORITY,
    SANITIZED_SCOREBOARD_AUTHORITY,
    SCHEMA_VERSION,
    activate_proof_demo_account,
    close_paper_position,
    event_count,
    get_account_state,
    list_positions,
    open_paper_position,
    proof_demo_contract,
)


def db(tmp_path: Path) -> Path:
    return tmp_path / "proof_demo.sqlite3"


def candidate():
    return {"symbol": "AAPL", "score": 917.25, "rank": 1, "signal": "CALL_BIAS", "nested": {"confidence": "HIGH"}}


def activate(path: Path, cash=1000):
    return activate_proof_demo_account(opening_demo_cash=cash, db_path=path)


def open_stock(path: Path, **overrides):
    payload = {
        "candidate": candidate(),
        "owner_fit_bucket": "NOW",
        "owner_fit_fingerprint": "fit_abc123",
        "owner_selected": True,
        "instrument_type": "STOCK",
        "symbol": "AAPL",
        "instrument_id": "AAPL",
        "quantity": 10,
        "entry_price": 10.0,
        "db_path": path,
    }
    payload.update(overrides)
    return open_paper_position(**payload)


def test_canonical_registry_already_contains_proof_demo():
    assert ACCOUNT_REGISTRY["proof_demo"] == {"key": "proof_demo", "label": "Proof / Demo"}


def test_contract_is_simulated_only_and_locked():
    c = proof_demo_contract()
    assert c["schema_version"] == SCHEMA_VERSION
    assert c["account_key"] == ACCOUNT_KEY
    assert c["capital_class"] == "SIMULATED_ONLY"
    assert c["real_capital"] is False
    assert c["broker_linked"] is False
    assert c["broker_submission"] is False
    assert c["capital_movement"] is False
    assert c["automatic_contract_selection"] is False
    assert c["live_auto_locked"] is True


def test_unactivated_state_fabricates_no_balance(tmp_path):
    state = get_account_state(db_path=db(tmp_path))
    assert state["status"] == "NOT_ACTIVATED"
    assert state["activated"] is False
    assert state["opening_demo_cash"] is None
    assert state["demo_cash"] is None
    assert state["realized_pnl"] is None


def test_activation_requires_explicit_positive_simulated_cash(tmp_path):
    path = db(tmp_path)
    for bad in (0, -1, "", None, float("inf")):
        with pytest.raises(ValueError):
            activate_proof_demo_account(opening_demo_cash=bad, db_path=path)


def test_only_proof_demo_can_be_activated(tmp_path):
    with pytest.raises(ValueError):
        activate_proof_demo_account(opening_demo_cash=1000, account_key="personal", db_path=db(tmp_path))


def test_activation_is_durable_and_idempotent(tmp_path):
    path = db(tmp_path)
    first = activate(path, 2500)
    second = activate(path, 2500)
    reread = get_account_state(db_path=path)
    assert first["already_active"] is False
    assert second["already_active"] is True
    assert reread["opening_demo_cash"] == 2500.0
    assert reread["demo_cash"] == 2500.0
    assert reread["activation_fingerprint"] == first["activation_fingerprint"]


def test_existing_history_cannot_be_silently_recapitalized(tmp_path):
    path = db(tmp_path)
    activate(path, 1000)
    with pytest.raises(ValueError):
        activate(path, 2000)


def test_paper_stock_open_records_simulated_state(tmp_path):
    path = db(tmp_path)
    activate(path)
    pos = open_stock(path)
    state = get_account_state(db_path=path)
    assert pos["status"] == "OPEN"
    assert pos["paper_only"] is True
    assert pos["broker_submission"] is False
    assert pos["entry_cost"] == 100.0
    assert state["demo_cash"] == 900.0
    assert state["committed_demo_capital_at_cost"] == 100.0
    assert state["recorded_demo_equity_at_cost"] == 1000.0


def test_option_contract_and_multiplier_must_be_explicit(tmp_path):
    path = db(tmp_path)
    activate(path, 2000)
    with pytest.raises(ValueError):
        open_paper_position(candidate=candidate(), owner_fit_bucket="NOW", owner_fit_fingerprint="fit_opt",
                            owner_selected=True, instrument_type="OPTION", symbol="AAPL",
                            instrument_id="AAPL260918C00200000", quantity=1, entry_price=2.0, db_path=path)
    pos = open_paper_position(candidate=candidate(), owner_fit_bucket="NOW", owner_fit_fingerprint="fit_opt",
                              owner_selected=True, instrument_type="OPTION", symbol="AAPL",
                              instrument_id="AAPL260918C00200000", quantity=1, multiplier=100,
                              entry_price=2.0, db_path=path)
    assert pos["multiplier"] == 100
    assert pos["entry_cost"] == 200.0


def test_watch_and_not_yet_cannot_open(tmp_path):
    path = db(tmp_path)
    activate(path)
    for bucket in ("WATCH", "NOT_YET"):
        with pytest.raises(ValueError):
            open_stock(path, owner_fit_bucket=bucket)


def test_owner_selection_is_required(tmp_path):
    path = db(tmp_path)
    activate(path)
    with pytest.raises(ValueError):
        open_stock(path, owner_selected=False)


def test_insufficient_demo_cash_blocks_open(tmp_path):
    path = db(tmp_path)
    activate(path, 50)
    with pytest.raises(ValueError):
        open_stock(path)


def test_market_candidate_object_is_not_mutated_or_rescored(tmp_path):
    path = db(tmp_path)
    activate(path)
    c = candidate()
    before = deepcopy(c)
    open_paper_position(candidate=c, owner_fit_bucket="NOW", owner_fit_fingerprint="fit_truth",
                        owner_selected=True, instrument_type="STOCK", symbol="AAPL", instrument_id="AAPL",
                        quantity=1, entry_price=10, db_path=path)
    assert c == before
    assert c["score"] == 917.25
    assert c["rank"] == 1


def test_close_records_realized_paper_pnl(tmp_path):
    path = db(tmp_path)
    activate(path)
    opened = open_stock(path)
    closed = close_paper_position(opened["lifecycle_id"], exit_price=12.0, owner_closed=True, db_path=path)
    state = get_account_state(db_path=path)
    assert closed["status"] == "CLOSED"
    assert closed["realized_pnl"] == 20.0
    assert state["demo_cash"] == 1020.0
    assert state["realized_pnl"] == 20.0
    assert state["open_position_count"] == 0
    assert state["closed_position_count"] == 1


def test_close_requires_owner_confirmation(tmp_path):
    path = db(tmp_path)
    activate(path)
    opened = open_stock(path)
    with pytest.raises(ValueError):
        close_paper_position(opened["lifecycle_id"], exit_price=12, owner_closed=False, db_path=path)


def test_positions_and_events_persist(tmp_path):
    path = db(tmp_path)
    activate(path)
    opened = open_stock(path)
    rows = list_positions(db_path=path)
    assert len(rows) == 1
    assert rows[0]["lifecycle_id"] == opened["lifecycle_id"]
    assert event_count(db_path=path) == 2


def test_account_state_does_not_fake_mark_to_market(tmp_path):
    path = db(tmp_path)
    activate(path)
    open_stock(path)
    state = get_account_state(db_path=path)
    assert state["mark_to_market_claimed"] is False
    assert state["live_broker_value_claimed"] is False
    assert state["unrealized_pnl"] is None


def test_authority_registry_registers_new_sibling_and_preserves_obrisk():
    registry = build_authority_registry({
        "canonical_engine_adapter": "This is NOT another engine",
        "options_research_contract": "OB_OPTIONS_RESEARCH_V1",
        "owner_fit_eligibility": "OB_OWNER_FIT_ELIGIBILITY_V1",
    })
    proof = registry["proof_demo_account"]
    assert proof["authority"] == SCHEMA_VERSION
    assert proof["service_present"] is True
    assert proof["real_capital"] is False
    assert proof["broker_submission"] is False
    assert proof["capital_movement"] is False
    assert proof["automatic_contract_selection"] is False
    assert proof["live_auto_locked"] is True
    assert registry["owner_operating_profile"]["authority"] == "OB_OWNER_OPERATING_PROFILE_V1"
    assert registry["owner_fit_eligibility"]["authority"] == "OB_OWNER_FIT_ELIGIBILITY_V1"
    assert registry["trade_intent"]["authority"] == "OB_TRADE_INTENT_V1"


def test_scoreboard_stays_separate_and_mode_authority_is_active():
    c = proof_demo_contract()
    assert c["sanitized_scoreboard_authority"] == SANITIZED_SCOREBOARD_AUTHORITY == "OB_PROOF_SANITIZED_SCOREBOARD_V1"
    assert c["sanitized_public_metrics_emitted_here"] is False
    assert c["mode_authority"] == MODE_AUTHORITY == "OB_OPERATING_MODE_V1"
    assert c["hybrid_execution"] is False
    assert c["automatic_execution"] is False


def test_default_runtime_store_is_ignored_local_archive():
    normalized = str(DEFAULT_DB_PATH).replace("\\", "/")
    assert "/data/_local_archives/" in normalized


def test_service_has_no_flask_or_broker_client_surface():
    source = Path("web/ob_proof_demo_account.py").read_text(encoding="utf-8").lower()
    for token in ("@app.route", "@bp.route", "from flask import", "import flask", "requests.post(",
                  "ib_insync", "alpaca_trade_api", "place_order(", "submit_order("):
        assert token not in source
