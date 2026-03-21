import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from engine.api_state import get_dashboard_state
from engine.trade_analytics import analytics
from engine.portfolio_summary import portfolio_summary
from engine.performance_tracker import performance_summary
from engine.account_snapshot import account_snapshot
from engine.unrealized_pnl import unrealized_pnl
from engine.strategy_performance import strategy_breakdown
from engine.position_monitor import monitor_open_positions
from engine.closed_trade_stats import closed_trade_stats
from engine.notifications import filtered_notifications_for_user, mark_all_read
from engine.notification_engine import notifications_for_user
from engine.notification_settings import get_notification_settings, save_notification_settings
from engine.user_preferences import get_preferences, save_preferences
from engine.billing_hooks import get_billing_status, set_billing_status
from engine.admin_tools import (
    list_users,
    get_user,
    reset_user_password,
    create_user,
    delete_user,
    update_user_tier,
)
from engine.auth_utils import (
    authenticate_user,
    ensure_secure_user_store,
    get_force_password_reset,
)
from engine.auth_policy import password_policy_check
from engine.admin_audit import get_admin_audit_log
from engine.trade_detail_builder import get_trade_detail_by_id
from engine.user_portfolio_store import (
    load_user_portfolio,
    save_mock_portfolio_from_form,
    clear_user_portfolio,
)
from engine.user_position_health import build_user_position_health
from engine.signal_feed import grouped_signals, load_signals
from engine.symbol_metadata import get_symbol_meta
from engine.symbol_news import get_symbol_news
from engine.admin_product_analytics import track_event, summarize_events
from engine.explanation_engine import (
    build_explanation_layers,
    slice_by_tier,
    build_premium_feed_post,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change_this_secret_key_later_to_something_long_random"

ensure_secure_user_store()
SESSION_TIMEOUT_MINUTES = 720


# ===========================================================
# DATA HELPERS
# ===========================================================

def load_json(path, default):
    file = Path(path)
    if not file.exists():
        return default
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, payload):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, "w") as f:
        json.dump(payload, f, indent=2)


# ===========================================================
# USER / SESSION HELPERS
# ===========================================================

def effective_tier():
    if session.get("preview_tier"):
        return session["preview_tier"]
    return session.get("tier", "Guest")


def current_tier_lower():
    return (effective_tier() or "Guest").lower()


def get_current_user():
    return {
        "username": session.get("username"),
        "tier": effective_tier(),
        "real_tier": session.get("tier", "Guest"),
        "role": session.get("role", "member"),
        "preview_tier": session.get("preview_tier"),
    }


def is_logged_in():
    return session.get("username") is not None


def is_master():
    return session.get("role") == "master"


def get_tier_config():
    tiers = load_json("data/subscription_tiers.json", {})
    tier = effective_tier()
    return tiers.get(tier, tiers.get("Guest", {}))


def has_access(feature):
    if is_master() and not session.get("preview_tier"):
        return True
    return bool(get_tier_config().get(feature, False))


def signal_history_limit_for_tier():
    if is_master() and not session.get("preview_tier"):
        return 9999

    limits = {
        "guest": 2,
        "free": 3,
        "starter": 5,
        "pro": 10,
        "elite": 9999,
    }
    return limits.get(current_tier_lower(), 3)


def can_access_all_symbols():
    if is_master() and not session.get("preview_tier"):
        return True
    return current_tier_lower() in {"starter", "pro", "elite"}


def premium_visible_mode():
    tier = current_tier_lower()

    if is_master() and not session.get("preview_tier"):
        return "elite"

    if tier == "free":
        return "free"
    if tier == "starter":
        return "starter"
    if tier == "pro":
        return "pro"
    if tier == "elite":
        return "elite"
    return "free"


def should_show_upgrade():
    return (not is_logged_in()) or effective_tier() != "Elite"


def visible_notifications():
    user = get_current_user()
    legacy_visible = filtered_notifications_for_user(
        user_tier=user["tier"],
        logged_in=is_logged_in(),
        username=user["username"],
    )
    tuned_visible = notifications_for_user(user["username"], user["tier"] or "guest")
    combined = legacy_visible + tuned_visible
    return sorted(combined, key=lambda x: x.get("timestamp", ""), reverse=True)


def visible_unread_count():
    return len(visible_notifications())


