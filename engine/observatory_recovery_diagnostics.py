
# ============================================================
# OBSERVATORY RECOVERY DIAGNOSTICS
# Patch label:
# OBSERVATORY_PATCH_QUOTE_QUALITY_AND_PORTFOLIO_DETECTOR_20260514
# Purpose:
# - Robustly locate open positions across Observatory data files.
# - Diagnose option quote quality and zero bid/ask chains.
# - Distinguish direct strategy reads from safe strategy writes.
# ============================================================

import os
import re
import ast
import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path("/content/SimpleeMrkTrade")
DATA_ROOT = PROJECT_ROOT / "data"


POSITION_KEYS = {
    "trade_id",
    "symbol",
    "status",
    "position_status",
    "vehicle",
    "vehicle_selected",
    "entry",
    "entry_price",
    "entry_premium",
    "current",
    "current_price",
    "current_premium",
    "monitoring",
    "monitoring_mode",
    "price_basis",
    "basis",
}

QUOTE_KEYS = {
    "bid",
    "ask",
    "last",
    "mark",
    "open_interest",
    "openInterest",
    "volume",
    "contract_score",
    "quote_quality",
    "execution_category",
    "execution_reason",
    "quote_flags",
    "contractSymbol",
    "contract_symbol",
    "option_symbol",
    "expiration",
    "expiry",
    "right",
    "strike",
}


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        return float(value)
    except Exception:
        return default


def _safe_str(value, default=""):
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def _read_json(path):
    path = Path(path)
    try:
        if not path.exists() or not path.is_file():
            return None
        # Keep this safe for Colab. Large ledger files can be huge.
        if path.stat().st_size > 85 * 1024 * 1024:
            return {
                "__skipped_large_file__": True,
                "path": str(path),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
            }
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        return {
            "__json_read_error__": str(exc),
            "path": str(path),
        }


def _walk_json(obj, path="root", max_items=250000):
    """
    Yield (path, value) pairs for nested JSON-ish structures.
    Has a max item guard so giant ledgers don't freeze the notebook.
    """
    seen = 0
    stack = [(path, obj)]
    while stack and seen < max_items:
        current_path, current = stack.pop()
        seen += 1
        yield current_path, current

        if isinstance(current, dict):
            for k, v in reversed(list(current.items())):
                stack.append((f"{current_path}.{k}", v))
        elif isinstance(current, list):
            for i, v in reversed(list(enumerate(current))):
                stack.append((f"{current_path}[{i}]", v))


def _looks_like_position(record):
    if not isinstance(record, dict):
        return False

    keys = set(record.keys())
    if not keys.intersection(POSITION_KEYS):
        return False

    symbol = _safe_str(record.get("symbol", "")).strip()
    if not symbol:
        return False

    status_blob = " ".join(
        _safe_str(record.get(k, ""))
        for k in ("status", "position_status", "execution_status")
    ).upper()

    if "OPEN" in status_blob:
        return True

    # Some current position records do not stamp status cleanly but do have live position fields.
    has_live_quantity = (
        _safe_float(record.get("shares"), 0.0) > 0
        or _safe_float(record.get("contracts"), 0.0) > 0
        or _safe_float(record.get("quantity"), 0.0) > 0
    )
    has_entry = (
        _safe_float(record.get("entry"), 0.0) > 0
        or _safe_float(record.get("entry_price"), 0.0) > 0
        or _safe_float(record.get("entry_premium"), 0.0) > 0
    )

    closed_blob = status_blob + " " + _safe_str(record.get("closed_at", "")).upper()
    if has_live_quantity and has_entry and "CLOSED" not in closed_blob:
        return True

    return False


