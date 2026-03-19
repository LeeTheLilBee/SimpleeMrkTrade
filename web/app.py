import sys
import os
import json
import subprocess
from pathlib import Path

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

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change_this_secret_key_later"

def load_json(path, default):
    file = Path(path)
    if not file.exists():
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_current_user():
    return {
        "username": session.get("username"),
        "tier": session.get("tier", "Guest")
    }

def is_logged_in():
    return session.get("username") is not None

def get_tier_config():
    tiers = load_json("data/subscription_tiers.json", {})
    tier = session.get("tier", "Guest")
    return tiers.get(tier, tiers.get("Guest", {}))

def has_access(feature):
    return bool(get_tier_config().get(feature, False))

def premium_depth():
    return get_tier_config().get("premium_depth", "none")

@app.route("/")
def landing_page():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports]

    return render_template(
        "landing.html",
        user=get_current_user(),
        snapshot=account_snapshot(),
        proof=performance_summary(),
        equity_values=equity_values,
        equity_labels=equity_labels
    )

@app.route("/get-started")
def get_started_page():
    return render_template("get_started.html", user=get_current_user())

@app.route("/onboarding")
def onboarding_page():
    return render_template("onboarding.html", user=get_current_user())

@app.route("/modes")
def modes_page():
    return render_template("modes.html", user=get_current_user())

@app.route("/proof")
def public_proof():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports]

    return render_template(
        "proof.html",
        snapshot=account_snapshot(),
        proof=performance_summary(),
        positions=load_json("data/open_positions.json", []),
        closed=load_json("data/closed_positions.json", []),
        equity_values=equity_values,
        equity_labels=equity_labels,
        proof_detail=has_access("proof_detail"),
        user=get_current_user()
    )

@app.route("/live-activity")
def live_activity_page():
    return render_template(
        "live_activity.html",
        activity=load_json("data/live_activity.json", []),
        user=get_current_user()
    )

@app.route("/dashboard")
def dashboard_page():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports]

    return render_template(
        "dashboard.html",
        state=get_dashboard_state(),
        snapshot=account_snapshot(),
        market=load_json("data/market_snapshot.json", {}),
        system=load_json("data/system_status.json", {}),
        top_candidates=load_json("data/top_candidates.json", []),
        proof=performance_summary(),
        unreal=unrealized_pnl(),
        strategies=strategy_breakdown(),
        drawdown=load_json("data/drawdown_history.json", []),
        equity_values=equity_values,
        equity_labels=equity_labels,
        signals=load_json("data/live_signals.json", []),
        user=get_current_user()
    )

@app.route("/trading")
def trading_overview():
    return render_template(
        "trading_overview.html",
        signals=load_json("data/live_signals.json", []),
        positions=monitor_open_positions(),
        user=get_current_user()
    )

@app.route("/analytics-overview")
def analytics_overview():
    return render_template(
        "analytics_overview.html",
        stats=analytics(),
        proof=performance_summary(),
        user=get_current_user()
    )

@app.route("/research")
def research_overview():
    return render_template(
        "research_overview.html",
        candidates=load_json("data/top_candidates.json", []),
        user=get_current_user()
    )

@app.route("/analytics")
def analytics_page():
    if not has_access("full_analytics"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "analytics.html",
        stats=analytics(),
        summary=portfolio_summary(),
        proof=performance_summary(),
        unreal=unrealized_pnl(),
        strategies=strategy_breakdown(),
        drawdown=load_json("data/drawdown_history.json", []),
        reports=load_json("data/recent_reports.json", []),
        user=get_current_user()
    )

@app.route("/knowledge")
def knowledge_page():
    return render_template("knowledge.html", user=get_current_user())

@app.route("/candidates")
def candidates_page():
    return render_template(
        "candidates.html",
        top_candidates=load_json("data/top_candidates.json", []),
        user=get_current_user()
    )

@app.route("/equity")
def equity_page():
    return render_template(
        "equity.html",
        curve=load_json("data/equity_curve.json", [1000]),
        user=get_current_user()
    )

@app.route("/status")
def status_page():
    return render_template(
        "status.html",
        system=load_json("data/system_status.json", {}),
        market=load_json("data/market_snapshot.json", {}),
        user=get_current_user()
    )

@app.route("/reports")
def reports_page():
    return render_template(
        "reports.html",
        reports=load_json("data/recent_reports.json", []),
        closed_stats=closed_trade_stats(),
        user=get_current_user()
    )