def session_debug_payload():
    username = session.get("username")
    return {
        "logged_in": is_logged_in(),
        "username": username,
        "session_tier": session.get("tier", "Guest"),
        "effective_tier": effective_tier(),
        "preview_tier": session.get("preview_tier"),
        "role": session.get("role", "member"),
        "last_seen": session.get("last_seen"),
        "force_password_reset": get_force_password_reset(username) if username else False,
    }


# ===========================================================
# STATE HELPERS
# ===========================================================

def build_capital_state(snapshot, system, market):
    reasons = []
    execution_blocked = False

    if isinstance(system, dict):
        if system.get("governor_blocked"):
            execution_blocked = True
            reasons.append("Governor blocked deployment.")
        if system.get("correlation_blocked"):
            execution_blocked = True
            reasons.append("Correlation risk blocked deployment.")
        if system.get("drawdown_blocked"):
            execution_blocked = True
            reasons.append("Drawdown brake blocked deployment.")
        if system.get("sector_cap_blocked"):
            execution_blocked = True
            reasons.append("Sector cap blocked deployment.")

        extra_reasons = system.get("block_reasons", [])
        if isinstance(extra_reasons, list):
            reasons.extend(extra_reasons)

    buying_power = float(snapshot.get("buying_power", 0) or 0)
    estimated_value = float(snapshot.get("estimated_account_value", 0) or 0)

    unused_pct = 0
    if estimated_value > 0:
        unused_pct = round((buying_power / estimated_value) * 100, 2)

    return {
        "buying_power": round(buying_power, 2),
        "execution_blocked": execution_blocked,
        "block_reasons": reasons,
        "unused_capital_pct": unused_pct,
        "mode": market.get("mode") if isinstance(market, dict) else "N/A",
    }


def maybe_track_page_view(page, symbol=None):
    if request.endpoint == "static":
        return
    track_event(
        event_type="page_view" if not symbol else "symbol_view",
        username=session.get("username"),
        page=page,
        symbol=symbol,
    )


def template_context(extra=None):
    user = get_current_user()
    prefs = get_preferences(user["username"]) if user["username"] else {"theme": "dark"}
    snapshot = account_snapshot()
    market = load_json("data/market_snapshot.json", {})
    system = load_json("data/system_status.json", {})
    capital_state = build_capital_state(snapshot, system, market)

    base = {
        "user": user,
        "unread_notifications": visible_unread_count(),
        "theme": prefs.get("theme", "dark"),
        "snapshot": snapshot,
        "market": market,
        "system": system,
        "capital_state": capital_state,
        "show_upgrade": should_show_upgrade(),
    }
    if extra:
        base.update(extra)
    return base


@app.context_processor
def inject_global_template_context():
    return template_context()


@app.before_request
def enforce_session_timeout():
    exempt = {
        "login_page",
        "signup_page",
        "landing_page",
        "static",
        "api_activity",
        "api_notifications",
        "api_signal_boards",
        "api_top_candidates",
        "api_signals",
        "api_account",
        "api_bot_status",
        "api_all_symbols",
    }

    if request.endpoint in exempt:
        return

    if is_logged_in():
        now = datetime.utcnow()
        last_seen_raw = session.get("last_seen")

        if last_seen_raw:
            try:
                last_seen = datetime.fromisoformat(last_seen_raw)
                if now - last_seen > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                    session.clear()
                    return redirect(url_for("login_page", info="Your session expired. Please log in again."))
            except Exception:
                pass

        session["last_seen"] = now.isoformat()


# ===========================================================
# SIGNAL / EXPLANATION HELPERS
# ===========================================================

def decorated_signal_boards(limit_per_symbol=None):
    boards = grouped_signals(limit_per_symbol=limit_per_symbol)
    decorated = []

    for board in boards:
        meta = get_symbol_meta(board["symbol"])
        latest_score = board.get("latest_score", 0)
        latest_conf = board.get("latest_confidence", "LOW")

        opinion = "Early setup worth monitoring."
        if latest_score >= 200:
            opinion = "High-conviction setup with strong alignment."
        elif latest_score >= 150:
            opinion = "Strong setup with meaningful confirmation."
        elif latest_score >= 100:
            opinion = "Developing setup with some alignment."

        board["company_name"] = meta["name"]
        board["company_blurb"] = meta["blurb"]
        board["visible_count"] = len(board.get("signals", []))
        board["opinion"] = opinion
        decorated.append(board)

    return sorted(decorated, key=lambda x: x.get("latest_score", 0), reverse=True)


