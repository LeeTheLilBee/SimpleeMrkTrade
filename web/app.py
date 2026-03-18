import sys
import os
import json
import subprocess
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, jsonify
from engine.api_state import get_dashboard_state
from engine.trade_analytics import analytics
from engine.portfolio_summary import portfolio_summary
from engine.performance_tracker import performance_summary
from engine.account_snapshot import account_snapshot
from engine.unrealized_pnl import unrealized_pnl
from engine.strategy_performance import strategy_breakdown

app = Flask(__name__, template_folder="templates", static_folder="static")

CURRENT_USER = {"username": None, "tier": "Starter"}
BOT_PROCESS = None

def load_json(path, default):
    file = Path(path)
    if not file.exists():
        return default
    with open(file, "r") as f:
        return json.load(f)

@app.route("/")
def home_page():
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
        equity_labels=equity_labels
    )

@app.route("/dashboard")
def dashboard_page():
    return home_page()

@app.route("/analytics")
def analytics_page():
    return render_template(
        "analytics.html",
        stats=analytics(),
        summary=portfolio_summary(),
        proof=performance_summary(),
        unreal=unrealized_pnl(),
        strategies=strategy_breakdown(),
        drawdown=load_json("data/drawdown_history.json", []),
        reports=load_json("data/recent_reports.json", [])
    )

@app.route("/knowledge")
def knowledge_page():
    return render_template("knowledge.html")

@app.route("/candidates")
def candidates_page():
    return render_template("candidates.html", top_candidates=load_json("data/top_candidates.json", []))

@app.route("/equity")
def equity_page():
    return render_template("equity.html", curve=load_json("data/equity_curve.json", [1000]))

@app.route("/status")
def status_page():
    return render_template(
        "status.html",
        system=load_json("data/system_status.json", {}),
        market=load_json("data/market_snapshot.json", {})
    )

@app.route("/reports")
def reports_page():
    return render_template("reports.html", reports=load_json("data/recent_reports.json", []))

@app.route("/signals")
def signals_page():
    return render_template("signals.html", signals=load_json("data/live_signals.json", []))

@app.route("/positions")
def positions_page():
    return render_template("positions.html", unreal=unrealized_pnl())

@app.route("/control")
def control_page():
    return render_template("control.html", bot_status=load_json("data/bot_status.json", {}))

@app.route("/runbot", methods=["POST"])
def runbot_action():
    global BOT_PROCESS
    status = load_json("data/bot_status.json", {})
    if status.get("running"):
        return "Bot already running"
    BOT_PROCESS = subprocess.Popen(["python", "-m", "engine.bot"])
    return "Bot Started"

@app.route("/stopbot", methods=["POST"])
def stopbot_action():
    subprocess.Popen(["pkill", "-f", "python -m engine.bot"])
    return "Stop signal sent"

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_submit():
    global CURRENT_USER
    username = request.form.get("username")
    password = request.form.get("password")

    users = load_json("data/users.json", [])

    for user in users:
        if user["username"] == username and user["password"] == password:
            CURRENT_USER = {"username": user["username"], "tier": user["tier"]}
            return f"Logged in as {user['username']} ({user['tier']})"

    return "Login failed"

@app.route("/tier")
def tier_page():
    tiers = load_json("data/subscription_tiers.json", {})
    return render_template("tier.html", user=CURRENT_USER, features=tiers.get(CURRENT_USER["tier"], {}))

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
