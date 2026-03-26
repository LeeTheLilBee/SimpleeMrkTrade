import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import sys
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
from flask import jsonify
from engine.admin_product_analytics import top_engaged_symbols
import json
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
    top_engaged_symbols_with_counts,
    most_underrated_symbols,
)
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
from engine.admin_product_analytics import (
    maybe_track_page_view,
    track_symbol_click,
    track_trade_click,
    track_upgrade_click,
    track_cta_click,
    build_product_analytics,
)


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


def build_admin_surface_alerts(admin_summary=None, monitoring=None):
    admin_summary = admin_summary or {}
    monitoring = monitoring or {}

    alerts = []

    activation = admin_summary.get("activation_quality", {}) or {}
    disagreement = admin_summary.get("disagreement", {}) or {}
    idea_quality = admin_summary.get("idea_quality", {}) or {}
    zones = admin_summary.get("zones", {}) or {}

    readiness = monitoring.get("readiness_buckets", {}) or {}
    thesis_quality = monitoring.get("thesis_quality", {}) or {}
    position_quality = monitoring.get("position_quality", {}) or {}
    strongest_friction = monitoring.get("strongest_friction", {}) or {}

    weak_activations = int(activation.get("weak_activations", 0) or 0)
    ready_activations = int(activation.get("ready_activations", 0) or 0)
    disagreement_count = int(disagreement.get("disagreement_count", 0) or 0)
    aligned_count = int(disagreement.get("aligned_count", 0) or 0)

    weak_plays = int(readiness.get("WEAK", 0) or 0)
    watch_plays = int(readiness.get("WATCH", 0) or 0)
    ready_plays = int(readiness.get("READY", 0) or 0)

    no_thesis = int(thesis_quality.get("without_thesis", 0) or 0)
    weak_open_positions = int(position_quality.get("weak_open_positions", 0) or 0)

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

    top_failure = zones.get("top_failure_cluster", {}) or {}
    if int(top_failure.get("count", 0) or 0) > 0:
        alerts.append({
            "level": "neutral",
            "headline": "Failure cluster is visible",
            "body": f"{top_failure.get('label')} is currently the dominant failure cluster.",
            "target": "/admin/intelligence?filter=failure",
            "target_label": "Review Failure Cluster",
        })

    friction_headline = str(strongest_friction.get("headline", "") or "").strip()
    friction_body = str(strongest_friction.get("body", "") or "").strip()
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

    priority_order = {
        "danger": 0,
        "warning": 1,
        "neutral": 2,
        "positive": 3,
    }
    alerts = sorted(alerts, key=lambda a: priority_order.get(a.get("level", "neutral"), 99))

    return {
        "top_alert": alerts[0] if alerts else None,
        "alerts": alerts[:4],
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

    open_positions = [
        p for p in positions
        if str(p.get("status", "")).strip().lower() != "closed"
    ]

    for play in plays:
        readiness = play.get("activation_readiness")
        if not readiness:
            readiness = classify_play_readiness(play)
            play["activation_readiness"] = readiness

        bucket = readiness.get("bucket", "UNKNOWN")
        if bucket == "READY":
            ready_plays += 1
        elif bucket in {"WATCH", "WEAK"}:
            weak_plays += 1

        candidate = play.get("engine_candidate") or {}
        candidate_strategy = str(candidate.get("strategy", "")).strip().upper()
        play_direction = str(play.get("direction", "UNKNOWN")).strip().upper()

        if candidate_strategy and play_direction in {"CALL", "PUT"}:
            if candidate_strategy == play_direction:
                aligned_count += 1
            else:
                disagreement_count += 1

    for pos in open_positions:
        agreement_score = int((pos.get("system_agreement", {}) or {}).get("score", 0) or 0)
        health_score = int((pos.get("health", {}) or {}).get("score", 0) or 0)
        if agreement_score < 55 or health_score < 35:
            weak_open_positions += 1

    wins = int((analysis.get("totals", {}) or {}).get("wins", 0) or 0)
    losses = int((analysis.get("totals", {}) or {}).get("losses", 0) or 0)
    flat = int((analysis.get("totals", {}) or {}).get("flat", 0) or 0)

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

    priority_order = {
        "danger": 0,
        "warning": 1,
        "neutral": 2,
        "positive": 3,
    }
    alerts = sorted(alerts, key=lambda a: priority_order.get(a.get("level", "neutral"), 99))

    top_alert = alerts[0] if alerts else None

    return {
        "top_alert": top_alert,
        "alerts": alerts[:4],
    }


def build_admin_intelligence_summary(plays, positions, analysis):
    plays = plays or []
    positions = positions or []
    analysis = analysis or {}

    total_plays = len(plays)
    total_positions = len(positions)
    closed_positions = [
        p for p in positions
        if str(p.get("status", "")).strip().lower() == "closed"
    ]

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
        readiness = play.get("activation_readiness")
        if not readiness:
            readiness = classify_play_readiness(play)
            play["activation_readiness"] = readiness

        bucket = readiness.get("bucket", "UNKNOWN")
        readiness_score = int(readiness.get("score", 0) or 0)
        agreement = play.get("system_agreement", {}) or {}
        agreement_score = int(agreement.get("score", 0) or 0)
        conviction = str(play.get("conviction", "Medium")).strip()
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

        candidate_strategy = str((candidate or {}).get("strategy", "")).strip().upper()
        play_direction = str(play.get("direction", "UNKNOWN")).strip().upper()

        if candidate_strategy and play_direction in {"CALL", "PUT"}:
            if candidate_strategy == play_direction:
                aligned_count += 1
            else:
                disagreement_count += 1
                pattern = f"{play.get('symbol', 'UNKNOWN')} | {play_direction} vs {candidate_strategy}"
                disagreement_patterns[pattern] = disagreement_patterns.get(pattern, 0) + 1

        if strongest_play is None or readiness_score > strongest_play["activation_readiness"]["score"]:
            strongest_play = play

        if weakest_play is None or readiness_score < weakest_play["activation_readiness"]["score"]:
            weakest_play = play

        condition_label = " | ".join([
            str(market_context.get("regime", "UNKNOWN")).strip().upper(),
            str(market_context.get("breadth", "UNKNOWN")).strip().upper(),
            str(market_context.get("mode", "UNKNOWN")).strip().upper(),
        ])

        if bucket == "READY":
            condition_strength[condition_label] = condition_strength.get(condition_label, 0) + 1
        elif bucket in {"WATCH", "WEAK"}:
            condition_weakness[condition_label] = condition_weakness.get(condition_label, 0) + 1

    for pos in closed_positions:
        agreement = pos.get("system_agreement", {}) or {}
        agreement_score = int(agreement.get("score", 0) or 0)
        health = pos.get("health", {}) or {}
        health_score = int(health.get("score", 0) or 0)
        candidate = pos.get("engine_candidate")
        direction = str(pos.get("direction", "UNKNOWN")).strip().upper()
        candidate_strategy = str((candidate or {}).get("strategy", "")).strip().upper()

        archived_play_status = "without candidate" if not candidate else "with candidate"
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

        if archived_play_status == "without candidate" and outcome == "LOSS":
            pattern = f"{pos.get('symbol', 'UNKNOWN')} | no engine tracking"
            weakest_activation_patterns[pattern] = weakest_activation_patterns.get(pattern, 0) + 1

    trade_totals = analysis.get("totals", {}) or {}
    wins = int(trade_totals.get("wins", 0) or 0)
    losses = int(trade_totals.get("losses", 0) or 0)
    flat = int(trade_totals.get("flat", 0) or 0)

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

def _top_item(counts, fallback="Not enough data yet."):
        if not counts:
            return {"label": fallback, "count": 0}
        label, count = max(counts.items(), key=lambda item: item[1])
        return {"label": label, "count": count}

    strongest_condition = _top_item(condition_strength, "No strong condition cluster yet.")
    weakest_condition = _top_item(condition_weakness, "No weak condition cluster yet.")
    top_failure_cluster = _top_item(weakest_activation_patterns, "No failure cluster yet.")
    top_disagreement_cluster = _top_item(disagreement_patterns, "No disagreement cluster yet.")

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
            "score": strongest_play["activation_readiness"]["score"],
            "headline": strongest_play["activation_readiness"]["headline"],
        } if strongest_play else None,
        "weakest_play": {
            "symbol": weakest_play.get("symbol"),
            "score": weakest_play["activation_readiness"]["score"],
            "headline": weakest_play["activation_readiness"]["headline"],
        } if weakest_play else None,
        "coaching_cards": coaching_cards,
    }