def all_symbol_rows():
    rows = []
    seen = set()
    for board in decorated_signal_boards(limit_per_symbol=signal_history_limit_for_tier()):
        symbol = board["symbol"]
        if symbol in seen:
            continue
        seen.add(symbol)
        rows.append({
            "symbol": symbol,
            "company_name": board["company_name"],
            "latest_score": board.get("latest_score", 0),
            "latest_confidence": board.get("latest_confidence", "LOW"),
            "latest_timestamp": board.get("latest_timestamp", ""),
            "opinion": board.get("opinion", ""),
            "trade_id": board.get("latest_trade_id"),
        })
    return rows


def build_symbol_explanation(symbol, score, confidence):
    base, elite = build_explanation_layers(score, confidence, symbol=symbol)
    sliced, show_teaser, show_elite = slice_by_tier(base, elite, effective_tier())
    return sliced, show_teaser, show_elite


def build_why_trade_items():
    raw = load_json("data/trade_details.json", [])
    if not isinstance(raw, list):
        raw = []

    items = []
    for trade in sorted(raw, key=lambda x: x.get("timestamp", ""), reverse=True):
        symbol = trade.get("symbol", "N/A")
        score = trade.get("score", 0)
        confidence = trade.get("confidence", "LOW")
        explanation, show_teaser, show_elite = build_symbol_explanation(symbol, score, confidence)

        items.append({
            "id": trade.get("id"),
            "symbol": symbol,
            "score": score,
            "confidence": confidence,
            "timestamp": trade.get("timestamp", ""),
            "strategy": trade.get("strategy", "N/A"),
            "entry": trade.get("entry", "N/A"),
            "explanation": explanation,
            "show_teaser": show_teaser,
            "show_elite": show_elite,
        })
    return items


def build_premium_feed_items():
    boards = decorated_signal_boards(limit_per_symbol=signal_history_limit_for_tier())
    items = []

    for board in boards[:12]:
        score = board.get("latest_score", 0)
        confidence = board.get("latest_confidence", "LOW")
        post = build_premium_feed_post(
            symbol=board["symbol"],
            score=score,
            confidence=confidence,
            mode=board.get("mode", "STANDARD"),
        )
        post["timestamp"] = board.get("latest_timestamp", "")
        items.append(post)

    return items


# ===========================================================
# ROUTES - PUBLIC / CORE
# ===========================================================

@app.route("/")
def landing_page():
    maybe_track_page_view("/")
    reports = load_json("data/recent_reports.json", [])
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r and isinstance(r["snapshot"], dict)
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]
    return render_template(
        "landing.html",
        **template_context(
            {
                "proof": performance_summary(),
                "equity_values": equity_values,
                "equity_labels": equity_labels,
            }
        ),
    )


@app.route("/proof")
def public_proof():
    maybe_track_page_view("/proof")
    reports = load_json("data/recent_reports.json", [])
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r and isinstance(r["snapshot"], dict)
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]
    return render_template(
        "proof.html",
        **template_context(
            {
                "proof": performance_summary(),
                "positions": load_json("data/open_positions.json", []),
                "closed": load_json("data/closed_positions.json", []),
                "equity_values": equity_values,
                "equity_labels": equity_labels,
                "proof_detail": has_access("proof_detail"),
            }
        ),
    )


@app.route("/dashboard")
def dashboard_page():
    maybe_track_page_view("/dashboard")
    reports = load_json("data/recent_reports.json", [])
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r and isinstance(r["snapshot"], dict)
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]

    return render_template(
        "dashboard.html",
        **template_context(
            {
                "state": get_dashboard_state(),
                "proof": performance_summary(),
                "unreal": unrealized_pnl(),
                "strategies": strategy_breakdown(),
                "drawdown": load_json("data/drawdown_history.json", []),
                "equity_values": equity_values,
                "equity_labels": equity_labels,
            }
        ),
    )


@app.route("/live-activity")
def live_activity_page():
    maybe_track_page_view("/live-activity")
    return render_template(
        "live_activity.html",
        **template_context({"activity": load_json("data/live_activity.json", [])}),
    )


