from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import json
import math
import sqlite3

from web.ob_owner_operating_profile import ACCOUNT_REGISTRY

SCHEMA_VERSION = "OB_PROOF_DEMO_ACCOUNT_V1"
SERVICE_VERSION = "OBPROOF001_005_PROOF_DEMO_ACCOUNT_ACTIVATION"
ACCOUNT_KEY = "proof_demo"
CAPITAL_CLASS = "SIMULATED_ONLY"
CANONICAL_MARKET_AUTHORITY = "existing_canonical_engine_feed"
OWNER_PROFILE_AUTHORITY = "OB_OWNER_OPERATING_PROFILE_V1"
OWNER_FIT_AUTHORITY = "OB_OWNER_FIT_ELIGIBILITY_V1"
SANITIZED_SCOREBOARD_AUTHORITY = "PENDING_OBPROOF006_010"
MODE_AUTHORITY = "PENDING_OBMODE"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "data" / "_local_archives" / "ob_proof_demo_account.sqlite3"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def stable_hash(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def clean_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def positive_number(value: Any, *, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric.")
    try:
        number = float(value)
    except Exception as exc:
        raise ValueError(f"{name} must be numeric.") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return round(number, 8)


def positive_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive whole number.")
    try:
        number = float(value)
    except Exception as exc:
        raise ValueError(f"{name} must be a positive whole number.") from exc
    if not math.isfinite(number) or not number.is_integer() or number <= 0:
        raise ValueError(f"{name} must be a positive whole number.")
    return int(number)


def proof_demo_contract() -> Dict[str, Any]:
    entry = ACCOUNT_REGISTRY.get(ACCOUNT_KEY)
    if not isinstance(entry, dict) or entry.get("key") != ACCOUNT_KEY:
        raise RuntimeError("Canonical owner operating-profile registry no longer contains proof_demo.")
    return {
        "schema_version": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "account_key": ACCOUNT_KEY,
        "account_label": entry.get("label") or "Proof / Demo",
        "account_registry_authority": OWNER_PROFILE_AUTHORITY,
        "owner_fit_authority": OWNER_FIT_AUTHORITY,
        "market_truth_authority": CANONICAL_MARKET_AUTHORITY,
        "capital_class": CAPITAL_CLASS,
        "real_capital": False,
        "broker_linked": False,
        "broker_submission": False,
        "capital_movement": False,
        "market_truth_mutation": False,
        "market_score_recalculation": False,
        "candidate_rank_recalculation": False,
        "automatic_contract_selection": False,
        "owner_selection_required": True,
        "owner_fit_now_required_for_paper_open": True,
        "paper_position_lifecycle": True,
        "durable_demo_state": True,
        "tracked_runtime_data_required": False,
        "mark_to_market_claimed": False,
        "live_broker_value_claimed": False,
        "sanitized_scoreboard_authority": SANITIZED_SCOREBOARD_AUTHORITY,
        "sanitized_public_metrics_emitted_here": False,
        "mode_authority": MODE_AUTHORITY,
        "hybrid_execution": False,
        "automatic_execution": False,
        "live_auto_locked": True,
    }


def resolve_db_path(db_path: Optional[Path] = None) -> Path:
    return Path(db_path) if db_path is not None else DEFAULT_DB_PATH


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_store(*, db_path: Optional[Path] = None) -> Path:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS account_state (
                account_key TEXT PRIMARY KEY,
                schema_version TEXT NOT NULL,
                opening_demo_cash REAL NOT NULL,
                demo_cash REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                activation_fingerprint TEXT NOT NULL,
                activated_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lifecycle_id TEXT NOT NULL UNIQUE,
                account_key TEXT NOT NULL,
                candidate_fingerprint TEXT NOT NULL,
                candidate_authority TEXT NOT NULL,
                owner_fit_fingerprint TEXT NOT NULL,
                owner_fit_bucket TEXT NOT NULL,
                instrument_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                instrument_id TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                multiplier INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                entry_cost REAL NOT NULL,
                exit_price REAL,
                exit_proceeds REAL,
                status TEXT NOT NULL,
                opened_at TEXT NOT NULL,
                closed_at TEXT,
                realized_pnl REAL,
                source_payload_json TEXT NOT NULL,
                position_fingerprint TEXT NOT NULL,
                FOREIGN KEY(account_key) REFERENCES account_state(account_key)
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_key TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                event_fingerprint TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
    return path


def append_event(conn: sqlite3.Connection, *, event_type: str, payload: Dict[str, Any], created_at: str) -> str:
    fingerprint = stable_hash({
        "schema_version": SCHEMA_VERSION,
        "account_key": ACCOUNT_KEY,
        "event_type": event_type,
        "payload": payload,
        "created_at": created_at,
    })
    conn.execute(
        "INSERT INTO events (account_key,event_type,payload_json,event_fingerprint,created_at) VALUES (?,?,?,?,?)",
        (ACCOUNT_KEY, event_type, canonical_json(payload), fingerprint, created_at),
    )
    return fingerprint


def state_from_conn(conn: sqlite3.Connection) -> Dict[str, Any]:
    row = conn.execute("SELECT * FROM account_state WHERE account_key = ?", (ACCOUNT_KEY,)).fetchone()
    base = proof_demo_contract()
    if row is None:
        return {
            **base,
            "status": "NOT_ACTIVATED",
            "activated": False,
            "opening_demo_cash": None,
            "demo_cash": None,
            "demo_buying_power": None,
            "committed_demo_capital_at_cost": None,
            "recorded_demo_equity_at_cost": None,
            "realized_pnl": None,
            "unrealized_pnl": None,
            "open_position_count": 0,
            "closed_position_count": 0,
            "activation_fingerprint": None,
            "activated_at": None,
            "updated_at": None,
        }
    open_row = conn.execute(
        "SELECT COUNT(*) AS count, COALESCE(SUM(entry_cost),0) AS committed FROM positions WHERE account_key = ? AND status = 'OPEN'",
        (ACCOUNT_KEY,),
    ).fetchone()
    closed_row = conn.execute(
        "SELECT COUNT(*) AS count FROM positions WHERE account_key = ? AND status = 'CLOSED'",
        (ACCOUNT_KEY,),
    ).fetchone()
    demo_cash = round(float(row["demo_cash"]), 8)
    committed = round(float(open_row["committed"]), 8)
    return {
        **base,
        "status": "PROOF_DEMO_ACTIVE",
        "activated": True,
        "opening_demo_cash": round(float(row["opening_demo_cash"]), 8),
        "demo_cash": demo_cash,
        "demo_buying_power": demo_cash,
        "committed_demo_capital_at_cost": committed,
        "recorded_demo_equity_at_cost": round(demo_cash + committed, 8),
        "realized_pnl": round(float(row["realized_pnl"]), 8),
        "unrealized_pnl": None,
        "open_position_count": int(open_row["count"]),
        "closed_position_count": int(closed_row["count"]),
        "activation_fingerprint": row["activation_fingerprint"],
        "activated_at": row["activated_at"],
        "updated_at": row["updated_at"],
    }


def get_account_state(*, db_path: Optional[Path] = None) -> Dict[str, Any]:
    path = initialize_store(db_path=db_path)
    with connect(path) as conn:
        return state_from_conn(conn)


def activate_proof_demo_account(*, opening_demo_cash: Any, account_key: Any = ACCOUNT_KEY, db_path: Optional[Path] = None) -> Dict[str, Any]:
    if clean_text(account_key).lower() != ACCOUNT_KEY:
        raise ValueError("OBPROOF001–005 only activates the explicit proof_demo account.")
    opening = positive_number(opening_demo_cash, name="opening_demo_cash")
    path = initialize_store(db_path=db_path)
    now = utc_now_iso()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "account_key": ACCOUNT_KEY,
        "capital_class": CAPITAL_CLASS,
        "opening_demo_cash": opening,
        "real_capital": False,
        "broker_linked": False,
    }
    fingerprint = stable_hash(payload)
    with connect(path) as conn:
        existing = conn.execute("SELECT * FROM account_state WHERE account_key = ?", (ACCOUNT_KEY,)).fetchone()
        if existing is not None:
            if round(float(existing["opening_demo_cash"]), 8) != opening:
                raise ValueError("proof_demo already has a different simulated opening balance; history will not be silently rewritten.")
            result = state_from_conn(conn)
            result["already_active"] = True
            return result
        conn.execute(
            "INSERT INTO account_state (account_key,schema_version,opening_demo_cash,demo_cash,realized_pnl,activation_fingerprint,activated_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (ACCOUNT_KEY, SCHEMA_VERSION, opening, opening, 0.0, fingerprint, now, now),
        )
        append_event(conn, event_type="PROOF_DEMO_ACTIVATED", payload=payload, created_at=now)
        result = state_from_conn(conn)
        result["already_active"] = False
        return result


def normalize_open(*, candidate: Dict[str, Any], candidate_authority: Any, owner_fit_bucket: Any, owner_fit_fingerprint: Any,
                   owner_selected: Any, instrument_type: Any, symbol: Any, instrument_id: Any, side: Any,
                   quantity: Any, entry_price: Any, multiplier: Any) -> Dict[str, Any]:
    if not isinstance(candidate, dict) or not candidate:
        raise ValueError("candidate must be a non-empty source-backed canonical candidate object.")
    candidate_copy = deepcopy(candidate)
    authority = clean_text(candidate_authority)
    if authority != CANONICAL_MARKET_AUTHORITY:
        raise ValueError("Proof/Demo must remain bound to existing canonical market truth.")
    bucket = clean_text(owner_fit_bucket).upper()
    if bucket != "NOW":
        raise ValueError("Only owner-fit NOW candidates may enter the Proof/Demo paper lifecycle.")
    fit_fp = clean_text(owner_fit_fingerprint)
    if not fit_fp:
        raise ValueError("owner_fit_fingerprint is required.")
    if owner_selected is not True:
        raise ValueError("Explicit owner selection is required.")
    kind = clean_text(instrument_type).upper()
    if kind not in {"STOCK", "OPTION"}:
        raise ValueError("instrument_type must be STOCK or OPTION.")
    sym = clean_text(symbol).upper()
    inst = clean_text(instrument_id)
    if not sym or not inst:
        raise ValueError("Explicit symbol and instrument_id are required; OBPROOF does not auto-select a contract.")
    normalized_side = clean_text(side).upper()
    if normalized_side != "LONG":
        raise ValueError("OBPROOF001–005 supports explicit LONG paper/sample positions only.")
    qty = positive_int(quantity, name="quantity")
    price = positive_number(entry_price, name="entry_price")
    if kind == "STOCK":
        mult = 1 if multiplier is None else positive_int(multiplier, name="multiplier")
        if mult != 1:
            raise ValueError("STOCK multiplier must equal 1.")
    else:
        if multiplier is None:
            raise ValueError("OPTION multiplier must be explicit; contract economics are not guessed.")
        mult = positive_int(multiplier, name="multiplier")
    cost = round(qty * mult * price, 8)
    return {
        "candidate": candidate_copy,
        "candidate_fingerprint": stable_hash(candidate_copy),
        "candidate_authority": authority,
        "owner_fit_bucket": bucket,
        "owner_fit_fingerprint": fit_fp,
        "instrument_type": kind,
        "symbol": sym,
        "instrument_id": inst,
        "side": normalized_side,
        "quantity": qty,
        "multiplier": mult,
        "entry_price": price,
        "entry_cost": cost,
    }


def row_to_position(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "account_key": row["account_key"],
        "lifecycle_id": row["lifecycle_id"],
        "status": row["status"],
        "candidate_fingerprint": row["candidate_fingerprint"],
        "candidate_authority": row["candidate_authority"],
        "owner_fit_fingerprint": row["owner_fit_fingerprint"],
        "owner_fit_bucket": row["owner_fit_bucket"],
        "instrument_type": row["instrument_type"],
        "symbol": row["symbol"],
        "instrument_id": row["instrument_id"],
        "side": row["side"],
        "quantity": int(row["quantity"]),
        "multiplier": int(row["multiplier"]),
        "entry_price": round(float(row["entry_price"]), 8),
        "entry_cost": round(float(row["entry_cost"]), 8),
        "exit_price": None if row["exit_price"] is None else round(float(row["exit_price"]), 8),
        "exit_proceeds": None if row["exit_proceeds"] is None else round(float(row["exit_proceeds"]), 8),
        "realized_pnl": None if row["realized_pnl"] is None else round(float(row["realized_pnl"]), 8),
        "opened_at": row["opened_at"],
        "closed_at": row["closed_at"],
        "position_fingerprint": row["position_fingerprint"],
        "paper_only": True,
        "broker_submission": False,
        "capital_movement": False,
        "automatic_execution": False,
    }


def get_position(lifecycle_id: Any, *, db_path: Optional[Path] = None) -> Dict[str, Any]:
    position_id = clean_text(lifecycle_id)
    if not position_id:
        raise ValueError("lifecycle_id is required.")
    path = initialize_store(db_path=db_path)
    with connect(path) as conn:
        row = conn.execute("SELECT * FROM positions WHERE lifecycle_id = ?", (position_id,)).fetchone()
        if row is None:
            raise KeyError(position_id)
        return row_to_position(row)


def open_paper_position(*, candidate: Dict[str, Any], owner_fit_bucket: Any, owner_fit_fingerprint: Any,
                        owner_selected: Any, instrument_type: Any, symbol: Any, instrument_id: Any,
                        quantity: Any, entry_price: Any, multiplier: Any = None, side: Any = "LONG",
                        candidate_authority: Any = CANONICAL_MARKET_AUTHORITY,
                        db_path: Optional[Path] = None) -> Dict[str, Any]:
    item = normalize_open(
        candidate=candidate,
        candidate_authority=candidate_authority,
        owner_fit_bucket=owner_fit_bucket,
        owner_fit_fingerprint=owner_fit_fingerprint,
        owner_selected=owner_selected,
        instrument_type=instrument_type,
        symbol=symbol,
        instrument_id=instrument_id,
        side=side,
        quantity=quantity,
        entry_price=entry_price,
        multiplier=multiplier,
    )
    path = initialize_store(db_path=db_path)
    now = utc_now_iso()
    with connect(path) as conn:
        account = conn.execute("SELECT * FROM account_state WHERE account_key = ?", (ACCOUNT_KEY,)).fetchone()
        if account is None:
            raise ValueError("Proof/Demo must be explicitly activated before a paper position can open.")
        cash = round(float(account["demo_cash"]), 8)
        if item["entry_cost"] > cash + 1e-8:
            raise ValueError("Insufficient simulated Proof/Demo cash.")
        seq = int(conn.execute("SELECT COALESCE(MAX(id),0)+1 AS n FROM positions").fetchone()["n"])
        lifecycle_id = "proofpos_" + stable_hash({
            "account_key": ACCOUNT_KEY,
            "sequence": seq,
            "candidate_fingerprint": item["candidate_fingerprint"],
            "owner_fit_fingerprint": item["owner_fit_fingerprint"],
            "instrument_id": item["instrument_id"],
        })[:24]
        immutable = {
            "schema_version": SCHEMA_VERSION,
            "lifecycle_id": lifecycle_id,
            "account_key": ACCOUNT_KEY,
            **{k: item[k] for k in (
                "candidate_fingerprint", "candidate_authority", "owner_fit_fingerprint", "owner_fit_bucket",
                "instrument_type", "symbol", "instrument_id", "side", "quantity", "multiplier", "entry_price", "entry_cost"
            )},
            "paper_only": True,
            "broker_submission": False,
            "capital_movement": False,
        }
        position_fp = stable_hash(immutable)
        source_payload = {
            "candidate": item["candidate"],
            "candidate_authority": item["candidate_authority"],
            "owner_fit_bucket": item["owner_fit_bucket"],
            "owner_fit_fingerprint": item["owner_fit_fingerprint"],
            "owner_selected": True,
        }
        conn.execute(
            "INSERT INTO positions (lifecycle_id,account_key,candidate_fingerprint,candidate_authority,owner_fit_fingerprint,owner_fit_bucket,instrument_type,symbol,instrument_id,side,quantity,multiplier,entry_price,entry_cost,status,opened_at,source_payload_json,position_fingerprint) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'OPEN',?,?,?)",
            (lifecycle_id, ACCOUNT_KEY, item["candidate_fingerprint"], item["candidate_authority"], item["owner_fit_fingerprint"],
             item["owner_fit_bucket"], item["instrument_type"], item["symbol"], item["instrument_id"], item["side"],
             item["quantity"], item["multiplier"], item["entry_price"], item["entry_cost"], now,
             canonical_json(source_payload), position_fp),
        )
        conn.execute("UPDATE account_state SET demo_cash = ?, updated_at = ? WHERE account_key = ?",
                     (round(cash - item["entry_cost"], 8), now, ACCOUNT_KEY))
        append_event(conn, event_type="PAPER_POSITION_OPENED", payload={**immutable, "position_fingerprint": position_fp}, created_at=now)
    return get_position(lifecycle_id, db_path=path)


def close_paper_position(lifecycle_id: Any, *, exit_price: Any, owner_closed: Any,
                         db_path: Optional[Path] = None) -> Dict[str, Any]:
    if owner_closed is not True:
        raise ValueError("Explicit owner close confirmation is required.")
    position_id = clean_text(lifecycle_id)
    if not position_id:
        raise ValueError("lifecycle_id is required.")
    exit_value = positive_number(exit_price, name="exit_price")
    path = initialize_store(db_path=db_path)
    now = utc_now_iso()
    with connect(path) as conn:
        row = conn.execute("SELECT * FROM positions WHERE lifecycle_id = ?", (position_id,)).fetchone()
        if row is None:
            raise KeyError(position_id)
        if row["status"] != "OPEN":
            raise ValueError("Only OPEN paper positions can be closed.")
        qty = int(row["quantity"])
        mult = int(row["multiplier"])
        entry = float(row["entry_price"])
        proceeds = round(qty * mult * exit_value, 8)
        realized = round((exit_value - entry) * qty * mult, 8)
        account = conn.execute("SELECT * FROM account_state WHERE account_key = ?", (ACCOUNT_KEY,)).fetchone()
        if account is None:
            raise RuntimeError("Proof/Demo account state disappeared.")
        new_cash = round(float(account["demo_cash"]) + proceeds, 8)
        new_realized = round(float(account["realized_pnl"]) + realized, 8)
        conn.execute(
            "UPDATE positions SET exit_price=?, exit_proceeds=?, status='CLOSED', closed_at=?, realized_pnl=? WHERE lifecycle_id=?",
            (exit_value, proceeds, now, realized, position_id),
        )
        conn.execute("UPDATE account_state SET demo_cash=?, realized_pnl=?, updated_at=? WHERE account_key=?",
                     (new_cash, new_realized, now, ACCOUNT_KEY))
        append_event(conn, event_type="PAPER_POSITION_CLOSED", payload={
            "lifecycle_id": position_id,
            "exit_price": exit_value,
            "exit_proceeds": proceeds,
            "realized_pnl": realized,
            "owner_closed": True,
            "broker_submission": False,
            "capital_movement": False,
        }, created_at=now)
    return get_position(position_id, db_path=path)


def list_positions(*, status: Optional[str] = None, db_path: Optional[Path] = None):
    path = initialize_store(db_path=db_path)
    query = "SELECT * FROM positions WHERE account_key = ?"
    params = [ACCOUNT_KEY]
    if status is not None:
        normalized = clean_text(status).upper()
        if normalized not in {"OPEN", "CLOSED"}:
            raise ValueError("status must be OPEN or CLOSED.")
        query += " AND status = ?"
        params.append(normalized)
    query += " ORDER BY id ASC"
    with connect(path) as conn:
        return [row_to_position(row) for row in conn.execute(query, tuple(params)).fetchall()]


def event_count(*, db_path: Optional[Path] = None) -> int:
    path = initialize_store(db_path=db_path)
    with connect(path) as conn:
        return int(conn.execute("SELECT COUNT(*) AS count FROM events WHERE account_key = ?", (ACCOUNT_KEY,)).fetchone()["count"])