def _normalize_position(record, source_path="", json_path=""):
    vehicle = (
        record.get("vehicle")
        or record.get("vehicle_selected")
        or record.get("selected_vehicle")
        or record.get("asset_type")
        or "UNKNOWN"
    )
    monitoring = (
        record.get("monitoring")
        or record.get("monitoring_mode")
        or record.get("price_basis")
        or record.get("basis")
        or ""
    )
    entry = (
        record.get("entry_premium")
        or record.get("entry")
        or record.get("entry_price")
        or record.get("avg_entry")
        or 0
    )
    current = (
        record.get("current_premium")
        or record.get("current")
        or record.get("current_price")
        or record.get("mark")
        or record.get("last")
        or 0
    )
    return {
        "symbol": _safe_str(record.get("symbol", "")).upper(),
        "trade_id": _safe_str(record.get("trade_id") or record.get("id") or ""),
        "vehicle": _safe_str(vehicle).upper(),
        "status": _safe_str(record.get("status", "")),
        "position_status": _safe_str(record.get("position_status", "")),
        "entry": entry,
        "current": current,
        "monitoring": _safe_str(monitoring),
        "basis": _safe_str(record.get("basis") or record.get("price_basis") or record.get("monitoring_mode") or ""),
        "source_file": source_path,
        "json_path": json_path,
    }


def discover_json_files(root=None):
    root = Path(root or PROJECT_ROOT)
    preferred = [
        DATA_ROOT / "open_positions.json",
        DATA_ROOT / "paper_portfolio.json",
        DATA_ROOT / "portfolio.json",
        DATA_ROOT / "account_state.json",
        DATA_ROOT / "canonical_ledger.json",
        DATA_ROOT / "trade_journal.json",
        DATA_ROOT / "trade_log.json",
        DATA_ROOT / "position_monitor.json",
        DATA_ROOT / "simulation_state.json",
    ]

    files = []
    for p in preferred:
        if p.exists() and p not in files:
            files.append(p)

    if DATA_ROOT.exists():
        for p in DATA_ROOT.rglob("*.json"):
            if p not in files:
                files.append(p)

    return files


def find_open_positions(root=None, verbose=False):
    """
    Return:
    {
      "open_count": int,
      "positions": list[dict],
      "files_checked": int,
      "sources": list[str],
      "errors": list[dict]
    }
    """
    files = discover_json_files(root)
    positions = []
    errors = []
    seen = set()

    for file_path in files:
        payload = _read_json(file_path)
        if payload is None:
            continue
        if isinstance(payload, dict) and payload.get("__json_read_error__"):
            errors.append(payload)
            continue

        for json_path, item in _walk_json(payload):
            if not _looks_like_position(item):
                continue

            pos = _normalize_position(item, str(file_path), json_path)
            key = (
                pos.get("trade_id") or "",
                pos.get("symbol") or "",
                pos.get("vehicle") or "",
                pos.get("source_file") or "",
                pos.get("json_path") or "",
            )
            if key in seen:
                continue
            seen.add(key)
            positions.append(pos)

    # Deduplicate harder by trade_id when present.
    by_trade_id = {}
    no_trade_id = []
    for pos in positions:
        tid = pos.get("trade_id")
        if tid:
            by_trade_id[tid] = pos
        else:
            no_trade_id.append(pos)

    final_positions = list(by_trade_id.values()) + no_trade_id

    result = {
        "open_count": len(final_positions),
        "positions": final_positions,
        "files_checked": len(files),
        "sources": sorted(set(p.get("source_file", "") for p in final_positions if p.get("source_file"))),
        "errors": errors[:10],
    }

    if verbose:
        print("OPEN POSITION DETECTOR:", {
            "open_count": result["open_count"],
            "files_checked": result["files_checked"],
            "sources": result["sources"],
            "error_count": len(errors),
        })
        for pos in final_positions:
            print({
                "symbol": pos["symbol"],
                "trade_id": pos["trade_id"],
                "vehicle": pos["vehicle"],
                "status": pos["status"],
                "position_status": pos["position_status"],
                "entry": pos["entry"],
                "current": pos["current"],
                "monitoring": pos["monitoring"],
                "basis": pos["basis"],
                "source_file": pos["source_file"],
            })

    return result