@app.route("/positions")
def positions_page():
    maybe_track_page_view("/positions")
    return render_template(
        "positions.html",
        **template_context({"positions": monitor_open_positions()}),
    )


@app.route("/equity")
def equity_page():
    maybe_track_page_view("/equity")
    return render_template(
        "equity.html",
        **template_context({"curve": load_json("data/equity_curve.json", [1000])}),
    )


@app.route("/reports")
def reports_page():
    maybe_track_page_view("/reports")
    return render_template(
        "reports.html",
        **template_context(
            {
                "reports": load_json("data/recent_reports.json", []),
                "closed_stats": closed_trade_stats(),
            }
        ),
    )


@app.route("/bot-log")
def bot_log_page():
    maybe_track_page_view("/bot-log")
    return render_template(
        "bot_log.html",
        **template_context({"bot_log": load_json("data/bot_log.json", [])}),
    )


@app.route("/research")
def research_overview():
    maybe_track_page_view("/research")
    return render_template(
        "research_overview.html",
        **template_context({"candidates": load_json("data/top_candidates.json", [])}),
    )


# ===========================================================
# ROUTES - SIGNALS
# ===========================================================

@app.route("/signals")
def signals_page():
    maybe_track_page_view("/signals")
    if not has_access("signals"):
        return redirect(url_for("upgrade_page"))

    boards = decorated_signal_boards(limit_per_symbol=signal_history_limit_for_tier())
    tier = current_tier_lower()

    if tier == "free":
        top_count = 3
        next_cap = 0
    elif tier == "starter":
        top_count = 5
        next_cap = 5
    elif tier == "pro":
        top_count = 5
        next_cap = 10
    elif tier == "elite":
        top_count = 5
        next_cap = 20
    else:
        top_count = 3
        next_cap = 0

    if is_master() and not session.get("preview_tier"):
        top_count = 5
        next_cap = 20

    top_five = boards[:top_count]
    next_twenty = boards[top_count:top_count + 
    next_cap]
    hidden_remaining = max(0, len(boards) - 
    (top_count + next_cap))

    return render_template(
        "signals.html",
        **template_context(
            {
                "top_five": top_five,
                "next_twenty": next_twenty,
                "hidden_remaining": hidden_remaining,
                "signal_history_limit": signal_history_limit_for_tier(),
                "can_access_all_symbols": can_access_all_symbols(),
            }
        ),
    )


@app.route("/all-symbols")
def all_symbols_page():
    maybe_track_page_view("/all-symbols")
    if not has_access("signals"):
        return redirect(url_for("upgrade_page"))

    if not can_access_all_symbols():
        return redirect(url_for("upgrade_page"))

    return render_template(
        "all_symbols.html",
        **template_context({"rows": all_symbol_rows()}),
    )


@app.route("/signals/<symbol>")
def signal_symbol_page(symbol):
    symbol = (symbol or "").upper()
    maybe_track_page_view(f"/signals/{symbol}", symbol=symbol)

    if not has_access("signals"):
        return redirect(url_for("upgrade_page"))

    limit = signal_history_limit_for_tier()
    all_signals = [s for s in load_signals() if (s.get("symbol") or "").upper() == symbol]
    all_signals = sorted(all_signals, key=lambda x: x.get("timestamp", ""), reverse=True)

    visible_signals = all_signals[:limit]
    company = get_symbol_meta(symbol)
    news_items = get_symbol_news(symbol, limit=8)

    latest_score = visible_signals[0].get("score", 0) if visible_signals else 0
    latest_conf = visible_signals[0].get("confidence", "LOW") if visible_signals else "LOW"

    explanation, show_teaser, show_elite = build_symbol_explanation(symbol, latest_score, latest_conf)

    opinion = "Early setup worth monitoring."
    if latest_score >= 200:
        opinion = "High-conviction setup with strong alignment."
    elif latest_score >= 150:
        opinion = "Strong setup with meaningful confirmation."
    elif latest_score >= 100:
        opinion = "Developing setup with some alignment."

    return render_template(
        "signal_symbol.html",
        **template_context(
            {
                "symbol": symbol,
                "company": company,
                "symbol_signals": visible_signals,
                "visible_signal_count": len(visible_signals),
                "total_signal_count": len(all_signals),
                "show_teaser": show_teaser,
                "show_elite": show_elite,
                "news_items": news_items,
                "opinion": opinion,
                "explanation": explanation,
            }
        ),
    )


