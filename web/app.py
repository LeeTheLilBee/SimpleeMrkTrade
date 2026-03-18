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

def load_json(path, default):
    file = Path(path)
    if not file.exists():
        return default
    with open(file, "r") as f:
        return json.load(f)

@app.route("/")
def home():
    state = get_dashboard_state()
    snapshot = account_snapshot()
    market = load_json("data/market_snapshot.json", {})
    system = load_json("data/system_status.json", {})
    return render_template("home.html", state=state, snapshot=snapshot, market=market, system=system)

@app.route("/dashboard")
def dashboard():
    state = get_dashboard_state()
    stats = analytics()
    summary = portfolio_summary()
    proof = performance_summary()
    snapshot = account_snapshot()
    market = load_json("data/market_snapshot.json", {})
    top_candidates = load_json("data/top_candidates.json", [])
    unreal = unrealized_pnl()
    strategies = strategy_breakdown()
    drawdown = load_json("data/drawdown_history.json", [])
    system = load_json("data/system_status.json", {})
    return render_template(
        "dashboard.html",
        state=state,
        stats=stats,
        summary=summary,
        proof=proof,
        snapshot=snapshot,
        market=market,
        top_candidates=top_candidates,
        unreal=unreal,
        strategies=strategies,
        drawdown=drawdown,
        system=system
    )

@app.route("/analytics")
def analytics_page():
    stats = analytics()
    summary = portfolio_summary()
    proof = performance_summary()
    unreal = unrealized_pnl()
    strategies = strategy_breakdown()
    drawdown = load_json("data/drawdown_history.json", [])
    reports = load_json("data/recent_reports.json", [])
    return render_template(
        "analytics.html",
        stats=stats,
        summary=summary,
        proof=proof,
        unreal=unreal,
        strategies=strategies,
        drawdown=drawdown,
        reports=reports
    )

@app.route("/knowledge")
def knowledge():
    return render_template("knowledge.html")

@app.route("/candidates")
def candidates():
    top_candidates = load_json("data/top_candidates.json", [])
    return render_template("candidates.html", top_candidates=top_candidates)

@app.route("/equity")
def equity():
    curve = load_json("data/equity_curve.json", [1000])
    return render_template("equity.html", curve=curve)

@app.route("/status")
def status():
    system = load_json("data/system_status.json", {})
    market = load_json("data/market_snapshot.json", {})
    return render_template("status.html", system=system, market=market)

@app.route("/reports")
def reports():
    reports = load_json("data/recent_reports.json", [])
    return render_template("reports.html", reports=reports)

@app.route("/signals")
def signals():
    signals = load_json("data/live_signals.json", [])
    return render_template("signals.html", signals=signals)

@app.route("/positions")
def positions():
    unreal = unrealized_pnl()
    return render_template("positions.html", positions=unreal["positions"])

@app.route("/control")
def control():
    return render_template("control.html")

@app.route("/runbot", methods=["POST"])
def runbot():
    subprocess.Popen(["python", "-m", "engine.bot"])
    return "Bot Started"

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
            CURRENT_USER = {
                "username": user["username"],
                "tier": user["tier"]
            }
            return f"Logged in as {user['username']} ({user['tier']})"

    return "Login failed"

@app.route("/tier")
def tier():
    tiers = load_json("data/subscription_tiers.json", {})
    user = CURRENT_USER
    features = tiers.get(user["tier"], {})
    return render_template("tier.html", user=user, features=features)

@app.route("/api/signals")
def api_signals():
    return jsonify(load_json("data/live_signals.json", []))

@app.route("/api/top-candidates")
def api_top_candidates():
    return jsonify(load_json("data/top_candidates.json", []))

@app.route("/api/account")
def api_account():
    return jsonify(account_snapshot())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