def _looks_like_option_quote(record):
    if not isinstance(record, dict):
        return False

    keys = set(record.keys())
    if not keys.intersection(QUOTE_KEYS):
        return False

    contract = record.get("contractSymbol") or record.get("contract_symbol") or record.get("option_symbol")
    right = record.get("right") or record.get("side")
    strike = record.get("strike")
    has_quote_numbers = any(k in record for k in ("bid", "ask", "last", "mark"))
    has_option_identity = bool(contract) or bool(right) or strike is not None

    return bool(has_quote_numbers and has_option_identity)


def classify_option_quote(record):
    bid = _safe_float(record.get("bid"), 0.0)
    ask = _safe_float(record.get("ask"), 0.0)
    last = _safe_float(record.get("last"), 0.0)
    mark = _safe_float(record.get("mark"), 0.0)
    volume = _safe_float(record.get("volume"), 0.0)
    oi = _safe_float(record.get("open_interest", record.get("openInterest", 0.0)), 0.0)
    score = _safe_float(record.get("contract_score"), 0.0)
    quote_flags = record.get("quote_flags") if isinstance(record.get("quote_flags"), dict) else {}

    zero_bid_ask = (bid <= 0 and ask <= 0)
    bid_missing = bid <= 0
    ask_missing = ask <= 0
    has_last_or_mark = last > 0 or mark > 0
    has_activity = volume > 0 or oi > 0

    if zero_bid_ask and has_last_or_mark and has_activity:
        diagnosis = "ZERO_BID_ASK_WITH_LAST_OR_MARK"
        explanation = "Chain has last/mark and activity, but bid/ask are unavailable. Treat as observed-only unless refreshed."
    elif zero_bid_ask:
        diagnosis = "ZERO_BID_ASK_NO_EXECUTABLE_QUOTE"
        explanation = "Bid/ask are both unavailable. Do not execute option from this snapshot."
    elif bid_missing or ask_missing:
        diagnosis = "ONE_SIDED_QUOTE"
        explanation = "Only one side of the quote is available. Do not execute without a cleaner refresh."
    elif score <= 0:
        diagnosis = "BAD_CONTRACT_SCORE"
        explanation = "Quote exists, but scoring says contract quality is unusable."
    elif score < 70:
        diagnosis = "LOW_CONTRACT_SCORE"
        explanation = "Quote exists, but contract quality is weak/caution."
    else:
        diagnosis = "QUOTE_LOOKS_EXECUTABLE"
        explanation = "Bid/ask and score look usable from this snapshot."

    return {
        "diagnosis": diagnosis,
        "explanation": explanation,
        "zero_bid_ask": zero_bid_ask,
        "bid_missing": bid_missing,
        "ask_missing": ask_missing,
        "has_last_or_mark": has_last_or_mark,
        "has_activity": has_activity,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "volume": volume,
        "open_interest": oi,
        "contract_score": score,
        "quote_quality": record.get("quote_quality", ""),
        "execution_category": record.get("execution_category", ""),
        "execution_reason": record.get("execution_reason", ""),
        "contractSymbol": record.get("contractSymbol") or record.get("contract_symbol") or record.get("option_symbol") or "",
        "symbol": record.get("symbol", ""),
        "right": record.get("right", ""),
        "strike": record.get("strike", ""),
        "expiration": record.get("expiration") or record.get("expiry") or "",
        "quote_flags": quote_flags,
    }