@app.route("/signals")
def signals_page():
    if not has_access("signals"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "signals.html",
        signals=load_json("data/live_signals.json", []),
        user=get_current_user()
    )

@app.route("/positions")
def positions_page():
    return render_template(
        "positions.html",
        positions=monitor_open_positions(),
        user=get_current_user()
    )

@app.route("/closed-trades")
def closed_trades_page():
    return render_template(
        "closed_trades.html",
        closed_trades=load_json("data/closed_positions.json", []),
        user=get_current_user()
    )

@app.route("/trade-timeline")
def trade_timeline_page():
    return render_template(
        "trade_timeline.html",
        timeline=load_json("data/trade_timeline.json", []),
        user=get_current_user()
    )

@app.route("/bot-log")
def bot_log_page():
    return render_template(
        "bot_log.html",
        bot_log=load_json("data/bot_log.json", []),
        user=get_current_user()
    )

@app.route("/control")
def control_page():
    return render_template(
        "control.html",
        bot_status=load_json("data/bot_status.json", {}),
        user=get_current_user()
    )

@app.route("/premium")
def premium_hub():
    if not is_logged_in():
        return redirect(url_for("login_page"))
    return render_template(
        "premium_hub.html",
        user=get_current_user(),
        tier_config=get_tier_config()
    )

@app.route("/premium-analysis")
def premium_analysis_page():
    if not is_logged_in():
        return redirect(url_for("login_page"))
    if not has_access("premium_analysis"):
        return redirect(url_for("upgrade_page"))

    analysis = load_json("data/premium_analysis.json", [])
    reports = load_json("data/recent_reports.json", [])
    equity_values = [r["snapshot"]["estimated_account_value"] for r in reports if "snapshot" in r]
    equity_labels = [r["timestamp"] for r in reports]

    return render_template(
        "premium_analysis.html",
        analysis=analysis,
        user=get_current_user(),
        equity_values=equity_values,
        equity_labels=equity_labels,
        premium_depth=premium_depth()
    )

@app.route("/why-this-trade")
def why_this_trade_page():
    if not is_logged_in():
        return redirect(url_for("login_page"))
    if not has_access("why_this_trade"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "why_this_trade.html",
        explanations=load_json("data/why_this_trade.json", []),
        user=get_current_user(),
        premium_depth=premium_depth()
    )

@app.route("/upgrade")
def upgrade_page():
    tiers = load_json("data/subscription_tiers.json", {})
    return render_template(
        "upgrade.html",
        user=get_current_user(),
        tiers=tiers
    )

@app.route("/login")
def login_page():
    return render_template("login.html", user=get_current_user())

@app.route("/login", methods=["POST"])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    users = load_json("data/users.json", [])

    for user in users:
        if user["username"] == username and user["password"] == password:
            session["username"] = user["username"]
            session["tier"] = user["tier"]
            return redirect(url_for("dashboard_page"))

    return redirect(url_for("login_page"))

@app.route("/signup")
def signup_page():
    return render_template("signup.html", user=get_current_user())

@app.route("/signup", methods=["POST"])
def signup_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    users = load_json("data/users.json", [])

    if any(u["username"] == username for u in users):
        return redirect(url_for("signup_page"))

    users.append({
        "username": username,
        "password": password,
        "tier": "Starter"
    })
    save_json("data/users.json", users)

    return redirect(url_for("login_page"))

@app.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("landing_page"))

@app.route("/runbot", methods=["POST"])
def runbot_action():
    status = load_json("data/bot_status.json", {})
    if not status.get("running"):
        subprocess.Popen(["python", "-m", "engine.bot"])
    return redirect(url_for("control_page"))

@app.route("/stopbot", methods=["POST"])
def stopbot_action():
    subprocess.Popen(["pkill", "-f", "python -m engine.bot"])
    return redirect(url_for("control_page"))

@app.route("/refreshstatus", methods=["POST"])
def refresh_status():
    return redirect(url_for("control_page"))

@app.route("/api/signals")
def api_signals():
    return jsonify(load_json("data/live_signals.json", []))

@app.route("/api/top-candidates")
def api_top_candidates():
    return jsonify(load_json("data/top_candidates.json", []))

@app.route("/api/account")
def api_account():
    return jsonify(account_snapshot())

@app.route("/api/bot-status")
def api_bot_status():
    return jsonify(load_json("data/bot_status.json", {}))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
