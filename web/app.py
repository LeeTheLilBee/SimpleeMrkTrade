
import os
import sys
sys.path.insert(0, "/content/SimpleeMrkTrade")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine_v2.dashboard_contract import build_dashboard_contract

from engine_v2.replay_batch_builder import build_replay_batch
from engine_v2.replay_page_context_builder import build_replay_page_context

import json
from pathlib import Path
# ADD THESE IMPORTS TO web/app.py

from engine_v2.spotlight_fusion_adapter import build_spotlight_fusion_cards
from engine_v2.market_map_builder import build_market_map
from engine_v2.constellation_mapper import map_tiles_to_constellation
from engine_v2.symbol_hero_contract import build_symbol_hero_contract
from engine_v2.symbol_deep_dive_contract import build_symbol_deep_dive_contract
from engine_v2.horizontal_hero_contract import build_horizontal_hero_contract
from engine_v2.market_map_interaction_contract import build_market_map_interaction_contract
from engine_v2.map_layer_toggle_contract import build_map_layer_toggle_contract
from engine_v2.spotlight_page_contract import build_spotlight_page_contract
from engine_v2.mode_router import resolve_user_modes
from typing import Any, Dict, List, Optional

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from jinja2 import TemplateNotFound

import engine.market_universe as market_universe

# ADD THESE IMPORTS TO web/app.py

from engine_v2.app_fusion_helper import build_full_product_fusion
from engine_v2.symbol_page_fusion_adapter import build_symbol_page_fusion_view
from engine_v2.spotlight_fusion_adapter import build_spotlight_fusion_cards
from engine_v2.dashboard_fusion_adapter import build_dashboard_fusion_view
# ADD THESE IMPORTS NEAR YOUR OTHER IMPORTS IN web/app.py

from web.final_brain_routes_engine import (
    build_symbol_final_brain,
    build_all_final_brains,
)
from engine_v2.final_brain_live_helpers import (
    build_final_symbol_context,
    build_final_spotlight_context,
    build_final_dashboard_context,
)
from web.final_brain_routes_engine import build_final_all_symbol_cards


# compatibility wrappers so the rest of app.py does not need to change
def load_market_universe():
    return market_universe.load_market_universe()

def refresh_market_universe():
    return market_universe.refresh_market_universe()

def refresh_market_universe_if_stale(max_age_hours: int = 12):
    return market_universe.refresh_market_universe_if_stale(max_age_hours=max_age_hours)

def get_market_universe_summary():
    return market_universe.get_market_universe_summary()

from engine.my_plays import (
    get_my_plays,
    add_play,
    get_play,
    update_play,
    archive_play,
    add_user_position_from_play,
    get_user_positions,
    get_user_position,
    update_user_position,
    close_user_position,
    analyze_user_trades,
)

from engine.symbols import load_symbol_news, refresh_symbol_news

from engine.admin_product_analytics import (
    log_event,
    maybe_track_page_view,
    track_symbol_click,
    track_trade_click,
    track_upgrade_click,
    track_cta_click,
    track_premium_wall_seen,
    track_premium_content_view,
    track_rejection_interest,
    build_product_analytics,
    top_engaged_symbols,
    top_engaged_symbols_with_counts,
    most_underrated_symbols,
)

from engine.trade_intelligence import attach_trade_intelligence
from engine.signal_tiering import slice_signals_by_tier, spotlight_sections
from engine.position_health import attach_position_health
from engine.portfolio_intelligence import evaluate_portfolio
from engine.alert_engine import generate_alerts
from engine.system_brain import build_system_brain

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "simpleemrktrade-dev-key-change-later"
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "simpleemrktrade-dev-key-change-later"

# SECTION 13G — AUTOMATIC market_universe HOOK

from datetime import datetime, timedelta

_AUTO_REFRESH_STATE = {
    "last_attempt_at": None,
    "last_success_at": None,
    "last_error": "",
}


def ensure_market_universe_ready(force: bool = False, max_age_hours: int = 12, min_retry_seconds: int = 300):
    """
    Keeps market_universe wired in automatically without refreshing constantly.
    - refreshes if missing
    - refreshes if stale
    - throttles repeated retries after failures
    """
    global _AUTO_REFRESH_STATE

    now = datetime.now()
    last_attempt_at = _AUTO_REFRESH_STATE.get("last_attempt_at")

    if not force and last_attempt_at:
        if now - last_attempt_at < timedelta(seconds=min_retry_seconds):
            return {
                "ok": bool(_AUTO_REFRESH_STATE.get("last_success_at")),
                "skipped": True,
                "reason": "retry_throttled",
                "state": dict(_AUTO_REFRESH_STATE),
            }

    _AUTO_REFRESH_STATE["last_attempt_at"] = now
    summary_before = {}

    try:
        summary_before = market_universe.get_market_universe_summary() or {}
    except Exception:
        summary_before = {}

    total_before = int(summary_before.get("total", 0) or 0)

    try:
        needs_refresh = force or total_before == 0 or market_universe.market_universe_is_stale(max_age_hours=max_age_hours)

        if needs_refresh:
            rows = market_universe.refresh_market_universe()
            _AUTO_REFRESH_STATE["last_success_at"] = datetime.now().isoformat()
            _AUTO_REFRESH_STATE["last_error"] = ""
            return {
                "ok": True,
                "refreshed": True,
                "row_count": len(rows) if isinstance(rows, list) else 0,
                "state": dict(_AUTO_REFRESH_STATE),
            }

        rows = market_universe.load_market_universe()
        _AUTO_REFRESH_STATE["last_success_at"] = datetime.now().isoformat()
        _AUTO_REFRESH_STATE["last_error"] = ""
        return {
            "ok": True,
            "refreshed": False,
            "row_count": len(rows) if isinstance(rows, list) else 0,
            "state": dict(_AUTO_REFRESH_STATE),
        }

    except Exception as e:
        _AUTO_REFRESH_STATE["last_error"] = str(e)
        return {
            "ok": False,
            "refreshed": False,
            "error": str(e),
            "state": dict(_AUTO_REFRESH_STATE),
        }


@app.before_request
def auto_refresh_market_universe():
    try:
        refresh_market_universe_if_stale(max_age_hours=12)
    except Exception as e:
        print(f"[MARKET_UNIVERSE_AUTO_REFRESH] {e}")


@app.before_request
def auto_refresh_news_cache():
    try:
        pipeline = get_pipeline_status()
        freshness = _freshness_bucket(pipeline.get("news_sync_at"), stale_after_minutes=180)

        if freshness.get("is_stale"):
            universe = load_market_universe()
            if universe:
                refresh_news_for_symbols(
                    symbol_rows=universe,
                    limit_per_symbol=6,
                    max_symbols=250,
                    force=False,
                )
    except Exception as e:
        print(f"[NEWS_CACHE_AUTO_REFRESH] {e}")


# ============================================================
# FILE HELPERS
# ============================================================

def load_json(path: str, default: Any) -> Any:
    try:
        file_path = Path(path)
        if not file_path.exists():
            return default
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: str, payload: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_canonical_closed_trade_ledger():
    candidates = [
        ("data/trade_journal_export.csv", "csv"),
        ("data/trade_replay_source.json", "json"),
        ("data/trade_details.json", "json"),
    ]

    rows = []

    for path, kind in candidates:
        try:
            if kind == "csv":
                if not os.path.exists(path):
                    continue

                import csv
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rows.append(dict(row))

                if rows:
                    break

            elif kind == "json":
                data = load_json(path, [])
                if isinstance(data, list) and data:
                    rows = data
                    break

        except Exception as e:
            print(f"[CANONICAL_LEDGER_LOAD:{path}] {e}")

    normalized = []

    for row in rows:
        try:
            if not isinstance(row, dict):
                continue

            symbol = str(row.get("symbol", "") or row.get("ticker", "") or "").upper().strip()
            if not symbol:
                continue

            pnl_raw = row.get("pnl", row.get("realized_pnl", row.get("profit_loss", 0)))
            try:
                pnl = float(pnl_raw or 0)
            except Exception:
                pnl = 0.0

            direction = str(row.get("direction", row.get("strategy", row.get("side", ""))) or "").upper().strip()
            outcome = str(row.get("outcome", "") or "").strip().lower()

            if not outcome:
                if pnl > 0:
                    outcome = "win"
                elif pnl < 0:
                    outcome = "loss"
                else:
                    outcome = "flat"

            opened_at = row.get("opened_at") or row.get("entry_time") or row.get("timestamp") or ""
            closed_at = row.get("closed_at") or row.get("exit_time") or row.get("timestamp") or ""

            normalized.append({
                "symbol": symbol,
                "direction": direction or "UNKNOWN",
                "pnl": pnl,
                "outcome": outcome,
                "opened_at": opened_at,
                "closed_at": closed_at,
                "raw": row,
            })

        except Exception as e:
            print(f"[CANONICAL_LEDGER_NORMALIZE:{row}] {e}")

    return normalized