def build_product_monitoring_summary(plays, positions, analysis):
    plays = plays or []
    positions = positions or []
    analysis = analysis or {}

    total_plays = len(plays)
    total_positions = len(positions)
    open_positions = [
        p for p in positions
        if str(p.get("status", "")).strip().lower() != "closed"
    ]
    closed_positions = [
        p for p in positions
        if str(p.get("status", "")).strip().lower() == "closed"
    ]

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
        readiness = play.get("activation_readiness")
        if not readiness:
            readiness = classify_play_readiness(play)
            play["activation_readiness"] = readiness

        bucket = readiness.get("bucket", "INACTIVE")
        readiness_buckets[bucket] = readiness_buckets.get(bucket, 0) + 1

        status = str(play.get("status", "Open")).strip().lower()
        thesis = str(play.get("thesis", "") or "").strip()
        notes = str(play.get("notes", "") or "").strip()
        conviction = str(play.get("conviction", "Medium")).strip().lower()
        agreement_score = int((play.get("system_agreement", {}) or {}).get("score", 0) or 0)
        health_score = int((play.get("health", {}) or {}).get("score", 0) or 0)

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
        agreement_score = int((pos.get("system_agreement", {}) or {}).get("score", 0) or 0)
        health_score = int((pos.get("health", {}) or {}).get("score", 0) or 0)

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

    wins = int((analysis.get("totals", {}) or {}).get("wins", 0) or 0)
    losses = int((analysis.get("totals", {}) or {}).get("losses", 0) or 0)
    flat = int((analysis.get("totals", {}) or {}).get("flat", 0) or 0)

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
        "body": "Not enough signal."
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


