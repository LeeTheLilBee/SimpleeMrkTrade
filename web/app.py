import os
import sys
from flask import jsonify
import json
from pathlib import Path
from typing import Any, Dict, List

from flask import (
    Flask,
    render_template,
    render_template_string,
    request,
    redirect,
    session,
    url_for,
)
from jinja2 import TemplateNotFound

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.trade_intelligence import attach_trade_intelligence
from engine.signal_tiering import slice_signals_by_tier, spotlight_sections
from engine.position_health import attach_position_health
from engine.portfolio_intelligence import evaluate_portfolio
from engine.alert_engine import generate_alerts
from engine.system_brain import build_system_brain


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "simpleemrktrade-dev-key-change-later"


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
    return current_tier_title() in {"Starter", "Pro", "Elite"}


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
    return {
        "user": get_current_user(),
        "theme": get_theme(),
        "show_upgrade": should_show_upgrade(),
        "unread_notifications": get_unread_notifications(),
        "snapshot": get_dashboard_snapshot(),
        "system": get_system_state(),
    }


# ============================================================
# ANALYTICS HELPERS
# ============================================================

def get_admin_metrics() -> Dict[str, Any]:
    metrics = load_json("data/admin_metrics.json", {})
    if not isinstance(metrics, dict):
        metrics = {}

    return {
        "page_views": metrics.get("page_views", {}),
        "clicks": metrics.get("clicks", {}),
        "friction_signals": metrics.get("friction_signals", {}),
        "engagement": metrics.get("engagement", {}),
    }


def maybe_track_page_view(path: str) -> None:
    metrics = load_json("data/admin_metrics.json", {})
    if not isinstance(metrics, dict):
        metrics = {}

    page_views = metrics.get("page_views", {})
    if not isinstance(page_views, dict):
        page_views = {}

    page_views[path] = int(page_views.get(path, 0)) + 1
    metrics["page_views"] = page_views
    save_json("data/admin_metrics.json", metrics)


# ============================================================
# DATA BUILDERS
# ============================================================