def enrich_trade_record(base: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(base, dict):
        return {}

    enriched = dict(base)
    raw = base.get("raw", {}) if isinstance(base.get("raw"), dict) else {}

    symbol = enriched.get("symbol") or raw.get("symbol")
    direction = enriched.get("direction") or raw.get("direction") or raw.get("strategy")
    pnl = float(enriched.get("pnl", 0) or 0)

    score_raw = raw.get("score", 0)
    confidence_raw = raw.get("confidence", "")
    reason_raw = str(raw.get("reason", "") or "").strip().upper()
    exit_explanation = str(raw.get("exit_explanation", "") or "").strip()

    try:
        score = float(score_raw or 0)
    except Exception:
        score = 0.0

    confidence = str(confidence_raw or "").strip().upper()

    enriched["symbol"] = symbol
    enriched["direction"] = direction
    enriched["pnl"] = pnl
    enriched["score"] = score
    enriched["confidence"] = confidence

    reason_hint = reason_raw

    if reason_hint == "TAKE_PROFIT" and score >= 180 and confidence == "HIGH":
        setup_family = "high_score_momentum"
    elif reason_hint == "TAKE_PROFIT" and score >= 120:
        setup_family = "strong_structured"
    elif reason_hint == "STOP_LOSS" and score >= 180:
        setup_family = "failed_high_score_momentum"
    elif reason_hint == "STOP_LOSS" and score >= 120:
        setup_family = "failed_structured"
    elif score >= 180 and confidence == "HIGH":
        setup_family = "high_score_momentum"
    elif score >= 120:
        setup_family = "structured"
    else:
        setup_family = "speculative"

    enriched["setup_family"] = setup_family

    if reason_hint == "TAKE_PROFIT" and score >= 180 and confidence == "HIGH":
        entry_quality = "high_conviction"
    elif reason_hint == "TAKE_PROFIT":
        entry_quality = "acceptable"
    elif reason_hint == "STOP_LOSS" and score >= 180:
        entry_quality = "overconfident"
    elif reason_hint == "STOP_LOSS" and score >= 120:
        entry_quality = "failed_clean"
    elif score >= 180 and confidence == "HIGH":
        entry_quality = "high_conviction"
    elif score >= 100 and confidence in {"HIGH", "MEDIUM"}:
        entry_quality = "acceptable"
    else:
        entry_quality = "weak"

    enriched["entry_quality"] = entry_quality

    enriched["exit_reason"] = reason_raw
    enriched["exit_explanation"] = exit_explanation

    failure_reason = ""
    success_reason = ""

    if enriched.get("outcome") == "loss":
        if reason_raw == "STOP_LOSS":
            failure_reason = "stopped_out"
        elif reason_raw == "TIME_EXIT":
            failure_reason = "time_exit_loss"
        elif score < 100:
            failure_reason = "weak_entry_structure"
        else:
            failure_reason = "loss_after_entry"
    elif enriched.get("outcome") == "win":
        if reason_raw == "TAKE_PROFIT":
            success_reason = "target_hit"
        elif score >= 180 and confidence == "HIGH":
            success_reason = "high_conviction_win"
        else:
            success_reason = "profitable_exit"

    enriched["failure_reason"] = failure_reason
    enriched["success_reason"] = success_reason

    enriched["market_regime"] = "unknown"
    enriched["volatility_state"] = "unknown"
    enriched["breadth"] = "unknown"
    enriched["engine_agreement"] = None
    enriched["thesis"] = []
    enriched["notes"] = ""

    return enriched


# ============================================================
# SECTION 73ZH — CALIBRATED SETUP FAMILY CLASSIFIER
# ============================================================

def classify_setup_family(trade: Dict[str, Any]) -> str:
    trade = trade or {}

    raw = trade.get("raw", {}) if isinstance(trade.get("raw", {}), dict) else {}

    candidates = [
        trade.get("setup_family"),
        trade.get("setup_type"),
        trade.get("pattern"),
        trade.get("thesis"),
        raw.get("setup_family"),
        raw.get("setup_type"),
        raw.get("pattern"),
        raw.get("thesis"),
        raw.get("notes"),
    ]

    text = " ".join(str(x or "") for x in candidates).strip().lower()

    if not text:
        return "structured"

    if "continuation" in text:
        return "continuation"
    if "breakout" in text:
        return "breakout"
    if "pullback" in text:
        return "pullback"
    if "reversal" in text:
        return "reversal"
    if "mean reversion" in text or "mean_reversion" in text:
        return "mean_reversion"
    if "trend" in text:
        return "trend"
    if "momentum" in text:
        return "momentum"
    if "bounce" in text:
        return "bounce"
    if "support" in text or "resistance" in text:
        return "levels"
    if "range" in text:
        return "range"
    if "scalp" in text:
        return "scalp"

    score = float(trade.get("score", raw.get("score", 0)) or 0)

    if score >= 85:
        return "momentum"
    if score >= 65:
        return "structured"
    return "unclear"


# ============================================================
# ENTRY QUALITY CLASSIFIER
# ============================================================

# ============================================================
# SECTION 73ZI — CALIBRATED ENTRY QUALITY CLASSIFIER
# ============================================================

def classify_entry_quality(trade: Dict[str, Any]) -> str:
    trade = trade or {}

    raw = trade.get("raw", {}) if isinstance(trade.get("raw", {}), dict) else {}

    explicit = str(
        trade.get("entry_quality")
        or raw.get("entry_quality")
        or ""
    ).strip().lower()

    if explicit in {"clean", "great", "ideal", "excellent"}:
        return "clean"
    if explicit in {"acceptable", "fine", "okay", "ok", "decent"}:
        return "acceptable"
    if explicit in {"late", "poor", "bad"}:
        return "late"
    if explicit in {"chased", "chase"}:
        return "chased"

    score = float(trade.get("score", raw.get("score", 0)) or 0)
    pnl = float(trade.get("pnl", 0) or 0)
    confidence = str(trade.get("confidence", raw.get("confidence", "")) or "").strip().upper()

    notes_blob = " ".join(
        str(x or "") for x in [
            trade.get("notes"),
            raw.get("notes"),
            raw.get("thesis"),
        ]
    ).lower()

    if "late" in notes_blob:
        return "late"
    if "chase" in notes_blob or "chased" in notes_blob:
        return "chased"
    if "clean" in notes_blob:
        return "clean"

    if score >= 85 and confidence in {"HIGH", "STRONG"}:
        return "clean"

    if score >= 70:
        return "acceptable"

    if score >= 50:
        return "late"

    if pnl > 0:
        return "acceptable"

    return "late"


def build_canonical_reporting_snapshot():
    raw_trades = load_canonical_closed_trade_ledger()

    closed_trades = []
    for t in raw_trades:
        enriched = enrich_trade_record(t)
        closed_trades.append(enriched)

    total_trades = len(closed_trades)
    wins = sum(1 for x in closed_trades if x.get("outcome") == "win")
    losses = sum(1 for x in closed_trades if x.get("outcome") == "loss")
    flats = sum(1 for x in closed_trades if x.get("outcome") == "flat")

    total_pnl = round(sum(float(x.get("pnl", 0) or 0) for x in closed_trades), 2)
    winrate = round((wins / total_trades), 2) if total_trades else 0.0

    strategy_counts = {}
    strategy_performance = {}

    for row in closed_trades:
        direction = str(row.get("direction", "UNKNOWN") or "UNKNOWN").upper()
        strategy_counts[direction] = strategy_counts.get(direction, 0) + 1

        if direction not in strategy_performance:
            strategy_performance[direction] = {
                "trades": 0,
                "wins": 0,
                "pnl": 0.0,
                "winrate": 0.0,
            }

        strategy_performance[direction]["trades"] += 1
        if row.get("outcome") == "win":
            strategy_performance[direction]["wins"] += 1
        strategy_performance[direction]["pnl"] += float(row.get("pnl", 0) or 0)

    for direction, stats in strategy_performance.items():
        trades = stats["trades"]
        wins_for_direction = stats["wins"]
        stats["pnl"] = round(stats["pnl"], 2)
        stats["winrate"] = round((wins_for_direction / trades), 2) if trades else 0.0

    positions = get_positions_with_intelligence()
    open_positions = [p for p in positions if str(p.get("status", "")).lower() != "closed"]
    closed_position_count = total_trades

    unrealized_total = 0.0
    unrealized_positions = []

    for p in open_positions:
        pnl = float((p.get("pnl") or p.get("unrealized_pnl") or 0) or 0)
        unrealized_total += pnl
        unrealized_positions.append({
            "symbol": p.get("symbol"),
            "unrealized_pnl": pnl,
        })

    unrealized_total = round(unrealized_total, 2)

    realized_pnl = total_pnl
    estimated_account_value = round(1000 + realized_pnl + unrealized_total, 2)
    buying_power = round(max(0, estimated_account_value), 2)

    equity_curve = []
    running_equity = 1000.0
    peak = 1000.0
    max_drawdown = 0.0

    for row in closed_trades:
        running_equity += float(row.get("pnl", 0) or 0)
        peak = max(peak, running_equity)
        drawdown = round(peak - running_equity, 2)
        max_drawdown = max(max_drawdown, drawdown)

        equity_curve.append({
            "equity": round(running_equity, 2),
            "drawdown": drawdown,
            "symbol": row.get("symbol"),
            "closed_at": row.get("closed_at", ""),
        })

    latest_symbol = closed_trades[-1]["symbol"] if closed_trades else None

    enriched_ledger = []
    for row in closed_trades:
        if not isinstance(row, dict):
            continue

        enriched_row = enrich_trade_record(row)
        enriched_ledger.append(enriched_row)

    return {
        "ledger": enriched_ledger,
        "performance": {
            "trades": total_trades,
            "wins": wins,
            "losses": losses,
            "flats": flats,
            "winrate": winrate,
            "total_pnl": total_pnl,
            "max_drawdown": round(max_drawdown, 2),
            "entries_today": 0,
            "closes_today": 0,
            "round_trips_today": 0,
            "realized_pnl_today": 0.0,
        },
        "analytics": {
            "trades": total_trades,
            "winrate": winrate,
            "strategies": strategy_counts,
            "last_trade": latest_symbol,
            "portfolio": {
                "open_positions": len(open_positions),
                "closed_positions": closed_position_count,
                "realized_pnl": realized_pnl,
            },
        },
        "portfolio_summary": {
            "open_positions": len(open_positions),
            "closed_positions": closed_position_count,
            "realized_pnl": realized_pnl,
        },
        "unrealized": {
            "total_unrealized": unrealized_total,
            "positions": unrealized_positions,
        },
        "strategy_performance": strategy_performance,
        "drawdown_history": equity_curve[-50:],
        "final_account_snapshot": {
            "cash": buying_power,
            "buying_power": buying_power,
            "equity": estimated_account_value,
            "open_positions": len(open_positions),
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_total,
            "estimated_account_value": estimated_account_value,
        },
    }


def write_canonical_reporting_snapshot():
    snapshot = build_canonical_reporting_snapshot()

    try:
        save_json("data/canonical_reporting_snapshot.json", snapshot)
    except Exception as e:
        print(f"[WRITE_CANONICAL_REPORTING_SNAPSHOT] {e}")

    return snapshot


# ============================================================
# SECTION 73N — CANONICAL SNAPSHOT ACCESSOR
# ============================================================

def get_canonical_snapshot() -> Dict[str, Any]:
    try:
        snapshot = write_canonical_reporting_snapshot()
        if not isinstance(snapshot, dict):
            return {}
        return snapshot
    except Exception as e:
        print(f"[CANONICAL SNAPSHOT ERROR] {e}")
        return {}


def performance_summary():
    snapshot = load_json("data/canonical_reporting_snapshot.json", {})
    if not isinstance(snapshot, dict) or not snapshot:
        snapshot = write_canonical_reporting_snapshot()
    return snapshot.get("performance", {})


def strategy_breakdown():
    snapshot = load_json("data/canonical_reporting_snapshot.json", {})
    if not isinstance(snapshot, dict) or not snapshot:
        snapshot = write_canonical_reporting_snapshot()
    return snapshot.get("strategy_performance", {})


def unrealized_pnl():
    snapshot = load_json("data/canonical_reporting_snapshot.json", {})
    if not isinstance(snapshot, dict) or not snapshot:
        snapshot = write_canonical_reporting_snapshot()
    return snapshot.get("unrealized", {})


def get_dashboard_snapshot():
    snapshot = load_json("data/canonical_reporting_snapshot.json", {})
    if not isinstance(snapshot, dict) or not snapshot:
        snapshot = write_canonical_reporting_snapshot()
    return snapshot.get("final_account_snapshot", {})


def build_portfolio_summary_from_canonical():
    snapshot = load_json("data/canonical_reporting_snapshot.json", {})
    if not isinstance(snapshot, dict) or not snapshot:
        snapshot = write_canonical_reporting_snapshot()
    return snapshot.get("portfolio_summary", {})


def load_backtest_summary():
    data = load_json("data/backtest_summary.json", {})
    if not isinstance(data, dict):
        data = {}
    return data


def template_exists(template_name: str) -> bool:
    try:
        app.jinja_env.get_or_select_template(template_name)
        return True
    except TemplateNotFound:
        return False


def render_template_safe(template_name: str, **context):
    if template_exists(template_name):
        return render_template(template_name, **context)

    fallback = """
    <!doctype html>
    <html>
    <head>
      <title>{{ title }}</title>
      <style>
        body { font-family: Arial, sans-serif; background: #0b1020; color: #f8fafc; padding: 40px; }
        .card { max-width: 900px; margin: 0 auto; background: #111827; padding: 24px; border-radius: 16px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>{{ title }}</h1>
        <p>{{ message }}</p>
      </div>
    </body>
    </html>
    """
    return render_template_string(
        fallback,
        title=context.get("title", template_name),
        message=context.get("message", f"Template '{template_name}' was not found."),
    )
# ============================================================
# LEARNING HELPERS
# ============================================================

# ============================================================
# SECTION 73C — TRADE OUTCOME CLASSIFIER
# ============================================================

def classify_trade_learning_outcome(trade: Dict[str, Any]) -> Dict[str, Any]:
    trade = trade or {}

    pnl = float(trade.get("pnl", 0) or 0)
    symbol = str(trade.get("symbol", "") or "").upper().strip()
    direction = str(trade.get("direction", trade.get("strategy", "")) or "").upper().strip()

    setup_family = str(trade.get("setup_family", "unknown") or "unknown").strip().lower()
    entry_quality = str(trade.get("entry_quality", "unknown") or "unknown").strip().lower()
    outcome = str(trade.get("outcome", "") or "").strip().lower()

    if not outcome:
        if pnl > 0:
            outcome = "win"
        elif pnl < 0:
            outcome = "loss"
        else:
            outcome = "flat"

    failure_tags = []
    success_tags = []

    if outcome == "loss":
        failure_tags.append("loss")

        if entry_quality == "weak":
            failure_tags.append("weak_entry_quality")
        elif entry_quality == "acceptable":
            failure_tags.append("acceptable_entry_loss")
        elif entry_quality == "high_conviction":
            failure_tags.append("high_conviction_loss")

        if setup_family == "speculative":
            failure_tags.append("setup_speculative")
        elif setup_family == "structured":
            failure_tags.append("setup_structured")
        elif setup_family == "strong_structured":
            failure_tags.append("setup_strong_structured")
        elif setup_family == "high_score_momentum":
            failure_tags.append("setup_high_score_momentum")

    elif outcome == "win":
        success_tags.append("profit")

        if entry_quality == "weak":
            success_tags.append("weak_entry_win")
        elif entry_quality == "acceptable":
            success_tags.append("acceptable_entry_win")
        elif entry_quality == "high_conviction":
            success_tags.append("high_conviction_win")

        if setup_family == "speculative":
            success_tags.append("setup_speculative")
        elif setup_family == "structured":
            success_tags.append("setup_structured")
        elif setup_family == "strong_structured":
            success_tags.append("setup_strong_structured")
        elif setup_family == "high_score_momentum":
            success_tags.append("setup_high_score_momentum")

    else:
        failure_tags.append("flat_result")

    headline = "Trade result classified."
    summary = "The learning engine reviewed this trade outcome."

    if outcome == "loss":
        headline = "Trade failed."
        summary = "The trade closed as a loss and should contribute to failure memory."
    elif outcome == "win":
        headline = "Trade succeeded."
        summary = "The trade closed profitably and should contribute to success memory."
    else:
        headline = "Trade finished flat."
        summary = "The trade closed flat and contributes weak learning pressure."

    return {
        "symbol": symbol,
        "direction": direction or "UNKNOWN",
        "setup_family": setup_family,
        "entry_quality": entry_quality,
        "outcome": outcome,
        "pnl": pnl,
        "headline": headline,
        "summary": summary,
        "failure_tags": failure_tags,
        "success_tags": success_tags,
    }


# ============================================================
# SECTION 73D — LEARNING MEMORY FROM CANONICAL LEDGER
# ============================================================

def build_learning_memory_from_ledger() -> Dict[str, Any]:
    snapshot = get_canonical_snapshot()
    ledger = snapshot.get("ledger", [])
    if not isinstance(ledger, list):
        ledger = []

    rows = []
    failure_counts = {}
    success_counts = {}
    by_symbol = {}
    by_setup = {}
    by_entry_quality = {}

    for item in ledger:
        if not isinstance(item, dict):
            continue

        raw = item.get("raw", {}) if isinstance(item.get("raw"), dict) else {}
        merged = dict(raw)
        merged.setdefault("symbol", item.get("symbol"))
        merged.setdefault("direction", item.get("direction"))
        merged.setdefault("pnl", item.get("pnl"))
        merged.setdefault("outcome", item.get("outcome"))
        merged.setdefault("setup_family", item.get("setup_family", "unknown"))
        merged.setdefault("entry_quality", item.get("entry_quality", "unknown"))

        classified = classify_trade_learning_outcome(merged)
        classified["setup_family"] = item.get("setup_family", "unknown")
        classified["entry_quality"] = item.get("entry_quality", "unknown")

        rows.append(classified)

        symbol = classified.get("symbol", "UNKNOWN")
        setup_family = classified.get("setup_family", "unknown")
        entry_quality = classified.get("entry_quality", "unknown")

        if symbol not in by_symbol:
            by_symbol[symbol] = {"wins": 0, "losses": 0, "flats": 0, "pnl": 0.0}

        if setup_family not in by_setup:
            by_setup[setup_family] = {"wins": 0, "losses": 0, "flats": 0, "pnl": 0.0}

        if entry_quality not in by_entry_quality:
            by_entry_quality[entry_quality] = {"wins": 0, "losses": 0, "flats": 0, "pnl": 0.0}

        if classified.get("outcome") == "win":
            by_symbol[symbol]["wins"] += 1
            by_setup[setup_family]["wins"] += 1
            by_entry_quality[entry_quality]["wins"] += 1
        elif classified.get("outcome") == "loss":
            by_symbol[symbol]["losses"] += 1
            by_setup[setup_family]["losses"] += 1
            by_entry_quality[entry_quality]["losses"] += 1
        else:
            by_symbol[symbol]["flats"] += 1
            by_setup[setup_family]["flats"] += 1
            by_entry_quality[entry_quality]["flats"] += 1

        pnl = float(classified.get("pnl", 0) or 0)
        by_symbol[symbol]["pnl"] += pnl
        by_setup[setup_family]["pnl"] += pnl
        by_entry_quality[entry_quality]["pnl"] += pnl

        for tag in classified.get("failure_tags", []):
            failure_counts[tag] = failure_counts.get(tag, 0) + 1

        for tag in classified.get("success_tags", []):
            success_counts[tag] = success_counts.get(tag, 0) + 1

    top_failures = sorted(
        [{"tag": k, "count": v} for k, v in failure_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )

    top_successes = sorted(
        [{"tag": k, "count": v} for k, v in success_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )

    for symbol in by_symbol:
        by_symbol[symbol]["pnl"] = round(by_symbol[symbol]["pnl"], 2)

    for setup_family in by_setup:
        by_setup[setup_family]["pnl"] = round(by_setup[setup_family]["pnl"], 2)

    for entry_quality in by_entry_quality:
        by_entry_quality[entry_quality]["pnl"] = round(by_entry_quality[entry_quality]["pnl"], 2)

    headline = "Learning memory is active." if rows else "No trade memory yet."
    summary = (
        "The engine is building outcome memory from canonical trade history."
        if rows else
        "The learning engine does not have enough closed trade history yet."
    )

    return {
        "headline": headline,
        "summary": summary,
        "total_classified": len(rows),
        "rows": rows,
        "top_failures": top_failures[:10],
        "top_successes": top_successes[:10],
        "by_symbol": by_symbol,
        "by_setup": by_setup,
        "by_entry_quality": by_entry_quality,
    }

# ============================================================
# SECTION 73E — LEARNING PRESSURE SUMMARY
# ============================================================

def build_learning_pressure_summary() -> Dict[str, Any]:
    memory = build_learning_memory_from_ledger()

    top_failures = memory.get("top_failures", []) or []
    top_successes = memory.get("top_successes", []) or []

    top_failure = top_failures[0] if top_failures else None
    top_success = top_successes[0] if top_successes else None

    if top_failure:
        headline = "The engine is seeing repeat failure pressure."
        summary = f"The strongest recurring failure pattern right now is {top_failure.get('tag', '').replace('_', ' ')}."
    elif top_success:
        headline = "The engine is seeing repeat success behavior."
        summary = f"The strongest recurring success pattern right now is {top_success.get('tag', '').replace('_', ' ')}."
    else:
        headline = "Learning pressure is quiet."
        summary = "The engine does not yet have enough classified history to detect strong recurring patterns."

    return {
        "headline": headline,
        "summary": summary,
        "top_failure": top_failure,
        "top_success": top_success,
        "memory": memory,
    }

# ============================================================
# SECTION 73F — LEARNING RECOMMENDATIONS
# ============================================================

def build_learning_recommendations() -> Dict[str, Any]:
    pressure = build_learning_pressure_summary()
    memory = pressure.get("memory", {}) or {}

    top_failures = memory.get("top_failures", []) or []
    recommendations = []

    for item in top_failures[:5]:
        tag = str(item.get("tag", "") or "")
        count = int(item.get("count", 0) or 0)

        if tag == "late_entry":
            recommendations.append({
                "tag": tag,
                "count": count,
                "headline": "Penalize late timing harder.",
                "body": "Late entries are recurring in failure memory. The engine should become less forgiving when timing quality is degraded.",
                "future_adjustment": "increase timing penalty",
            })
        elif tag == "loss":
            recommendations.append({
                "tag": tag,
                "count": count,
                "headline": "Loss memory is building.",
                "body": "The engine should route repeated losses into setup and environment review instead of treating them as isolated.",
                "future_adjustment": "increase failure review weight",
            })
        elif tag == "setup_continuation":
            recommendations.append({
                "tag": tag,
                "count": count,
                "headline": "Continuation setups need review.",
                "body": "Continuation trades are appearing repeatedly in failure memory and may need stricter gates.",
                "future_adjustment": "tighten continuation readiness",
            })
        else:
            recommendations.append({
                "tag": tag,
                "count": count,
                "headline": f"Review {tag.replace('_', ' ')} behavior.",
                "body": "This recurring pattern is showing up enough to deserve future scoring pressure.",
                "future_adjustment": "review and calibrate",
            })

    return {
        "headline": "Learning recommendations are active." if recommendations else "No learning recommendations yet.",
        "summary": (
            "The engine translated repeated outcome memory into future adjustments."
            if recommendations else
            "There is not enough repeated memory yet to recommend scoring changes."
        ),
        "items": recommendations,
        "top_item": recommendations[0] if recommendations else None,
    }

# ============================================================
# SECTION 73G — LEARNING DASHBOARD PAYLOAD
# ============================================================

def build_learning_dashboard_payload() -> Dict[str, Any]:
    memory = build_learning_memory_from_ledger()
    pressure = build_learning_pressure_summary()
    recommendations = build_learning_recommendations()

    return {
        "memory": memory,
        "pressure": pressure,
        "recommendations": recommendations,
    }


# ============================================================
# STABILITY HELPERS
# ============================================================

def build_admin_play_command_summary(plays):
    plays = plays or []

    for play in plays:
        if "activation_readiness" not in play:
            play["activation_readiness"] = classify_play_readiness(play)
        if "promotion_guidance" not in play:
            play["promotion_guidance"] = build_promotion_guidance(play)
        if "rebuild_profile" not in play:
            play["rebuild_profile"] = build_weak_play_rebuild_profile(play)

    plays_summary = build_my_plays_summary(plays)
    promotion_summary = plays_summary.get("promotion_summary", {}) or {}
    rebuild_summary = plays_summary.get("rebuild_summary", {}) or {}
    top_failure_causes = plays_summary.get("top_failure_causes", []) or []

    top_promotion_candidate = promotion_summary.get("top_candidate")
    top_near_miss = promotion_summary.get("top_near_miss")
    top_rebuild = rebuild_summary.get("top_rebuild")

    if top_promotion_candidate:
        command_headline = "Promotion candidate available."
        command_summary = "At least one play is strong enough to be considered for activation."
    elif top_near_miss:
        command_headline = "No promotion candidate yet, but something is developing."
        command_summary = "The queue is empty, but the system sees at least one play worth improving."
    elif top_rebuild:
        command_headline = "Playbook needs rebuilding."
        command_summary = "The current focus should be repairing weak ideas before thinking about promotion."
    else:
        command_headline = "No actionable playbook signal."
        command_summary = "The system does not currently see promotion or rebuild candidates."

    return {
        "headline": command_headline,
        "summary": command_summary,
        "top_failure_causes": top_failure_causes[:5],
        "promotion_summary": promotion_summary,
        "rebuild_summary": rebuild_summary,
        "top_promotion_candidate": top_promotion_candidate,
        "top_near_miss": top_near_miss,
        "top_rebuild": top_rebuild,
        "strongest_play": plays_summary.get("strongest_play"),
        "weakest_play": plays_summary.get("weakest_play"),
        "counts": {
            "total": plays_summary.get("total", 0),
            "ready": plays_summary.get("ready_to_activate", 0),
            "close": plays_summary.get("close_to_ready", 0),
            "weak": plays_summary.get("weak_or_pressured", 0),
            "watching": plays_summary.get("watching", 0),
        },
    }

def build_near_miss_promotion_candidates(plays):
    plays = plays or []

    results = []

    for play in plays:
        readiness = play.get("activation_readiness", {}) or {}
        score = int(readiness.get("score", 0) or 0)
        bucket = str(readiness.get("bucket", "") or "").upper()

        if bucket == "CLOSE" or score >= 50:
            results.append({
                "symbol": play.get("symbol"),
                "play_id": play.get("play_id"),
                "bucket": bucket,
                "score": score,
                "headline": readiness.get("headline"),
                "summary": readiness.get("summary"),
                "blockers": readiness.get("blockers", []),
                "guidance": readiness.get("guidance", []),
                "promotion_message": (play.get("promotion_guidance", {}) or {}).get("message"),
                "failure_tags": readiness.get("failure_tags", []),
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:5]


def build_promotion_queue_diagnosis(plays):
    plays = plays or []

    failure_clusters = build_failure_clusters(plays)
    near_misses = build_near_miss_promotion_candidates(plays)

    if not plays:
        return {
            "queue_empty": True,
            "headline": "No plays in system.",
            "summary": "You need to build your idea book before promotion can exist.",
            "top_blocker": None,
            "top_blocker_count": 0,
            "near_misses": [],
            "failure_clusters": [],
        }

    has_candidates = any(
        (p.get("activation_readiness", {}) or {}).get("bucket") in {"READY", "CLOSE"}
        for p in plays
    )

    if not has_candidates:
        all_weak = all(
            int((p.get("activation_readiness", {}) or {}).get("score", 0) or 0) < 30
            for p in plays
        )

        if all_weak:
            return {
                "queue_empty": True,
                "headline": "No viable setups right now.",
                "summary": "Your current ideas are structurally weak. Focus on rebuilding higher-quality setups instead of trying to promote them.",
                "top_blocker": failure_clusters[0]["cause"] if failure_clusters else None,
                "top_blocker_count": failure_clusters[0]["count"] if failure_clusters else 0,
                "near_misses": [],
                "failure_clusters": failure_clusters,
            }

        return {
            "queue_empty": True,
            "headline": "Nothing qualifies yet, but some are developing.",
            "summary": "Some plays are progressing, but none meet promotion standards yet.",
            "top_blocker": failure_clusters[0]["cause"] if failure_clusters else None,
            "top_blocker_count": failure_clusters[0]["count"] if failure_clusters else 0,
            "near_misses": near_misses,
            "failure_clusters": failure_clusters,
        }

    return {
        "queue_empty": False,
        "headline": "Promotion system active.",
        "summary": "You have plays moving through readiness stages.",
        "top_blocker": failure_clusters[0]["cause"] if failure_clusters else None,
        "top_blocker_count": failure_clusters[0]["count"] if failure_clusters else 0,
        "near_misses": near_misses,
        "failure_clusters": failure_clusters,
    }


def build_play_promotion_summary(plays):
    plays = plays or []

    promotion_queue = build_play_promotion_queue(plays)
    near_misses = build_near_miss_promotion_candidates(plays)
    diagnosis = build_promotion_queue_diagnosis(plays)

    ready_candidates = [p for p in promotion_queue if p.get("bucket") == "READY"]
    close_candidates = [p for p in promotion_queue if p.get("bucket") == "CLOSE"]

    top_candidate = promotion_queue[0] if promotion_queue else None
    top_near_miss = near_misses[0] if near_misses else None

    if promotion_queue:
        headline = "You have promotable plays."
        summary = "At least one play currently looks strong enough to be considered for live activation."
    elif near_misses:
        headline = "Your queue is close, not empty."
        summary = "Nothing qualifies yet, but some plays are close enough to improve."
    else:
        headline = "No promotion candidates yet."
        summary = "No plays currently deserve serious promotion consideration."

    return {
        "headline": headline,
        "summary": summary,
        "total_candidates": len(promotion_queue),
        "ready_candidates": len(ready_candidates),
        "close_candidates": len(close_candidates),
        "top_candidate": top_candidate,
        "top_near_miss": top_near_miss,
        "promotion_queue": promotion_queue[:10],
        "near_misses": near_misses[:5],
        "diagnosis": diagnosis,
    }

def build_play_promotion_candidate(play):
    play = play or {}

    readiness = play.get("activation_readiness", {}) or {}
    promotion = play.get("promotion_guidance", {}) or {}
    agreement = play.get("system_agreement", {}) or {}
    health = play.get("health", {}) or {}
    conviction = str(play.get("conviction", "Medium") or "Medium").strip().title()

    symbol = str(play.get("symbol", "") or "").strip().upper()
    bucket = str(readiness.get("bucket", "") or "").upper()
    readiness_score = int(readiness.get("score", 0) or 0)
    agreement_score = int(agreement.get("score", 0) or 0)
    health_score = int(health.get("score", 0) or 0)

    if bucket not in {"READY", "CLOSE"}:
        return None

    promotion_score = readiness_score

    if bucket == "READY":
        promotion_score += 12
    elif bucket == "CLOSE":
        promotion_score += 4

    if conviction == "High":
        promotion_score += 4
    elif conviction == "Medium":
        promotion_score += 1

    if agreement_score >= 80:
        promotion_score += 4

    if health_score >= 80:
        promotion_score += 4

    blockers = readiness.get("blockers", []) or []
    guidance = readiness.get("guidance", []) or []

    return {
        "symbol": symbol,
        "play_id": play.get("play_id"),
        "bucket": bucket,
        "promotion_score": max(0, promotion_score),
        "readiness_score": readiness_score,
        "agreement_score": agreement_score,
        "health_score": health_score,
        "headline": readiness.get("headline", ""),
        "summary": readiness.get("summary", ""),
        "promotion_message": promotion.get("message", ""),
        "promotion_focus": promotion.get("focus", []),
        "blockers": blockers[:3],
        "guidance": guidance[:3],
        "conviction": conviction,
        "status": play.get("status", "Open"),
        "direction": play.get("direction", ""),
    }

def build_play_promotion_queue(plays):
    plays = plays or []

    candidates = []

    for play in plays:
        try:
            candidate = build_play_promotion_candidate(play)
            if candidate:
                candidates.append(candidate)
        except Exception as e:
            print(f"[PROMOTION_QUEUE:{play.get('symbol', 'UNKNOWN')}] {e}")

    candidates = sorted(
        candidates,
        key=lambda x: (
            x.get("bucket") == "READY",
            x.get("promotion_score", 0),
            x.get("readiness_score", 0),
            x.get("agreement_score", 0),
            x.get("health_score", 0),
        ),
        reverse=True,
    )

    return candidates


def classify_play_readiness(play):
    play = play or {}

    status = str(play.get("status", "Open")).strip().lower()
    conviction = str(play.get("conviction", "Medium")).strip().lower()

    health = play.get("health", {}) or {}
    agreement = play.get("system_agreement", {}) or {}
    candidate = play.get("engine_candidate")
    feedback = play.get("system_feedback", []) or []

    health_score = int(health.get("score", 0) or 0)
    agreement_score = int(agreement.get("score", 0) or 0)
    health_label = str(health.get("label", "")).strip().upper()

    readiness_score = 0
    reasons = []
    blockers = []
    guidance = []
    failure_tags = []

    # -------------------------
    # STATUS
    # -------------------------
    if status in {"open", "watching"}:
        readiness_score += 10
        reasons.append("play is active")
    else:
        blockers.append("play is not active")
        failure_tags.append("inactive")

    # -------------------------
    # HEALTH
    # -------------------------
    if health_score >= 75:
        readiness_score += 30
        reasons.append("health is strong")
    elif health_score >= 55:
        readiness_score += 15
        reasons.append("health is stable")
        guidance.append("wait for cleaner structure before trusting this fully")
        failure_tags.append("mid_health")
    elif health_score >= 35:
        readiness_score += 5
        blockers.append("health is mixed")
        guidance.append("wait for cleaner structure before trusting this")
        failure_tags.append("weak_health")
    else:
        readiness_score -= 25
        blockers.append("health is weak")
        guidance.append("do not activate until structure improves")
        failure_tags.append("broken_health")

    # -------------------------
    # AGREEMENT
    # -------------------------
    if agreement_score >= 75:
        readiness_score += 30
        reasons.append("system agreement is strong")
    elif agreement_score >= 55:
        readiness_score += 15
        reasons.append("system agreement is usable")
        guidance.append("look for stronger alignment before entry")
        failure_tags.append("mid_agreement")
    elif agreement_score >= 35:
        readiness_score += 5
        blockers.append("system agreement is mixed")
        guidance.append("wait for better alignment across signals")
        failure_tags.append("weak_agreement")
    else:
        readiness_score -= 25
        blockers.append("system disagreement")
        guidance.append("do not take trades the system disagrees with")
        failure_tags.append("disagreement")

    # -------------------------
    # ENGINE TRACKING
    # -------------------------
    if candidate:
        readiness_score += 10
        reasons.append("engine is tracking this symbol")
    else:
        readiness_score -= 10
        blockers.append("not tracked by engine")
        guidance.append("align this setup with known engine patterns or expand engine coverage")
        failure_tags.append("no_engine")

    # -------------------------
    # CONVICTION
    # -------------------------
    if conviction == "high":
        readiness_score += 5
        reasons.append("high conviction")
    elif conviction == "medium":
        readiness_score += 2

    # -------------------------
    # PRESSURE CONDITIONS
    # -------------------------
    if health_label in {"BROKEN", "UNDER PRESSURE"}:
        readiness_score -= 15
        blockers.append("play is under pressure")
        guidance.append("let pressure resolve before entering")
        failure_tags.append("pressure")

    # -------------------------
    # FEEDBACK ANALYSIS
    # -------------------------
    for line in feedback:
        text = str(line).lower()

        if "counter-trend" in text:
            readiness_score -= 10
            blockers.append("counter-trend setup")
            guidance.append("align with dominant trend direction")
            failure_tags.append("counter_trend")

        if "defensive" in text:
            readiness_score -= 10
            blockers.append("defensive market environment")
            guidance.append("wait for better market conditions")
            failure_tags.append("bad_environment")

    readiness_score = max(0, min(100, readiness_score))

    # -------------------------
    # BUCKET
    # -------------------------
    if status not in {"open", "watching"}:
        bucket = "INACTIVE"
        headline = "Not eligible"
        summary = "This play is not active."
    elif readiness_score >= 80:
        bucket = "READY"
        headline = "Ready to activate"
        summary = "Strong structure and alignment."
    elif readiness_score >= 60:
        bucket = "CLOSE"
        headline = "Close to ready"
        summary = "Needs one or two improvements."
    elif readiness_score >= 40:
        bucket = "WATCH"
        headline = "Watch, don’t rush"
        summary = "Not strong enough yet."
    else:
        bucket = "WEAK"
        headline = "Weak setup"
        summary = "Too many issues right now."

    return {
        "score": readiness_score,
        "bucket": bucket,
        "headline": headline,
        "summary": summary,
        "reasons": reasons[:4],
        "blockers": blockers[:4],
        "guidance": guidance[:4],
        "failure_tags": failure_tags,
    }

def build_rebuild_suggestions_from_failure_tags(failure_tags):
    failure_tags = failure_tags or []

    suggestions = []
    promotable_conditions = []

    for tag in failure_tags:
        tag = str(tag or "").strip().lower()

        if tag == "mid_health":
            suggestions.append("Tighten the structure so the setup stops looking soft.")
            promotable_conditions.append("Health needs to move from stable into strong territory.")

        elif tag == "weak_health":
            suggestions.append("Wait for the chart structure to repair before trusting the setup.")
            promotable_conditions.append("Health needs to recover into at least workable territory.")

        elif tag == "broken_health":
            suggestions.append("Do not force this idea. Rebuild it only after the structure clearly recovers.")
            promotable_conditions.append("Broken behavior must fully resolve before promotion is possible.")

        elif tag == "mid_agreement":
            suggestions.append("Wait for stronger alignment between the setup and the system read.")
            promotable_conditions.append("Agreement needs to improve from usable to strong.")

        elif tag == "weak_agreement":
            suggestions.append("Do not trust this setup until agreement improves materially.")
            promotable_conditions.append("Agreement must move out of mixed territory.")

        elif tag == "disagreement":
            suggestions.append("Drop or rethink the setup unless the system read flips in its favor.")
            promotable_conditions.append("System disagreement must resolve before promotion.")

        elif tag == "no_engine":
            suggestions.append("Either align this setup more closely with engine patterns or expand engine coverage.")
            promotable_conditions.append("Engine tracking must recognize the symbol/setup before promotion.")

        elif tag == "pressure":
            suggestions.append("Let the setup come out of pressure before considering promotion.")
            promotable_conditions.append("Pressure conditions must clear.")

        elif tag == "counter_trend":
            suggestions.append("Avoid fighting the dominant trend unless the reversal becomes truly proven.")
            promotable_conditions.append("Trend conflict must resolve.")

        elif tag == "bad_environment":
            suggestions.append("Wait for a less defensive environment before trusting this play.")
            promotable_conditions.append("Market posture needs to improve.")

        elif tag == "inactive":
            suggestions.append("This play needs to return to an active state before it can be evaluated seriously.")
            promotable_conditions.append("Play status must be active.")

    def _dedupe_keep_order(items):
        seen = set()
        out = []
        for item in items:
            item = str(item or "").strip()
            if item and item not in seen:
                out.append(item)
                seen.add(item)
        return out

    return {
        "suggestions": _dedupe_keep_order(suggestions)[:5],
        "promotable_conditions": _dedupe_keep_order(promotable_conditions)[:5],
    }

def build_failure_clusters(plays):
    from collections import Counter

    counter = Counter()

    for play in plays:
        readiness = play.get("activation_readiness", {}) or {}
        tags = readiness.get("failure_tags", []) or []

        for tag in tags:
            counter[tag] += 1

    top = counter.most_common(5)

    return [{"cause": cause, "count": count} for cause, count in top]

def build_weak_play_rebuild_profile(play):
    play = play or {}

    readiness = play.get("activation_readiness", {}) or {}
    failure_tags = readiness.get("failure_tags", []) or []
    rebuild_map = build_rebuild_suggestions_from_failure_tags(failure_tags)

    bucket = str(readiness.get("bucket", "") or "").upper()
    score = int(readiness.get("score", 0) or 0)

    severity = "low"
    if bucket == "WEAK" and score <= 15:
        severity = "high"
    elif bucket == "WATCH" or score <= 40:
        severity = "medium"

    rebuild_priority = 0
    if bucket == "WEAK":
        rebuild_priority += 20
    if score <= 15:
        rebuild_priority += 20
    if "disagreement" in failure_tags:
        rebuild_priority += 10
    if "no_engine" in failure_tags:
        rebuild_priority += 8
    if "bad_environment" in failure_tags:
        rebuild_priority += 6

    return {
        "symbol": str(play.get("symbol", "") or "").upper(),
        "play_id": play.get("play_id"),
        "bucket": bucket,
        "score": score,
        "headline": readiness.get("headline", ""),
        "summary": readiness.get("summary", ""),
        "severity": severity,
        "rebuild_priority": rebuild_priority,
        "blockers": (readiness.get("blockers", []) or [])[:4],
        "guidance": (readiness.get("guidance", []) or [])[:4],
        "failure_tags": failure_tags,
        "rebuild_suggestions": rebuild_map.get("suggestions", []),
        "promotable_conditions": rebuild_map.get("promotable_conditions", []),
    }

def build_weak_play_rebuild_queue(plays):
    plays = plays or []

    queue = []

    for play in plays:
        readiness = play.get("activation_readiness", {}) or {}
        bucket = str(readiness.get("bucket", "") or "").upper()

        if bucket not in {"WATCH", "WEAK"}:
            continue

        try:
            queue.append(build_weak_play_rebuild_profile(play))
        except Exception as e:
            print(f"[REBUILD_QUEUE:{play.get('symbol', 'UNKNOWN')}] {e}")

    queue = sorted(
        queue,
        key=lambda x: (
            x.get("severity") == "high",
            x.get("rebuild_priority", 0),
            x.get("score", 0),
        ),
        reverse=True,
    )

    return queue[:10]

def build_weak_play_rebuild_summary(plays):
    plays = plays or []

    rebuild_queue = build_weak_play_rebuild_queue(plays)
    top_rebuild = rebuild_queue[0] if rebuild_queue else None

    high_severity = [x for x in rebuild_queue if x.get("severity") == "high"]
    medium_severity = [x for x in rebuild_queue if x.get("severity") == "medium"]

    if not rebuild_queue:
        headline = "No rebuild queue."
        summary = "There are no weak/watch plays that currently need rebuild attention."
    elif high_severity:
        headline = "Some plays need rebuilding."
        summary = "At least one active play is weak enough that it should be repaired before promotion is even considered."
    else:
        headline = "Some plays need refinement."
        summary = "The weakest plays are not broken, but they still need structure work before they can move up."

    return {
        "headline": headline,
        "summary": summary,
        "total_rebuild_candidates": len(rebuild_queue),
        "high_severity": len(high_severity),
        "medium_severity": len(medium_severity),
        "top_rebuild": top_rebuild,
        "rebuild_queue": rebuild_queue,
    }

def build_promotion_guidance(play):
    play = play or {}

    readiness = play.get("activation_readiness", {}) or {}
    blockers = readiness.get("blockers", []) or []

    bucket = str(readiness.get("bucket", "") or "").upper()

    if bucket == "READY":
        return {
            "next_step": "execute",
            "message": "This play is ready. Consider moving it into a live position.",
            "focus": [],
        }

    if bucket == "CLOSE":
        return {
            "next_step": "refine",
            "message": "This is close. Clean up the weak areas to promote it.",
            "focus": blockers[:2],
        }

    if bucket == "WATCH":
        return {
            "next_step": "wait",
            "message": "Wait for structure and agreement to improve.",
            "focus": blockers[:2],
        }

    if bucket == "WEAK":
        return {
            "next_step": "discard_or_rebuild",
            "message": "This setup needs major improvement before consideration.",
            "focus": blockers[:2],
        }

    return {
        "next_step": "unknown",
        "message": "No clear promotion path yet.",
        "focus": [],
    }


def build_my_plays_summary(plays):
    plays = plays or []

    total = len(plays)
    open_count = 0
    watching_count = 0
    archived_count = 0
    high_agreement_count = 0
    weak_count = 0
    ready_count = 0
    close_count = 0
    watching_not_ready_count = 0
    high_conviction_count = 0

    strongest_play = None
    weakest_play = None

    for play in plays:
        status = str(play.get("status", "Open")).strip().lower()
        agreement_score = int((play.get("system_agreement", {}) or {}).get("score", 0) or 0)
        conviction = str(play.get("conviction", "Medium")).strip().lower()

        readiness = classify_play_readiness(play)
        play["activation_readiness"] = readiness
        play["promotion_guidance"] = build_promotion_guidance(play)

        if status == "open":
            open_count += 1
        elif status == "watching":
            watching_count += 1
        elif status == "archived":
            archived_count += 1

        if agreement_score >= 75:
            high_agreement_count += 1

        if readiness["bucket"] == "READY":
            ready_count += 1
        elif readiness["bucket"] == "CLOSE":
            close_count += 1
        elif readiness["bucket"] in {"WATCH", "WEAK"}:
            weak_count += 1

        if status == "watching" and readiness["bucket"] != "READY":
            watching_not_ready_count += 1

        if conviction == "high":
            high_conviction_count += 1

        if strongest_play is None or readiness["score"] > strongest_play["activation_readiness"]["score"]:
            strongest_play = play

        if weakest_play is None or readiness["score"] < weakest_play["activation_readiness"]["score"]:
            weakest_play = play

    top_failure_causes = build_failure_clusters(plays)
    promotion_summary = build_play_promotion_summary(plays)
    rebuild_summary = build_weak_play_rebuild_summary(plays)

    if total == 0:
        headline = "No plays yet."
        summary = "Start building your idea book so the system can pressure-test your setups."
        action_message = "You do not have any plays in the system yet."
    elif ready_count >= max(1, int(total * 0.2)):
        headline = "You have real activation candidates."
        summary = "A meaningful portion of your playbook is structurally ready."
        action_message = "Your playbook contains enough READY setups to support selective activation."
    elif ready_count > 0:
        headline = "You have at least one real setup."
        summary = "There is something actionable, but the bench still needs strengthening."
        action_message = "You have a live candidate, but most of the playbook still needs development."
    elif close_count > 0:
        headline = "Your plays are close, not ready."
        summary = "A number of ideas are warming up, but they still need cleaner confirmation."
        action_message = "Focus on promoting CLOSE setups into READY instead of forcing weaker ideas."
    elif weak_count >= max(2, int(total * 0.6)):
        headline = "Too many weak setups."
        summary = "Your playbook currently contains more weak or watch-level ideas than truly ready setups."
        action_message = "Tighten play quality, improve structure, and focus on the top failure causes."
    else:
        headline = "Your playbook is developing."
        summary = "There is some structure forming, but nothing currently deserves activation."
        action_message = "Use blocker and guidance output to improve the best candidates."

    strongest_promotion = strongest_play.get("promotion_guidance", {}) if strongest_play else {}
    weakest_promotion = weakest_play.get("promotion_guidance", {}) if weakest_play else {}

    return {
        "total": total,
        "open": open_count,
        "watching": watching_count,
        "archived": archived_count,
        "high_agreement": high_agreement_count,
        "weak_or_pressured": weak_count,
        "ready_to_activate": ready_count,
        "close_to_ready": close_count,
        "watching_not_ready": watching_not_ready_count,
        "high_conviction": high_conviction_count,
        "headline": headline,
        "summary": summary,
        "action_message": action_message,
        "top_failure_causes": top_failure_causes[:5],
        "promotion_summary": promotion_summary,
        "rebuild_summary": rebuild_summary,
        "strongest_play": {
            "symbol": strongest_play.get("symbol"),
            "score": strongest_play["activation_readiness"]["score"],
            "headline": strongest_play["activation_readiness"]["headline"],
            "bucket": strongest_play["activation_readiness"]["bucket"],
            "promotion_message": strongest_promotion.get("message", ""),
            "promotion_focus": strongest_promotion.get("focus", []),
        } if strongest_play else None,
        "weakest_play": {
            "symbol": weakest_play.get("symbol"),
            "score": weakest_play["activation_readiness"]["score"],
            "headline": weakest_play["activation_readiness"]["headline"],
            "bucket": weakest_play["activation_readiness"]["bucket"],
            "promotion_message": weakest_promotion.get("message", ""),
            "promotion_focus": weakest_promotion.get("focus", []),
        } if weakest_play else None,
    }

def effective_tier_title() -> str:
    preview = session.get("preview_tier")
    if is_master() and preview:
        return str(preview).title()

    tier = session.get("tier")
    if tier:
        return str(tier).title()

    return "Free"


def effective_tier_lower() -> str:
    return str(effective_tier_title() or "Free").strip().lower()


def current_user_context() -> Dict[str, Any]:
    username = str(session.get("username", "") or "").strip()
    role = str(session.get("role", "guest") or "guest").strip().lower()
    real_tier = str(session.get("tier", "Free") or "Free").title()
    preview_tier = session.get("preview_tier")

    return {
        "username": username,
        "role": role,
        "tier": effective_tier_title(),
        "real_tier": real_tier,
        "preview_tier": str(preview_tier).title() if preview_tier else None,
    }


def current_tier_title() -> str:
    return effective_tier_title()


def current_tier_lower() -> str:
    return effective_tier_lower()


def is_logged_in() -> bool:
    return bool(str(session.get("username", "") or "").strip())


def is_master() -> bool:
    return str(session.get("role", "") or "").strip().lower() == "master"


def can_access_all_symbols() -> bool:
    tier = effective_tier_lower()
    return tier in {"starter", "pro", "elite"} or is_master()


def show_upgrade_prompt() -> bool:
    return is_logged_in() and effective_tier_lower() not in {"elite"}


def template_context(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx = dict(extra or {})
    user_ctx = current_user_context()

    ctx.setdefault("theme", get_theme() if "get_theme" in globals() else session.get("theme", "dark"))
    ctx.setdefault("user", user_ctx)
    ctx.setdefault("show_upgrade", show_upgrade_prompt())
    ctx.setdefault("can_access_all_symbols", can_access_all_symbols())
    ctx.setdefault("unread_notifications", 0)
    ctx.setdefault("snapshot", get_dashboard_snapshot() if "get_dashboard_snapshot" in globals() else {})
    return ctx

def get_current_tier_for_routes() -> str:
    try:
        return str(current_tier_title() or "Free")
    except Exception:
        return "Free"


def build_decision_bundle_from_product_fusion(product_fusion: dict) -> dict:
    if not isinstance(product_fusion, dict):
        product_fusion = {}

    fusion = product_fusion.get("fusion", {}) if isinstance(product_fusion.get("fusion", {}), dict) else {}
    master = product_fusion.get("master_decision", {}) if isinstance(product_fusion.get("master_decision", {}), dict) else {}

    enhanced_package = master.get("enhanced_package", {}) if isinstance(master.get("enhanced_package", {}), dict) else {}
    truth_package = master.get("truth_package", {}) if isinstance(master.get("truth_package", {}), dict) else {}

    return {
        "base_decision": {
            "action": product_fusion.get("command", "wait"),
            "confidence": (
                master.get("experience", {}).get("next_action")
                or "low"
            ),
        },
        "explainability": {
            "message": product_fusion.get("fusion_summary", "") or "",
            "narrative": product_fusion.get("fusion_summary", "") or "",
        },
        "enhanced": {
            "enhanced_voice": {
                "enhanced_verdict": enhanced_package.get("enhanced_summary", {}).get("verdict", ""),
                "enhanced_insight": enhanced_package.get("enhanced_summary", {}).get("insight", ""),
                "enhanced_command_phrase": enhanced_package.get("enhanced_summary", {}).get("command", ""),
            },
            "enhanced_package": enhanced_package,
        },
        "truth": {
            "truth_override": {
                "truth_final_action": truth_package.get("truth_summary", {}).get("final_action", product_fusion.get("command", "wait")),
                "truth_final_confidence": truth_package.get("truth_summary", {}).get("final_confidence", "low"),
                "truth_verdict": truth_package.get("truth_summary", {}).get("verdict", ""),
                "truth_insight": truth_package.get("truth_summary", {}).get("insight", ""),
                "truth_command_phrase": truth_package.get("truth_summary", {}).get("command", ""),
                "truth_override_reason": truth_package.get("truth_notes", {}).get("override_reason", ""),
            },
            "truth_package": truth_package,
        },
        "behavior": master.get("behavior_intelligence", {}) if isinstance(master.get("behavior_intelligence", {}), dict) else {},
        "causality": master.get("causality_intelligence", {}) if isinstance(master.get("causality_intelligence", {}), dict) else {},
        "counterfactual": master.get("counterfactual_intelligence", {}) if isinstance(master.get("counterfactual_intelligence", {}), dict) else {},
    }


def build_final_brain_from_signal(symbol: str, fusion_signal: dict) -> tuple[dict, dict]:
    product_fusion = build_symbol_fusion_payload(fusion_signal)
    decision_bundle = build_decision_bundle_from_product_fusion(product_fusion)
    final_brain = build_symbol_final_brain(symbol, decision_bundle)
    return product_fusion, final_brain


# ADD THIS HELPER TO web/app.py

def build_all_symbols_fusion_payloads(limit: int = 100):
    boards = get_signal_boards()
    if not isinstance(boards, list):
        boards = []

    fusion_payloads = []

    for board in boards[:limit]:
        if not isinstance(board, dict):
            continue

        signal = {
            "symbol": board.get("symbol", ""),
            "company_name": board.get("company_name", board.get("symbol", "")),
            "direction": board.get("direction", "CALL"),
            "setup_type": board.get("setup_type", "continuation"),
            "trend_strength": board.get("latest_score", 70),
            "volume_confirmation": 70,
            "extension_score": 35,
            "pullback_quality": 72,
            "score": board.get("latest_score", 75),
            "structure_quality": 84,
            "liquidity_score": 92,
            "spread_score": 74,
            "premium_efficiency_score": 82,
            "open_interest_score": 76,
            "iv_context": "normal",
            "visible_volatility": 22,
            "last_pnl": 25,
        }

        try:
            fusion_payloads.append(build_symbol_fusion_payload(signal))
        except Exception as e:
            print(f"[ALL_SYMBOLS_FUSION:{signal.get('symbol')}] {e}")

    return fusion_payloads


# ADD THESE HELPERS TO web/app.py

def get_fusion_user_data():
    return {
        "recent_trades": 2,
        "page_views": 5,
    }


def get_fusion_market_data():
    system = safe_run("get_system_state", get_system_state, {})
    return {
        "trend_strength": float(system.get("trend_strength", 70) or 70),
        "volatility_level": float(system.get("volatility_level", 40) or 40),
        "breadth_score": float(system.get("breadth_score", 65) or 65),
    }


def get_fusion_trade_results():
    snapshot = get_canonical_snapshot()
    ledger = snapshot.get("ledger", [])
    if not isinstance(ledger, list):
        ledger = []

    results = []
    for item in ledger[-20:]:
        if not isinstance(item, dict):
            continue
        pnl = float(item.get("pnl", 0) or 0)
        results.append({
            "outcome": "win" if pnl > 0 else "loss" if pnl < 0 else "flat",
            "edge_score": item.get("raw", {}).get("score", 75) if isinstance(item.get("raw"), dict) else 75,
        })
    return results


def get_fusion_setup_stats():
    return {
        "families": {
            "continuation": {"win_rate": 0.60, "count": 8},
            "breakout_extension": {"win_rate": 0.35, "count": 5},
            "reversal_attempt": {"win_rate": 0.45, "count": 4},
        }
    }


def get_fusion_context(symbol: str = ""):
    return {
        "event_type": "",
        "minutes_to_event": 99999,
        "news_heat_score": 20,
        "contradictory_news": False,
        "hype_score": 15,
        "hidden_risk_score": 20,
        "follow_through_score": 70,
    }


def get_fusion_system_state():
    return {
        "max_open_positions": 6,
        "data_integrity_ok": True,
        "broker_connection_ok": True,
        "execution_error_count": 0,
        "governance_priority": True,
        "system_ready": True,
    }


def get_fusion_portfolio_state():
    positions = safe_run(
        "get_positions_with_intelligence",
        get_positions_with_intelligence,
        [],
    )
    if not isinstance(positions, list):
        positions = []

    return {
        "daily_loss_pct": 0,
        "open_positions": len(positions),
        "drawdown_state": "normal",
        "stress_state": (
            "low"
            if len(positions) <= 3
            else "moderate"
            if len(positions) <= 6
            else "critical"
        ),
    }


def build_symbol_fusion_payload(signal: dict):
    if not isinstance(signal, dict):
        signal = {}

    tier = current_tier_title()

    return build_full_product_fusion(
        signal=signal,
        user_data=get_fusion_user_data(),
        market_data=get_fusion_market_data(),
        portfolio_positions=safe_run(
            "get_positions_with_intelligence",
            get_positions_with_intelligence,
            [],
        ),
        trade_results=get_fusion_trade_results(),
        setup_stats=get_fusion_setup_stats(),
        context=get_fusion_context(signal.get("symbol", "")),
        system_state=get_fusion_system_state(),
        portfolio_state=get_fusion_portfolio_state(),
        tier=tier,
    )


def get_v2_symbol_hero(symbol: str):
    try:
        return build_symbol_hero_contract(symbol)
    except Exception as e:
        print(f"[V2_SYMBOL_HERO] {e}")
        return {
            "symbol": symbol,
            "company_name": symbol,
            "hero": {},
            "lanes": {},
            "meta": {"error": str(e)},
        }


def get_v2_symbol_deep_dive(symbol: str):
    try:
        return build_symbol_deep_dive_contract(symbol)
    except Exception as e:
        print(f"[V2_SYMBOL_DEEP_DIVE] {e}")
        return {
            "symbol": symbol,
            "hero": {},
            "panels": [],
            "timeline": [],
            "meta": {"error": str(e)},
        }


def get_v2_horizontal_hero():
    try:
        return build_horizontal_hero_contract()
    except Exception as e:
        print(f"[V2_HORIZONTAL_HERO] {e}")
        return {
            "enabled_on": [],
            "disabled_on": [],
            "behavior": {},
            "cards": [],
            "meta": {"error": str(e)},
        }

def get_v2_market_map():
    try:
        return build_market_map()
    except Exception as e:
        print(f"[V2_MARKET_MAP] {e}")
        return {
            "tiles": [],
            "grouped_tiles": {},
            "legend": {},
            "meta": {"error": str(e)},
        }


def get_v2_market_map_interactions():
    try:
        return build_market_map_interaction_contract()
    except Exception as e:
        print(f"[V2_MARKET_MAP_INTERACTIONS] {e}")
        return {
            "hover_cards": [],
            "tile_actions": [],
            "interaction_rules": {},
            "meta": {"error": str(e)},
        }


def get_v2_map_layers():
    try:
        return build_map_layer_toggle_contract()
    except Exception as e:
        print(f"[V2_MAP_LAYERS] {e}")
        return {
            "default_layer": "pressure",
            "layers": [],
            "interaction_model": {},
            "meta": {"error": str(e)},
        }

def get_v2_dashboard_contract(username: str):
    try:
        return build_dashboard_contract(username)
    except Exception as e:
        print(f"[V2_DASHBOARD_CONTRACT] {e}")
        return {
            "username": username,
            "mode_bar": {},
            "command_cards": [],
            "sections": [],
            "meta": {
                "error": str(e),
            },
        }


def get_v2_spotlight_contract(username: str):
    try:
        return build_spotlight_page_contract(username)
    except Exception as e:
        print(f"[V2_SPOTLIGHT_CONTRACT] {e}")
        return {
            "username": username,
            "hero": {},
            "lane_sections": [],
            "side_panels": [],
            "meta": {
                "error": str(e),
            },
        }

def safe_list(value):
    return value if isinstance(value, list) else []


def safe_dict(value):
    return value if isinstance(value, dict) else {}


def safe_run(label: str, fn, default):
    try:
        return fn()
    except Exception as e:
        print(f"[SAFE_RUN:{label}] {e}")
        return default


def get_pipeline_status() -> Dict[str, Any]:
    status = load_json("data/pipeline_status.json", {})
    if not isinstance(status, dict):
        status = {}

    return {
        "engine_run_at": status.get("engine_run_at"),
        "symbol_intelligence_run_at": status.get("symbol_intelligence_run_at"),
        "news_sync_at": status.get("news_sync_at"),
        "symbol_news_sync": safe_dict(status.get("symbol_news_sync")),
    }


def _freshness_bucket(iso_value: Any, stale_after_minutes: int = 60) -> Dict[str, Any]:
    text = _norm_text(iso_value, "")
    if not text:
        return {
            "label": "Missing",
            "minutes_old": None,
            "is_stale": True,
            "level": "danger",
        }

    try:
        then = datetime.fromisoformat(text)
        now = datetime.now()
        minutes_old = int((now - then).total_seconds() / 60)
    except Exception:
        return {
            "label": "Unreadable",
            "minutes_old": None,
            "is_stale": True,
            "level": "danger",
        }

    if minutes_old < stale_after_minutes:
        return {
            "label": f"{minutes_old}m old",
            "minutes_old": minutes_old,
            "is_stale": False,
            "level": "positive",
        }

    if minutes_old < stale_after_minutes * 4:
        return {
            "label": f"{minutes_old}m old",
            "minutes_old": minutes_old,
            "is_stale": True,
            "level": "warning",
        }

    return {
        "label": f"{minutes_old}m old",
        "minutes_old": minutes_old,
        "is_stale": True,
        "level": "danger",
    }


def build_data_health_summary() -> Dict[str, Any]:
    pipeline = get_pipeline_status()

    signals = load_json("data/signals.json", [])
    symbol_intel = load_json("data/symbol_intelligence.json", {})
    symbol_meta = load_json("data/symbol_meta.json", {})
    symbol_news = load_json("data/symbol_news.json", {})
    recent_reports = load_json("data/recent_reports.json", [])
    users = load_json("data/users.json", [])

    signals = safe_list(signals)
    symbol_intel = safe_dict(symbol_intel)
    symbol_meta = safe_dict(symbol_meta)
    symbol_news = safe_dict(symbol_news)
    recent_reports = safe_list(recent_reports)
    users = safe_list(users)

    engine_freshness = _freshness_bucket(pipeline.get("engine_run_at"), stale_after_minutes=90)
    symbol_freshness = _freshness_bucket(pipeline.get("symbol_intelligence_run_at"), stale_after_minutes=120)
    news_freshness = _freshness_bucket(pipeline.get("news_sync_at"), stale_after_minutes=120)

    cards = []

    if not signals:
        cards.append({
            "headline": "Signals data missing",
            "body": "The signals layer is empty, so multiple downstream surfaces may soften or go blank.",
            "level": "danger",
        })

    if not symbol_intel:
        cards.append({
            "headline": "Symbol intelligence missing",
            "body": "Symbol pages may load without their richer intelligence layer.",
            "level": "warning",
        })

    if not symbol_meta:
        cards.append({
            "headline": "Symbol meta missing",
            "body": "Company names and blurbs may fall back to ticker-only display.",
            "level": "neutral",
        })

    if not symbol_news:
        cards.append({
            "headline": "Symbol news cache missing",
            "body": "News can still fetch on demand, but the cache currently looks empty.",
            "level": "neutral",
        })

    if not recent_reports:
        cards.append({
            "headline": "Recent reports missing",
            "body": "Analytics and proof views may have weaker historical context.",
            "level": "warning",
        })

    if not cards:
        cards.append({
            "headline": "Core data surfaces are present",
            "body": "The main data files are loaded and available.",
            "level": "positive",
        })

    return {
        "pipeline": pipeline,
        "freshness": {
            "engine": engine_freshness,
            "symbol_intelligence": symbol_freshness,
            "news": news_freshness,
        },
        "counts": {
            "signals": len(signals),
            "symbol_intelligence": len(symbol_intel),
            "symbol_meta": len(symbol_meta),
            "symbol_news": len(symbol_news),
            "recent_reports": len(recent_reports),
            "users": len(users),
        },
        "cards": cards,
    }


# ============================================================
# BASIC STATE HELPERS
# ============================================================

def effective_tier() -> str:
    preview = session.get("preview_tier")
    if preview:
        return preview
    return session.get("tier", "Guest")


def current_tier_title() -> str:
    tier = (effective_tier() or "Guest").title()
    if tier not in {"Guest", "Free", "Starter", "Pro", "Elite"}:
        return "Guest"
    return tier


def current_tier_lower() -> str:
    return current_tier_title().lower()


def is_logged_in() -> bool:
    return bool(session.get("username"))


def is_master() -> bool:
    return session.get("role") == "master"


def should_show_upgrade() -> bool:
    return current_tier_title() != "Elite"


def can_access_all_symbols() -> bool:
    if is_master() and not session.get("preview_tier"):
        return True
    return current_tier_title() == "Elite"


def get_current_user() -> Dict[str, Any]:
    return {
        "username": session.get("username"),
        "tier": current_tier_title(),
        "real_tier": session.get("tier", "Guest"),
        "role": session.get("role", "member"),
        "preview_tier": session.get("preview_tier"),
    }


def get_theme() -> str:
    theme = session.get("theme", "dark")
    return "light" if theme == "light" else "dark"


def get_unread_notifications() -> int:
    items = load_json("data/notifications.json", [])
    if not isinstance(items, list):
        return 0

    username = session.get("username")
    if not username:
        return 0

    unread = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("username") not in [None, "", username]:
            continue
        if not item.get("read", False):
            unread += 1
    return unread


@app.context_processor
def inject_global_context():
    try:
        ensure_market_universe_ready()
    except Exception as e:
        print(f"[MARKET_UNIVERSE_AUTO_CHECK] {e}")

    return {
        "user": safe_run("get_current_user", get_current_user, {
            "username": None,
            "tier": "Guest",
            "real_tier": "Guest",
            "role": "member",
            "preview_tier": None,
        }),
        "theme": safe_run("get_theme", get_theme, "dark"),
        "show_upgrade": safe_run("should_show_upgrade", should_show_upgrade, True),
        "unread_notifications": safe_run("get_unread_notifications", get_unread_notifications, 0),
        "snapshot": safe_run("get_dashboard_snapshot", get_dashboard_snapshot, {
            "estimated_account_value": 10000,
            "buying_power": 5000,
            "open_positions": 0,
        }),
        "system": safe_run("get_system_state", get_system_state, {
            "regime": "Neutral",
            "volatility": "Normal",
            "engine_state": "Unknown",
        }),
        "execution_summary": safe_run(
            "execution_summary",
            lambda: load_json("data/execution_summary.json", {}),
            {},
        ),
    }


# ============================================================
# ANALYTICS HELPERS
# ============================================================



def get_admin_metrics() -> Dict[str, Any]:
    metrics = load_json("data/admin_metrics.json", {})
    if not isinstance(metrics, dict):
        metrics = {}

    return {
        "page_views": metrics.get("page_views", {}) if isinstance(metrics.get("page_views", {}), dict) else {},
        "clicks": metrics.get("clicks", {}) if isinstance(metrics.get("clicks", {}), dict) else {},
        "friction_signals": metrics.get("friction_signals", {}) if isinstance(metrics.get("friction_signals", {}), dict) else {},
        "engagement": metrics.get("engagement", {}) if isinstance(metrics.get("engagement", {}), dict) else {},
    }


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _norm_text(value, default=""):
    text = str(value or "").strip()
    return text if text else default


def _norm_upper(value, default="UNKNOWN"):
    text = _norm_text(value, "").upper()
    return text if text else default


def _top_count_item(counts, fallback="Not enough data yet."):
    if not counts:
        return {"label": fallback, "count": 0}
    label, count = max(counts.items(), key=lambda item: item[1])
    return {"label": label, "count": count}


def get_recent_behavior_events_for_symbol(symbol, limit=20):
    symbol = str(symbol or "").strip().upper()
    rows = get_event_log()
    matches = []

    for row in reversed(rows):
        payload = row.get("payload", {}) or {}
        row_symbol = str(payload.get("symbol", "")).strip().upper()
        if row_symbol == symbol:
            matches.append(row)
        if len(matches) >= limit:
            break

    return matches


def build_trade_behavior_flags(position):
    symbol = str(position.get("symbol", "")).strip().upper()
    conviction = str(position.get("conviction", "")).strip()
    thesis = str(position.get("thesis", "") or "").strip()

    flags = []
    events = get_recent_behavior_events_for_symbol(symbol, limit=25)

    activated_against_engine = False
    edited_after_weak_health = False
    closed_weak = False
    created_after_loss_close = False

    for row in events:
        event_type = str(row.get("event_type", "")).strip()
        payload = row.get("payload", {}) or {}

        if event_type == "play_activated" and bool(payload.get("activated_against_engine", False)):
            activated_against_engine = True

        if event_type == "play_edited" and bool(payload.get("edited_after_weak_health", False)):
            edited_after_weak_health = True

        if event_type == "position_closed" and bool(payload.get("closed_weak", False)):
            closed_weak = True

        if event_type == "play_created" and bool(payload.get("created_after_loss_close", False)):
            created_after_loss_close = True

    if activated_against_engine:
        flags.append({
            "tag": "Against Engine",
            "note": "This setup appears to have been activated against the engine direction."
        })

    if conviction.lower() == "high" and not thesis:
        flags.append({
            "tag": "High Conviction / No Thesis",
            "note": "This trade carried high conviction without a written thesis."
        })

    if edited_after_weak_health:
        flags.append({
            "tag": "Late Edit",
            "note": "This setup appears to have been edited after weakness was already showing."
        })

    if closed_weak:
        flags.append({
            "tag": "Late Weak Close",
            "note": "This trade appears to have been closed after agreement or health was already weak."
        })

    if created_after_loss_close:
        flags.append({
            "tag": "Post-Loss Creation",
            "note": "This setup may have been created shortly after a losing close."
        })

    return flags


def build_behavior_coaching_line(position, flags):
    if not flags:
        return "No strong behavior warning is attached to this trade yet."

    flag_tags = [f.get("tag", "Behavior") for f in flags]

    if "Against Engine" in flag_tags and "Late Edit" in flag_tags:
        return "This trade looks less like a clean miss and more like a discipline leak: you pushed against the system, then managed late."
    if "High Conviction / No Thesis" in flag_tags:
        return "This trade shows confidence outrunning structure. Strong belief without written reasoning is harder to review and harder to trust."
    if "Late Weak Close" in flag_tags:
        return "The issue here may not just be the idea. It may be that you stayed too long after the evidence weakened."
    if "Post-Loss Creation" in flag_tags:
        return "This trade may have been influenced by recent emotional flow rather than clean setup quality."
    if "Against Engine" in flag_tags:
        return "This trade carried a directional disagreement with the system, so the burden of proof needed to be higher."
    if "Late Edit" in flag_tags:
        return "This trade suggests reactive management. The system is warning that adjustment may have come after damage had already started."

    return "This trade carries behavior flags that matter as much as the outcome itself."


def build_behavior_habit_summary(enriched_trades):
    counts = {
        "against_engine": 0,
        "high_conviction_no_thesis": 0,
        "late_edit": 0,
        "late_weak_close": 0,
        "post_loss_creation": 0,
    }

    for trade in enriched_trades:
        for flag in trade.get("behavior_flags", []):
            tag = str(flag.get("tag", "")).strip()

            if tag == "Against Engine":
                counts["against_engine"] += 1
            elif tag == "High Conviction / No Thesis":
                counts["high_conviction_no_thesis"] += 1
            elif tag == "Late Edit":
                counts["late_edit"] += 1
            elif tag == "Late Weak Close":
                counts["late_weak_close"] += 1
            elif tag == "Post-Loss Creation":
                counts["post_loss_creation"] += 1

    cards = []

    if counts["against_engine"] > 0:
        cards.append(f"{counts['against_engine']} archived trade(s) show against-engine activation behavior.")
    if counts["high_conviction_no_thesis"] > 0:
        cards.append(f"{counts['high_conviction_no_thesis']} archived trade(s) carried high conviction without a written thesis.")
    if counts["late_edit"] > 0:
        cards.append(f"{counts['late_edit']} archived trade(s) show edits happening after weakness was already visible.")
    if counts["late_weak_close"] > 0:
        cards.append(f"{counts['late_weak_close']} archived trade(s) appear to have been closed late after weakness.")
    if counts["post_loss_creation"] > 0:
        cards.append(f"{counts['post_loss_creation']} archived trade(s) may have been created too soon after a loss.")

    if not cards:
        cards.append("No strong behavior habit signals are standing out yet.")

    return {
        "counts": counts,
        "cards": cards,
    }


def _is_closed_status(value):
    return _norm_text(value, "").lower() == "closed"


def _agreement_score(row):
    return _safe_int((row.get("system_agreement", {}) or {}).get("score", 0), 0)


def _health_score(row):
    return _safe_int((row.get("health", {}) or {}).get("score", 0), 0)


def _activation_bucket(play):
    readiness = play.get("activation_readiness") or {}
    return _norm_upper(readiness.get("bucket"), "UNKNOWN")


def _ensure_activation_readiness(plays):
    plays = plays or []
    for play in plays:
        if not play.get("activation_readiness"):
            play["activation_readiness"] = classify_play_readiness(play)
    return plays


def build_admin_shared_context():
    try:
        plays = _ensure_activation_readiness(get_my_plays())
    except Exception:
        plays = []

    for play in plays:
        try:
            if "activation_readiness" not in play:
                play["activation_readiness"] = classify_play_readiness(play)
            if "promotion_guidance" not in play:
                play["promotion_guidance"] = build_promotion_guidance(play)
            if "rebuild_profile" not in play:
                play["rebuild_profile"] = build_weak_play_rebuild_profile(play)
        except Exception as e:
            print(f"[ADMIN_SHARED_PLAY_ENRICH:{play.get('symbol', 'UNKNOWN')}] {e}")

    try:
        positions = get_user_positions(include_closed=True)
    except Exception:
        positions = []

    try:
        learning = build_learning_dashboard_payload()
    except Exception:
        learning = {
            "memory": {},
            "pressure": {},
            "recommendations": {},
        }

    try:
        analysis = analyze_user_trades()
    except Exception:
        analysis = {
            "totals": {"archived": 0, "wins": 0, "losses": 0, "flat": 0},
            "direction_counts": {},
            "conviction_counts": {},
            "average_health": 0,
            "insights": ["Trade analysis is temporarily unavailable."],
            "behavior_summary": {"counts": {}, "cards": ["Behavior summary is temporarily unavailable."]},
            "trades": [],
        }

    try:
        admin_summary = build_admin_intelligence_summary(plays, positions, analysis)
    except Exception:
        admin_summary = {}

    try:
        monitoring = build_product_monitoring_summary(plays, positions, analysis)
    except Exception:
        monitoring = {}

    try:
        behavioral_insights = build_behavioral_event_insights()
    except Exception:
        behavioral_insights = {"counts": {}, "cards": []}

    try:
        behavior_risk = build_behavior_risk_summary_from_analysis(analysis)
    except Exception:
        behavior_risk = {
            "headline": "Behavior risk unavailable.",
            "summary": "Could not compute behavior risk.",
            "counts": {},
            "cards": [],
        }

    try:
        behavior_priority = build_behavior_priority_engine(analysis)
    except Exception:
        behavior_priority = {
            "headline": "Behavior priority unavailable.",
            "summary": "Could not compute behavior priority.",
            "top_fix": None,
            "items": [],
            "totals": {"archived": 0, "wins": 0, "losses": 0},
        }

    try:
        surface_alerts = build_admin_surface_alerts(
            admin_summary=admin_summary,
            monitoring=monitoring,
            behavioral_insights=behavioral_insights,
            behavior_risk=behavior_risk,
        )
    except Exception:
        surface_alerts = {}

    try:
        quick_actions = build_operator_quick_actions(
            admin_summary=admin_summary,
            monitoring=monitoring,
            behavioral_insights=behavioral_insights,
            behavior_risk=behavior_risk,
        )
    except Exception:
        quick_actions = {"actions": []}

    try:
        alert_explanations = build_shared_operator_alert_explanations(surface_alerts)
    except Exception:
        alert_explanations = {
            "headline": "Shared operator alerts explanation layer",
            "summary": "Alert explanation is temporarily unavailable.",
            "items": [],
        }

    try:
        play_command = build_admin_play_command_summary(plays)
    except Exception:
        play_command = {
            "headline": "Play command unavailable.",
            "summary": "Could not compute play command layer.",
            "top_failure_causes": [],
            "promotion_summary": {},
            "rebuild_summary": {},
            "top_promotion_candidate": None,
            "top_near_miss": None,
            "top_rebuild": None,
            "strongest_play": None,
            "weakest_play": None,
            "counts": {
                "total": 0,
                "ready": 0,
                "close": 0,
                "weak": 0,
                "watching": 0,
            },
        }

    return {
        "plays": plays,
        "positions": positions,
        "analysis": analysis,
        "admin_summary": admin_summary,
        "monitoring": monitoring,
        "learning": learning,
        "behavioral_insights": behavioral_insights,
        "behavior_risk": behavior_risk,
        "behavior_priority": behavior_priority,
        "surface_alerts": surface_alerts,
        "alert_explanations": alert_explanations,
        "quick_actions": quick_actions,
        "play_command": play_command,
    }


def build_operator_quick_actions(admin_summary=None, monitoring=None, behavioral_insights=None, behavior_risk=None):
    admin_summary = admin_summary or {}
    monitoring = monitoring or {}
    behavioral_insights = behavioral_insights or {}
    behavior_risk = behavior_risk or {}

    ready_plays = _safe_int((admin_summary.get("counts", {}) or {}).get("ready_plays", 0))
    weak_plays = _safe_int((admin_summary.get("counts", {}) or {}).get("weak_plays", 0))
    weak_open_positions = _safe_int((monitoring.get("position_quality", {}) or {}).get("weak_open_positions", 0))
    no_thesis = _safe_int((monitoring.get("thesis_quality", {}) or {}).get("without_thesis", 0))
    losses = _safe_int((admin_summary.get("trade_totals", {}) or {}).get("losses", 0))
    disagreement_count = _safe_int((admin_summary.get("disagreement", {}) or {}).get("disagreement_count", 0))

    behavior_counts = behavioral_insights.get("counts", {}) or {}
    activated_against_engine = _safe_int(behavior_counts.get("activated_against_engine", 0))
    high_conviction_no_thesis = _safe_int(behavior_counts.get("high_conviction_no_thesis", 0))
    edited_after_weak_health = _safe_int(behavior_counts.get("edited_after_weak_health", 0))
    closed_weak = _safe_int(behavior_counts.get("closed_weak", 0))
    created_after_loss_close = _safe_int(behavior_counts.get("created_after_loss_close", 0))

    risk_counts = behavior_risk.get("counts", {}) or {}
    archived_against_engine = _safe_int(risk_counts.get("against_engine", 0))
    archived_late_edit = _safe_int(risk_counts.get("late_edit", 0))
    archived_late_weak_close = _safe_int(risk_counts.get("late_weak_close", 0))

    actions = [
        {
            "headline": "Ready Plays",
            "body": f"{ready_plays} play(s) currently look ready for activation.",
            "target": "/my-plays?filter=ready",
            "target_label": "Open Ready Plays",
            "tone": "gold",
        },
        {
            "headline": "Weak Plays",
            "body": f"{weak_plays} play(s) currently look weak or watch-only.",
            "target": "/my-plays?filter=weak",
            "target_label": "Open Weak Plays",
            "tone": "standard",
        },
        {
            "headline": "Weak Positions",
            "body": f"{weak_open_positions} open position(s) need faster review.",
            "target": "/my-positions?filter=weak",
            "target_label": "Review Weak Positions",
            "tone": "standard",
        },
        {
            "headline": "Trade Analysis",
            "body": f"{losses} archived loss(es) currently recorded in the coaching layer.",
            "target": "/my-positions/analyze",
            "target_label": "Open Trade Analysis",
            "tone": "standard",
        },
        {
            "headline": "Failure Cluster",
            "body": "Open the current dominant failure pattern and review what keeps breaking down.",
            "target": "/admin/intelligence?filter=failure",
            "target_label": "Review Failure Cluster",
            "tone": "standard",
        },
        {
            "headline": "Disagreement Review",
            "body": f"{disagreement_count} disagreement case(s) are currently visible.",
            "target": "/admin/intelligence?filter=disagreement",
            "target_label": "Review Disagreement",
            "tone": "standard",
        },
        {
            "headline": "Thesis Cleanup",
            "body": f"{no_thesis} play(s) are missing a thesis.",
            "target": "/admin/product-monitoring?filter=thesis",
            "target_label": "Review Thesis Quality",
            "tone": "standard",
        },
        {
            "headline": "Readiness Distribution",
            "body": "See how much of the playbook is actually actionable versus soft.",
            "target": "/admin/product-monitoring?filter=readiness",
            "target_label": "Open Readiness View",
            "tone": "standard",
        },
    ]

    if activated_against_engine > 0:
        actions.append({
            "headline": "Against-Engine Activations",
            "body": f"{activated_against_engine} activation event(s) were recorded against the engine.",
            "target": "/admin/intelligence?filter=disagreement",
            "target_label": "Review Behavior Drift",
            "tone": "standard",
        })

    if high_conviction_no_thesis > 0:
        actions.append({
            "headline": "High Conviction / No Thesis",
            "body": f"{high_conviction_no_thesis} creation event(s) showed strong conviction without a written thesis.",
            "target": "/admin/product-monitoring?filter=thesis",
            "target_label": "Clean This Up",
            "tone": "standard",
        })

    if edited_after_weak_health > 0:
        actions.append({
            "headline": "Edits After Weakness",
            "body": f"{edited_after_weak_health} edit event(s) happened after setups were already weak.",
            "target": "/my-plays?filter=weak",
            "target_label": "Review Weak Setups",
            "tone": "standard",
        })

    if closed_weak > 0:
        actions.append({
            "headline": "Late Weak Closes",
            "body": f"{closed_weak} close event(s) happened while trades were already weak.",
            "target": "/my-positions/analyze",
            "target_label": "Review Late Closes",
            "tone": "standard",
        })

    if created_after_loss_close > 0:
        actions.append({
            "headline": "Created After Loss",
            "body": f"{created_after_loss_close} play creation event(s) happened after a losing close.",
            "target": "/my-plays",
            "target_label": "Review Reactive Behavior",
            "tone": "standard",
        })

    if archived_against_engine > 0:
        actions.append({
            "headline": "Archived Against-Engine Trades",
            "body": f"{archived_against_engine} archived trade(s) show against-engine activation behavior.",
            "target": "/my-positions/analyze",
            "target_label": "Review Archived Behavior",
            "tone": "standard",
        })

    if archived_late_edit > 0 or archived_late_weak_close > 0:
        actions.append({
            "headline": "Management Leak Review",
            "body": f"{archived_late_edit + archived_late_weak_close} archived trade(s) show late management behavior.",
            "target": "/my-positions/analyze",
            "target_label": "Review Management Leaks",
            "tone": "standard",
        })

    return {
        "actions": actions[:12]
    }


def build_admin_surface_alerts(admin_summary=None, monitoring=None, behavioral_insights=None, behavior_risk=None):
    admin_summary = admin_summary or {}
    monitoring = monitoring or {}
    behavioral_insights = behavioral_insights or {}
    behavior_risk = behavior_risk or {}

    alerts = []

    activation = admin_summary.get("activation_quality", {}) or {}
    disagreement = admin_summary.get("disagreement", {}) or {}
    zones = admin_summary.get("zones", {}) or {}
    readiness = monitoring.get("readiness_buckets", {}) or {}
    thesis_quality = monitoring.get("thesis_quality", {}) or {}
    position_quality = monitoring.get("position_quality", {}) or {}
    strongest_friction = monitoring.get("strongest_friction", {}) or {}
    behavior_counts = behavioral_insights.get("counts", {}) or {}
    risk_counts = behavior_risk.get("counts", {}) or {}

    weak_activations = _safe_int(activation.get("weak_activations", 0))
    ready_activations = _safe_int(activation.get("ready_activations", 0))
    disagreement_count = _safe_int(disagreement.get("disagreement_count", 0))
    aligned_count = _safe_int(disagreement.get("aligned_count", 0))
    weak_plays = _safe_int(readiness.get("WEAK", 0))
    watch_plays = _safe_int(readiness.get("WATCH", 0))
    ready_plays = _safe_int(readiness.get("READY", 0))
    no_thesis = _safe_int(thesis_quality.get("without_thesis", 0))
    weak_open_positions = _safe_int(position_quality.get("weak_open_positions", 0))

    activated_against_engine = _safe_int(behavior_counts.get("activated_against_engine", 0))
    high_conviction_no_thesis = _safe_int(behavior_counts.get("high_conviction_no_thesis", 0))
    edited_after_weak_health = _safe_int(behavior_counts.get("edited_after_weak_health", 0))
    closed_weak = _safe_int(behavior_counts.get("closed_weak", 0))
    created_after_loss_close = _safe_int(behavior_counts.get("created_after_loss_close", 0))

    archived_against_engine = _safe_int(risk_counts.get("against_engine", 0))
    archived_high_conviction_no_thesis = _safe_int(risk_counts.get("high_conviction_no_thesis", 0))
    archived_late_edit = _safe_int(risk_counts.get("late_edit", 0))
    archived_late_weak_close = _safe_int(risk_counts.get("late_weak_close", 0))
    archived_post_loss_creation = _safe_int(risk_counts.get("post_loss_creation", 0))

    if weak_activations > ready_activations:
        alerts.append({
            "level": "danger",
            "headline": "Weak activations are outweighing strong ones",
            "body": "Promoted ideas are leaking too much quality after activation.",
            "target": "/admin/intelligence?filter=activation",
            "target_label": "Review Activation Quality",
        })

    if disagreement_count > aligned_count:
        alerts.append({
            "level": "warning",
            "headline": "Disagreement is elevated",
            "body": "The operator is fighting the engine more often than aligning with it.",
            "target": "/admin/intelligence?filter=disagreement",
            "target_label": "Review Disagreement",
        })

    if weak_plays + watch_plays > ready_plays:
        alerts.append({
            "level": "warning",
            "headline": "Too many soft ideas are surviving",
            "body": "The playbook has more weak/watch ideas than truly ready setups.",
            "target": "/admin/product-monitoring?filter=readiness",
            "target_label": "Review Readiness",
        })

    if no_thesis > 0:
        alerts.append({
            "level": "neutral",
            "headline": "Thesis quality needs work",
            "body": f"{no_thesis} play(s) are missing a thesis, which weakens later review and coaching quality.",
            "target": "/admin/product-monitoring?filter=thesis",
            "target_label": "Review Thesis Quality",
        })

    if weak_open_positions > 0:
        alerts.append({
            "level": "warning",
            "headline": "Weak open positions need review",
            "body": f"{weak_open_positions} open position(s) currently look weak by health or agreement.",
            "target": "/admin/product-monitoring?filter=positions",
            "target_label": "Review Open Positions",
        })

    if activated_against_engine > 0:
        alerts.append({
            "level": "warning",
            "headline": "Behavior drift: against-engine activations",
            "body": f"{activated_against_engine} activation event(s) were recorded against engine direction.",
            "target": "/admin/intelligence?filter=disagreement",
            "target_label": "Review Behavior Drift",
        })

    if high_conviction_no_thesis > 0:
        alerts.append({
            "level": "warning",
            "headline": "Behavior drift: confidence without structure",
            "body": f"{high_conviction_no_thesis} creation event(s) showed high conviction without a written thesis.",
            "target": "/admin/product-monitoring?filter=thesis",
            "target_label": "Fix Thesis Discipline",
        })

    if edited_after_weak_health > 0:
        alerts.append({
            "level": "neutral",
            "headline": "Edits are happening late",
            "body": f"{edited_after_weak_health} edit event(s) happened after setups were already weak.",
            "target": "/my-plays?filter=weak",
            "target_label": "Review Weak Plays",
        })

    if closed_weak > 0:
        alerts.append({
            "level": "warning",
            "headline": "Late weak closes are showing up",
            "body": f"{closed_weak} position close event(s) happened after weakness was already obvious.",
            "target": "/my-positions/analyze",
            "target_label": "Review Late Closes",
        })

    if created_after_loss_close > 0:
        alerts.append({
            "level": "neutral",
            "headline": "Reactive behavior may be forming",
            "body": f"{created_after_loss_close} play creation event(s) happened after a losing close.",
            "target": "/my-plays",
            "target_label": "Review Post-Loss Behavior",
        })

    if archived_against_engine > 0:
        alerts.append({
            "level": "warning",
            "headline": "Archived trades show against-engine behavior",
            "body": f"{archived_against_engine} archived trade(s) show against-engine activation behavior.",
            "target": "/my-positions/analyze",
            "target_label": "Review Archived Behavior",
        })

    if archived_high_conviction_no_thesis > 0:
        alerts.append({
            "level": "warning",
            "headline": "Archived trades show confidence without structure",
            "body": f"{archived_high_conviction_no_thesis} archived trade(s) carried high conviction without a thesis.",
            "target": "/my-positions/analyze",
            "target_label": "Review Archived Discipline",
        })

    if archived_late_edit > 0 or archived_late_weak_close > 0:
        alerts.append({
            "level": "warning",
            "headline": "Archived management behavior is leaking edge",
            "body": f"{archived_late_edit + archived_late_weak_close} archived trade(s) show late edits or late closes.",
            "target": "/my-positions/analyze",
            "target_label": "Review Management Leaks",
        })

    if archived_post_loss_creation > 0:
        alerts.append({
            "level": "neutral",
            "headline": "Archived trades show post-loss re-entry behavior",
            "body": f"{archived_post_loss_creation} archived trade(s) may have been created too soon after a loss.",
            "target": "/my-positions/analyze",
            "target_label": "Review Emotional Flow",
        })

    top_failure = zones.get("top_failure_cluster", {}) or {}
    if _safe_int(top_failure.get("count", 0)) > 0:
        alerts.append({
            "level": "neutral",
            "headline": "Failure cluster is visible",
            "body": f"{top_failure.get('label')} is currently the dominant failure cluster.",
            "target": "/admin/intelligence?filter=failure",
            "target_label": "Review Failure Cluster",
        })

    friction_headline = _norm_text(strongest_friction.get("headline", ""))
    friction_body = _norm_text(strongest_friction.get("body", ""))
    if friction_headline:
        alerts.append({
            "level": "neutral",
            "headline": friction_headline,
            "body": friction_body,
            "target": "/admin/product-monitoring?filter=friction",
            "target_label": "Review Friction",
        })

    if not alerts:
        alerts.append({
            "level": "positive",
            "headline": "Operator system looks stable",
            "body": "No shared cross-surface issue is standing out right now.",
            "target": "/admin",
            "target_label": "Stay on Admin",
        })

    priority_order = {"danger": 0, "warning": 1, "neutral": 2, "positive": 3}
    alerts = sorted(alerts, key=lambda a: priority_order.get(a.get("level", "neutral"), 99))

    return {
        "top_alert": alerts[0] if alerts else None,
        "alerts": alerts[:4],
    }


def build_shared_operator_alert_explanations(surface_alerts=None):
    surface_alerts = surface_alerts or {}
    alerts = surface_alerts.get("alerts", []) or []

    explained = []

    for alert in alerts:
        headline = _norm_text(alert.get("headline", "Operator Alert"))
        body = _norm_text(alert.get("body", ""))
        target = _norm_text(alert.get("target", "/admin"))
        target_label = _norm_text(alert.get("target_label", "Review"))
        level = _norm_text(alert.get("level", "neutral")).lower()

        trigger = "A cross-surface condition was detected."
        why_it_matters = "This issue can weaken decision quality, trust, or product clarity."
        first_action = f"Open {target_label.lower()} and review the underlying records."
        if_ignored = "The system may keep leaking edge or hiding quality problems."

        headline_lower = headline.lower()
        body_lower = body.lower()

        if "weak activations" in headline_lower:
            trigger = "Closed trade behavior suggests too many promoted ideas were weak when they were moved forward."
            why_it_matters = "Bad promotions contaminate trade outcomes and make the system look less accurate than it really is."
            first_action = "Open Activation Quality and compare weak activations against ready activations."
            if_ignored = "You will keep promoting soft setups and blaming the engine for avoidable losses."

        elif "disagreement" in headline_lower or "against-engine" in headline_lower:
            trigger = "The operator is taking or activating ideas that conflict with the engine direction more often than expected."
            why_it_matters = "Disagreement is only valuable when it is rare and well-justified. Too much of it turns the system into decoration."
            first_action = "Open Disagreement review and isolate the repeated symbols, setups, or conditions behind the conflict."
            if_ignored = "You risk training yourself to ignore the best part of the system: alignment."

        elif "soft ideas" in headline_lower or "readiness" in target.lower():
            trigger = "The playbook currently contains more weak/watch ideas than truly ready setups."
            why_it_matters = "A soft idea book makes the product feel noisy and makes activation discipline harder."
            first_action = "Open Readiness review and trim or downgrade weak/watch setups aggressively."
            if_ignored = "The inventory will keep bloating and signal quality will feel diluted."

        elif "thesis quality" in headline_lower or "without structure" in headline_lower:
            trigger = "Too many ideas are entering the system without enough written reasoning."
            why_it_matters = "No-thesis ideas weaken coaching, reduce accountability, and make review quality worse."
            first_action = "Open Thesis Quality and fix high-conviction plays that still have no written thesis."
            if_ignored = "Confidence will keep outrunning structure, and later analysis will stay muddy."

        elif "weak open positions" in headline_lower or "late weak closes" in headline_lower:
            trigger = "The live position layer contains setups that are already weak by health or agreement."
            why_it_matters = "Weak positions can turn manageable damage into larger losses if they are reviewed too late."
            first_action = "Open Weak Positions or Trade Analysis and review late-management behavior first."
            if_ignored = "The system will keep catching the weakness after the damage instead of before it."

        elif "failure cluster" in headline_lower:
            trigger = "A repeated failure pattern is appearing often enough to stand out as a cluster."
            why_it_matters = "Clusters are where the real edge leaks live. They usually expose a repeated structural mistake."
            first_action = "Open the failure cluster view and identify whether the leak is selection, disagreement, or management."
            if_ignored = "The same bad pattern will keep repeating under different symbols and conditions."

        elif "friction" in headline_lower or "friction" in body_lower:
            trigger = "The product monitoring layer found repeated usage friction."
            why_it_matters = "Friction causes abandonment, confusion, and lower trust in the workflow."
            first_action = "Open Product Monitoring and inspect the strongest friction point first."
            if_ignored = "Users will keep feeling the drag even if the engine itself improves."

        explained.append({
            "headline": headline,
            "body": body,
            "level": level,
            "target": target,
            "target_label": target_label,
            "trigger": trigger,
            "why_it_matters": why_it_matters,
            "first_action": first_action,
            "if_ignored": if_ignored,
        })

    if not explained:
        explained.append({
            "headline": "No shared operator alerts yet",
            "body": "The shared alert layer is not currently surfacing a major cross-system issue.",
            "level": "positive",
            "target": "/admin",
            "target_label": "Stay on Admin",
            "trigger": "No cross-surface threat is currently dominating.",
            "why_it_matters": "This usually means the system is stable enough to focus on refinement instead of repair.",
            "first_action": "Continue monitoring readiness, behavior, and data health.",
            "if_ignored": "Minor issues may still grow quietly if diagnostics are not checked regularly.",
        })

    return {
        "headline": "Shared operator alerts explanation layer",
        "summary": "These cards explain what triggered each alert, why it matters, and what to do next.",
        "items": explained,
    }


def build_admin_alerts(plays, positions, analysis):
    plays = plays or []
    positions = positions or []
    analysis = analysis or {}

    alerts = []
    ready_plays = 0
    weak_plays = 0
    disagreement_count = 0
    aligned_count = 0
    weak_open_positions = 0

    open_positions = [p for p in positions if not _is_closed_status(p.get("status", ""))]

    for play in _ensure_activation_readiness(plays):
        bucket = _activation_bucket(play)
        if bucket == "READY":
            ready_plays += 1
        elif bucket in {"WATCH", "WEAK"}:
            weak_plays += 1

        candidate = play.get("engine_candidate") or {}
        candidate_strategy = _norm_upper(candidate.get("strategy", ""))
        play_direction = _norm_upper(play.get("direction", ""))

        if candidate_strategy and play_direction in {"CALL", "PUT"}:
            if candidate_strategy == play_direction:
                aligned_count += 1
            else:
                disagreement_count += 1

    for pos in open_positions:
        if _agreement_score(pos) < 55 or _health_score(pos) < 35:
            weak_open_positions += 1

    wins = _safe_int((analysis.get("totals", {}) or {}).get("wins", 0))
    losses = _safe_int((analysis.get("totals", {}) or {}).get("losses", 0))
    flat = _safe_int((analysis.get("totals", {}) or {}).get("flat", 0))

    if weak_plays > ready_plays:
        alerts.append({
            "level": "warning",
            "headline": "Idea book is too soft",
            "body": "You currently have more weak/watch-only plays than ready plays. Tighten filtering before promoting more ideas.",
            "target": "/my-plays?filter=weak",
            "target_label": "Open Weak Plays",
        })

    if disagreement_count > aligned_count:
        alerts.append({
            "level": "warning",
            "headline": "Engine disagreement is elevated",
            "body": "More ideas are fighting the engine than aligning with it. That may be leaking edge.",
            "target": "/admin/intelligence",
            "target_label": "Review Admin Intelligence",
        })

    if weak_open_positions > 0:
        alerts.append({
            "level": "warning",
            "headline": "Weak positions are still open",
            "body": f"{weak_open_positions} open position(s) currently look weak by health or agreement and may need faster review.",
            "target": "/my-positions?filter=weak",
            "target_label": "Review Weak Positions",
        })

    if losses > wins:
        alerts.append({
            "level": "danger",
            "headline": "Loss pressure is leading",
            "body": "Archived losses are outweighing wins right now. Activation discipline and alignment need attention.",
            "target": "/my-positions/analyze",
            "target_label": "Open Trade Analysis",
        })

    if ready_plays > 0 and wins >= losses:
        alerts.append({
            "level": "positive",
            "headline": "There are real candidates on deck",
            "body": f"{ready_plays} play(s) currently look ready, and performance is not underwater.",
            "target": "/my-plays?filter=ready",
            "target_label": "Review Ready Plays",
        })

    if flat > max(1, wins):
        alerts.append({
            "level": "neutral",
            "headline": "Too many ideas are going nowhere",
            "body": "Flat outcomes are piling up. Some setups may be getting preserved without real edge.",
            "target": "/admin/product-monitoring",
            "target_label": "Open Product Monitoring",
        })

    if not alerts:
        alerts.append({
            "level": "positive",
            "headline": "Operator posture looks stable",
            "body": "No major cross-system alert is standing out right now.",
            "target": "/admin/intelligence",
            "target_label": "Open Admin Intelligence",
        })

    priority_order = {"danger": 0, "warning": 1, "neutral": 2, "positive": 3}
    alerts = sorted(alerts, key=lambda a: priority_order.get(a.get("level", "neutral"), 99))

    return {
        "top_alert": alerts[0] if alerts else None,
        "alerts": alerts[:4],
    }


def build_admin_intelligence_summary(plays, positions, analysis):
    plays = _ensure_activation_readiness(plays or [])
    positions = positions or []
    analysis = analysis or {}

    total_plays = len(plays)
    total_positions = len(positions)
    closed_positions = [p for p in positions if _is_closed_status(p.get("status", ""))]

    ready_plays = 0
    close_plays = 0
    weak_plays = 0
    inactive_plays = 0
    high_agreement_plays = 0
    high_conviction_plays = 0

    activated_ready = 0
    activated_close = 0
    activated_weak = 0
    activated_without_candidate = 0

    disagreement_count = 0
    aligned_count = 0

    weakest_activation_patterns = {}
    disagreement_patterns = {}
    condition_strength = {}
    condition_weakness = {}

    strongest_play = None
    weakest_play = None

    for play in plays:
        readiness = play.get("activation_readiness") or {}
        bucket = _activation_bucket(play)
        readiness_score = _safe_int(readiness.get("score", 0))
        agreement_score = _agreement_score(play)
        conviction = _norm_text(play.get("conviction", "Medium"))
        candidate = play.get("engine_candidate")
        market_context = play.get("market_context", {}) or {}

        if bucket == "READY":
            ready_plays += 1
        elif bucket == "CLOSE":
            close_plays += 1
        elif bucket in {"WATCH", "WEAK"}:
            weak_plays += 1
        else:
            inactive_plays += 1

        if agreement_score >= 75:
            high_agreement_plays += 1
        if conviction.lower() == "high":
            high_conviction_plays += 1

        candidate_strategy = _norm_upper((candidate or {}).get("strategy", ""))
        play_direction = _norm_upper(play.get("direction", ""))

        if candidate_strategy and play_direction in {"CALL", "PUT"}:
            if candidate_strategy == play_direction:
                aligned_count += 1
            else:
                disagreement_count += 1
                pattern = f"{play.get('symbol', 'UNKNOWN')} | {play_direction} vs {candidate_strategy}"
                disagreement_patterns[pattern] = disagreement_patterns.get(pattern, 0) + 1

        if strongest_play is None or readiness_score > _safe_int(strongest_play.get("activation_readiness", {}).get("score", 0)):
            strongest_play = play
        if weakest_play is None or readiness_score < _safe_int(weakest_play.get("activation_readiness", {}).get("score", 0)):
            weakest_play = play

        condition_label = " | ".join([
            _norm_upper(market_context.get("regime", "UNKNOWN")),
            _norm_upper(market_context.get("breadth", "UNKNOWN")),
            _norm_upper(market_context.get("mode", "UNKNOWN")),
        ])

        if bucket == "READY":
            condition_strength[condition_label] = condition_strength.get(condition_label, 0) + 1
        elif bucket in {"WATCH", "WEAK"}:
            condition_weakness[condition_label] = condition_weakness.get(condition_label, 0) + 1

    for pos in closed_positions:
        agreement_score = _agreement_score(pos)
        health_score = _health_score(pos)
        candidate = pos.get("engine_candidate")
        direction = _norm_upper(pos.get("direction", ""))
        candidate_strategy = _norm_upper((candidate or {}).get("strategy", ""))
        outcome = classify_trade_outcome(pos)

        if agreement_score >= 75 and health_score >= 75:
            if outcome == "WIN":
                activated_ready += 1
            elif outcome in {"LOSS", "FLAT"}:
                activated_close += 1
        elif agreement_score < 55 or health_score < 35:
            if outcome in {"LOSS", "FLAT"}:
                activated_weak += 1

        if not candidate:
            activated_without_candidate += 1

        if candidate_strategy and direction in {"CALL", "PUT"} and candidate_strategy != direction:
            pattern = f"{pos.get('symbol', 'UNKNOWN')} | activated {direction} against {candidate_strategy}"
            weakest_activation_patterns[pattern] = weakest_activation_patterns.get(pattern, 0) + 1

        if not candidate and outcome == "LOSS":
            pattern = f"{pos.get('symbol', 'UNKNOWN')} | no engine tracking"
            weakest_activation_patterns[pattern] = weakest_activation_patterns.get(pattern, 0) + 1

    trade_totals = analysis.get("totals", {}) or {}
    wins = _safe_int(trade_totals.get("wins", 0))
    losses = _safe_int(trade_totals.get("losses", 0))
    flat = _safe_int(trade_totals.get("flat", 0))

    if wins > losses:
        performance_headline = "System-aligned behavior is producing more wins than losses."
        performance_summary = "The system is finding enough signal to matter, but weak process can still leak edge."
    elif losses > wins:
        performance_headline = "Losses are outweighing wins."
        performance_summary = "The leak is likely coming from weak activations, misalignment, or management issues."
    else:
        performance_headline = "Performance is balanced."
        performance_summary = "The edge is present, but not yet sharp enough to dominate outcomes."

    if ready_plays > weak_plays:
        idea_quality_headline = "Idea quality is leaning constructive."
        idea_quality_summary = "You have more serious candidates than weak setups, which is what a healthy idea book should look like."
    elif weak_plays > ready_plays:
        idea_quality_headline = "Too many weak ideas are surviving."
        idea_quality_summary = "The system needs stricter filtering before ideas get promoted or preserved."
    else:
        idea_quality_headline = "Idea quality is mixed."
        idea_quality_summary = "Some setups are worth attention, but the book is not clean enough yet."

    if activated_weak > activated_ready:
        activation_headline = "Weak activations are costing more than strong ones are paying."
        activation_summary = "Too many promoted plays did not deserve live handling when they were moved forward."
    elif activated_ready > 0:
        activation_headline = "The better activations are earning their place."
        activation_summary = "When strong setups are promoted, the system has a better chance to convert them into useful outcomes."
    else:
        activation_headline = "Activation quality is still unclear."
        activation_summary = "There is not enough clean separation yet between strong promotions and weak ones."

    if disagreement_count > aligned_count:
        disagreement_headline = "You are fighting the engine too often."
        disagreement_summary = "A meaningful share of ideas is leaning against the engine instead of working with it."
    elif aligned_count > disagreement_count:
        disagreement_headline = "Most active ideas are aligned with the engine."
        disagreement_summary = "That is a healthier posture and gives the system a better chance to prove its edge."
    else:
        disagreement_headline = "Alignment vs disagreement is still mixed."
        disagreement_summary = "The operator posture is not clearly cooperative or clearly adversarial yet."

    strongest_condition = _top_count_item(condition_strength, "No strong condition cluster yet.")
    weakest_condition = _top_count_item(condition_weakness, "No weak condition cluster yet.")
    top_failure_cluster = _top_count_item(weakest_activation_patterns, "No failure cluster yet.")
    top_disagreement_cluster = _top_count_item(disagreement_patterns, "No disagreement cluster yet.")

    coaching_cards = []
    if weak_plays > ready_plays:
        coaching_cards.append({
            "headline": "Tighten the book",
            "body": "Your current play inventory has too many weak or watch-only ideas hanging around. Cleanliness matters."
        })
    if activated_weak > activated_ready:
        coaching_cards.append({
            "headline": "Promotions are too loose",
            "body": "You are moving too many soft setups into live management before they have earned it."
        })
    if disagreement_count > aligned_count:
        coaching_cards.append({
            "headline": "Respect the engine more",
            "body": "Disagreement is not automatically bad, but too much of it turns the system into decoration instead of edge."
        })
    if losses > wins:
        coaching_cards.append({
            "headline": "Loss pressure is real",
            "body": "Right now the product should prioritize better activation discipline and stronger alignment filters before scaling confidence."
        })
    if not coaching_cards:
        coaching_cards.append({
            "headline": "System posture is constructive",
            "body": "The current structure is behaving well enough to keep refining rather than overcorrecting."
        })

    return {
        "counts": {
            "plays": total_plays,
            "positions": total_positions,
            "closed_positions": len(closed_positions),
            "ready_plays": ready_plays,
            "close_plays": close_plays,
            "weak_plays": weak_plays,
            "inactive_plays": inactive_plays,
            "high_agreement_plays": high_agreement_plays,
            "high_conviction_plays": high_conviction_plays,
        },
        "performance": {
            "headline": performance_headline,
            "summary": performance_summary,
        },
        "idea_quality": {
            "headline": idea_quality_headline,
            "summary": idea_quality_summary,
        },
        "activation_quality": {
            "headline": activation_headline,
            "summary": activation_summary,
            "ready_activations": activated_ready,
            "weak_activations": activated_weak,
            "unclear_activations": activated_close,
            "without_candidate": activated_without_candidate,
        },
        "disagreement": {
            "headline": disagreement_headline,
            "summary": disagreement_summary,
            "aligned_count": aligned_count,
            "disagreement_count": disagreement_count,
            "top_cluster": top_disagreement_cluster,
        },
        "trade_totals": {
            "wins": wins,
            "losses": losses,
            "flat": flat,
        },
        "zones": {
            "strongest_condition": strongest_condition,
            "weakest_condition": weakest_condition,
            "top_failure_cluster": top_failure_cluster,
        },
        "strongest_play": {
            "symbol": strongest_play.get("symbol"),
            "score": _safe_int((strongest_play.get("activation_readiness", {}) or {}).get("score", 0)),
            "headline": (strongest_play.get("activation_readiness", {}) or {}).get("headline"),
        } if strongest_play else None,
        "weakest_play": {
            "symbol": weakest_play.get("symbol"),
            "score": _safe_int((weakest_play.get("activation_readiness", {}) or {}).get("score", 0)),
            "headline": (weakest_play.get("activation_readiness", {}) or {}).get("headline"),
        } if weakest_play else None,
        "coaching_cards": coaching_cards,
    }


def build_product_monitoring_summary(plays, positions, analysis):
    plays = _ensure_activation_readiness(plays or [])
    positions = positions or []
    analysis = analysis or {}

    total_plays = len(plays)
    total_positions = len(positions)

    open_positions = [p for p in positions if not _is_closed_status(p.get("status", ""))]
    closed_positions = [p for p in positions if _is_closed_status(p.get("status", ""))]

    no_thesis_count = 0
    no_notes_count = 0
    high_conviction_no_thesis = 0
    watching_count = 0
    archived_count = 0
    open_play_count = 0
    weak_open_positions = 0
    strong_open_positions = 0

    readiness_buckets = {
        "READY": 0,
        "CLOSE": 0,
        "WATCH": 0,
        "WEAK": 0,
        "INACTIVE": 0,
    }

    friction_points = []
    setup_quality_counts = {}
    thesis_quality_counts = {
        "with_thesis": 0,
        "without_thesis": 0,
    }

    for play in plays:
        bucket = _activation_bucket(play)
        readiness_buckets[bucket] = readiness_buckets.get(bucket, 0) + 1

        status = _norm_text(play.get("status", "Open")).lower()
        thesis = _norm_text(play.get("thesis", ""))
        notes = _norm_text(play.get("notes", ""))
        conviction = _norm_text(play.get("conviction", "Medium")).lower()
        agreement_score = _agreement_score(play)
        health_score = _health_score(play)

        if not thesis:
            no_thesis_count += 1
            thesis_quality_counts["without_thesis"] += 1
        else:
            thesis_quality_counts["with_thesis"] += 1

        if not notes:
            no_notes_count += 1

        if conviction == "high" and not thesis:
            high_conviction_no_thesis += 1

        if status == "watching":
            watching_count += 1
        elif status == "archived":
            archived_count += 1
        elif status == "open":
            open_play_count += 1

        setup_label = "strong" if agreement_score >= 75 and health_score >= 75 else "soft"
        setup_quality_counts[setup_label] = setup_quality_counts.get(setup_label, 0) + 1

    for pos in open_positions:
        agreement_score = _agreement_score(pos)
        health_score = _health_score(pos)

        if agreement_score >= 75 and health_score >= 75:
            strong_open_positions += 1
        if agreement_score < 55 or health_score < 35:
            weak_open_positions += 1

    if no_thesis_count > 0:
        friction_points.append({
            "headline": "Ideas without thesis",
            "body": f"{no_thesis_count} plays do not have a written thesis. That weakens coaching quality and later review quality."
        })
    if high_conviction_no_thesis > 0:
        friction_points.append({
            "headline": "High conviction without explanation",
            "body": f"{high_conviction_no_thesis} high-conviction plays were entered without a thesis. Confidence without reasoning is a product and behavior risk."
        })
    if weak_open_positions > 0:
        friction_points.append({
            "headline": "Weak positions still open",
            "body": f"{weak_open_positions} open positions currently look weak by health or agreement. That suggests active decision friction."
        })
    if readiness_buckets.get("WATCH", 0) + readiness_buckets.get("WEAK", 0) > readiness_buckets.get("READY", 0):
        friction_points.append({
            "headline": "Too many watch-only ideas",
            "body": "A large share of the playbook is sitting in weak or watch states instead of becoming clean activation candidates."
        })
    if not friction_points:
        friction_points.append({
            "headline": "Friction looks controlled",
            "body": "The current playbook and position behavior do not show obvious product-usage breakdowns right now."
        })

    wins = _safe_int((analysis.get("totals", {}) or {}).get("wins", 0))
    losses = _safe_int((analysis.get("totals", {}) or {}).get("losses", 0))
    flat = _safe_int((analysis.get("totals", {}) or {}).get("flat", 0))

    if total_plays == 0:
        adoption_headline = "No meaningful usage yet."
        adoption_summary = "The system needs more play creation and interaction before usage patterns are trustworthy."
    elif open_play_count > 0 or total_positions > 0:
        adoption_headline = "The workflow is being used."
        adoption_summary = "Users are creating ideas and carrying some of them into live management, which is a good signal for core product usefulness."
    else:
        adoption_headline = "Usage exists, but the flow is stalling."
        adoption_summary = "Ideas are being stored, but not enough are progressing into deeper parts of the workflow."

    if wins > losses:
        retention_headline = "The system has retention potential."
        retention_summary = "Winning behavior is showing up often enough that the experience can feel reinforcing."
    elif losses > wins:
        retention_headline = "The experience may feel discouraging."
        retention_summary = "If losses dominate, the product needs clearer coaching and stronger filtering to protect trust."
    else:
        retention_headline = "Retention signal is still mixed."
        retention_summary = "Outcomes are not yet clearly strong enough or weak enough to define stickiness."

    strongest_friction = friction_points[0] if friction_points else {
        "headline": "No clear friction point yet.",
        "body": "Not enough signal.",
    }

    return {
        "counts": {
            "plays": total_plays,
            "positions": total_positions,
            "open_positions": len(open_positions),
            "closed_positions": len(closed_positions),
            "open_plays": open_play_count,
            "watching_plays": watching_count,
            "archived_plays": archived_count,
        },
        "readiness_buckets": readiness_buckets,
        "setup_quality": {
            "strong": setup_quality_counts.get("strong", 0),
            "soft": setup_quality_counts.get("soft", 0),
        },
        "thesis_quality": thesis_quality_counts,
        "position_quality": {
            "strong_open_positions": strong_open_positions,
            "weak_open_positions": weak_open_positions,
        },
        "adoption": {
            "headline": adoption_headline,
            "summary": adoption_summary,
        },
        "retention": {
            "headline": retention_headline,
            "summary": retention_summary,
        },
        "outcomes": {
            "wins": wins,
            "losses": losses,
            "flat": flat,
        },
        "friction_points": friction_points,
        "strongest_friction": strongest_friction,
    }


from datetime import datetime


EVENT_LOG_FILE = "data/event_log.json"


def get_event_log() -> List[Dict[str, Any]]:
    rows = load_json(EVENT_LOG_FILE, [])
    return rows if isinstance(rows, list) else []


def save_event_log(rows: List[Dict[str, Any]]) -> None:
    if not isinstance(rows, list):
        rows = []
    save_json(EVENT_LOG_FILE, rows)


def track_event(event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
    payload = payload or {}

    rows = get_event_log()
    rows.append(
        {
            "event_type": str(event_type or "").strip(),
            "payload": payload,
            "created_at": datetime.now().isoformat(),
        }
    )

    rows = rows[-5000:]
    save_event_log(rows)


def build_event_analytics_summary() -> Dict[str, Any]:
    rows = get_event_log()

    event_counts: Dict[str, int] = {}
    recent_events = rows[-25:] if rows else []

    play_created = 0
    play_edited = 0
    play_activated = 0
    position_updated = 0
    position_closed = 0

    for row in rows:
        event_type = str(row.get("event_type", "")).strip()
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

        if event_type == "play_created":
            play_created += 1
        elif event_type == "play_edited":
            play_edited += 1
        elif event_type == "play_activated":
            play_activated += 1
        elif event_type == "position_updated":
            position_updated += 1
        elif event_type == "position_closed":
            position_closed += 1

    if play_created == 0:
        headline = "No event behavior recorded yet."
        summary = "The behavioral event layer has not captured enough actions yet."
    elif play_activated > play_created:
        headline = "Activation flow is running hot."
        summary = "More activation behavior is being recorded than expected relative to creation, so review event quality and user flow."
    elif play_activated > 0:
        headline = "Behavior tracking is live."
        summary = "The system is capturing creation, activation, and management behavior well enough to build deeper operator insights."
    else:
        headline = "Ideas are being created, but activation is lagging."
        summary = "Users are starting the workflow, but they are not progressing deeply enough into live action."

    return {
        "headline": headline,
        "summary": summary,
        "counts": {
            "play_created": play_created,
            "play_edited": play_edited,
            "play_activated": play_activated,
            "position_updated": position_updated,
            "position_closed": position_closed,
        },
        "event_counts": event_counts,
        "recent_events": recent_events,
    }


def build_behavioral_event_insights() -> Dict[str, Any]:
    rows = get_event_log()

    activated_against_engine = 0
    high_conviction_no_thesis = 0
    edited_after_weak_health = 0
    closed_weak = 0
    loss_closes = 0
    created_after_loss_close = 0

    last_loss_close_at = None

    for row in rows:
        event_type = str(row.get("event_type", "")).strip()
        payload = row.get("payload", {}) or {}
        created_at = str(row.get("created_at", "")).strip()

        if event_type == "play_created":
            if payload.get("conviction") == "High" and not payload.get("has_thesis", False):
                high_conviction_no_thesis += 1
            if last_loss_close_at:
                created_after_loss_close += 1

        elif event_type == "play_activated":
            if bool(payload.get("activated_against_engine", False)):
                activated_against_engine += 1

        elif event_type == "play_edited":
            if bool(payload.get("edited_after_weak_health", False)):
                edited_after_weak_health += 1

        elif event_type == "position_closed":
            if bool(payload.get("closed_weak", False)):
                closed_weak += 1
            if str(payload.get("outcome", "")).strip().upper() == "LOSS":
                loss_closes += 1
                last_loss_close_at = created_at

    cards = []

    if activated_against_engine > 0:
        cards.append({
            "headline": "Activated against engine",
            "body": f"{activated_against_engine} activation event(s) were recorded against the engine’s direction.",
        })

    if high_conviction_no_thesis > 0:
        cards.append({
            "headline": "High conviction without thesis",
            "body": f"{high_conviction_no_thesis} play creation event(s) showed high conviction without a written thesis.",
        })

    if edited_after_weak_health > 0:
        cards.append({
            "headline": "Edits after weakness",
            "body": f"{edited_after_weak_health} play edit event(s) happened after the setup was already weak.",
        })

    if closed_weak > 0:
        cards.append({
            "headline": "Late weak closes",
            "body": f"{closed_weak} close event(s) happened while agreement or health was already weak.",
        })

    if created_after_loss_close > 0:
        cards.append({
            "headline": "Created after loss close",
            "body": f"{created_after_loss_close} play creation event(s) happened after a recorded losing close, which may indicate reactive behavior.",
        })

    if not cards:
        cards.append({
            "headline": "Behavior layer still early",
            "body": "Not enough behavioral signal yet to identify operator habit patterns.",
        })

    return {
        "counts": {
            "activated_against_engine": activated_against_engine,
            "high_conviction_no_thesis": high_conviction_no_thesis,
            "edited_after_weak_health": edited_after_weak_health,
            "closed_weak": closed_weak,
            "loss_closes": loss_closes,
            "created_after_loss_close": created_after_loss_close,
        },
        "cards": cards,
    }


def maybe_track_page_view(path: str) -> None:
    metrics = load_json("data/admin_metrics.json", {})
    if not isinstance(metrics, dict):
        metrics = {}

    page_views = metrics.get("page_views", {})
    if not isinstance(page_views, dict):
        page_views = {}

    page_views[path] = _safe_int(page_views.get(path, 0), 0) + 1
    metrics["page_views"] = page_views
    save_json("data/admin_metrics.json", metrics)


def build_admin_dashboard_context():
    shared = build_admin_shared_context()
    users = load_json("data/users.json", [])
    if not isinstance(users, list):
        users = []

    data_health = build_data_health_summary()

    return {
        "positions": shared.get("positions", []),
        "signals": get_signals(),
        "users": users,
        "metrics": get_admin_metrics(),
        "proof": performance_summary(),
        "snapshot": get_dashboard_snapshot(),
        "system": get_system_state(),
        "admin_alerts": build_admin_alerts(
            shared.get("plays", []),
            shared.get("positions", []),
            shared.get("analysis", {}),
        ),
        "surface_alerts": shared.get("surface_alerts", {}),
        "quick_actions": shared.get("quick_actions", {}),
        "event_analytics": build_event_analytics_summary(),
        "behavior_priority": shared.get("behavior_priority", {}),
        "behavioral_insights": shared.get("behavioral_insights", {}),
        "behavior_risk": shared.get("behavior_risk", {}),
        "data_health": data_health,
        "play_command": shared.get("play_command", {}),
        "canonical": shared.get("canonical", {}),
    }

def build_all_symbols_page_summary(rows):
    rows = rows or []

    total = len(rows)
    strong = 0
    medium = 0
    weak = 0

    for row in rows:
        score = _safe_int(row.get("latest_score", 0))
        if score >= 75:
            strong += 1
        elif score >= 55:
            medium += 1
        else:
            weak += 1

    if total == 0:
        headline = "No symbol coverage loaded yet."
        summary = "The broader symbol directory does not currently have enough coverage loaded."
        chip = "Missing Coverage"
    elif strong > weak:
        headline = "Broad coverage is loaded and usable."
        summary = "The symbol directory has enough strong candidates to feel like a real research surface instead of a placeholder list."
        chip = "Constructive"
    elif weak > strong:
        headline = "Coverage exists, but the directory is still soft."
        summary = "A larger share of the visible symbols is weak or mixed, so this page is giving breadth more than conviction."
        chip = "Mixed"
    else:
        headline = "The symbol directory is balanced but not sharp."
        summary = "Coverage is present, but the intelligence layer still needs stronger separation between high-quality and low-quality symbols."
        chip = "Neutral"

    return {
        "headline": headline,
        "summary": summary,
        "chip": chip,
        "total": total,
        "strong": strong,
        "medium": medium,
        "weak": weak,
    }


# ============================================================
# DIAGNOSTICS BUILDERS
# ============================================================

def build_template_diagnostics() -> Dict[str, Any]:
    required_templates = [
        "landing.html",
        "dashboard.html",
        "signals.html",
        "signal_symbol.html",
        "positions.html",
        "proof.html",
        "admin.html",
        "admin_intelligence.html",
        "admin_product_monitoring.html",
        "my_plays.html",
        "my_play_detail.html",
        "my_positions.html",
        "my_position_detail.html",
        "my_trade_analysis.html",
        "all_symbols.html",
        "trade_detail.html",
        "why_this_trade.html",
        "premium_analysis.html",
        "analytics.html",
        "analytics_overview.html",
        "analytics_performance.html",
        "analytics_risk.html",
        "strategy_behavior.html",
        "simulation.html",
        "login.html",
        "signup.html",
        "upgrade.html",
        "notifications.html",
        "account.html",
    ]

    rows = []
    missing = 0

    for name in required_templates:
        exists = template_exists(name)
        if not exists:
            missing += 1
        rows.append({
            "name": name,
            "exists": exists,
            "status": "OK" if exists else "MISSING",
        })

    headline = "Template surface looks healthy." if missing == 0 else "Some templates are missing."
    summary = (
        "All expected templates were found."
        if missing == 0 else
        f"{missing} expected template(s) are missing, which may force fallback rendering."
    )

    return {
        "headline": headline,
        "summary": summary,
        "missing_count": missing,
        "rows": rows,
    }


def build_file_diagnostics() -> Dict[str, Any]:
    targets = [
        "data/signals.json",
        "data/symbol_intelligence.json",
        "data/symbol_meta.json",
        "data/symbol_news.json",
        "data/recent_reports.json",
        "data/portfolio_summary.json",
        "data/account_snapshot.json",
        "data/performance_summary.json",
        "data/drawdown_history.json",
        "data/users.json",
        "data/admin_metrics.json",
        "data/event_log.json",
        "data/notifications.json",
        "data/trade_details.json",
        "data/candidate_log.json",
        "data/live_activity.json",
        "data/equity_curve.json",
        "data/system_state.json",
        "data/pipeline_status.json",
    ]

    rows = []
    missing = 0

    for path in targets:
        file_path = Path(path)
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0

        parsed_type = "missing"
        item_count = None

        if exists:
            payload = load_json(path, None)
            if isinstance(payload, list):
                parsed_type = "list"
                item_count = len(payload)
            elif isinstance(payload, dict):
                parsed_type = "dict"
                item_count = len(payload)
            elif payload is None:
                parsed_type = "unreadable"
            else:
                parsed_type = type(payload).__name__

        if not exists:
            missing += 1

        rows.append({
            "path": path,
            "exists": exists,
            "size": size,
            "parsed_type": parsed_type,
            "item_count": item_count,
            "status": "OK" if exists else "MISSING",
        })

    headline = "Core data files look present." if missing == 0 else "Some core data files are missing."
    summary = (
        "The main data files exist and are readable enough for the app to function."
        if missing == 0 else
        f"{missing} core data file(s) are missing."
    )

    return {
        "headline": headline,
        "summary": summary,
        "missing_count": missing,
        "rows": rows,
    }


def build_symbol_coverage_diagnostics() -> Dict[str, Any]:
    universe_summary = safe_run("get_market_universe_summary", get_market_universe_summary, {
        "total": 0,
        "counts_by_type": {},
        "top_sources": [],
        "rows": [],
    })

    symbol_meta = safe_dict(load_json("data/symbol_meta.json", {}))
    symbol_intel = safe_dict(load_json("data/symbol_intelligence.json", {}))
    symbol_news = safe_dict(load_json("data/symbol_news.json", {}))

    universe_rows = safe_list(universe_summary.get("rows", []))

    coverage_rows = []
    missing_meta = 0
    missing_intel = 0
    missing_news = 0

    for item in universe_rows:
        if not isinstance(item, dict):
            continue

        symbol = _norm_upper(item.get("symbol"))
        if not symbol:
            continue

        has_meta = isinstance(symbol_meta.get(symbol), dict)
        has_intel = isinstance(symbol_intel.get(symbol), dict)

        news_row = symbol_news.get(symbol, {})
        has_news = False
        if isinstance(news_row, dict):
            has_news = isinstance(news_row.get("items", []), list) and len(news_row.get("items", [])) > 0
        elif isinstance(news_row, list):
            has_news = len(news_row) > 0

        if not has_meta:
            missing_meta += 1
        if not has_intel:
            missing_intel += 1
        if not has_news:
            missing_news += 1

        coverage_rows.append({
            "symbol": symbol,
            "has_meta": has_meta,
            "has_intelligence": has_intel,
            "has_news": has_news,
            "priority_rank": item.get("priority_rank", 0),
            "source_tags": item.get("source_tags", []),
            "asset_type": item.get("asset_type", "equity"),
        })

    headline = "Market universe coverage is connected." if universe_rows else "No market universe loaded yet."
    summary = (
        f"{len(coverage_rows)} universe symbol(s) checked across meta, intelligence, and news."
        if universe_rows else
        "The market universe is empty, so coverage cannot be evaluated yet."
    )

    return {
        "headline": headline,
        "summary": summary,
        "total_symbols": len(coverage_rows),
        "missing_meta": missing_meta,
        "missing_intelligence": missing_intel,
        "missing_news": missing_news,
        "counts_by_type": universe_summary.get("counts_by_type", {}),
        "top_sources": universe_summary.get("top_sources", []),
        "rows": coverage_rows[:150],
    }

def build_admin_diagnostics() -> Dict[str, Any]:
    data_health = build_data_health_summary()
    file_diagnostics = build_file_diagnostics()
    template_diagnostics = build_template_diagnostics()
    symbol_coverage = build_symbol_coverage_diagnostics()

    cards = []

    if file_diagnostics["missing_count"] > 0:
        cards.append({
            "headline": "Missing data files detected",
            "body": f"{file_diagnostics['missing_count']} core data file(s) are missing.",
            "level": "danger",
        })

    if template_diagnostics["missing_count"] > 0:
        cards.append({
            "headline": "Template gaps detected",
            "body": f"{template_diagnostics['missing_count']} expected template(s) are missing.",
            "level": "warning",
        })

    if symbol_coverage["missing_news"] > 0:
        cards.append({
            "headline": "News coverage gaps detected",
            "body": f"{symbol_coverage['missing_news']} tracked symbol(s) do not currently have cached news.",
            "level": "warning",
        })

    if symbol_coverage["missing_intelligence"] > 0:
        cards.append({
            "headline": "Symbol intelligence gaps detected",
            "body": f"{symbol_coverage['missing_intelligence']} tracked symbol(s) do not currently have symbol intelligence records.",
            "level": "warning",
        })

    if not cards:
        cards.append({
            "headline": "Diagnostics surface looks healthy",
            "body": "No major structural diagnostics issue is standing out right now.",
            "level": "positive",
        })

    diagnostics = {
        "headline": "Admin diagnostics are live.",
        "summary": "This page checks whether the system has the files, templates, freshness, and symbol coverage it needs.",
        "cards": cards,
        "data_health": data_health,
        "file_diagnostics": file_diagnostics,
        "template_diagnostics": template_diagnostics,
        "symbol_coverage": symbol_coverage,
    }

    diagnostics["repair_recommendations"] = build_repair_recommendations(diagnostics)
    return diagnostics


def _recommendation_card(
    key: str,
    headline: str,
    severity: str,
    why: str,
    action: str,
    owner: str,
    target: str = "/admin/diagnostics",
    target_label: str = "Open Diagnostics",
) -> Dict[str, Any]:
    return {
        "key": key,
        "headline": headline,
        "severity": severity,
        "why": why,
        "action": action,
        "owner": owner,
        "target": target,
        "target_label": target_label,
    }


def build_repair_recommendations(diagnostics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    diagnostics = diagnostics or build_admin_diagnostics()

    data_health = diagnostics.get("data_health", {}) or {}
    file_diag = diagnostics.get("file_diagnostics", {}) or {}
    template_diag = diagnostics.get("template_diagnostics", {}) or {}
    symbol_cov = diagnostics.get("symbol_coverage", {}) or {}

    freshness = data_health.get("freshness", {}) or {}
    file_rows = file_diag.get("rows", []) or []
    template_rows = template_diag.get("rows", []) or []

    recommendations = []

    missing_files = [row for row in file_rows if not row.get("exists")]
    missing_templates = [row for row in template_rows if not row.get("exists")]

    critical_files = {
        "data/signals.json": {
            "why": "Signals power multiple pages and downstream intelligence layers.",
            "action": "Re-run the signal-generation pipeline and confirm the file is being written.",
            "owner": "signals pipeline",
        },
        "data/symbol_intelligence.json": {
            "why": "Symbol pages lose their deep intelligence layer without this file.",
            "action": "Rebuild symbol intelligence and verify the write step is completing.",
            "owner": "symbol intelligence pipeline",
        },
        "data/recent_reports.json": {
            "why": "Analytics and proof surfaces weaken when recent reports are missing.",
            "action": "Re-run the report generation step and confirm report history is being saved.",
            "owner": "reporting pipeline",
        },
        "data/pipeline_status.json": {
            "why": "Freshness and diagnostics depend on this file for last-run visibility.",
            "action": "Restore pipeline status writes after each major pipeline stage.",
            "owner": "pipeline status writer",
        },
    }

    optional_files = {
        "data/equity_curve.json": {
            "why": "Equity views and visual history can soften without this file.",
            "action": "Rebuild the equity curve export if you want the visual equity surface restored.",
            "owner": "analytics export layer",
        },
        "data/live_activity.json": {
            "why": "Live activity surfaces become thinner without this file.",
            "action": "Restore the activity writer if you want richer live-feed surfaces.",
            "owner": "activity logging layer",
        },
        "data/notifications.json": {
            "why": "Notification surfaces fall back quieter without this file.",
            "action": "Rebuild or regenerate notifications if the notification center matters right now.",
            "owner": "notification layer",
        },
    }

    for row in missing_files:
        path = row.get("path")
        if path in critical_files:
            meta = critical_files[path]
            recommendations.append(
                _recommendation_card(
                    key=f"missing:{path}",
                    headline=f"Restore critical file: {path}",
                    severity="danger",
                    why=meta["why"],
                    action=meta["action"],
                    owner=meta["owner"],
                )
            )
        else:
            meta = optional_files.get(path, {
                "why": "This file is expected by at least one app surface.",
                "action": "Restore the process that generates this file or mark it intentionally optional.",
                "owner": "supporting data pipeline",
            })
            recommendations.append(
                _recommendation_card(
                    key=f"missing:{path}",
                    headline=f"Restore supporting file: {path}",
                    severity="warning",
                    why=meta["why"],
                    action=meta["action"],
                    owner=meta["owner"],
                )
            )

    if missing_templates:
        names = ", ".join([row.get("name", "unknown") for row in missing_templates[:5]])
        recommendations.append(
            _recommendation_card(
                key="missing_templates",
                headline="Restore missing template coverage",
                severity="warning",
                why="Fallback rendering can keep the app alive, but missing templates weaken the product experience.",
                action=f"Create or restore the missing template(s): {names}.",
                owner="template layer",
            )
        )

    engine_freshness = freshness.get("engine", {}) or {}
    symbol_freshness = freshness.get("symbol_intelligence", {}) or {}
    news_freshness = freshness.get("news", {}) or {}

    if engine_freshness.get("is_stale"):
        recommendations.append(
            _recommendation_card(
                key="stale_engine",
                headline="Refresh stale engine state",
                severity="warning" if engine_freshness.get("level") == "warning" else "danger",
                why="Old engine state can make signals, admin views, and downstream logic feel stale or misleading.",
                action="Re-run the engine pipeline and confirm pipeline_status is updated after completion.",
                owner="engine runner",
            )
        )

    if symbol_freshness.get("is_stale"):
        recommendations.append(
            _recommendation_card(
                key="stale_symbol_intel",
                headline="Refresh stale symbol intelligence",
                severity="warning" if symbol_freshness.get("level") == "warning" else "danger",
                why="Symbol pages lose quality when intelligence becomes old or disconnected from the latest signal layer.",
                action="Rebuild symbol intelligence and confirm fresh writes to symbol_intelligence.json and pipeline_status.json.",
                owner="symbol intelligence pipeline",
            )
        )

    if news_freshness.get("is_stale"):
        recommendations.append(
            _recommendation_card(
                key="stale_news",
                headline="Refresh stale news cache",
                severity="warning" if news_freshness.get("level") == "warning" else "danger",
                why="Old news weakens symbol pages and reduces the system’s sense of current awareness.",
                action="Run a bulk symbol news refresh and verify symbol_news.json is filling with current items.",
                owner="news refresh pipeline",
            )
        )

    total_symbols = _safe_int(symbol_cov.get("total_symbols", 0))
    missing_intelligence = _safe_int(symbol_cov.get("missing_intelligence", 0))
    missing_news = _safe_int(symbol_cov.get("missing_news", 0))
    missing_meta = _safe_int(symbol_cov.get("missing_meta", 0))

    if total_symbols > 0 and missing_intelligence > 0:
        recommendations.append(
            _recommendation_card(
                key="coverage_intelligence",
                headline="Repair symbol intelligence coverage gaps",
                severity="warning",
                why=f"{missing_intelligence} tracked symbol(s) do not currently have intelligence records.",
                action="Backfill symbol intelligence across the tracked universe, then verify coverage counts improve.",
                owner="symbol intelligence coverage builder",
            )
        )

    if total_symbols > 0 and missing_news > 0:
        recommendations.append(
            _recommendation_card(
                key="coverage_news",
                headline="Repair cached news coverage gaps",
                severity="warning",
                why=f"{missing_news} tracked symbol(s) do not currently have cached news.",
                action="Run a bulk tracked-symbol news refresh and confirm the symbol news cache begins filling.",
                owner="news cache builder",
            )
        )

    if total_symbols > 0 and missing_meta > 0:
        recommendations.append(
            _recommendation_card(
                key="coverage_meta",
                headline="Repair symbol metadata coverage gaps",
                severity="neutral",
                why=f"{missing_meta} tracked symbol(s) are missing metadata like company name or blurb.",
                action="Backfill symbol_meta.json so coverage feels richer and less ticker-only.",
                owner="symbol metadata builder",
            )
        )

    if total_symbols < 200:
        recommendations.append(
            _recommendation_card(
                key="broad_universe",
                headline="Expand market universe coverage",
                severity="warning",
                why=f"Only {total_symbols} tracked symbol(s) are currently visible. That is not broad enough for near-market-wide awareness.",
                action="Add a broader market-universe file and pipeline stage, then cull user-facing results from that larger base.",
                owner="market universe pipeline",
            )
        )

    if not recommendations:
        recommendations.append(
            _recommendation_card(
                key="stable",
                headline="No urgent repair recommendation",
                severity="positive",
                why="Diagnostics are not surfacing a major structural gap right now.",
                action="Keep monitoring freshness, coverage, and behavior diagnostics regularly.",
                owner="operator",
            )
        )

    severity_order = {
        "danger": 0,
        "warning": 1,
        "neutral": 2,
        "positive": 3,
    }
    recommendations = sorted(
        recommendations,
        key=lambda x: severity_order.get(x.get("severity", "neutral"), 99),
    )

    top_fix = recommendations[0] if recommendations else None

    return {
        "headline": "Repair recommendations are active.",
        "summary": "These recommendations translate diagnostics into action steps, priorities, and ownership.",
        "top_fix": top_fix,
        "items": recommendations[:12],
    }


# ============================================================
# DATA BUILDERS
# ============================================================

# ============================================================
# SECTION 72AP — CANONICAL DASHBOARD SNAPSHOT
# ============================================================

def get_dashboard_snapshot() -> Dict[str, Any]:
    snapshot = get_canonical_snapshot()
    final_account = snapshot.get("final_account_snapshot", {})
    if not isinstance(final_account, dict):
        final_account = {}

    return {
        "estimated_account_value": final_account.get("estimated_account_value", 1000),
        "buying_power": final_account.get("buying_power", 1000),
        "open_positions": final_account.get("open_positions", 0),
        "realized_pnl": final_account.get("realized_pnl", 0.0),
        "unrealized_pnl": final_account.get("unrealized_pnl", 0.0),
        "cash": final_account.get("cash", 1000),
        "equity": final_account.get("equity", 1000),
    }


def build_trade_detail_payload(trade_id):
    trade_details = load_json("data/trade_details.json", [])
    open_positions = load_json("data/open_positions.json", [])
    closed_positions = load_json("data/closed_positions.json", [])
    candidate_log = load_json("data/candidate_log.json", [])
    trade_log = load_json("data/trade_log.json", [])
    timelines = load_json("data/trade_timeline.json", [])

    if not isinstance(trade_details, list):
        trade_details = []
    if not isinstance(open_positions, list):
        open_positions = []
    if not isinstance(closed_positions, list):
        closed_positions = []
    if not isinstance(candidate_log, list):
        candidate_log = []
    if not isinstance(trade_log, list):
        trade_log = []
    if not isinstance(timelines, list):
        timelines = []

    trade_id = str(trade_id)
    target = None

    # 1) Prefer rich saved trade_details
    for item in trade_details:
        if str(item.get("trade_id")) == trade_id or str(item.get("id")) == trade_id:
            target = dict(item)
            break

    # 2) Fall back to open / closed positions
    if not target:
        for pool in [open_positions, closed_positions]:
            for item in pool:
                if str(item.get("trade_id")) == trade_id or str(item.get("id")) == trade_id:
                    target = dict(item)
                    break
            if target:
                break

    # 3) Fall back to trade log
    if not target:
        for item in trade_log:
            if str(item.get("trade_id")) == trade_id or str(item.get("id")) == trade_id:
                target = dict(item)
                break

    if not target:
        return None

    symbol = target.get("symbol")
    strategy = target.get("strategy", "CALL")
    entry = target.get("entry", target.get("price"))
    atr = target.get("atr")
    score = target.get("score")
    confidence = target.get("confidence")

    # Candidate context — exact trade match first
    candidate = None
    for row in candidate_log:
        if str(row.get("trade_id")) == trade_id:
            candidate = row
            break

    # Narrow symbol fallback only if still missing and only one candidate exists
    if not candidate and symbol:
        symbol_matches = [row for row in candidate_log if row.get("symbol") == symbol]
        if len(symbol_matches) == 1:
            candidate = symbol_matches[0]

    # Timeline — exact trade match only
    trade_timeline = []
    for row in timelines:
        if str(row.get("trade_id")) == trade_id:
            trade_timeline.append(row)

    target.setdefault("entry", entry)
    target.setdefault("atr", atr)
    target.setdefault("score", score)
    target.setdefault("confidence", confidence)

    target.setdefault("risk", {
        "stop_logic": (
            f"Stop anchored near {target.get('stop')}"
            if target.get("stop") is not None else
            "Stop logic not fully defined yet."
        ),
        "note": (
            "Risk is framed around stop/target distance."
            if target.get("stop") is not None and target.get("target") is not None else
            "Risk note unavailable."
        ),
        "story": (
            "This trade should stay healthy above the stop and improve as it moves toward target."
            if target.get("stop") is not None else
            "No deeper risk story saved yet."
        ),
    })

    target.setdefault("signal_decay", {
        "minutes_old": "N/A",
        "decay_pct": "N/A",
        "adjusted_score": score if score is not None else "N/A",
    })

    target.setdefault("crowd_pressure", {
        "score": "N/A",
        "label": "UNKNOWN",
        "note": "No crowd pressure data saved.",
    })

    target.setdefault("thesis", target.get("why", [
        "No thesis lines saved yet."
    ]))

    target.setdefault("narrative", {
        "entry_story": (
            f"Trade entered in {strategy} direction around {entry}."
            if entry is not None else
            "No entry story saved yet."
        ),
        "management_story": (
            "Management will depend on follow-through, stop integrity, and progress toward target."
        ),
        "exit_story": (
            target.get("exit_explanation")
            or "No exit story saved yet."
        ),
    })

    target.setdefault("context", [
        f"Mode: {target.get('mode', 'UNKNOWN')}",
        f"Regime: {target.get('regime', 'UNKNOWN')}",
        f"Breadth: {target.get('breadth', 'UNKNOWN')}",
        f"Volatility: {target.get('volatility_state', 'UNKNOWN')}",
    ])

    target.setdefault(
        "why_not_this_trade",
        [target.get("rejection_reason")] if target.get("rejection_reason") else []
    )

    target["timeline"] = trade_timeline

    if candidate:
        if not target.get("why") and candidate.get("why"):
            target["why"] = candidate.get("why", [])
        if not target.get("option_explanation") and candidate.get("option_explanation"):
            target["option_explanation"] = candidate.get("option_explanation", [])
        if not target.get("rejection_reason") and candidate.get("rejection_reason"):
            target["rejection_reason"] = candidate.get("rejection_reason")

    return target


def get_execution_summary() -> Dict[str, Any]:
    summary = load_json("data/execution_summary.json", {})
    if not isinstance(summary, dict):
        summary = {}

    return {
        "selected_symbols": summary.get("selected_symbols", []),
        "selected_count": summary.get("selected_count", 0),
        "eligible_count": summary.get("eligible_count", 0),
        "rejected_count": summary.get("rejected_count", 0),
        "cap": summary.get("cap", 0),
        "regime": summary.get("regime", "neutral"),
        "volatility": summary.get("volatility", "normal"),
    }


def get_system_state() -> Dict[str, Any]:
    system = load_json("data/system_state.json", {})
    if not isinstance(system, dict):
        system = {}

    return {
        "regime": system.get("regime", "Neutral"),
        "volatility": system.get("volatility", "Normal"),
        "engine_state": system.get("engine_state", "Active"),
    }


def get_positions() -> List[Dict[str, Any]]:
    positions = load_json("data/positions.json", [])
    if isinstance(positions, list):
        return positions
    return []


def get_signals() -> List[Dict[str, Any]]:
    signals = load_json("data/signals.json", [])
    if not isinstance(signals, list):
        return []

    cleaned = []
    for item in signals:
        if not isinstance(item, dict):
            continue

        cleaned.append({
            "symbol": item.get("symbol"),
            "score": item.get("score", 0),
            "previous_score": item.get("previous_score", item.get("score", 0)),
            "confidence": item.get("confidence", "LOW"),
            "company_name": item.get("company_name", item.get("symbol")),
            "opinion": item.get("opinion", "Active setup."),
            "timestamp": item.get("timestamp", ""),
            "setup_type": item.get("setup_type", "Continuation"),
            "eligible": item.get("eligible", False),
            "execution_quality": item.get("execution_quality", 0),
        })

    return cleaned


def get_positions_with_intelligence() -> List[Dict[str, Any]]:
    positions = safe_run("get_positions", get_positions, [])
    positions = safe_run("attach_trade_intelligence", lambda: attach_trade_intelligence(positions), positions)
    positions = safe_run("attach_position_health", lambda: attach_position_health(positions), positions)
    return safe_list(positions)


def get_signal_boards() -> List[Dict[str, Any]]:
    signals = safe_run("get_signals", get_signals, [])
    boards = []

    for item in safe_list(signals):
        if not isinstance(item, dict):
            continue

        boards.append(
            {
                "symbol": item.get("symbol"),
                "company_name": item.get("company_name", item.get("symbol")),
                "latest_score": item.get("score", 0),
                "latest_confidence": item.get("confidence", "LOW"),
                "latest_timestamp": item.get("timestamp", ""),
                "opinion": item.get("opinion", "Active setup."),
            }
        )

    return boards


def get_all_symbol_rows() -> List[Dict[str, Any]]:
    boards = get_signal_boards()
    board_map = {}

    for board in boards:
        symbol = board.get("symbol")
        if not symbol:
            continue
        board_map[symbol] = board

    universe_rows = safe_run("load_market_universe", load_market_universe, [])
    universe_rows = safe_list(universe_rows)

    rows = []
    seen = set()

    # start from broad universe
    for item in universe_rows:
        if not isinstance(item, dict):
            continue

        symbol = item.get("symbol")
        if not symbol or symbol in seen:
            continue

        seen.add(symbol)
        board = board_map.get(symbol, {})

        rows.append(
            {
                "symbol": symbol,
                "company_name": board.get("company_name", item.get("company_name", symbol)),
                "latest_score": board.get("latest_score", 0),
                "latest_confidence": board.get("latest_confidence", "LOW"),
                "latest_timestamp": board.get("latest_timestamp", ""),
                "opinion": board.get("opinion", "No active opinion available yet."),
                "priority_rank": item.get("priority_rank", 0),
                "source_tags": item.get("source_tags", []),
            }
        )

    # add any board symbols not already in universe
    for symbol, board in board_map.items():
        if symbol in seen:
            continue

        rows.append(
            {
                "symbol": symbol,
                "company_name": board.get("company_name", symbol),
                "latest_score": board.get("latest_score", 0),
                "latest_confidence": board.get("latest_confidence", "LOW"),
                "latest_timestamp": board.get("latest_timestamp", ""),
                "opinion": board.get("opinion", "Active setup."),
                "priority_rank": 0,
                "source_tags": ["signals"],
            }
        )

    rows.sort(
        key=lambda x: (
            -_safe_int(x.get("latest_score", 0)),
            -_safe_int(x.get("priority_rank", 0)),
            x.get("symbol", ""),
        )
    )

    return rows


def get_all_symbol_rows() -> List[Dict[str, Any]]:
    boards = get_signal_boards()
    board_map = {}

    for board in boards:
        symbol = board.get("symbol")
        if not symbol:
            continue
        board_map[symbol] = board

    universe_rows = safe_run("load_market_universe", load_market_universe, [])
    universe_rows = safe_list(universe_rows)

    rows = []
    seen = set()

    for item in universe_rows:
        if not isinstance(item, dict):
            continue

        symbol = item.get("symbol")
        if not symbol or symbol in seen:
            continue

        seen.add(symbol)
        board = board_map.get(symbol, {})

        rows.append(
            {
                "symbol": symbol,
                "company_name": board.get("company_name", item.get("company_name", symbol)),
                "latest_score": board.get("latest_score", 0),
                "latest_confidence": board.get("latest_confidence", "LOW"),
                "latest_timestamp": board.get("latest_timestamp", ""),
                "opinion": board.get("opinion", "No active opinion available yet."),
                "priority_rank": item.get("priority_rank", 0),
                "source_tags": item.get("source_tags", []),
                "asset_type": item.get("asset_type", "equity"),
            }
        )

    for symbol, board in board_map.items():
        if symbol in seen:
            continue

        rows.append(
            {
                "symbol": symbol,
                "company_name": board.get("company_name", symbol),
                "latest_score": board.get("latest_score", 0),
                "latest_confidence": board.get("latest_confidence", "LOW"),
                "latest_timestamp": board.get("latest_timestamp", ""),
                "opinion": board.get("opinion", "Active setup."),
                "priority_rank": 0,
                "source_tags": ["signals"],
                "asset_type": "equity",
            }
        )

    rows.sort(
        key=lambda x: (
            -_safe_int(x.get("latest_score", 0)),
            -_safe_int(x.get("priority_rank", 0)),
            x.get("symbol", ""),
        )
    )

    return rows

def template_context(extra: Dict[str, Any]) -> Dict[str, Any]:
    base = {
        "user": get_current_user(),
        "theme": get_theme(),
        "snapshot": get_dashboard_snapshot(),
        "system": get_system_state(),
        "show_upgrade": should_show_upgrade(),
        "unread_notifications": get_unread_notifications(),
    }
    base.update(extra)
    return base

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def landing_page():
    maybe_track_page_view("/")
    if is_logged_in():
        if is_master():
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard_page"))

    return render_template_safe("landing.html", **template_context({}))


# PATCH YOUR /dashboard ROUTE TO ADD DASHBOARD FUSION

@app.route("/dashboard")
def dashboard_page():
    maybe_track_page_view("/dashboard")

    snapshot = get_canonical_snapshot()

    performance = snapshot.get("performance", {})
    analytics = snapshot.get("analytics", {})
    portfolio_summary = snapshot.get("portfolio_summary", {})
    unreal = snapshot.get("unrealized", {})
    strategies = snapshot.get("strategy_performance", {})
    drawdown = snapshot.get("drawdown_history", [])
    final_account = snapshot.get("final_account_snapshot", {})

    system = get_system_state()
    positions = get_positions_with_intelligence()
    reports = load_json("data/recent_reports.json", [])
    if not isinstance(reports, list):
        reports = []

    equity_values = [row.get("equity", 0) for row in drawdown]
    equity_labels = [row.get("closed_at", "") for row in drawdown]

    sample_signals = [
        {
            "symbol": "USO",
            "company_name": "United States Oil Fund",
            "direction": "CALL",
            "setup_type": "continuation",
            "trend_strength": 75,
            "volume_confirmation": 70,
            "extension_score": 35,
            "pullback_quality": 72,
            "score": 91,
            "structure_quality": 84,
            "liquidity_score": 92,
            "spread_score": 74,
            "premium_efficiency_score": 82,
            "open_interest_score": 76,
            "iv_context": "normal",
            "visible_volatility": 22,
            "last_pnl": 25,
        }
    ]

    fusion_payloads = []
    final_brain_map = {}

    for signal in sample_signals:
        try:
            product_fusion, final_brain = build_final_brain_from_signal(signal.get("symbol", ""), signal)
            fusion_payloads.append(product_fusion)
            final_brain_map[signal.get("symbol", "")] = final_brain
        except Exception as e:
            print(f"[DASHBOARD_FINAL_BRAIN:{signal.get('symbol')}] {e}")

    tier = get_current_tier_for_routes()

    final_dashboard_context = build_final_dashboard_context(
        final_brain_map=final_brain_map,
        tier=tier.lower(),
    )

    final_spotlight_cards = build_final_spotlight_context(
        final_brain_map=final_brain_map,
        tier=tier.lower(),
    )

    return render_template_safe(
        "dashboard.html",
        **template_context(
            {
                "state": final_account,
                "proof": performance,
                "analytics": analytics,
                "portfolio_summary": portfolio_summary,
                "unreal": unreal,
                "strategies": strategies,
                "drawdown": drawdown,
                "equity_values": equity_values,
                "equity_labels": equity_labels,
                "positions": positions,
                "snapshot": final_account,
                "system": system,
                "reports": reports,
                "fusion_payloads": fusion_payloads,
                "final_brain_map": final_brain_map,
                "final_dashboard_context": final_dashboard_context,
                "final_spotlight_cards": final_spotlight_cards,
                "tier": tier,
            }
        ),
    )


@app.route("/my-plays/<play_id>/archive", methods=["POST"])
def archive_my_play(play_id):
    archive_play(play_id)
    return redirect("/my-plays")


@app.route("/signals")
def signals_page():
    maybe_track_page_view("/signals")

    access_debug = {
        "current_tier_title": current_tier_title(),
        "session_tier": session.get("tier"),
        "preview_tier": session.get("preview_tier"),
        "is_master": is_master(),
        "can_access_all_symbols": can_access_all_symbols(),
    }

    tier = current_tier_title()
    boards = get_signal_boards()
    visible_signals, hidden_signals, hidden_count = slice_signals_by_tier(
        boards=boards,
        tier=tier,
        is_master=is_master(),
        preview_tier=session.get("preview_tier"),
    )
    top_five, next_twenty = spotlight_sections(
        visible_signals=visible_signals,
        tier=tier,
        is_master=is_master(),
        preview_tier=session.get("preview_tier"),
    )
    most_viewed_symbols = top_engaged_symbols_with_counts(limit=5)
    engaged_spotlight = most_viewed_symbols[0] if most_viewed_symbols else None

    return render_template_safe(
        "signals.html",
        **template_context(
            {
                "visible_signals": visible_signals,
                "hidden_signals": hidden_signals,
                "hidden_count": hidden_count,
                "tier": tier,
                "top_five": top_five,
                "most_viewed_symbols": most_viewed_symbols,
                "engaged_spotlight": engaged_spotlight,
                "next_twenty": next_twenty,
                "hidden_remaining": hidden_count,
                "can_access_all_symbols": can_access_all_symbols(),
                "access_debug": access_debug,
            }
        ),
    )


# ADD / UPDATE THIS ROUTE IN web/app.py

@app.route("/all-symbols")
def all_symbols_page():
    maybe_track_page_view("/all-symbols")

    if not can_access_all_symbols():
        return redirect(url_for("upgrade"))

    fusion_payloads = build_all_symbols_fusion_payloads(limit=150)

    final_brain_map = {}
    decision_map = {}

    for payload in fusion_payloads:
        try:
            master = payload.get("master_decision", {}) if isinstance(payload.get("master_decision", {}), dict) else {}
            symbol = str(master.get("symbol", "") or "").upper().strip()
            if not symbol:
                continue

            decision_bundle = build_decision_bundle_from_product_fusion(payload)
            decision_map[symbol] = decision_bundle
            final_brain_map[symbol] = build_symbol_final_brain(symbol, decision_bundle)

        except Exception as e:
            print(f"[ALL_SYMBOLS_FINAL_BRAIN:{payload}] {e}")

    tier = get_current_tier_for_routes()

    final_all_symbol_cards = build_final_all_symbol_cards(
        decision_map=decision_map,
        tier=tier.lower(),
    )

    return render_template_safe(
        "all_symbols.html",
        **template_context(
            {
                "final_all_symbol_cards": final_all_symbol_cards,
                "fusion_payloads": fusion_payloads,
                "final_brain_map": final_brain_map,
                "tier": tier,
            }
        ),
    )


@app.route("/signals/<symbol>")
@app.route("/symbol/<symbol>")
def signal_symbol_page(symbol: str):
    symbol = str(symbol or "").upper().strip()
    maybe_track_page_view(f"/signals/{symbol}")

    log_event("symbol_exposed", {
        "symbol": symbol,
        "source": "/signals",
    })
    track_symbol_click(symbol, source="/signals")

    detail = safe_run(
        "get_symbol_detail",
        lambda: get_symbol_detail(symbol),
        {
            "symbol": symbol,
            "company": {
                "name": symbol,
                "blurb": "Symbol detail is temporarily unavailable.",
            },
            "board": {
                "symbol": symbol,
                "company_name": symbol,
                "latest_score": 0,
                "latest_confidence": "LOW",
                "latest_timestamp": "",
                "opinion": "No active opinion available.",
            },
            "primary_intelligence": {},
            "signals": [],
            "news_items": [],
        },
    )

    try:
        if not detail.get("news_items"):
            detail["news_items"] = refresh_symbol_news(
                symbol=detail["symbol"],
                company_name=detail["company"].get("name", ""),
                limit=8,
                max_age_minutes=30,
            )
    except Exception as e:
        print(f"[SYMBOL_NEWS_REFRESH:{symbol}] {e}")
        detail["news_items"] = detail.get("news_items", [])

    data_health = build_data_health_summary()
    symbol_news_meta = safe_dict(
        data_health.get("pipeline", {}).get("symbol_news_sync", {}).get(detail["symbol"], {})
    )

    v2_symbol_hero = get_v2_symbol_hero(detail["symbol"])
    v2_symbol_deep_dive = get_v2_symbol_deep_dive(detail["symbol"])
    v2_horizontal_hero = get_v2_horizontal_hero()

    fusion_signal = {
        "symbol": detail["symbol"],
        "company_name": detail.get("company", {}).get("name", detail["symbol"]),
        "direction": (
            v2_symbol_hero.get("hero", {}).get("direction")
            or detail.get("primary_intelligence", {}).get("direction")
            or "CALL"
        ),
        "setup_type": (
            v2_symbol_hero.get("hero", {}).get("setup_type")
            or detail.get("primary_intelligence", {}).get("setup_type")
            or "continuation"
        ),
        "trend_strength": (
            v2_symbol_deep_dive.get("panels", [{}])[0]
            .get("content", {})
            .get("scanner", {})
            .get("score", 75)
        ),
        "volume_confirmation": 70,
        "extension_score": 35,
        "pullback_quality": 72,
        "score": detail.get("board", {}).get("latest_score", 80),
        "structure_quality": 84,
        "liquidity_score": 92,
        "spread_score": 74,
        "premium_efficiency_score": 82,
        "open_interest_score": 76,
        "iv_context": "normal",
        "visible_volatility": 22,
        "last_pnl": 25,
    }

    product_fusion = {}
    final_brain = {}
    symbol_fusion_view = {}
    symbol_explainability = {}

    try:
        product_fusion, final_brain = build_final_brain_from_signal(detail["symbol"], fusion_signal)
        symbol_fusion_view = build_symbol_page_fusion_view(product_fusion)
        symbol_explainability = build_symbol_page_explainability(final_brain)
    except Exception as e:
        print(f"[SYMBOL_FINAL_BRAIN:{symbol}] {e}")

    tier = get_current_tier_for_routes()

    try:
        final_symbol_context = build_final_symbol_context(
            symbol=detail["symbol"],
            final_brain=final_brain,
            tier=tier.lower(),
        )
    except Exception as e:
        print(f"[FINAL_SYMBOL_CONTEXT:{symbol}] {e}")
        final_symbol_context = {}

    return render_template_safe(
        "signal_symbol.html",
        **template_context(
            {
                "detail": detail,
                "symbol": detail["symbol"],
                "company": detail["company"],
                "board": detail["board"],
                "primary_intelligence": detail.get("primary_intelligence", {}),
                "symbol_signals": detail.get("signals", []),
                "visible_signal_count": len(detail.get("signals", [])),
                "total_signal_count": len(detail.get("signals", [])),
                "show_teaser": False,
                "show_elite": tier == "Elite",
                "news_items": detail.get("news_items", []),
                "opinion": detail.get("board", {}).get("opinion", "Active setup."),
                "explanation": {},
                "data_health": data_health,
                "symbol_news_meta": symbol_news_meta,
                "v2_symbol_hero": v2_symbol_hero,
                "v2_symbol_deep_dive": v2_symbol_deep_dive,
                "v2_horizontal_hero": v2_horizontal_hero,
                "product_fusion": product_fusion,
                "symbol_fusion_view": symbol_fusion_view,
                "symbol_explainability": symbol_explainability,
                "final_brain": final_brain,
                "final_symbol_context": final_symbol_context,
                "tier": tier,
            }
        ),
    )


@app.route("/trade-review")
def trade_review_page():
    maybe_track_page_view("/trade-review")

    raw_trades = load_json("data/trade_replay_source.json", [])
    if not isinstance(raw_trades, list):
        raw_trades = []

    decision_bundles = {}
    replay_debug = {
        "raw_trade_count": len(raw_trades),
        "bundle_count": 0,
        "replay_count": 0,
    }

    for trade in raw_trades:
        try:
            if not isinstance(trade, dict):
                continue

            symbol = str(trade.get("symbol", "") or "").upper().strip()
            if not symbol:
                continue

            fusion_signal = {
                "symbol": symbol,
                "company_name": trade.get("company_name", symbol),
                "direction": trade.get("direction", "CALL"),
                "setup_type": trade.get("setup_family", "continuation"),
                "trend_strength": trade.get("trend_strength", 70),
                "volume_confirmation": trade.get("volume_confirmation", 65),
                "extension_score": trade.get("extension_score", 35),
                "pullback_quality": trade.get("pullback_quality", 65),
                "score": trade.get("score", 75),
                "structure_quality": trade.get("structure_quality", 75),
                "liquidity_score": trade.get("liquidity_score", 80),
                "spread_score": trade.get("spread_score", 70),
                "premium_efficiency_score": trade.get("premium_efficiency_score", 75),
                "open_interest_score": trade.get("open_interest_score", 70),
                "iv_context": trade.get("iv_context", "normal"),
                "visible_volatility": trade.get("visible_volatility", 20),
                "last_pnl": trade.get("pnl", 0),
            }

            product_fusion = build_symbol_fusion_payload(fusion_signal)
            decision_bundles[symbol] = build_decision_bundle_from_product_fusion(product_fusion)

        except Exception as e:
            print(f"[TRADE_REVIEW_DECISION_BUNDLE:{trade.get('symbol', '')}] {e}")

    replay_debug["bundle_count"] = len(decision_bundles)

    replay_packages = build_replay_batch(raw_trades, decision_bundles)
    replay_debug["replay_count"] = len(replay_packages)

    replay_page_context = build_replay_page_context(replay_packages)

    print("[TRADE_REVIEW_DEBUG]", replay_debug)
    print("[TRADE_REVIEW_FEED_SIZE]", len(replay_page_context.get("replay_feed", [])))

    return render_template_safe(
        "trade_review.html",
        **template_context(
            {
                "replay_page_context": replay_page_context,
                "replay_feed": replay_page_context.get("replay_feed", []),
                "replay_summary": replay_page_context.get("summary", {}),
                "replay_debug": replay_debug,
            }
        ),
    )

@app.route("/position/<trade_id>")
def position_detail_page(trade_id):
    positions = get_positions_with_intelligence()

    target = None
    for p in positions:
        if p.get("trade_id") == trade_id:
            target = p
            break

    if not target:
        return render_template_safe(
            "position_detail.html",
            **template_context({
                "detail": None,
                "error": "Position not found.",
            }),
        )

    return render_template_safe(
        "position_detail.html",
        **template_context({
            "detail": target,
        }),
    )


@app.route("/market-map")
def market_map_page():
    maybe_track_page_view("/market-map")

    v2_market_map = get_v2_market_map()
    v2_market_interactions = get_v2_market_map_interactions()
    v2_map_layers = get_v2_map_layers()

    grouped = v2_market_map.get("grouped_tiles", {}) if isinstance(v2_market_map, dict) else {}
    mapped_constellations = {}

    if isinstance(grouped, dict):
        for bucket, tiles in grouped.items():
            try:
                mapped_constellations[bucket] = map_tiles_to_constellation(bucket, tiles)
            except Exception as e:
                print(f"[MAP_CONSTELLATION_{bucket}] {e}")
                mapped_constellations[bucket] = {
                    "bucket": bucket,
                    "constellation": "fallback",
                    "label": "Fallback",
                    "stars": [],
                    "overflow": [],
                    "lines": [],
                }

    return render_template_safe(
        "market_map.html",
        **template_context(
            {
                "v2_market_map": v2_market_map,
                "v2_market_interactions": v2_market_interactions,
                "v2_map_layers": v2_map_layers,
                "mapped_constellations": mapped_constellations,
            }
        ),
    )


@app.route("/admin/intelligence")
def admin_intelligence_page():
    maybe_track_page_view("/admin/intelligence")

    shared = build_admin_shared_context()
    admin_summary = shared["admin_summary"]

    filter_key = str(request.args.get("filter", "overview") or "overview").strip().lower()

    spotlight_title = "Operator Overview"
    spotlight_note = "Showing the full operator intelligence layer."
    spotlight_cards = []

    if filter_key == "disagreement":
        spotlight_title = "Disagreement Spotlight"
        spotlight_note = "Showing where user direction is fighting the engine most often."
        top_cluster = (admin_summary.get("disagreement", {}) or {}).get("top_cluster", {}) or {}
        if top_cluster.get("count", 0) > 0:
            spotlight_cards.append({
                "headline": "Top Disagreement Cluster",
                "body": f"{top_cluster.get('label')} — count {top_cluster.get('count')}",
            })
        spotlight_cards.append({
            "headline": "Alignment Count",
            "body": f"{admin_summary.get('disagreement', {}).get('aligned_count', 0)} aligned ideas currently tracked.",
        })
        spotlight_cards.append({
            "headline": "Disagreement Count",
            "body": f"{admin_summary.get('disagreement', {}).get('disagreement_count', 0)} disagreement cases currently tracked.",
        })

    elif filter_key == "activation":
        spotlight_title = "Activation Quality Spotlight"
        spotlight_note = "Showing whether promoted ideas are earning their place or leaking edge."
        activation = admin_summary.get("activation_quality", {}) or {}
        spotlight_cards.append({
            "headline": "Strong Activations",
            "body": f"{activation.get('ready_activations', 0)} promoted ideas behaved like strong activations.",
        })
        spotlight_cards.append({
            "headline": "Weak Activations",
            "body": f"{activation.get('weak_activations', 0)} promoted ideas behaved like weak activations.",
        })
        spotlight_cards.append({
            "headline": "Unclear Activations",
            "body": f"{activation.get('unclear_activations', 0)} promoted ideas were not cleanly strong or weak.",
        })
        spotlight_cards.append({
            "headline": "Without Engine Tracking",
            "body": f"{activation.get('without_candidate', 0)} closed positions were activated without active engine tracking.",
        })

    elif filter_key == "failure":
        spotlight_title = "Failure Cluster Spotlight"
        spotlight_note = "Showing the dominant failure cluster currently visible in the system."
        cluster = (admin_summary.get("zones", {}) or {}).get("top_failure_cluster", {}) or {}
        spotlight_cards.append({
            "headline": "Top Failure Cluster",
            "body": f"{cluster.get('label', 'No failure cluster yet.')} — count {cluster.get('count', 0)}",
        })
        spotlight_cards.append({
            "headline": "Weak Plays",
            "body": f"{admin_summary.get('counts', {}).get('weak_plays', 0)} active ideas are currently classified as weak/watch.",
        })
        spotlight_cards.append({
            "headline": "Losses",
            "body": f"{admin_summary.get('trade_totals', {}).get('losses', 0)} archived trade losses are currently recorded.",
        })

    elif filter_key == "strong_zone":
        spotlight_title = "Strongest Condition Zone"
        spotlight_note = "Showing the market backdrop where your system currently looks strongest."
        zone = (admin_summary.get("zones", {}) or {}).get("strongest_condition", {}) or {}
        spotlight_cards.append({
            "headline": "Strongest Zone",
            "body": f"{zone.get('label', 'No strong zone yet.')} — count {zone.get('count', 0)}",
        })
        strongest_play = admin_summary.get("strongest_play")
        if strongest_play:
            spotlight_cards.append({
                "headline": "Strongest Play",
                "body": f"{strongest_play.get('symbol')} — score {strongest_play.get('score')} — {strongest_play.get('headline')}",
            })

    elif filter_key == "weak_zone":
        spotlight_title = "Weakest Condition Zone"
        spotlight_note = "Showing the market backdrop where your system currently looks weakest."
        zone = (admin_summary.get("zones", {}) or {}).get("weakest_condition", {}) or {}
        spotlight_cards.append({
            "headline": "Weakest Zone",
            "body": f"{zone.get('label', 'No weak zone yet.')} — count {zone.get('count', 0)}",
        })
        weakest_play = admin_summary.get("weakest_play")
        if weakest_play:
            spotlight_cards.append({
                "headline": "Weakest Play",
                "body": f"{weakest_play.get('symbol')} — score {weakest_play.get('score')} — {weakest_play.get('headline')}",
            })

    return render_template_safe(
        "admin_intelligence.html",
        **template_context({
            "admin": admin_summary,
            "surface_alerts": shared["surface_alerts"],
            "quick_actions": shared["quick_actions"],
            "filter_key": filter_key,
            "spotlight_title": spotlight_title,
            "spotlight_note": spotlight_note,
            "spotlight_cards": spotlight_cards,
        }),
    )


# REWRITE YOUR /signals/<symbol> ROUTE TO INCLUDE FUSION


@app.route("/positions")
def positions_page():
    maybe_track_page_view("/positions")

    positions = get_positions_with_intelligence()
    portfolio = evaluate_portfolio(positions)
    alerts = generate_alerts(positions)
    brain = build_system_brain(positions, portfolio, alerts)

    return render_template_safe(
        "positions.html",
        **template_context({
            "positions": positions,
            "portfolio": portfolio,
            "alerts": alerts,
            "brain": brain
        }),
    )


@app.route("/admin/product-monitoring")
def admin_product_monitoring_page():
    maybe_track_page_view("/admin/product-monitoring")

    shared = build_admin_shared_context()
    monitoring = shared["monitoring"]

    filter_key = str(request.args.get("filter", "overview") or "overview").strip().lower()

    spotlight_title = "Product Overview"
    spotlight_note = "Showing the full product monitoring layer."
    spotlight_cards = []

    if filter_key == "friction":
        spotlight_title = "Friction Spotlight"
        spotlight_note = "Showing the strongest friction patterns currently visible in the product."
        strongest_friction = monitoring.get("strongest_friction", {}) or {}
        spotlight_cards.append({
            "headline": strongest_friction.get("headline", "No strong friction point yet."),
            "body": strongest_friction.get("body", "Not enough friction signal yet."),
        })
        for card in (monitoring.get("friction_points", []) or [])[:3]:
            spotlight_cards.append({
                "headline": card.get("headline", "Friction"),
                "body": card.get("body", ""),
            })

    elif filter_key == "readiness":
        spotlight_title = "Readiness Distribution Spotlight"
        spotlight_note = "Showing how much of the playbook is actually actionable versus soft."
        buckets = monitoring.get("readiness_buckets", {}) or {}
        spotlight_cards.extend([
            {
                "headline": "Ready Plays",
                "body": f"{buckets.get('READY', 0)} play(s) currently look ready for activation.",
            },
            {
                "headline": "Close Plays",
                "body": f"{buckets.get('CLOSE', 0)} play(s) are close but not fully proven.",
            },
            {
                "headline": "Watch Plays",
                "body": f"{buckets.get('WATCH', 0)} play(s) are still too mixed to promote confidently.",
            },
            {
                "headline": "Weak Plays",
                "body": f"{buckets.get('WEAK', 0)} play(s) currently look soft or conflicted.",
            },
        ])

    elif filter_key == "thesis":
        spotlight_title = "Thesis Quality Spotlight"
        spotlight_note = "Showing whether users are actually explaining their ideas well enough for coaching and review."
        thesis_quality = monitoring.get("thesis_quality", {}) or {}
        spotlight_cards.extend([
            {
                "headline": "With Thesis",
                "body": f"{thesis_quality.get('with_thesis', 0)} play(s) currently have a written thesis.",
            },
            {
                "headline": "Without Thesis",
                "body": f"{thesis_quality.get('without_thesis', 0)} play(s) currently do not have a written thesis.",
            },
        ])

    elif filter_key == "positions":
        spotlight_title = "Open Position Quality Spotlight"
        spotlight_note = "Showing whether the live position layer is strong or leaking quality."
        position_quality = monitoring.get("position_quality", {}) or {}
        spotlight_cards.extend([
            {
                "headline": "Strong Open Positions",
                "body": f"{position_quality.get('strong_open_positions', 0)} open position(s) currently look strong by health and agreement.",
            },
            {
                "headline": "Weak Open Positions",
                "body": f"{position_quality.get('weak_open_positions', 0)} open position(s) currently look weak by health or agreement.",
            },
        ])

    elif filter_key == "retention":
        spotlight_title = "Retention Signal Spotlight"
        spotlight_note = "Showing whether the current user experience is likely to feel rewarding or frustrating."
        retention = monitoring.get("retention", {}) or {}
        adoption = monitoring.get("adoption", {}) or {}
        spotlight_cards.extend([
            {
                "headline": retention.get("headline", "Retention signal"),
                "body": retention.get("summary", ""),
            },
            {
                "headline": adoption.get("headline", "Adoption signal"),
                "body": adoption.get("summary", ""),
            },
        ])

    return render_template_safe(
        "admin_product_monitoring.html",
        **template_context({
            "monitoring": monitoring,
            "surface_alerts": shared["surface_alerts"],
            "quick_actions": shared["quick_actions"],
            "filter_key": filter_key,
            "spotlight_title": spotlight_title,
            "spotlight_note": spotlight_note,
            "spotlight_cards": spotlight_cards,
        }),
    )


@app.route("/my-positions")
def my_positions_page():
    maybe_track_page_view("/my-positions")

    positions = get_user_positions(include_closed=False)
    page_summary = build_my_positions_page_summary(positions)
    filter_key = str(request.args.get("filter", "all") or "all").strip().lower()

    filtered_positions = positions
    filter_title = "All Open Positions"
    filter_note = "Showing your full live position layer."

    if filter_key == "weak":
        filtered_positions = [
            p for p in positions
            if _agreement_score(p) < 55 or _health_score(p) < 35
        ]
        filter_title = "Weak Positions"
        filter_note = "Showing open positions that look weak by health or agreement."
    elif filter_key == "strong":
        filtered_positions = [
            p for p in positions
            if _agreement_score(p) >= 75 and _health_score(p) >= 75
        ]
        filter_title = "Strong Positions"
        filter_note = "Showing open positions with stronger health and alignment."
    elif filter_key == "high_agreement":
        filtered_positions = [p for p in positions if _agreement_score(p) >= 75]
        filter_title = "High Agreement Positions"
        filter_note = "Showing positions with stronger system agreement."
    elif filter_key == "under_pressure":
        filtered_positions = [
            p for p in positions
            if _norm_upper((p.get("health", {}) or {}).get("label", "")) in {"UNDER PRESSURE", "BROKEN"}
        ]
        filter_title = "Under Pressure Positions"
        filter_note = "Showing positions whose behavior is signaling pressure or damage."

    return render_template_safe(
        "my_positions.html",
        **template_context({
            "positions": filtered_positions,
            "page_summary": page_summary,
            "filter_key": filter_key,
            "filter_title": filter_title,
            "filter_note": filter_note,
        }),
    )


@app.route("/my-positions/<position_id>")
def my_position_detail_page(position_id):
    maybe_track_page_view(f"/my-positions/{position_id}")
    position = get_user_position(position_id)

    return render_template_safe(
        "my_position_detail.html",
        **template_context({
            "position": position,
            "page_summary": build_position_detail_summary(position),
            "error": None if position else "Position not found.",
        }),
    )


@app.route("/my-positions/<position_id>/edit", methods=["POST"])
def edit_my_position(position_id):
    stop = request.form.get("stop", "")
    target = request.form.get("target", "")
    conviction = request.form.get("conviction", "Medium")
    notes = request.form.get("notes", "")
    status = request.form.get("status", "Open")

    updated = update_user_position(
        position_id=position_id,
        stop=stop,
        target=target,
        notes=notes,
        conviction=conviction,
        status=status,
    )

    if updated:
        track_event("position_updated", {
            "position_id": position_id,
            "symbol": updated.get("symbol"),
            "status": updated.get("status"),
            "conviction": updated.get("conviction"),
            "agreement_score": (updated.get("system_agreement", {}) or {}).get("score", 0),
            "health_score": (updated.get("health", {}) or {}).get("score", 0),
            "has_notes": bool(str(updated.get("notes", "")).strip()),
        })

    return redirect(f"/my-positions/{position_id}")


@app.route("/my-positions/<position_id>/close", methods=["POST"])
def close_my_position(position_id):
    closed = close_user_position(position_id)

    if closed:
        track_event("position_closed", {
            "position_id": position_id,
            "symbol": closed.get("symbol"),
            "direction": closed.get("direction"),
            "conviction": closed.get("conviction"),
            "agreement_score": (closed.get("system_agreement", {}) or {}).get("score", 0),
            "health_score": (closed.get("health", {}) or {}).get("score", 0),
            "outcome": classify_trade_outcome(closed),
            "closed_weak": (
                int((closed.get("system_agreement", {}) or {}).get("score", 0) or 0) < 55
                or int((closed.get("health", {}) or {}).get("score", 0) or 0) < 35
            ),
        })

    return redirect("/my-positions")


@app.route("/my-positions/archived")
def my_positions_archived_page():
    maybe_track_page_view("/my-positions/archived")

    positions = get_user_positions(include_closed=True)

    archived = [
        p for p in positions
        if str(p.get("status", "")).lower() == "closed"
    ]

    return render_template_safe(
        "my_positions_archived.html",
        **template_context({
            "positions": archived,
        }),
    )


# ADD / UPDATE YOUR /spotlight ROUTE LIKE THIS

@app.route("/spotlight")
def spotlight_page():
    maybe_track_page_view("/spotlight")

    contracts = load_json("data_v2/spotlight_page_contract.json", {})
    lane_sections = contracts.get("lane_sections", []) if isinstance(contracts, dict) else []

    sample_signals = [
        {
            "symbol": "USO",
            "company_name": "United States Oil Fund",
            "direction": "CALL",
            "setup_type": "continuation",
            "trend_strength": 75,
            "volume_confirmation": 70,
            "extension_score": 35,
            "pullback_quality": 72,
            "score": 91,
            "structure_quality": 84,
            "liquidity_score": 92,
            "spread_score": 74,
            "premium_efficiency_score": 82,
            "open_interest_score": 76,
            "iv_context": "normal",
            "visible_volatility": 22,
            "last_pnl": 25,
        }
    ]

    fusion_payloads = []
    final_brain_map = {}

    for signal in sample_signals:
        try:
            product_fusion, final_brain = build_final_brain_from_signal(signal.get("symbol", ""), signal)
            fusion_payloads.append(product_fusion)
            final_brain_map[signal.get("symbol", "")] = final_brain
        except Exception as e:
            print(f"[SPOTLIGHT_FINAL_BRAIN:{signal.get('symbol')}] {e}")

    tier = get_current_tier_for_routes()
    final_spotlight_cards = build_final_spotlight_context(
        final_brain_map=final_brain_map,
        tier=tier.lower(),
    )

    return render_template_safe(
        "spotlight.html",
        **template_context(
            {
                "spotlight_contract": contracts,
                "lane_sections": lane_sections,
                "fusion_payloads": fusion_payloads,
                "final_brain_map": final_brain_map,
                "final_spotlight_cards": final_spotlight_cards,
                "tier": tier,
            }
        ),
    )


@app.route("/my-positions/analyze")
def analyze_my_trades_page():
    maybe_track_page_view("/my-positions/analyze")
    analysis = analyze_user_trades()

    return render_template_safe(
        "my_trade_analysis.html",
        **template_context({
            "analysis": analysis,
            "page_summary": build_trade_analysis_summary(analysis),
        }),
    )


@app.route("/simulation")
def simulation_dashboard():
    maybe_track_page_view("/simulation")
    positions = get_positions_with_intelligence()
    portfolio = evaluate_portfolio(positions)
    alerts = generate_alerts(positions)
    brain = build_system_brain(positions, portfolio, alerts)
    return render_template_safe(
        "simulation.html",
        **template_context({
            "positions": positions,
            "portfolio": portfolio,
            "alerts": alerts,
            "brain": brain,
        }),
    )


@app.route("/api/live-state")
def api_live_state():
    positions = get_positions_with_intelligence()
    portfolio = evaluate_portfolio(positions)
    alerts = generate_alerts(positions)
    brain = build_system_brain(positions, portfolio, alerts)

    return jsonify({
        "positions": positions,
        "portfolio": portfolio,
        "alerts": alerts,
        "brain": brain,
    })

@app.route("/proof")
def proof_page():
    proof = performance_summary()
    return render_template_safe(
        "proof.html",
        **template_context({
            "proof": proof,
        }),
    )


@app.route("/research")
def research_overview():
    most_underrated = most_underrated_symbols(limit=5)
    underrated_spotlight = most_underrated[0] if most_underrated else None
    return render_template_safe("research_overview.html",
                                **template_context(
                                    {
                                      "most_underrated": most_underrated,
                                      "underrated_spotlight": underrated_spotlight,
                                    }),
                                )


@app.route("/analytics-overview")
def analytics_overview():
    maybe_track_page_view("/analytics-overview")

    snapshot = get_canonical_snapshot()
    analytics = snapshot.get("analytics", {})
    proof = snapshot.get("performance", {})
    portfolio_summary = snapshot.get("portfolio_summary", {})

    return render_template_safe(
        "analytics_overview.html",
        **template_context({
            "stats": analytics,
            "proof": proof,
            "portfolio_summary": portfolio_summary,
        }),
    )


@app.route("/analytics")
def analytics_page():
    snapshot = get_canonical_snapshot()

    analytics = snapshot.get("analytics", {})
    portfolio_summary = snapshot.get("portfolio_summary", {})
    proof = snapshot.get("performance", {})
    unreal = snapshot.get("unrealized", {})
    strategies = snapshot.get("strategy_performance", {})
    drawdown = snapshot.get("drawdown_history", [])
    final_account = snapshot.get("final_account_snapshot", {})

    return render_template_safe(
        "analytics.html",
        **template_context(
            {
                "stats": analytics,
                "summary": portfolio_summary,
                "proof": proof,
                "unreal": unreal,
                "strategies": strategies,
                "drawdown": drawdown,
                "reports": [],
                "snapshot": final_account,
            }
        ),
    )


@app.route("/analytics/performance")
def analytics_performance_page():
    maybe_track_page_view("/analytics/performance")

    snapshot = get_canonical_snapshot()

    proof = snapshot.get("performance", {})
    portfolio_summary = snapshot.get("portfolio_summary", {})

    return render_template_safe(
        "analytics_performance.html",
        **template_context(
            {
                "proof": proof,
                "reports": [],
                "summary": portfolio_summary,
            }
        ),
    )



@app.route("/analytics/strategy")
@app.route("/strategy-behavior")
def strategy_behavior_page():
    maybe_track_page_view("/analytics/strategy")
    return render_template_safe(
        "strategy_behavior.html",
        **template_context({
            "behavior": {
                "summary": "Strategy behavior view is active.",
                "items": []
            }
        }),
    )


@app.route("/my-plays")
def my_plays_page():
    maybe_track_page_view("/my-plays")

    plays = get_my_plays()

    for play in plays:
        play["activation_readiness"] = classify_play_readiness(play)
        play["promotion_guidance"] = build_promotion_guidance(play)
        play["rebuild_profile"] = build_weak_play_rebuild_profile(play)

    plays_summary = build_my_plays_summary(plays)
    page_summary = build_my_plays_page_summary(plays)

    filter_key = str(request.args.get("filter", "all") or "all").strip().lower()

    filtered_plays = plays
    filter_title = "All Plays"
    filter_note = "Showing your full idea book."

    if filter_key == "ready":
        filtered_plays = [
            p for p in plays
            if (p.get("activation_readiness", {}) or {}).get("bucket") == "READY"
        ]
        filter_title = "Ready Plays"
        filter_note = "Showing only ideas that currently look ready for activation."

    elif filter_key == "close":
        filtered_plays = [
            p for p in plays
            if (p.get("activation_readiness", {}) or {}).get("bucket") == "CLOSE"
        ]
        filter_title = "Close to Ready"
        filter_note = "Showing ideas that are warming up but still need cleaner confirmation."

    elif filter_key == "weak":
        filtered_plays = [
            p for p in plays
            if (p.get("activation_readiness", {}) or {}).get("bucket") in {"WATCH", "WEAK"}
        ]
        filter_title = "Weak / Watch Plays"
        filter_note = "Showing ideas that currently look too soft, conflicted, or underdeveloped."

    elif filter_key == "high_agreement":
        filtered_plays = [
            p for p in plays
            if int((p.get("system_agreement", {}) or {}).get("score", 0) or 0) >= 75
        ]
        filter_title = "High Agreement Plays"
        filter_note = "Showing plays with stronger system agreement."

    elif filter_key == "high_conviction":
        filtered_plays = [
            p for p in plays
            if str(p.get("conviction", "Medium")).strip().lower() == "high"
        ]
        filter_title = "High Conviction Plays"
        filter_note = "Showing only high-conviction ideas."

    elif filter_key == "watching":
        filtered_plays = [
            p for p in plays
            if str(p.get("status", "Open")).strip().lower() == "watching"
        ]
        filter_title = "Watching Plays"
        filter_note = "Showing only plays currently marked as watching."

    elif filter_key == "archived":
        filtered_plays = [
            p for p in plays
            if str(p.get("status", "Open")).strip().lower() == "archived"
        ]
        filter_title = "Archived Plays"
        filter_note = "Showing archived ideas."

    return render_template_safe(
        "my_plays.html",
        **template_context({
            "plays": filtered_plays,
            "plays_summary": plays_summary,
            "page_summary": page_summary,
            "filter_key": filter_key,
            "filter_title": filter_title,
            "filter_note": filter_note,
        }),
    )


@app.route("/my-plays/add", methods=["POST"])
def add_my_play():
    symbol = request.form.get("symbol", "").strip().upper()
    entry = request.form.get("entry", "")
    stop = request.form.get("stop", "")
    target = request.form.get("target", "")
    conviction = request.form.get("conviction", "Medium")
    thesis = request.form.get("thesis", "")
    notes = request.form.get("notes", "")

    try:
        created = add_play(
            symbol=symbol,
            entry=entry,
            stop=stop,
            target=target,
            conviction=conviction,
            thesis=thesis,
            notes=notes,
        )

        recent_events = list(reversed(get_event_log()))
        created_after_loss_close = False

        for row in recent_events[:10]:
            if str(row.get("event_type", "")).strip() != "position_closed":
                continue
            payload = row.get("payload", {}) or {}
            if str(payload.get("outcome", "")).strip().upper() == "LOSS":
                created_after_loss_close = True
                break

        track_event("play_created", {
            "symbol": created.get("symbol"),
            "conviction": created.get("conviction"),
            "direction": created.get("direction"),
            "has_thesis": bool(str(created.get("thesis", "")).strip()),
            "has_notes": bool(str(created.get("notes", "")).strip()),
            "created_after_loss_close": created_after_loss_close,
        })

        return redirect("/my-plays")
    except ValueError as e:
        plays = get_my_plays()
        plays_summary = build_my_plays_summary(plays)
        return render_template_safe(
            "my_plays.html",
            **template_context({
                "plays": plays,
                "plays_summary": plays_summary,
                "error": str(e),
            }),
        )


@app.route("/my-plays/<play_id>")
def my_play_detail_page(play_id):
    maybe_track_page_view(f"/my-plays/{play_id}")

    play = get_play(play_id)

    if play:
        play["activation_readiness"] = classify_play_readiness(play)
        play["promotion_guidance"] = build_promotion_guidance(play)
        play["rebuild_profile"] = build_weak_play_rebuild_profile(play)

    return render_template_safe(
        "my_play_detail.html",
        **template_context({
            "play": play,
            "page_summary": build_play_detail_summary(play),
            "error": None if play else "Play not found.",
        }),
    )


@app.route("/my-plays/<play_id>/edit", methods=["POST"])
def edit_my_play(play_id):
    symbol = request.form.get("symbol", "").strip().upper()
    entry = request.form.get("entry", "")
    stop = request.form.get("stop", "")
    target = request.form.get("target", "")
    conviction = request.form.get("conviction", "Medium")
    thesis = request.form.get("thesis", "")
    notes = request.form.get("notes", "")
    status = request.form.get("status", "Open")

    try:
        updated = update_play(
            play_id=play_id,
            symbol=symbol,
            entry=entry,
            stop=stop,
            target=target,
            conviction=conviction,
            thesis=thesis,
            notes=notes,
            status=status,
        )

        if updated:
            track_event("play_edited", {
                "play_id": play_id,
                "symbol": updated.get("symbol"),
                "status": updated.get("status"),
                "conviction": updated.get("conviction"),
                "direction": updated.get("direction"),
                "agreement_score": (updated.get("system_agreement", {}) or {}).get("score", 0),
                "health_score": (updated.get("health", {}) or {}).get("score", 0),
                "has_thesis": bool(str(updated.get("thesis", "")).strip()),
                "has_notes": bool(str(updated.get("notes", "")).strip()),
                "edited_after_weak_health": int((updated.get("health", {}) or {}).get("score", 0) or 0) < 35,
            })

        return redirect(f"/my-plays/{play_id}")
    except ValueError as e:
        play = get_play(play_id)
        if play:
            play["activation_readiness"] = classify_play_readiness(play)
        return render_template_safe(
            "my_play_detail.html",
            **template_context({
                "play": play,
                "error": str(e),
            }),
        )


@app.route("/my-plays/<play_id>/activate", methods=["POST"])
def activate_my_play(play_id):
    position = add_user_position_from_play(play_id)
    play = get_play(play_id)

    if not play:
        return render_template_safe(
            "my_play_detail.html",
            **template_context({
                "play": None,
                "error": f"Play {play_id} was not found.",
            }),
        )

    play["activation_readiness"] = classify_play_readiness(play)

    if not position:
        return render_template_safe(
            "my_play_detail.html",
            **template_context({
                "play": play,
                "error": "Could not activate this play.",
            }),
        )

    track_event("play_activated", {
        "play_id": play_id,
        "position_id": position.get("position_id"),
        "symbol": position.get("symbol"),
        "direction": position.get("direction"),
        "conviction": position.get("conviction"),
        "agreement_score": (position.get("system_agreement", {}) or {}).get("score", 0),
        "health_score": (position.get("health", {}) or {}).get("score", 0),
        "engine_strategy": ((position.get("engine_candidate") or {}).get("strategy") if position.get("engine_candidate") else None),
        "activated_against_engine": (
            str(((position.get("engine_candidate") or {}).get("strategy", ""))).strip().upper() not in {"", str(position.get("direction", "")).strip().upper()}
            if position.get("engine_candidate") else False
        ),
        "has_thesis": bool(str(position.get("thesis", "")).strip()),
    })

    return redirect("/my-positions")


@app.route("/analytics/risk")
def analytics_risk_page():
    snapshot = get_canonical_snapshot()

    proof = snapshot.get("performance", {})
    portfolio_summary = snapshot.get("portfolio_summary", {})
    drawdown = snapshot.get("drawdown_history", [])
    system = get_system_state()

    return render_template_safe(
        "analytics_risk.html",
        **template_context(
            {
                "proof": proof,
                "summary": portfolio_summary,
                "system": system,
                "drawdown": drawdown,
            }
        ),
    )


@app.route("/live-activity")
def live_activity_page():
    return render_template_safe(
        "live_activity.html",
        **template_context({"activity": load_json("data/live_activity.json", [])}),
    )


@app.route("/equity")
def equity_page():
    return render_template_safe(
        "equity.html",
        **template_context({"curve": load_json("data/equity_curve.json", [1000])}),
    )


@app.route("/reports")
def reports_page():
    return render_template_safe(
        "reports.html",
        **template_context({"reports": load_json("data/recent_reports.json", [])}),
    )


@app.route("/bot-log")
def bot_log_page():
    return render_template_safe(
        "bot_log.html",
        **template_context({"bot_log": load_json("data/bot_log.json", [])}),
    )


@app.route("/trade/<trade_id>")
def trade_detail_page(trade_id):
    detail = build_trade_detail_payload(trade_id)
    if detail:
        track_trade_click(
            detail.get("symbol", "UNKNOWN"),
            trade_id=trade_id,
            source="/why-this-trade",
        )
    return render_template_safe(
        "trade_detail.html",
        **template_context({
            "detail": detail,
            "error": None if detail else "Trade detail not found.",
        }),
    )


@app.route("/why-this-trade")
def why_this_trade_page():
    maybe_track_page_view("/why-this-trade")
    track_premium_content_view(source="/why-this-trade", section="why_this_trade_page")
    track_premium_wall_seen(source="/why-this-trade", section="why_this_trade_page")

    trades = load_json("data/trade_details.json", [])
    if not isinstance(trades, list):
        trades = []

    candidate_rows = load_json("data/candidate_log.json", [])
    if not isinstance(candidate_rows, list):
        candidate_rows = []

    enriched = []

    for trade in trades:
        row = dict(trade)

        trade_id = row.get("trade_id") or row.get("id")
        if trade_id:
            built = build_trade_detail_payload(trade_id)
            if built:
                row = built

        if not row.get("context"):
            row["context"] = [
                f"Mode: {row.get('mode', 'UNKNOWN')}",
                f"Regime: {row.get('regime', 'UNKNOWN')}",
                f"Breadth: {row.get('breadth', 'UNKNOWN')}",
                f"Volatility: {row.get('volatility_state', 'UNKNOWN')}",
            ]

        if not row.get("summary_text"):
            row["summary_text"] = (
                row.get("rejection_reason")
                or (row.get("why")[0] if row.get("why") else None)
                or row.get("exit_explanation")
                or (row.get("rejection_analysis")[0] if row.get("rejection_analysis") else None)
                or "This setup has been recorded, but its explanation package has not been fully attached yet."
            )

        enriched.append(row)

    for row in candidate_rows:
        if row.get("status") != "approved_not_selected":
            continue

        item = dict(row)

        if not item.get("context"):
            item["context"] = [
                f"Mode: {item.get('mode', 'UNKNOWN')}",
                f"Regime: {item.get('regime', 'UNKNOWN')}",
                f"Breadth: {item.get('breadth', 'UNKNOWN')}",
                f"Volatility: {item.get('volatility_state', 'UNKNOWN')}",
            ]

        if not item.get("summary_text"):
            item["summary_text"] = (
                item.get("rejection_reason")
                or (item.get("rejection_analysis")[0] if item.get("rejection_analysis") else None)
                or "This setup passed baseline checks but was not selected."
            )

        enriched.append(item)

    enriched.sort(
        key=lambda x: x.get("timestamp", x.get("opened_at", x.get("closed_at", ""))),
        reverse=True,
    )

    featured_trades = enriched[:5]

    for row in featured_trades:
        if row.get("rejection_reason"):
            track_rejection_interest(
                row.get("symbol", "UNKNOWN"),
                source="/why-this-trade",
            )

    return render_template_safe(
        "why_this_trade.html",
        **template_context({
            "trades": enriched,
            "featured_trades": featured_trades,
        }),
    )

@app.route("/premium-analysis")
def premium_analysis_page():
    maybe_track_page_view("/premium-analysis")
    track_premium_content_view(source="/premium-analysis", section="premium_analysis_page")
    if current_tier_lower() not in {"starter", "pro", "elite"}:
      track_premium_wall_seen(source="/premium-analysis", section="premium_analysis_page")
    feed_items = load_json("data/premium_feed.json", [])
    if not isinstance(feed_items, list):
        feed_items = []
    return render_template_safe(
        "premium_analysis.html",
        **template_context({"feed_items": feed_items, "premium_mode": current_tier_lower()}),
    )

@app.route("/admin")
def admin_dashboard():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    metrics = get_admin_metrics()
    proof = performance_summary()
    snapshot = get_dashboard_snapshot()
    system = get_system_state()

    shared = build_admin_shared_context()
    data_health = build_data_health_summary()

    users = load_json("data/users.json", [])
    if not isinstance(users, list):
        users = []

    return render_template_safe(
        "admin.html",
        **template_context({
            "positions": get_positions_with_intelligence(),
            "signals": get_signals(),
            "users": users,
            "metrics": metrics,
            "proof": proof,
            "snapshot": snapshot,
            "system": system,
            "admin_alerts": build_admin_alerts(
                shared.get("plays", []),
                shared.get("positions", []),
                shared.get("analysis", {}),
            ),
            "surface_alerts": shared.get("surface_alerts", {}),
            "quick_actions": shared.get("quick_actions", {}),
            "event_analytics": build_event_analytics_summary(),
            "alert_explanations": shared.get("alert_explanations", {}),
            "behavior_priority": shared.get("behavior_priority", {}),
            "behavioral_insights": shared.get("behavioral_insights", {}),
            "behavior_risk": shared.get("behavior_risk", {}),
            "data_health": data_health,
            "play_command": shared.get("play_command", {}),
        }),
    )


@app.route("/account")
def account_page():
    return render_template_safe(
        "account.html",
        **template_context({"billing": load_json("data/billing.json", {}), "prefs": {"theme": get_theme()}}),
    )


@app.route("/my-portfolio")
def my_portfolio_page():
    portfolio = {"positions": get_positions_with_intelligence()}
    return render_template_safe("my_portfolio.html", **template_context({"portfolio": portfolio}))


@app.route("/billing")
def billing_page():
    return render_template_safe(
        "billing.html",
        **template_context({"billing": load_json("data/billing.json", {})}),
    )


@app.route("/notifications")
def notifications_page():
    notifications = load_json("data/notifications.json", [])
    if not isinstance(notifications, list):
        notifications = []
    return render_template_safe("notifications.html", **template_context({"notifications": notifications}))


@app.route("/upgrade")
def upgrade_page():
    maybe_track_page_view("/upgrade")
    track_upgrade_click(source="/upgrade", tier="unknown")
    tiers = load_json("data/subscription_tiers.json", {})
    if not isinstance(tiers, dict):
        tiers = {}
    return render_template_safe(
        "upgrade.html",
        **template_context({"tiers": tiers, "alacarte_products": []}),
    )


@app.route("/set-theme/<theme>")
def set_theme(theme: str):
    session["theme"] = "light" if theme == "light" else "dark"
    return redirect(request.referrer or url_for("landing_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    maybe_track_page_view("/login")

    if is_logged_in():
        if is_master():
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        username = str(request.form.get("username", "") or "").strip()
        password = str(request.form.get("password", "") or "").strip()

        if not username:
            return render_template_safe(
                "login.html",
                **template_context({
                    "error": "Enter your username.",
                    "info": None,
                }),
            )

        if not password:
            return render_template_safe(
                "login.html",
                **template_context({
                    "error": "Enter your password.",
                    "info": None,
                }),
            )

        session["username"] = username

        if username.lower() in {"admin", "master", "solice"}:
            session["tier"] = "Elite"
            session["role"] = "master"
        else:
            session["tier"] = session.get("tier", "Free")
            session["role"] = "member"

        session.pop("preview_tier", None)

        if session.get("role") == "master":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("dashboard_page"))

    return render_template_safe(
        "login.html",
        **template_context({
            "info": request.args.get("info"),
            "error": request.args.get("error"),
        }),
    )


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    maybe_track_page_view("/signup")

    if is_logged_in():
        if is_master():
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        username = str(request.form.get("username", "") or "").strip()
        password = str(request.form.get("password", "") or "").strip()

        if not username:
            return render_template_safe(
                "signup.html",
                **template_context({"error": "Choose a username."}),
            )

        if not password:
            return render_template_safe(
                "signup.html",
                **template_context({"error": "Choose a password."}),
            )

        session["username"] = username
        session["tier"] = "Free"
        session["role"] = "member"
        session.pop("preview_tier", None)

        return redirect(url_for("dashboard_page"))

    return render_template_safe("signup.html", **template_context({}))


@app.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("landing_page"))


@app.route("/admin/preview-tier/<tier>")
def admin_preview_tier(tier: str):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    clean_tier = str(tier or "").strip().title()
    allowed = {"Guest", "Free", "Starter", "Pro", "Elite"}

    if clean_tier in allowed:
        session["preview_tier"] = clean_tier

    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/preview-tier/clear")
def admin_clear_preview_tier():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    session.pop("preview_tier", None)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/diagnostics")
def admin_diagnostics_page():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    maybe_track_page_view("/admin/diagnostics")

    diagnostics = build_admin_diagnostics()

    return render_template_safe(
        "admin_diagnostics.html",
        **template_context({
            "diagnostics": diagnostics,
        }),
    )


@app.route("/admin/refresh-market-universe")
def admin_refresh_market_universe():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    try:
        result = ensure_market_universe_ready(
            force=True,
            max_age_hours=12,
            min_retry_seconds=0,
        )
        print(f"[ADMIN_REFRESH_MARKET_UNIVERSE] {result}")
    except Exception as e:
        print(f"[ADMIN_REFRESH_MARKET_UNIVERSE] {e}")

    return redirect(request.referrer or url_for("admin_diagnostics_page"))

@app.route("/admin/refresh-news-cache")
def admin_refresh_news_cache():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    try:
        universe = load_market_universe()
        refresh_news_for_symbols(
            symbol_rows=universe,
            limit_per_symbol=6,
            max_symbols=500,
            force=True,
        )
    except Exception as e:
        print(f"[ADMIN_REFRESH_NEWS_CACHE] {e}")

    return redirect(request.referrer or url_for("admin_diagnostics_page"))


@app.route("/admin/product-analytics")
def admin_product_analytics_page():
    maybe_track_page_view("/admin/product-analytics")
    analytics = build_product_analytics()

    return render_template_safe(
        "admin_product_analytics.html",
        **template_context({
            "analytics": analytics,
        }),
    )


# SECTION 13H — STARTUP SAFETY HOOK

if __name__ == "__main__":
    try:
        startup_result = ensure_market_universe_ready(force=False, max_age_hours=12, min_retry_seconds=0)
        print("market_universe startup:", startup_result)
    except Exception as e:
        print("market_universe startup failed:", e)

    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