def diagnose_option_quotes(root=None, limit=80, verbose=False):
    files = discover_json_files(root)
    quotes = []
    seen = set()

    for file_path in files:
        payload = _read_json(file_path)
        if payload is None:
            continue
        if isinstance(payload, dict) and (payload.get("__json_read_error__") or payload.get("__skipped_large_file__")):
            continue

        for json_path, item in _walk_json(payload):
            if not _looks_like_option_quote(item):
                continue

            diag = classify_option_quote(item)
            key = (
                diag.get("contractSymbol", ""),
                diag.get("symbol", ""),
                diag.get("expiration", ""),
                diag.get("strike", ""),
                diag.get("right", ""),
                str(file_path),
                json_path,
            )
            if key in seen:
                continue
            seen.add(key)
            diag["source_file"] = str(file_path)
            diag["json_path"] = json_path
            quotes.append(diag)

            if len(quotes) >= limit:
                break
        if len(quotes) >= limit:
            break

    summary = {}
    for q in quotes:
        summary[q["diagnosis"]] = summary.get(q["diagnosis"], 0) + 1

    result = {
        "quote_count": len(quotes),
        "summary": summary,
        "quotes": quotes,
        "files_checked": len(files),
    }

    if verbose:
        print("OPTION QUOTE DIAGNOSTICS:", {
            "quote_count": result["quote_count"],
            "summary": result["summary"],
            "files_checked": result["files_checked"],
        })
        for q in quotes[:25]:
            print({
                "symbol": q["symbol"],
                "contract": q["contractSymbol"],
                "diagnosis": q["diagnosis"],
                "bid": q["bid"],
                "ask": q["ask"],
                "last": q["last"],
                "mark": q["mark"],
                "volume": q["volume"],
                "open_interest": q["open_interest"],
                "score": q["contract_score"],
                "quality": q["quote_quality"],
                "execution_category": q["execution_category"],
                "reason": q["execution_reason"],
            })

    return result


class _StrategyReadVisitor(ast.NodeVisitor):
    def __init__(self):
        self.reads = []
        self.writes = []

    def visit_Subscript(self, node):
        is_strategy_subscript = False
        try:
            if isinstance(node.slice, ast.Constant) and node.slice.value == "strategy":
                is_strategy_subscript = True
            elif hasattr(ast, "Index") and isinstance(node.slice, ast.Index):
                inner = node.slice.value
                if isinstance(inner, ast.Constant) and inner.value == "strategy":
                    is_strategy_subscript = True
        except Exception:
            is_strategy_subscript = False

        if is_strategy_subscript:
            ctx = type(node.ctx).__name__
            item = {"line": getattr(node, "lineno", None), "ctx": ctx}
            if isinstance(node.ctx, ast.Load):
                self.reads.append(item)
            elif isinstance(node.ctx, (ast.Store, ast.Del)):
                self.writes.append(item)

        self.generic_visit(node)