# ===========================================================
# ROUTES - ANALYTICS
# ===========================================================

@app.route("/analytics-overview")
def analytics_overview():
    maybe_track_page_view("/analytics-overview")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    return render_template(
        "analytics_overview.html",
        **template_context(
            {
                "stats": analytics(),
                "proof": performance_summary(),
            }
        ),
    )


@app.route("/analytics")
def analytics_page():
    maybe_track_page_view("/analytics")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("full_analytics"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "analytics.html",
        **template_context(
            {
                "stats": analytics(),
                "summary": portfolio_summary(),
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
    maybe_track_page_view("/analytics/performance")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("full_analytics"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "analytics_performance.html",
        **template_context(
            {
                "stats": analytics(),
                "proof": performance_summary(),
                "reports": load_json("data/recent_reports.json", []),
                "summary": portfolio_summary(),
            }
        ),
    )


@app.route("/analytics/strategy")
def analytics_strategy_page():
    maybe_track_page_view("/analytics/strategy")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("full_analytics"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "analytics_strategy.html",
        **template_context(
            {
                "strategies": strategy_breakdown(),
                "stats": analytics(),
                "system": load_json("data/system_status.json", {}),
                "market": load_json("data/market_snapshot.json", {}),
            }
        ),
    )


@app.route("/analytics/risk")
def analytics_risk_page():
    maybe_track_page_view("/analytics/risk")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("full_analytics"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "analytics_risk.html",
        **template_context(
            {
                "proof": performance_summary(),
                "summary": portfolio_summary(),
                "system": load_json("data/system_status.json", {}),
                "drawdown": load_json("data/drawdown_history.json", []),
            }
        ),
    )


# ===========================================================
# ROUTES - WHY THIS TRADE / PREMIUM
# ===========================================================

@app.route("/why-this-trade")
def why_this_trade_page():
    maybe_track_page_view("/why-this-trade")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("why_this_trade"):
        return redirect(url_for("upgrade_page"))

    trades = build_why_trade_items()

    return render_template(
        "why_this_trade.html",
        **template_context(
            {
                "trades": trades,
            }
        ),
    )


@app.route("/premium")
def premium_hub():
    maybe_track_page_view("/premium")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    return render_template(
        "premium_hub.html",
        **template_context({"tier_config": get_tier_config()}),
    )


@app.route("/premium-analysis")
def premium_analysis_page():
    maybe_track_page_view("/premium-analysis")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("premium_analysis"):
        return redirect(url_for("upgrade_page"))

    mode = premium_visible_mode()
    items = build_premium_feed_items()

    return render_template(
        "premium_analysis.html",
        **template_context(
            {
                "feed_items": items,
                "premium_mode": mode,
            }
        ),
    )


@app.route("/trade/<trade_id>")
def trade_detail_page(trade_id):
    detail = get_trade_detail_by_id(trade_id)
    if not detail:
        return render_template(
            "trade_detail.html",
            **template_context(
                {
                    "detail": {
                        "symbol": "Not Found",
                        "strategy": "N/A",
                        "score": "N/A",
                        "confidence": "N/A",
                        "entry": "N/A",
                        "atr": "N/A",
                        "risk": {
                            "stop_logic": "N/A",
                            "note": "Trade not found.",
                            "story": "Trade detail could not be located.",
                        },
                        "thesis": ["Trade detail could not be located."],
                        "narrative": {
                            "entry_story": "No entry story available.",
                            "management_story": "No management story available.",
                            "exit_story": "No exit story available.",
                        },
                        "context": [],
                        "timeline": [],
                    }
                }
            ),
        )
    return render_template("trade_detail.html", **template_context({"detail": detail}))


# ===========================================================
# ROUTES - ACCOUNT / BILLING / AUTH
# ===========================================================

@app.route("/upgrade")
def upgrade_page():
    maybe_track_page_view("/upgrade")
    tiers = load_json("data/subscription_tiers.json", {})
    return render_template(
        "upgrade.html",
        **template_context(
            {
                "tiers": tiers,
                "alacarte_products": [],
            }
        ),
    )


@app.route("/upgrade-tier/<tier>")
def upgrade_tier_action(tier):
    track_event(
        event_type="upgrade_click",
        username=session.get("username"),
        page="/upgrade",
        meta={"target_tier": tier},
    )

    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    if effective_tier() == tier:
        return redirect(url_for("upgrade_page"))

    update_user_tier(session["username"], tier)
    session["tier"] = tier
    set_billing_status(session["username"], tier, status="active", provider="mock")
    return redirect(url_for("signals_page"))


@app.route("/billing")
def billing_page():
    maybe_track_page_view("/billing")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    return render_template(
        "billing.html",
        **template_context({"billing": get_billing_status(session["username"])}),
    )


@app.route("/my-portfolio", methods=["GET", "POST"])
def my_portfolio_page():
    maybe_track_page_view("/my-portfolio")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    username = session["username"]

    if request.method == "POST":
        broker = request.form.get("broker", "IBKR")
        cash = request.form.get("cash", 0)
        buying_power = request.form.get("buying_power", 0)
        notes = request.form.get("notes", "")

        existing = load_user_portfolio(username)
        positions = existing.get("positions", [])

        save_mock_portfolio_from_form(
            username=username,
            broker=broker,
            cash=cash,
            buying_power=buying_power,
            notes=notes,
            positions=positions,
        )
        return redirect(url_for("my_portfolio_page"))

    portfolio = build_user_position_health(load_user_portfolio(username))
    return render_template(
        "my_portfolio.html",
        **template_context({"portfolio": portfolio}),
    )


@app.route("/my-portfolio/clear")
def clear_my_portfolio():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    clear_user_portfolio(session["username"])
    return redirect(url_for("my_portfolio_page"))


@app.route("/notifications")
def notifications_page():
    maybe_track_page_view("/notifications")
    return render_template(
        "notifications.html",
        **template_context({"notifications": visible_notifications()}),
    )


@app.route("/notification-settings", methods=["GET", "POST"])
def notification_settings_page():
    maybe_track_page_view("/notification-settings")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    username = session["username"]

    if request.method == "POST":
        settings = {
            "high_conviction_only": bool(request.form.get("high_conviction_only")),
            "research_alerts": bool(request.form.get("research_alerts")),
            "execution_alerts": bool(request.form.get("execution_alerts")),
            "risk_alerts": bool(request.form.get("risk_alerts")),
            "system_alerts": bool(request.form.get("system_alerts")),
            "min_score": int(request.form.get("min_score", 0)),
            "strategy_filter": request.form.get("strategy_filter", "ALL"),
            "volatility_filter": request.form.get("volatility_filter", "ALL"),
        }
        save_notification_settings(username, settings)
        return redirect(url_for("notification_settings_page"))

    return render_template(
        "notification_settings.html",
        **template_context({"settings": get_notification_settings(username)}),
    )


@app.route("/notifications/read-all")
def notifications_read_all():
    mark_all_read()
    return redirect(url_for("notifications_page"))


@app.route("/account")
def account_page():
    maybe_track_page_view("/account")
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    return render_template(
        "account.html",
        **template_context(
            {
                "prefs": get_preferences(session["username"]),
                "billing": get_billing_status(session["username"]),
                "message": request.args.get("message"),
                "error": request.args.get("error"),
            }
        ),
    )


@app.route("/account/preferences", methods=["POST"])
def account_preferences_save():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    prefs = {
        "email_notifications": bool(request.form.get("email_notifications")),
        "signal_notifications": bool(request.form.get("signal_notifications")),
        "risk_notifications": bool(request.form.get("risk_notifications")),
        "premium_notifications": bool(request.form.get("premium_notifications")),
        "system_notifications": bool(request.form.get("system_notifications")),
        "theme": request.form.get("theme", "dark"),
    }

    save_preferences(session["username"], prefs)
    return redirect(url_for("account_page", message="Preferences saved."))


@app.route("/account/change-password", methods=["POST"])
def account_change_password():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")

    auth = authenticate_user(session["username"], current_password)
    if not auth:
        return redirect(url_for("account_page", error="Current password is incorrect."))

    policy = password_policy_check(new_password)
    if not policy["ok"]:
        return redirect(url_for("account_page", error=" ".join(policy["errors"])))

    reset_user_password(session["username"], new_password)
    return redirect(url_for("account_page", message="Password updated successfully."))


@app.route("/login", methods=["GET", "POST"])
def login_page():
    next_url = request.args.get("next", "")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        next_url = request.args.get("next", "")

        auth = authenticate_user(username, password)

        if auth:
            session["username"] = auth["username"]
            session["tier"] = auth["tier"]
            session["role"] = auth["role"]
            session["last_seen"] = datetime.utcnow().isoformat()
            session.pop("preview_tier", None)

            if auth.get("force_password_reset"):
                return redirect(url_for("account_page", error="You must change your password before continuing."))

            if next_url:
                return redirect(next_url)

            return redirect(url_for("dashboard_page"))

        track_event(
            event_type="login_failure",
            username=username,
            page="/login",
        )

        return render_template(
            "login.html",
            **template_context(
                {
                    "error": "Invalid username or password.",
                    "info": request.args.get("info"),
                    "next_url": next_url,
                }
            ),
        )

    return render_template(
        "login.html",
        **template_context(
            {
                "error": request.args.get("error"),
                "info": request.args.get("info"),
                "next_url": next_url,
            }
        ),
    )


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        policy = password_policy_check(password)
        if not policy["ok"]:
            return render_template(
                "signup.html",
                **template_context({"error": " ".join(policy["errors"])}),
            )

        ok, msg = create_user(
            username=username,
            password=password,
            email=email,
            tier="Free",
            role="member",
        )

        if ok:
            set_billing_status(username, "Free", status="active", provider="mock")
            return redirect(url_for("login_page", info="Account created. Please log in."))

        return render_template(
            "signup.html",
            **template_context({"error": msg}),
        )

    return render_template(
        "signup.html",
        **template_context({"error": request.args.get("error")}),
    )


@app.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("landing_page"))


# ===========================================================
# ROUTES - ADMIN
# ===========================================================

@app.route("/admin")
def admin_console():
    if not is_master():
        return redirect(url_for("dashboard_page"))
    return render_template(
        "admin.html",
        **template_context({"users": list_users()}),
    )


@app.route("/admin/product-analytics")
def admin_product_analytics_page():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    summary = summarize_events(days=30)
    return render_template(
        "admin_product_analytics.html",
        **template_context({"summary": summary}),
    )


@app.route("/admin/session-debug")
def admin_session_debug_page():
    if not is_master():
        return redirect(url_for("dashboard_page"))
    return render_template(
        "admin_session_debug.html",
        **template_context({"session_debug": session_debug_payload()}),
    )


@app.route("/admin/audit-log")
def admin_audit_log_page():
    if not is_master():
        return redirect(url_for("dashboard_page"))
    return render_template(
        "admin_audit_log.html",
        **template_context({"audit": get_admin_audit_log()}),
    )


@app.route("/admin/preview-tier/<tier>")
def admin_preview_tier(tier):
    if not is_master():
        return redirect(url_for("dashboard_page"))
    session["preview_tier"] = tier
    return redirect(url_for("dashboard_page"))


@app.route("/admin/preview-tier/clear")
def admin_clear_preview_tier():
    if not is_master():
        return redirect(url_for("dashboard_page"))
    session.pop("preview_tier", None)
    return redirect(url_for("dashboard_page"))


# ===========================================================
# API
# ===========================================================

@app.route("/api/signals")
def api_signals():
    return jsonify(load_signals())


@app.route("/api/signal-boards")
def api_signal_boards():
    return jsonify(decorated_signal_boards(limit_per_symbol=signal_history_limit_for_tier()))


@app.route("/api/all-symbols")
def api_all_symbols():
    return jsonify(all_symbol_rows())


@app.route("/api/top-candidates")
def api_top_candidates():
    return jsonify(load_json("data/top_candidates.json", []))


@app.route("/api/account")
def api_account():
    return jsonify(account_snapshot())


@app.route("/api/bot-status")
def api_bot_status():
    return jsonify(load_json("data/bot_status.json", {}))


@app.route("/api/activity")
def api_activity():
    return jsonify(load_json("data/live_activity.json", []))


@app.route("/api/notifications")
def api_notifications():
    return jsonify(visible_notifications())


@app.route("/debug-tier")
def debug_tier():
    if not is_logged_in():
        return jsonify({"logged_in": False})

    return jsonify({
        "username": session.get("username"),
        "session_tier": session.get("tier"),
        "effective_tier": effective_tier(),
        "preview_tier": session.get("preview_tier"),
        "session_role": session.get("role"),
        "billing": get_billing_status(session["username"]),
        "user_record": get_user(session["username"]),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