@app.route("/my-plays/<play_id>/archive", methods=["POST"])
def archive_my_play(play_id):
    archive_play(play_id)
    return redirect("/my-plays")


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


@app.route("/admin/intelligence")
def admin_intelligence_page():
    maybe_track_page_view("/admin/intelligence")

    plays = get_my_plays()
    for play in plays:
        if not play.get("activation_readiness"):
            play["activation_readiness"] = classify_play_readiness(play)

    positions = get_user_positions(include_closed=True)
    analysis = analyze_user_trades()

    admin_summary = build_admin_intelligence_summary(plays, positions, analysis)
    monitoring = build_product_monitoring_summary(plays, positions, analysis)
    surface_alerts = build_admin_surface_alerts(admin_summary=admin_summary, monitoring=monitoring)

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
            "surface_alerts": surface_alerts,
            "filter_key": filter_key,
            "spotlight_title": spotlight_title,
            "spotlight_note": spotlight_note,
            "spotlight_cards": spotlight_cards,
        }),
    )

    
@app.route("/signals/<symbol>")
@app.route("/symbol/<symbol>")
def signal_symbol_page(symbol: str):
    maybe_track_page_view(f"/signals/{symbol}")
    log_event("symbol_exposed", {
        "symbol": symbol,
        "source": "/signals",
    })
    track_symbol_click(symbol, source="/signals")

    detail = get_symbol_detail(symbol)
    return render_template_safe(
        "signal_symbol.html",
        **template_context(
            {
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


@app.route("/admin/product-monitoring")
def admin_product_monitoring_page():
    maybe_track_page_view("/admin/product-monitoring")

    plays = get_my_plays()
    for play in plays:
        if not play.get("activation_readiness"):
            play["activation_readiness"] = classify_play_readiness(play)

    positions = get_user_positions(include_closed=True)
    analysis = analyze_user_trades()

    monitoring = build_product_monitoring_summary(plays, positions, analysis)
    admin_summary = build_admin_intelligence_summary(plays, positions, analysis)
    surface_alerts = build_admin_surface_alerts(admin_summary=admin_summary, monitoring=monitoring)

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
            "surface_alerts": surface_alerts,
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
    filter_key = str(request.args.get("filter", "all") or "all").strip().lower()

    filtered_positions = positions
    filter_title = "All Open Positions"
    filter_note = "Showing your full live position layer."

    if filter_key == "weak":
        filtered_positions = [
            p for p in positions
            if int((p.get("system_agreement", {}) or {}).get("score", 0) or 0) < 55
            or int((p.get("health", {}) or {}).get("score", 0) or 0) < 35
        ]
        filter_title = "Weak Positions"
        filter_note = "Showing open positions that look weak by health or agreement."
    elif filter_key == "strong":
        filtered_positions = [
            p for p in positions
            if int((p.get("system_agreement", {}) or {}).get("score", 0) or 0) >= 75
            and int((p.get("health", {}) or {}).get("score", 0) or 0) >= 75
        ]
        filter_title = "Strong Positions"
        filter_note = "Showing open positions with stronger health and alignment."
    elif filter_key == "high_agreement":
        filtered_positions = [
            p for p in positions
            if int((p.get("system_agreement", {}) or {}).get("score", 0) or 0) >= 75
        ]
        filter_title = "High Agreement Positions"
        filter_note = "Showing positions with stronger system agreement."
    elif filter_key == "under_pressure":
        filtered_positions = [
            p for p in positions
            if str((p.get("health", {}) or {}).get("label", "")).strip().upper() in {"UNDER PRESSURE", "BROKEN"}
        ]
        filter_title = "Under Pressure Positions"
        filter_note = "Showing positions whose behavior is signaling pressure or damage."

    return render_template_safe(
        "my_positions.html",
        **template_context({
            "positions": filtered_positions,
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

    update_user_position(
        position_id=position_id,
        stop=stop,
        target=target,
        conviction=conviction,
        notes=notes,
        status=status,
    )
    return redirect(f"/my-positions/{position_id}")


@app.route("/my-positions/<position_id>/close", methods=["POST"])
def close_my_position(position_id):
    close_user_position(position_id)
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


@app.route("/my-positions/analyze")
def analyze_my_trades_page():
    maybe_track_page_view("/my-positions/analyze")
    analysis = analyze_user_trades()
    return render_template_safe(
        "my_trade_analysis.html",
        **template_context({
            "analysis": analysis,
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
    maybe_track_page_view("/analytics/performance")
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

    if status in {"open", "watching"}:
        readiness_score += 10
        reasons.append("play is still active")
    else:
        reasons.append("play is not in an active state")

    if health_score >= 75:
        readiness_score += 30
        reasons.append("health is strong")
    elif health_score >= 55:
        readiness_score += 15
        reasons.append("health is stable")
    elif health_score >= 35:
        readiness_score += 5
        reasons.append("health is mixed")
    else:
        readiness_score -= 25
        reasons.append("health is weak")

    if agreement_score >= 75:
        readiness_score += 30
        reasons.append("system agreement is strong")
    elif agreement_score >= 55:
        readiness_score += 15
        reasons.append("system agreement is usable")
    elif agreement_score >= 35:
        readiness_score += 5
        reasons.append("system agreement is mixed")
    else:
        readiness_score -= 25
        reasons.append("system agreement is weak")

    if candidate:
        readiness_score += 10
        reasons.append("engine is actively tracking the symbol")
    else:
        readiness_score -= 10
        reasons.append("engine is not actively tracking the symbol")

    if conviction == "high":
        readiness_score += 5
        reasons.append("you have high conviction")
    elif conviction == "medium":
        readiness_score += 2
        reasons.append("you have moderate conviction")

    if health_label in {"BROKEN", "UNDER PRESSURE"}:
        readiness_score -= 15
        reasons.append("behavior is under pressure")

    if any("counter-trend" in str(line).lower() for line in feedback):
        readiness_score -= 10
        reasons.append("system feedback flags counter-trend behavior")

    if any("defensive market posture" in str(line).lower() for line in feedback):
        readiness_score -= 10
        reasons.append("system feedback flags a defensive environment conflict")

    readiness_score = max(0, min(100, readiness_score))

    if status not in {"open", "watching"}:
        bucket = "INACTIVE"
        headline = "Not eligible for activation"
        summary = "This play is not in an active working state right now."
    elif readiness_score >= 80:
        bucket = "READY"
        headline = "Ready to activate"
        summary = "This idea has enough structural support to be treated like a serious candidate for live management."
    elif readiness_score >= 60:
        bucket = "CLOSE"
        headline = "Close, but not fully proven"
        summary = "This idea has some real support, but it still needs cleaner evidence before it deserves full activation."
    elif readiness_score >= 40:
        bucket = "WATCH"
        headline = "Watch, don’t rush"
        summary = "This play is not dead, but it is not strong enough to promote with confidence."
    else:
        bucket = "WEAK"
        headline = "Weak setup"
        summary = "This idea does not currently deserve activation. The evidence is too soft or too conflicted."

    return {
        "score": readiness_score,
        "bucket": bucket,
        "headline": headline,
        "summary": summary,
        "reasons": reasons[:4],
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

    if ready_count > 0:
        headline = "You have plays that may deserve activation."
        summary = "Some ideas are showing strong enough behavior and agreement to be considered real candidates."
    elif close_count > 0:
        headline = "Some ideas are getting warmer."
        summary = "A few plays are close, but still need cleaner confirmation before they deserve live management."
    elif total == 0:
        headline = "No plays yet."
        summary = "Start building your idea book so the system can pressure-test your setups."
    else:
        headline = "Your idea book needs more filtering."
        summary = "Most current plays still look more watchable than actionable."

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
        "strongest_play": {
            "symbol": strongest_play.get("symbol"),
            "score": strongest_play["activation_readiness"]["score"],
            "headline": strongest_play["activation_readiness"]["headline"],
        } if strongest_play else None,
        "weakest_play": {
            "symbol": weakest_play.get("symbol"),
            "score": weakest_play["activation_readiness"]["score"],
            "headline": weakest_play["activation_readiness"]["headline"],
        } if weakest_play else None,
    }


@app.route("/my-plays")
def my_plays_page():
    maybe_track_page_view("/my-plays")

    plays = get_my_plays()
    plays_summary = build_my_plays_summary(plays)

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
        filter_note = "Showing ideas that are getting warmer but still need cleaner confirmation."
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
        add_play(
            symbol=symbol,
            entry=entry,
            stop=stop,
            target=target,
            conviction=conviction,
            thesis=thesis,
            notes=notes,
        )
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
    return render_template_safe(
        "my_play_detail.html",
        **template_context({
            "play": play,
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
        update_play(
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
        return redirect(f"/my-plays/{play_id}")
    except ValueError as e:
        play = get_play(play_id)
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

    if not position:
        return render_template_safe(
            "my_play_detail.html",
            **template_context({
                "play": play,
                "error": "Could not activate this play.",
            }),
        )

    return redirect("/my-positions")

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

    # First: rich trade detail records
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

        for row in enriched[:5]:
            if row.get("rejection_reason"):
                track_rejection_interest(
                    row.get("symbol", "UNKNOWN"),
                    source="/why-this-trade",
                )

    # Second: approved-not-selected records from candidate_log
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

    return render_template_safe(
        "why_this_trade.html",
        **template_context({
            "trades": enriched,
            "featured_trades": featured_trades,
        }),
    )

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
    positions = get_positions_with_intelligence()
    proof = performance_summary()
    snapshot = get_dashboard_snapshot()
    system = get_system_state()

    plays = get_my_plays()
    for play in plays:
        if not play.get("activation_readiness"):
            play["activation_readiness"] = classify_play_readiness(play)

    analysis = analyze_user_trades()
    admin_alerts = build_admin_alerts(plays, positions, analysis)

    return render_template_safe(
        "admin.html",
        **template_context({
            "positions": positions,
            "signals": get_signals(),
            "users": load_json("data/users.json", []),
            "metrics": metrics,
            "proof": proof,
            "snapshot": snapshot,
            "system": system,
            "admin_alerts": admin_alerts,
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