def get_dashboard_snapshot() -> Dict[str, Any]:
    summary = load_json("data/portfolio_summary.json", {})
    if not isinstance(summary, dict):
        summary = {}

    reports = load_json("data/recent_reports.json", [])
    if not isinstance(reports, list):
        reports = []

    snapshot_file = load_json("data/account_snapshot.json", {})
    if not isinstance(snapshot_file, dict):
        snapshot_file = {}

    latest_report = reports[-1] if reports and isinstance(reports[-1], dict) else {}
    latest_snapshot = latest_report.get("snapshot", {}) if isinstance(latest_report, dict) else {}
    if not isinstance(latest_snapshot, dict):
        latest_snapshot = {}

    positions = summary.get("positions", [])
    if not isinstance(positions, list):
        positions = []

    estimated_account_value = (
        latest_snapshot.get("estimated_account_value")
        or summary.get("estimated_account_value")
        or snapshot_file.get("estimated_account_value")
        or 10000
    )

    buying_power = (
        latest_snapshot.get("buying_power")
        or summary.get("buying_power")
        or snapshot_file.get("buying_power")
        or 5000
    )

    open_positions = (
        latest_snapshot.get("open_positions")
        or summary.get("open_positions")
        or snapshot_file.get("open_positions")
        or len(positions)
    )

    return {
        "estimated_account_value": estimated_account_value,
        "buying_power": buying_power,
        "open_positions": open_positions,
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

    target = None

    # 1) Prefer rich saved trade_details
    for item in trade_details:
        if str(item.get("trade_id")) == str(trade_id) or str(item.get("id")) == str(trade_id):
            target = dict(item)
            break

    # 2) Fall back to open / closed positions
    if not target:
        for pool in [open_positions, closed_positions]:
            for item in pool:
                if str(item.get("trade_id")) == str(trade_id) or str(item.get("id")) == str(trade_id):
                    target = dict(item)
                    break
            if target:
                break

    # 3) Fall back to trade log
    if not target:
        for item in trade_log:
            if str(item.get("trade_id")) == str(trade_id) or str(item.get("id")) == str(trade_id):
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

    # Candidate context
    candidate = None
    for row in candidate_log:
        same_trade = str(row.get("trade_id")) == str(trade_id)
        same_symbol = row.get("symbol") == symbol
        if same_trade or same_symbol:
            candidate = row
            break

    # Timeline
    trade_timeline = []
    for row in timelines:
        same_trade = str(row.get("trade_id")) == str(trade_id)
        same_symbol = row.get("symbol") == symbol
        if same_trade or same_symbol:
            trade_timeline.append(row)

    # Enrich fallback blocks if missing
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

    # Pull explainability from candidate log if missing
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


def performance_summary() -> Dict[str, Any]:
    summary = load_json("data/portfolio_summary.json", {})
    if not isinstance(summary, dict):
        summary = {}

    perf_file = load_json("data/performance_summary.json", {})
    if not isinstance(perf_file, dict):
        perf_file = {}

    reports = load_json("data/recent_reports.json", [])
    if not isinstance(reports, list):
        reports = []

    latest_report = reports[-1] if reports and isinstance(reports[-1], dict) else {}
    latest_proof = latest_report.get("proof", {}) if isinstance(latest_report, dict) else {}
    if not isinstance(latest_proof, dict):
        latest_proof = {}

    return {
        "trades": (
            latest_proof.get("trades")
            or perf_file.get("trades")
            or summary.get("trades")
            or 0
        ),
        "winrate": (
            latest_proof.get("winrate")
            or perf_file.get("winrate")
            or summary.get("winrate")
            or "N/A"
        ),
        "max_drawdown": (
            latest_proof.get("max_drawdown")
            or perf_file.get("max_drawdown")
            or summary.get("max_drawdown")
            or "N/A"
        ),
    }


def unrealized_pnl() -> Any:
    summary = load_json("data/unrealized_pnl.json", {})
    if isinstance(summary, dict):
        return summary.get("value", 0)
    return 0


def strategy_breakdown() -> Dict[str, Any]:
    data = load_json("data/strategy_breakdown.json", {})
    if not isinstance(data, dict):
        return {}
    return data


def get_dashboard_state() -> Dict[str, Any]:
    return {
        "snapshot": get_dashboard_snapshot(),
        "system": get_system_state(),
    }


def get_positions() -> List[Dict[str, Any]]:
    positions = load_json("data/positions.json", [])
    if isinstance(positions, list) and positions:
        return positions

    summary = load_json("data/portfolio_summary.json", {})
    if isinstance(summary, dict):
        summary_positions = summary.get("positions", [])
        if isinstance(summary_positions, list):
            return summary_positions

    reports = load_json("data/recent_reports.json", [])
    if isinstance(reports, list) and reports:
        latest_report = reports[-1]
        if isinstance(latest_report, dict):
            report_positions = latest_report.get("positions", [])
            if isinstance(report_positions, list):
                return report_positions

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
    positions = get_positions()
    positions = attach_trade_intelligence(positions)
    positions = attach_position_health(positions)
    return positions


def get_signal_boards() -> List[Dict[str, Any]]:
    signals = get_signals()
    boards = []

    for item in signals:
        boards.append(
            {
                "symbol": item["symbol"],
                "company_name": item["company_name"],
                "latest_score": item["score"],
                "latest_confidence": item["confidence"],
                "latest_timestamp": item.get("timestamp", ""),
                "opinion": item.get("opinion", "Active setup."),
            }
        )

    return boards


def get_all_symbol_rows() -> List[Dict[str, Any]]:
    boards = get_signal_boards()
    rows = []
    seen = set()

    for board in boards:
        symbol = board.get("symbol")
        if symbol in seen:
            continue

        seen.add(symbol)
        rows.append(
            {
                "symbol": symbol,
                "company_name": board.get("company_name", symbol),
                "latest_score": board.get("latest_score", 0),
                "latest_confidence": board.get("latest_confidence", "LOW"),
                "latest_timestamp": board.get("latest_timestamp", ""),
                "opinion": board.get("opinion", "Active setup."),
            }
        )

    return rows


def get_symbol_detail(symbol: str) -> Dict[str, Any]:
    symbol = (symbol or "").upper()

    signals = get_signals()

    symbol_intel_map = load_json("data/symbol_intelligence.json", {})
    if not isinstance(symbol_intel_map, dict):
        symbol_intel_map = {}

    meta = load_json("data/symbol_meta.json", {})
    if not isinstance(meta, dict):
        meta = {}

    news = load_json("data/symbol_news.json", {})
    if not isinstance(news, dict):
        news = {}

    symbol_signals = [s for s in signals if s.get("symbol") == symbol]
    symbol_signals = attach_trade_intelligence(symbol_signals)

    primary_intel = symbol_intel_map.get(symbol, {})

    company = meta.get(symbol, {})
    if not isinstance(company, dict):
        company = {}

    news_items = news.get(symbol, [])
    if not isinstance(news_items, list):
        news_items = []

    if symbol_signals:
        top = symbol_signals[0]
        board = {
            "symbol": symbol,
            "company_name": top.get("company_name", symbol),
            "latest_score": top.get("score", 0),
            "latest_confidence": top.get("confidence", "LOW"),
            "latest_timestamp": top.get("timestamp", ""),
            "opinion": top.get("opinion", "Active setup."),
        }
    else:
        board = {
            "symbol": symbol,
            "company_name": symbol,
            "latest_score": 0,
            "latest_confidence": "LOW",
            "latest_timestamp": "",
            "opinion": "No active opinion available.",
        }

    return {
        "symbol": symbol,
        "company": {
            "name": company.get("name", board["company_name"]),
            "blurb": company.get("blurb", "No company overview available yet."),
        },
        "board": board,
        "primary_intelligence": primary_intel,
        "signals": symbol_signals,
        "news_items": news_items[:8],
    }


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


@app.route("/dashboard")
def dashboard_page():
    maybe_track_page_view("/dashboard")

    snapshot = get_dashboard_snapshot()
    system = get_system_state()
    proof = performance_summary()
    positions = get_positions_with_intelligence()

    reports = load_json("data/recent_reports.json", [])
    if not isinstance(reports, list):
        reports = []

    equity_values = []
    equity_labels = []

    for item in reports:
        if not isinstance(item, dict):
            continue

        snapshot_block = item.get("snapshot", {})
        if isinstance(snapshot_block, dict):
            equity_values.append(snapshot_block.get("estimated_account_value", 0))

        equity_labels.append(item.get("timestamp", ""))

    return render_template_safe(
        "dashboard.html",
        **template_context(
            {
                "state": get_dashboard_state(),
                "proof": proof,
                "unreal": unrealized_pnl(),
                "strategies": strategy_breakdown(),
                "drawdown": load_json("data/drawdown_history.json", []),
                "equity_values": equity_values,
                "equity_labels": equity_labels,
                "positions": positions,
                "snapshot": snapshot,
                "system": system,
                "reports": reports,
            }
        ),
    )


@app.route("/signals")
def signals_page():
    maybe_track_page_view("/signals")

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

    return render_template_safe(
        "signals.html",
        **template_context(
            {
                "visible_signals": visible_signals,
                "hidden_signals": hidden_signals,
                "hidden_count": hidden_count,
                "tier": tier,
                "top_five": top_five,
                "next_twenty": next_twenty,
                "hidden_remaining": hidden_count,
                "can_access_all_symbols": can_access_all_symbols(),
            }
        ),
    )


@app.route("/all-symbols")
def all_symbols_page():
    rows = get_all_symbol_rows()

    if not can_access_all_symbols():
        return redirect(url_for("upgrade_page"))

    return render_template_safe(
        "all_symbols.html",
        **template_context({"rows": rows}),
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

@app.route("/signals/<symbol>")
@app.route("/symbol/<symbol>")
def signal_symbol_page(symbol: str):
    detail = get_symbol_detail(symbol)
    return render_template_safe(
        "signal_symbol.html",
        **template_context(
            {
                "detail": detail,
                "symbol": detail["symbol"],
                "company": detail["company"],
                "symbol_signals": detail["signals"],
                "visible_signal_count": len(detail["signals"]),
                "total_signal_count": len(detail["signals"]),
                "show_teaser": current_tier_title() in {"Free", "Starter", "Guest"},
                "show_elite": current_tier_title() == "Elite",
                "news_items": detail["news_items"],
                "opinion": detail["board"].get("opinion", "Active setup."),
                "explanation": {},
            }
        ),
    )

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


@app.route("/my-positions")
def user_positions_page():
    maybe_track_page_view("/my-positions")
    positions = load_json("data/user_positions.json", [])
    if not isinstance(positions, list):
        positions = []
    return render_template_safe(
        "user_positions.html",
        **template_context({
            "positions": positions
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
    return render_template_safe("proof.html", **template_context({"proof": performance_summary()}))


@app.route("/research")
def research_overview():
    return render_template_safe("research_overview.html", **template_context({}))


@app.route("/analytics-overview")
def analytics_overview():
    maybe_track_page_view("/analytics-overview")

    stats = load_json("data/analytics_overview.json", {})
    if not isinstance(stats, dict):
        stats = {}

    return render_template_safe(
        "analytics_overview.html",
        **template_context({"stats": stats, "proof": performance_summary()}),
    )


@app.route("/analytics")
def analytics_page():
    stats = load_json("data/analytics_overview.json", {})
    if not isinstance(stats, dict):
        stats = {}

    return render_template_safe(
        "analytics.html",
        **template_context(
            {
                "stats": stats,
                "summary": load_json("data/portfolio_summary.json", {}),
                "proof": performance_summary(),
                "unreal": unrealized_pnl(),
                "strategies": strategy_breakdown(),
                "drawdown": load_json("data/drawdown_history.json", []),
                "reports": load_json("data/recent_reports.json", []),
            }
        ),
    )


@app.route("/analytics/performance")
def analytics_performance_page():
    return render_template_safe(
        "analytics_performance.html",
        **template_context(
            {
                "proof": performance_summary(),
                "reports": load_json("data/recent_reports.json", []),
                "summary": load_json("data/portfolio_summary.json", {}),
            }
        ),
    )


@app.route("/analytics/strategy")
@app.route("/strategy-behavior")
def strategy_behavior_page():
    return render_template_safe(
        "strategy_behavior.html",
        **template_context({
            "behavior": {
                "summary": "Strategy behavior view is active.",
                "items": []
            }
        }),
    )


@app.route("/analytics/risk")
def analytics_risk_page():
    return render_template_safe(
        "analytics_risk.html",
        **template_context(
            {
                "proof": performance_summary(),
                "summary": load_json("data/portfolio_summary.json", {}),
                "system": get_system_state(),
                "drawdown": load_json("data/drawdown_history.json", []),
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
    maybe_track_page_view(f"/trade/{trade_id}")
    detail = build_trade_detail_payload(trade_id)
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

    trades = load_json("data/trade_details.json", [])
    if not isinstance(trades, list):
        trades = []

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
            if row.get("rejection_reason"):
                row["summary_text"] = row["rejection_reason"]
            elif row.get("why"):
                row["summary_text"] = row["why"][0]
            elif row.get("exit_explanation"):
                row["summary_text"] = row["exit_explanation"]
            elif row.get("rejection_analysis"):
                row["summary_text"] = row["rejection_analysis"][0]
            else:
                row["summary_text"] = "This setup has been recorded, but its explanation package has not been fully attached yet."

        enriched.append(row)

    enriched.sort(
        key=lambda x: x.get("timestamp", x.get("opened_at", x.get("closed_at", ""))),
        reverse=True,
    )

    featured_trades = enriched[:5]

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
    positions = get_positions_with_intelligence()
    proof = performance_summary()
    snapshot = get_dashboard_snapshot()
    system = get_system_state()

    return render_template_safe(
        "admin.html",
        **template_context({
            "positions": positions,
            "signals": get_signals(),
            "users": load_json("data/users.json", []),
            "metrics": metrics,
            "proof": proof,
            "snapshot": snapshot,
            "system": system
        }),
    )


@app.route("/login", methods=["GET", "POST"])
def login_page():
    maybe_track_page_view("/login")

    if request.method == "POST":
        username = (request.form.get("username") or "").strip() or "demo_user"
        session["username"] = username

        # Keep admin/master redirect behavior locked in
        if username.lower() in {"admin", "master", "solice"}:
            session["tier"] = "Elite"
            session["role"] = "master"
        else:
            session["tier"] = session.get("tier", "Free")
            session["role"] = session.get("role", "member")

        if session.get("role") == "master":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("dashboard_page"))

    return render_template_safe(
        "login.html",
        **template_context({"info": request.args.get("info"), "error": request.args.get("error")}),
    )


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    maybe_track_page_view("/signup")

    if request.method == "POST":
        username = (request.form.get("username") or "").strip() or "new_user"
        session["username"] = username
        session["tier"] = "Free"
        session["role"] = "member"
        return redirect(url_for("dashboard_page"))

    return render_template_safe("signup.html", **template_context({}))


@app.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("landing_page"))


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


@app.route("/admin/preview-tier/<tier>")
def admin_preview_tier(tier: str):
    if is_master():
        session["preview_tier"] = tier.title()
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/preview-tier/clear")
def admin_clear_preview_tier():
    if is_master():
        session.pop("preview_tier", None)
    return redirect(request.referrer or url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
