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

from engine.notifications import (
    filtered_notifications_for_user,
    unread_count_for_user,
    mark_all_read,
)

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


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


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
    return filtered_notifications_for_user(
        user_tier=user["tier"],
        logged_in=is_logged_in(),
        username=user["username"],
    )


def visible_unread_count():
    user = get_current_user()
    return unread_count_for_user(
        user_tier=user["tier"],
        logged_in=is_logged_in(),
        username=user["username"],
    )


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


@app.before_request
def enforce_session_timeout():
    exempt = {
        "login_page",
        "signup_page",
        "landing_page",
        "static",
        "api_activity",
        "api_notifications",
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
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]

    return render_template(
        "landing.html",
        user=get_current_user(),
        snapshot=account_snapshot(),
        proof=performance_summary(),
        equity_values=equity_values,
        equity_labels=equity_labels,
        unread_notifications=visible_unread_count(),
    )


@app.route("/get-started")
def get_started_page():
    return render_template(
        "get_started.html",
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/onboarding")
def onboarding_page():
    return render_template(
        "onboarding.html",
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/modes")
def modes_page():
    return render_template(
        "modes.html",
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/proof")
def public_proof():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]

    return render_template(
        "proof.html",
        snapshot=account_snapshot(),
        proof=performance_summary(),
        positions=load_json("data/open_positions.json", []),
        closed=load_json("data/closed_positions.json", []),
        equity_values=equity_values,
        equity_labels=equity_labels,
        proof_detail=has_access("proof_detail"),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/live-activity")
def live_activity_page():
    return render_template(
        "live_activity.html",
        activity=load_json("data/live_activity.json", []),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/notifications")
def notifications_page():
    return render_template(
        "notifications.html",
        notifications=visible_notifications(),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/notifications/read-all")
def notifications_read_all():
    mark_all_read()
    return redirect(url_for("notifications_page"))


@app.route("/dashboard")
def dashboard_page():
    reports = load_json("data/recent_reports.json", [])
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]

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
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/trading")
def trading_overview():
    return render_template(
        "trading_overview.html",
        signals=load_json("data/live_signals.json", []),
        positions=monitor_open_positions(),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/analytics-overview")
def analytics_overview():
    return render_template(
        "analytics_overview.html",
        stats=analytics(),
        proof=performance_summary(),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/research")
def research_overview():
    return render_template(
        "research_overview.html",
        candidates=load_json("data/top_candidates.json", []),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
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
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/knowledge")
def knowledge_page():
    return render_template(
        "knowledge.html",
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/candidates")
def candidates_page():
    return render_template(
        "candidates.html",
        top_candidates=load_json("data/top_candidates.json", []),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/equity")
def equity_page():
    return render_template(
        "equity.html",
        curve=load_json("data/equity_curve.json", [1000]),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/status")
def status_page():
    return render_template(
        "status.html",
        system=load_json("data/system_status.json", {}),
        market=load_json("data/market_snapshot.json", {}),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/reports")
def reports_page():
    return render_template(
        "reports.html",
        reports=load_json("data/recent_reports.json", []),
        closed_stats=closed_trade_stats(),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/signals")
def signals_page():
    if not has_access("signals"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "signals.html",
        signals=load_json("data/live_signals.json", []),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/positions")
def positions_page():
    return render_template(
        "positions.html",
        positions=monitor_open_positions(),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/closed-trades")
def closed_trades_page():
    return render_template(
        "closed_trades.html",
        closed_trades=load_json("data/closed_positions.json", []),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/trade-timeline")
def trade_timeline_page():
    timeline = load_json("data/trade_timeline.json", [])
    if not isinstance(timeline, list):
        timeline = []

    return render_template(
        "trade_timeline.html",
        timeline=timeline,
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/bot-log")
def bot_log_page():
    bot_log = load_json("data/bot_log.json", [])
    if not isinstance(bot_log, list):
        bot_log = []

    return render_template(
        "bot_log.html",
        bot_log=bot_log,
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/control")
def control_page():
    return render_template(
        "control.html",
        bot_status=load_json("data/bot_status.json", {}),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/premium")
def premium_hub():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    return render_template(
        "premium_hub.html",
        user=get_current_user(),
        tier_config=get_tier_config(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/premium-analysis")
def premium_analysis_page():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("premium_analysis"):
        return redirect(url_for("upgrade_page"))

    analysis = load_json("data/premium_analysis.json", [])
    reports = load_json("data/recent_reports.json", [])
    equity_values = [
        r["snapshot"]["estimated_account_value"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]
    equity_labels = [
        r["timestamp"]
        for r in reports
        if isinstance(r, dict) and "snapshot" in r
    ]

    return render_template(
        "premium_analysis.html",
        analysis=analysis,
        user=get_current_user(),
        equity_values=equity_values,
        equity_labels=equity_labels,
        premium_depth=premium_depth(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/why-this-trade")
def why_this_trade_page():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))
    if not has_access("why_this_trade"):
        return redirect(url_for("upgrade_page"))

    return render_template(
        "why_this_trade.html",
        explanations=load_json("data/why_this_trade.json", []),
        user=get_current_user(),
        premium_depth=premium_depth(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/upgrade")
def upgrade_page():
    tiers = load_json("data/subscription_tiers.json", {})
    return render_template(
        "upgrade.html",
        user=get_current_user(),
        tiers=tiers,
        unread_notifications=visible_unread_count(),
    )


@app.route("/upgrade-tier/<tier>")
def upgrade_tier_action(tier):
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    update_user_tier(session["username"], tier)
    session["tier"] = tier
    set_billing_status(session["username"], tier, status="active", provider="mock")
    return redirect(url_for("premium_hub"))


@app.route("/billing")
def billing_page():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    return render_template(
        "billing.html",
        billing=get_billing_status(session["username"]),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/billing/mock/<plan>")
def billing_mock(plan):
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    set_billing_status(session["username"], plan, status="active", provider="mock")
    update_user_tier(session["username"], plan)
    session["tier"] = plan
    return redirect(url_for("billing_page"))


@app.route("/account")
def account_page():
    if not is_logged_in():
        return redirect(url_for("login_page", next=request.path))

    return render_template(
        "account.html",
        user=get_current_user(),
        prefs=get_preferences(session["username"]),
        billing=get_billing_status(session["username"]),
        unread_notifications=visible_unread_count(),
        message=request.args.get("message"),
        error=request.args.get("error"),
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


@app.route("/auth-status")
def auth_status_page():
    return render_template(
        "auth_status.html",
        auth=session_debug_payload(),
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/admin")
def admin_console():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    return render_template(
        "admin.html",
        user=get_current_user(),
        users=list_users(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/admin/audit-log")
def admin_audit_log_page():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    return render_template(
        "admin_audit_log.html",
        user=get_current_user(),
        audit=get_admin_audit_log(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/admin/session-debug")
def admin_session_debug_page():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    return render_template(
        "admin_session_debug.html",
        user=get_current_user(),
        session_debug=session_debug_payload(),
        unread_notifications=visible_unread_count(),
    )


@app.route("/admin/create-user", methods=["POST"])
def admin_create_user():
    if not is_master():
        return redirect(url_for("dashboard_page"))

    username = request.form.get("username")
    password = request.form.get("password")
    tier = request.form.get("tier", "Starter")
    role = request.form.get("role", "member")

    policy = password_policy_check(password)
    if not policy["ok"]:
        return redirect(url_for("admin_console"))

    create_user(username=username, password=password, tier=tier, role=role)
    log_admin_action(session["username"], "create_user", username, {"tier": tier, "role": role})
    return redirect(url_for("admin_console"))


@app.route("/admin/user/<username>")
def admin_user_page(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    record = get_user(username)
    if record is None:
        return redirect(url_for("admin_console"))

    return render_template(
        "admin_user.html",
        user=get_current_user(),
        record=record,
        unread_notifications=visible_unread_count(),
    )


@app.route("/admin/user/<username>/tier", methods=["POST"])
def admin_user_tier(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    new_tier = request.form.get("tier", "Starter")
    update_user_tier(username, new_tier)
    admin_set_billing_status(username, plan=new_tier)
    log_admin_action(session["username"], "update_tier", username, {"tier": new_tier})
    return redirect(url_for("admin_user_page", username=username))


@app.route("/admin/user/<username>/password", methods=["POST"])
def admin_user_password(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    new_password = request.form.get("password", "")
    policy = password_policy_check(new_password)
    if not policy["ok"]:
        return redirect(url_for("admin_user_page", username=username))

    reset_user_password(username, new_password)
    log_admin_action(session["username"], "reset_password", username, {})
    return redirect(url_for("admin_user_page", username=username))


@app.route("/admin/user/<username>/rename", methods=["POST"])
def admin_user_rename(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    new_username = request.form.get("new_username")
    ok, _ = rename_user(username, new_username)
    if ok:
        log_admin_action(session["username"], "rename_user", username, {"new_username": new_username})
        return redirect(url_for("admin_user_page", username=new_username))

    return redirect(url_for("admin_user_page", username=username))


@app.route("/admin/user/<username>/billing", methods=["POST"])
def admin_user_billing(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    status = request.form.get("status")
    plan = request.form.get("plan")
    provider = request.form.get("provider")

    admin_set_billing_status(username, status=status, plan=plan, provider=provider)
    log_admin_action(
        session["username"],
        "update_billing",
        username,
        {"status": status, "plan": plan, "provider": provider},
    )
    return redirect(url_for("admin_user_page", username=username))


@app.route("/admin/user/<username>/force-reset", methods=["POST"])
def admin_user_force_reset(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    required = request.form.get("required", "true").lower() == "true"
    admin_force_password_reset(username, required=required)
    log_admin_action(session["username"], "force_password_reset", username, {"required": required})
    return redirect(url_for("admin_user_page", username=username))


@app.route("/admin/user/<username>/delete", methods=["POST"])
def admin_user_delete(username):
    if not is_master():
        return redirect(url_for("dashboard_page"))

    if username == session.get("username"):
        return redirect(url_for("admin_user_page", username=username))

    delete_user(username)
    log_admin_action(session["username"], "delete_user", username, {})
    return redirect(url_for("admin_console"))


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

            if auth.get("force_password_reset"):
                return redirect(url_for("account_page", error="You must change your password before continuing."))

            if next_url:
                return redirect(next_url)

            return redirect(url_for("dashboard_page"))

        return render_template(
            "login.html",
            user=get_current_user(),
            unread_notifications=visible_unread_count(),
            error="Invalid username or password.",
            info=request.args.get("info"),
            next_url=next_url,
        )

    return render_template(
        "login.html",
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
        error=request.args.get("error"),
        info=request.args.get("info"),
        next_url=next_url,
    )


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        policy = password_policy_check(password)
        if not policy["ok"]:
            return render_template(
                "signup.html",
                user=get_current_user(),
                unread_notifications=visible_unread_count(),
                error=" ".join(policy["errors"]),
            )

        ok, msg = create_user(
            username=username,
            password=password,
            tier="Starter",
            role="member",
        )

        if ok:
            set_billing_status(username, "Starter", status="active", provider="mock")
            return redirect(url_for("login_page", info="Account created. Please log in."))

        return render_template(
            "signup.html",
            user=get_current_user(),
            unread_notifications=visible_unread_count(),
            error=msg,
        )

    return render_template(
        "signup.html",
        user=get_current_user(),
        unread_notifications=visible_unread_count(),
        error=request.args.get("error"),
    )


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


@app.route("/api/activity")
def api_activity():
    return jsonify(load_json("data/live_activity.json", []))


@app.route("/api/notifications")
def api_notifications():
    return jsonify(visible_notifications())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
