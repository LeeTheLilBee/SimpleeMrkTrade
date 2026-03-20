import sys
import os
import json
import subprocess
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
from engine.notifications import filtered_notifications_for_user, unread_count_for_user, mark_all_read
from engine.notification_engine import notifications_for_user
from engine.notification_settings import get_notification_settings, save_notification_settings
from engine.user_preferences import get_preferences, save_preferences
from engine.billing_hooks import get_billing_status, set_billing_status
from engine.admin_tools import (
    list_users,
    get_user,
    reset_user_password,
    rename_user,
    set_billing_status as admin_set_billing_status,
    create_user,
    delete_user,
    update_user_tier,
    force_password_reset as admin_force_password_reset,
)
from engine.auth_utils import (
    authenticate_user,
    ensure_secure_user_store,
    get_force_password_reset,
)
from engine.auth_policy import password_policy_check
from engine.admin_audit import log_admin_action, get_admin_audit_log
from engine.stripe_stub import start_checkout, open_customer_portal, simulate_checkout_success, process_webhook_event
from engine.trade_detail_builder import get_trade_detail_by_id

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change_this_secret_key_later_to_something_long_random"

ensure_secure_user_store()
SESSION_TIMEOUT_MINUTES = 720

def load_json(path, default):
    file = Path(path)
    if not file.exists():
        return default
    with open(file, "r") as f:
        return json.load(f)

def get_current_user():
    return {
        "username": session.get("username"),
        "tier": session.get("tier", "Guest"),
        "role": session.get("role", "member"),
    }

def is_logged_in():
    return session.get("username") is not None

def is_master():
    return session.get("role") == "master"

def get_tier_config():
    tiers = load_json("data/subscription_tiers.json", {})
    tier = session.get("tier", "Guest")
    return tiers.get(tier, tiers.get("Guest", {}))

def has_access(feature):
    if is_master():
        return True
    return bool(get_tier_config().get(feature, False))

def premium_depth():
    if is_master():
        return "max"
    return get_tier_config().get("premium_depth", "none")

def visible_notifications():
    user = get_current_user()
    legacy_visible = filtered_notifications_for_user(
        user_tier=user["tier"],
        logged_in=is_logged_in(),
        username=user["username"],
    )
    tuned_visible = notifications_for_user(user["username"], user["tier"] or "guest")
    combined = legacy_visible + tuned_visible
    combined = sorted(combined, key=lambda x: x.get("timestamp", ""), reverse=True)
    return combined

def visible_unread_count():
    return len(visible_notifications())

def session_debug_payload():
    username = session.get("username")
    return {
        "logged_in": is_logged_in(),
        "username": username,
        "tier": session.get("tier", "Guest"),
        "role": session.get("role", "member"),
        "last_seen": session.get("last_seen"),
        "force_password_reset": get_force_password_reset(username) if username else False,
    }

def build_capital_state(snapshot, system, market):
    reasons = []
    execution_blocked = False

    block_reasons = system.get("block_reasons", []) if isinstance(system, dict) else []
    if block_reasons:
        execution_blocked = True
        reasons.extend(block_reasons)

    if isinstance(system, dict) and system.get("governor_blocked"):
        execution_blocked = True
        reasons.append("Governor blocked deployment.")

    open_positions = snapshot.get("open_positions", 0) or 0
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
        "open_positions": open_positions,
        "mode": market.get("mode") if isinstance(market, dict) else None,
    }

def template_context(extra=None):
    user = get_current_user()
    prefs = get_preferences(user["username"]) if user["username"] else {"theme": "dark"}
    base = {
        "user": user,
        "unread_notifications": visible_unread_count(),
        "theme": prefs.get("theme", "dark")
    }
    if extra:
        base.update(extra)
    return base

@app.before_request
def enforce_session_timeout():
    exempt = {
        "login_page",
        "signup_page",
        "landing_page",
        "static",
        "api_activity",
        "api_notifications",
        "stripe_webhook_page",
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

@app.route("/")
def landing_page():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if isinstance(r, dict) and "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports if isinstance(r, dict) and "snapshot" in r]
    return render_template("landing.html", **template_context({
        "snapshot": account_snapshot(),
        "proof": performance_summary(),
        "equity_values": equity_values,
        "equity_labels": equity_labels,
    }))

@app.route("/dashboard")
def dashboard_page():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if isinstance(r, dict) and "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports if isinstance(r, dict) and "snapshot" in r]

    snapshot = account_snapshot()
    market = load_json("data/market_snapshot.json", {})
    system = load_json("data/system_status.json", {})
    capital_state = build_capital_state(snapshot, system, market)

    return render_template("dashboard.html", **template_context({
        "state": get_dashboard_state(),
        "snapshot": snapshot,
        "market": market,
        "system": system,
        "capital_state": capital_state,
        "top_candidates": load_json("data/top_candidates.json", []),
        "proof": performance_summary(),
        "unreal": unrealized_pnl(),
        "strategies": strategy_breakdown(),
        "drawdown": load_json("data/drawdown_history.json", []),
        "equity_values": equity_values,
        "equity_labels": equity_labels,
        "signals": load_json("data/live_signals.json", []),
    }))

@app.route("/knowledge")
def knowledge_page():
    return render_template("knowledge.html", **template_context())

@app.route("/notifications")
def notifications_page():
    return render_template("notifications.html", **template_context({
        "notifications": visible_notifications(),
    }))

@app.route("/notification-settings", methods=["GET", "POST"])
def notification_settings_page():
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

    return render_template("notification_settings.html", **template_context({
        "settings": get_notification_settings(username),
    }))

@app.route("/signals")
def signals_page():
    if not has_access("signals"):
        return redirect(url_for("upgrade_page"))
    return render_template("signals.html", **template_context({
        "signals": load_json("data/live_signals.json", []),
        "research_signals": load_json("data/research_signals.json", []),
    }))

@app.route("/premium-analysis")
def premium_analysis_page():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("premium_analysis"):
        return redirect(url_for("upgrade_page"))

    execution_analysis = load_json("data/premium_analysis.json", [])
    research_analysis = load_json("data/research_premium_analysis.json", [])

    if not isinstance(execution_analysis, list):
        execution_analysis = []
    if not isinstance(research_analysis, list):
        research_analysis = []

    all_analysis = sorted(
        execution_analysis + research_analysis,
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )

    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if isinstance(r, dict) and "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports if isinstance(r, dict) and "snapshot" in r]

    return render_template("premium_analysis.html", **template_context({
        "all_analysis": all_analysis,
        "equity_values": equity_values,
        "equity_labels": equity_labels,
        "premium_depth": premium_depth(),
    }))

@app.route("/trade/<trade_id>")
def trade_detail_page(trade_id):
    detail = get_trade_detail_by_id(trade_id)
    if not detail:
        return render_template("trade_detail.html", **template_context({
            "detail": {
                "symbol": "Not Found",
                "strategy": "N/A",
                "score": "N/A",
                "confidence": "N/A",
                "entry": "N/A",
                "atr": "N/A",
                "risk": {"stop_logic": "N/A", "note": "Trade not found.", "story": "Trade detail could not be located."},
                "thesis": ["Trade detail could not be located."],
                "narrative": {
                    "entry_story": "No entry story available.",
                    "management_story": "No management story available.",
                    "exit_story": "No exit story available.",
                },
                "context": [],
                "timeline": [],
            }
        }))
    return render_template("trade_detail.html", **template_context({
        "detail": detail,
    }))

# keep your other existing routes below this line as they already work
# proof, live activity, analytics, reports, account, admin, billing, auth, APIs, etc.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