def scan_strategy_subscripts(path):
    """
    Distinguishes true dangerous reads from safe writes.
    Example:
      trade["strategy"] = strategy  -> write, safe
      x = trade["strategy"]         -> read, dangerous
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    visitor = _StrategyReadVisitor()
    visitor.visit(tree)

    lines = text.splitlines()
    for item in visitor.reads + visitor.writes:
        line_no = item.get("line")
        if line_no and 1 <= line_no <= len(lines):
            item["text"] = lines[line_no - 1].strip()

    return {
        "path": str(path),
        "dangerous_reads": visitor.reads,
        "safe_writes": visitor.writes,
        "dangerous_read_count": len(visitor.reads),
        "safe_write_count": len(visitor.writes),
    }


def print_recovery_snapshot(label="OBSERVATORY_RECOVERY_SNAPSHOT"):
    print("=" * 80)
    print(label)
    print("=" * 80)

    positions = find_open_positions(verbose=True)
    quotes = diagnose_option_quotes(verbose=True)

    bot_path = PROJECT_ROOT / "engine" / "bot.py"
    strategy_scan = None
    if bot_path.exists():
        try:
            strategy_scan = scan_strategy_subscripts(bot_path)
            print("STRATEGY SUBSCRIPT SCAN:", {
                "dangerous_read_count": strategy_scan["dangerous_read_count"],
                "safe_write_count": strategy_scan["safe_write_count"],
                "dangerous_reads": strategy_scan["dangerous_reads"][:10],
                "safe_writes": strategy_scan["safe_writes"][:10],
            })
        except Exception as exc:
            print("STRATEGY SUBSCRIPT SCAN ERROR:", exc)

    return {
        "positions": positions,
        "quotes": quotes,
        "strategy_scan": strategy_scan,
    }




# ============================================================
# OBSERVATORY_PATCH_FORCE_STRICT_ACTIVE_BOOK_DETECTOR_20260514
# Purpose:
# - Authoritative active-position detector for recovery tests.
# - This intentionally ignores archives, candidate logs, reports,
#   trade queues, journals, and stale account history.
# - The active execution book is data/positions.json.
# ============================================================

def _observatory_safe_upper(value, default=""):
    try:
        text = str(value if value is not None else "").strip().upper()
        return text if text else default
    except Exception:
        return default


def _observatory_safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _observatory_load_json_file(path, default=None):
    import json
    import os

    if default is None:
        default = []    

    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _observatory_walk_json_active_book(obj, path="root", max_depth=40):
    """
    Walk JSON safely, but only accept records that live under active-position
    style containers. This prevents raw_source_trade history, reports, and
    stale nested snapshots from being treated as active positions.
    """
    if max_depth <= 0:
        return

    if isinstance(obj, dict):
        yield path, obj
        for key, value in obj.items():
            key_text = str(key)
            next_path = f"{path}.{key_text}"
            yield from _observatory_walk_json_active_book(value, next_path, max_depth - 1)

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            next_path = f"{path}[{idx}]"
            yield from _observatory_walk_json_active_book(item, next_path, max_depth - 1)


def _observatory_path_allowed_for_active_book(json_path):
    """
    Only allow top-level/list-level position records and recognized active
    position containers. Reject nested raw_source_trade chains because those
    are historical payload echoes, not authoritative active book rows.
    """
    p = str(json_path or "").lower()

    if "raw_source_trade" in p:
        return False

    if "closed" in p:
        return False

    allowed_tokens = [
        "root[",
        "root.positions",
        "root.open_positions",
        "root.active_positions",
        "root.current_positions",
        "root.portfolio_positions",
        "root.holdings",
    ]

    return any(token in p for token in allowed_tokens)


def _observatory_record_looks_like_active_position(record):
    if not isinstance(record, dict):
        return False

    symbol = str(record.get("symbol") or record.get("ticker") or "").strip().upper()
    if not symbol:
        return False

    status = _observatory_safe_upper(
        record.get("position_status")
        or record.get("status")
        or record.get("state")
        or ""
    )

    # If status is present, it must be active/open-like.
    if status:
        active_statuses = {
            "OPEN",
            "ACTIVE",
            "HELD",
            "HOLDING",
            "FILLED_OPEN",
            "LIVE",
        }
        closed_statuses = {
            "CLOSED",
            "CLOSE",
            "EXITED",
            "SOLD",
            "TAKE_PROFIT",
            "STOP_LOSS",
            "CANCELLED",
            "CANCELED",
            "REJECTED",
            "EXPIRED",
            "ARCHIVED",
            "QUARANTINED",
            "EXECUTION_READY",
            "EXECUTION_READY_NOT_SELECTED",
            "SELECTED",
        }

        if status in closed_statuses:
            return False

        if status not in active_statuses and status != "":
            return False

    # Must have something position-like.
    position_like_keys = {
        "entry",
        "entry_price",
        "entry_premium",
        "premium_entry",
        "quantity",
        "qty",
        "shares",
        "contracts",
        "vehicle",
        "asset_type",
        "trade_id",
        "opened_at",
    }

    if not any(k in record for k in position_like_keys):
        return False

    return True


def _observatory_normalize_active_position(record, source_file="", json_path=""):
    symbol = str(record.get("symbol") or record.get("ticker") or "").strip().upper()

    vehicle = _observatory_safe_upper(
        record.get("vehicle")
        or record.get("asset_type")
        or record.get("trade_type")
        or "UNKNOWN",
        "UNKNOWN",
    )

    trade_id = str(
        record.get("trade_id")
        or record.get("id")
        or record.get("position_id")
        or ""
    ).strip()

    status = _observatory_safe_upper(record.get("status") or "OPEN", "OPEN")
    position_status = _observatory_safe_upper(
        record.get("position_status") or status or "OPEN",
        "OPEN",
    )

    entry = _observatory_safe_float(
        record.get("entry")
        or record.get("entry_price")
        or record.get("entry_premium")
        or record.get("premium_entry")
        or record.get("fill_price")
        or 0.0,
        0.0,
    )

    current = _observatory_safe_float(
        record.get("current")
        or record.get("current_price")
        or record.get("current_premium")
        or record.get("premium_current")
        or record.get("current_option_mark")
        or record.get("mark")
        or entry,
        entry,
    )

    monitoring = _observatory_safe_upper(
        record.get("monitoring")
        or record.get("monitoring_mode")
        or record.get("monitoring_price_type")
        or record.get("price_review_basis")
        or ""
    )

    basis = _observatory_safe_upper(
        record.get("basis")
        or record.get("pnl_basis")
        or record.get("price_basis")
        or record.get("price_review_basis")
        or ""
    )

    # Normalize option monitoring labels for cleaner diagnostics.
    if vehicle == "OPTION" and not monitoring:
        monitoring = "OPTION_PREMIUM"
    if vehicle == "OPTION" and not basis:
        basis = "OPTION_PREMIUM"
    if vehicle == "STOCK" and not monitoring:
        monitoring = "UNDERLYING"
    if vehicle == "STOCK" and not basis:
        basis = "STOCK_PRICE"

    return {
        "symbol": symbol,
        "trade_id": trade_id,
        "vehicle": vehicle,
        "status": status,
        "position_status": position_status,
        "entry": entry,
        "current": current,
        "monitoring": monitoring,
        "basis": basis,
        "source_file": str(source_file),
        "json_path": str(json_path),
    }


def find_open_positions(verbose=True):
    """
    Authoritative strict detector.

    Recovery tests must use this version. It only reads data/positions.json
    and only counts records that look like active book positions.
    """
    import os

    project_root = "/content/SimpleeMrkTrade"
    data_dir = os.path.join(project_root, "data")

    active_book_files = [
        os.path.join(data_dir, "positions.json"),
    ]

    positions = []
    sources = []
    errors = []

    for file_path in active_book_files:
        if not os.path.exists(file_path):
            continue

        payload = _observatory_load_json_file(file_path, default=[])

        for json_path, record in _observatory_walk_json_active_book(payload):
            if not _observatory_path_allowed_for_active_book(json_path):
                continue

            if not _observatory_record_looks_like_active_position(record):
                continue

            normalized = _observatory_normalize_active_position(
                record,
                source_file=file_path,
                json_path=json_path,
            )

            # De-dupe by trade_id if available; otherwise symbol/vehicle/path.
            dedupe_key = (
                normalized.get("trade_id")
                or f"{normalized.get('symbol')}|{normalized.get('vehicle')}|{normalized.get('json_path')}"
            )

            if not any(
                (p.get("trade_id") or f"{p.get('symbol')}|{p.get('vehicle')}|{p.get('json_path')}") == dedupe_key
                for p in positions
            ):
                positions.append(normalized)

        if positions and file_path not in sources:
            sources.append(file_path)

    result = {
        "open_count": len(positions),
        "positions": positions,
        "sources": sources,
        "files_checked": len(active_book_files),
        "error_count": len(errors),
        "errors": errors,
        "detector_mode": "strict_active_book_only_path_filtered",
        "allowed_path_tokens": [
            "positions",
            "open_positions",
            "active_positions",
            "current_positions",
            "portfolio_positions",
            "holdings",
        ],
        "patch_marker": "OBSERVATORY_PATCH_FORCE_STRICT_ACTIVE_BOOK_DETECTOR_20260514",
    }

    if verbose:
        print("STRICT OPEN POSITION DETECTOR:", {
            "open_count": result["open_count"],
            "files_checked": result["files_checked"],
            "sources": result["sources"],
            "error_count": result["error_count"],
            "detector_mode": result["detector_mode"],
        })
        for position in positions:
            print(position)

    return result
