import json
from pathlib import Path
from datetime import datetime

PLAYS_FILE = "data/my_plays.json"
USER_POSITIONS_FILE = "data/user_positions.json"
TOP_CANDIDATES_FILE = "data/top_candidates.json"
SYSTEM_STATUS_FILE = "data/system_status.json"


def _load(path, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def build_play_id(symbol):
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{symbol.upper()}-{ts}"


def load_my_plays():
    rows = _load(PLAYS_FILE, [])
    return rows if isinstance(rows, list) else []


def save_my_plays(rows):
    _save(PLAYS_FILE, rows)


def load_user_positions():
    rows = _load(USER_POSITIONS_FILE, [])
    return rows if isinstance(rows, list) else []


def save_user_positions(rows):
    _save(USER_POSITIONS_FILE, rows)


def latest_market_context():
    status = _load(SYSTEM_STATUS_FILE, {})
    if not isinstance(status, dict):
        status = {}
    return {
        "mode": status.get("mode", "UNKNOWN"),
        "breadth": status.get("breadth", "UNKNOWN"),
        "regime": status.get("regime", "UNKNOWN"),
        "volatility_state": status.get("volatility_state", "UNKNOWN"),
    }


def load_top_candidates():
    rows = _load(TOP_CANDIDATES_FILE, [])
    return rows if isinstance(rows, list) else []


def get_candidate_for_symbol(symbol):
    symbol = str(symbol or "").upper()
    for row in load_top_candidates():
        if str(row.get("symbol", "")).upper() == symbol:
            return row
    return None


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


def determine_direction(play):
    entry = _safe_float(play.get("entry"))
    target = _safe_float(play.get("target"))
    if target > entry:
        return "CALL"
    if target < entry:
        return "PUT"
    return "NEUTRAL"


def validate_play_inputs(entry, stop, target):
    entry = _safe_float(entry)
    stop = _safe_float(stop)
    target = _safe_float(target)

    if entry <= 0:
        raise ValueError("Entry must be greater than 0.")
    if stop <= 0:
        raise ValueError("Stop must be greater than 0.")
    if target <= 0:
        raise ValueError("Target must be greater than 0.")
    if stop == entry:
        raise ValueError("Stop cannot equal entry.")
    if target == entry:
        raise ValueError("Target cannot equal entry.")

    bullish = target > entry and stop < entry
    bearish = target < entry and stop > entry

    if not bullish and not bearish:
        raise ValueError(
            "Your setup must be coherent: bullish plays need stop below entry and target above entry; bearish plays need stop above entry and target below entry."
        )

    return {
        "entry": entry,
        "stop": stop,
        "target": target,
    }


def determine_play_health(play):
    entry = _safe_float(play.get("entry"))
    stop = _safe_float(play.get("stop"))
    target = _safe_float(play.get("target"))
    current = _safe_float(play.get("current_price", entry))

    if not entry:
        return {
            "score": 50,
            "label": "UNSET",
            "status": "Needs setup",
            "note": "Entry has not been fully defined yet.",
        }

    if current <= 0:
        current = entry

    if determine_direction(play) == "CALL":
        if stop and current <= stop:
            return {
                "score": 10,
                "label": "BROKEN",
                "status": "Below stop",
                "note": "Price has moved through the stop area.",
            }
        if target and current >= target:
            return {
                "score": 95,
                "label": "WINNING",
                "status": "At target",
                "note": "Price has reached or exceeded the target area.",
            }
        if stop and current < entry:
            return {
                "score": 35,
                "label": "UNDER PRESSURE",
                "status": "Needs review",
                "note": "Price is below entry but has not broken the stop.",
            }
        if target and current > entry:
            return {
                "score": 75,
                "label": "WORKING",
                "status": "In progress",
                "note": "Price is moving in the intended direction.",
            }
    else:
        if stop and current >= stop:
            return {
                "score": 10,
                "label": "BROKEN",
                "status": "Above stop",
                "note": "Price has moved through the stop area.",
            }
        if target and current <= target:
            return {
                "score": 95,
                "label": "WINNING",
                "status": "At target",
                "note": "Price has reached or exceeded the target area.",
            }
        if stop and current > entry:
            return {
                "score": 35,
                "label": "UNDER PRESSURE",
                "status": "Needs review",
                "note": "Price is above entry but has not broken the stop.",
            }
        if target and current < entry:
            return {
                "score": 75,
                "label": "WORKING",
                "status": "In progress",
                "note": "Price is moving in the intended direction.",
            }

    return {
        "score": 55,
        "label": "EARLY",
        "status": "Watching",
        "note": "The play is active but has not developed much yet.",
    }


def build_play_feedback(play, market_context=None, candidate=None):
    feedback = []
    market_context = market_context or {}

    mode = market_context.get("mode", "UNKNOWN")
    breadth = market_context.get("breadth", "UNKNOWN")
    regime = market_context.get("regime", "UNKNOWN")
    direction = determine_direction(play)

    if mode == "DEFENSIVE_BEAR" and direction == "CALL":
        feedback.append("This play is pushing against a defensive market posture.")
    elif mode == "DEFENSIVE_BEAR" and direction == "PUT":
        feedback.append("This play aligns with defensive market positioning.")
    elif mode == "AGGRESSIVE_BULL" and direction == "CALL":
        feedback.append("This play aligns with aggressive bullish conditions.")
    elif mode == "AGGRESSIVE_BULL" and direction == "PUT":
        feedback.append("This play is counter-trend relative to bullish conditions.")

    if breadth == "BULLISH":
        feedback.append("Market breadth is supportive of upside participation.")
    elif breadth == "BEARISH":
        feedback.append("Market breadth is weak and may limit upside follow-through.")

    if regime == "BEAR_TREND":
        feedback.append("The broader regime remains bearish, so upside plays may require stronger confirmation.")
    elif regime == "BULL_TREND":
        feedback.append("The broader regime is bullish, which can support continuation ideas.")

    if candidate:
        feedback.append(
            f"The engine is actively tracking this symbol with a score of {candidate.get('score', 'N/A')} and {candidate.get('confidence', 'N/A')} confidence."
        )
        if candidate.get("strategy"):
            feedback.append(f"The engine currently leans {candidate.get('strategy')} on this symbol.")
    else:
        feedback.append("This symbol is not currently showing up as a top engine candidate.")

    if not feedback:
        feedback.append("No strong system feedback available yet.")

    return feedback


def build_play_agreement(play, market_context=None, candidate=None):
    market_context = market_context or {}
    direction = determine_direction(play)
    score = 50
    reasons = []

    mode = market_context.get("mode", "UNKNOWN")
    breadth = market_context.get("breadth", "UNKNOWN")
    regime = market_context.get("regime", "UNKNOWN")

    if direction == "CALL":
        if breadth == "BULLISH":
            score += 10
            reasons.append("bullish breadth supports upside")
        if regime == "BULL_TREND":
            score += 15
            reasons.append("bull trend supports continuation")
        if mode == "DEFENSIVE_BEAR":
            score -= 20
            reasons.append("defensive market mode works against upside")
    elif direction == "PUT":
        if breadth == "BEARISH":
            score += 10
            reasons.append("bearish breadth supports downside")
        if regime == "BEAR_TREND":
            score += 15
            reasons.append("bear trend supports downside")
        if mode == "AGGRESSIVE_BULL":
            score -= 20
            reasons.append("aggressive bull mode works against downside")

    if candidate:
        candidate_score = _safe_float(candidate.get("score"))
        score += min(20, int(candidate_score / 15))
        reasons.append("engine is actively tracking this symbol")

        candidate_strategy = str(candidate.get("strategy", "")).upper()
        if candidate_strategy and candidate_strategy == direction:
            score += 10
            reasons.append("engine direction aligns with your play")
        elif candidate_strategy and direction != "NEUTRAL":
            score -= 10
            reasons.append("engine direction conflicts with your play")
    else:
        score -= 10
        reasons.append("symbol is not in current top engine candidates")

    score = max(0, min(100, score))

    if score >= 75:
        label = "HIGH AGREEMENT"
    elif score >= 55:
        label = "MODERATE AGREEMENT"
    elif score >= 35:
        label = "MIXED"
    else:
        label = "LOW AGREEMENT"

    return {
        "score": score,
        "label": label,
        "reasons": reasons,
    }


def build_behavior_risk_summary_from_analysis(analysis):
    analysis = analysis or {}
    behavior_summary = analysis.get("behavior_summary", {}) or {}
    counts = behavior_summary.get("counts", {}) or {}

    against_engine = int(counts.get("against_engine", 0) or 0)
    high_conviction_no_thesis = int(counts.get("high_conviction_no_thesis", 0) or 0)
    late_edit = int(counts.get("late_edit", 0) or 0)
    late_weak_close = int(counts.get("late_weak_close", 0) or 0)
    post_loss_creation = int(counts.get("post_loss_creation", 0) or 0)

    total_flags = (
        against_engine
        + high_conviction_no_thesis
        + late_edit
        + late_weak_close
        + post_loss_creation
    )

    cards = []

    if against_engine > 0:
        cards.append({
            "headline": "Against-engine behavior",
            "body": f"{against_engine} archived trade(s) show against-engine activation behavior.",
        })

    if high_conviction_no_thesis > 0:
        cards.append({
            "headline": "Confidence without structure",
            "body": f"{high_conviction_no_thesis} archived trade(s) carried high conviction without a written thesis.",
        })

    if late_edit > 0:
        cards.append({
            "headline": "Reactive editing",
            "body": f"{late_edit} archived trade(s) show editing after weakness was already visible.",
        })

    if late_weak_close > 0:
        cards.append({
            "headline": "Late weak closes",
            "body": f"{late_weak_close} archived trade(s) appear to have been closed after weakness was already obvious.",
        })

    if post_loss_creation > 0:
        cards.append({
            "headline": "Post-loss re-entry behavior",
            "body": f"{post_loss_creation} archived trade(s) may have been created too soon after a loss.",
        })

    if total_flags == 0:
        headline = "Behavior risk looks contained."
        summary = "No major recurring behavior leak is standing out."
    elif late_weak_close + late_edit >= max(1, against_engine):
        headline = "Management behavior is the bigger leak."
        summary = "Late edits and late closes are hurting you more than idea disagreement."
    elif against_engine >= max(1, late_edit + late_weak_close):
        headline = "Directional disagreement is the bigger leak."
        summary = "Fighting the system is costing more than trade management."
    else:
        headline = "Multiple behavior leaks are active."
        summary = "More than one discipline issue is showing up."

    return {
        "headline": headline,
        "summary": summary,
        "counts": counts,
        "cards": cards,
    }


def build_behavior_priority_engine(analysis):
    analysis = analysis or {}
    behavior_summary = analysis.get("behavior_summary", {}) or {}
    counts = behavior_summary.get("counts", {}) or {}
    totals = analysis.get("totals", {}) or {}

    wins = int(totals.get("wins", 0) or 0)
    losses = int(totals.get("losses", 0) or 0)
    archived = int(totals.get("archived", 0) or 0)

    against_engine = int(counts.get("against_engine", 0) or 0)
    high_conviction_no_thesis = int(counts.get("high_conviction_no_thesis", 0) or 0)
    late_edit = int(counts.get("late_edit", 0) or 0)
    late_weak_close = int(counts.get("late_weak_close", 0) or 0)
    post_loss_creation = int(counts.get("post_loss_creation", 0) or 0)

    loss_multiplier = 1.0
    if losses > wins:
        loss_multiplier = 1.5
    elif losses == wins and losses > 0:
        loss_multiplier = 1.2

    items = []

    if late_weak_close > 0:
        base = late_weak_close * 4
        impact_score = round(base * loss_multiplier, 1)
        items.append({
            "key": "late_weak_close",
            "headline": "Stop letting weak trades drag on",
            "body": f"{late_weak_close} archived trade(s) were closed after weakness was already obvious.",
            "severity_score": base,
            "impact_score": impact_score,
            "damage_type": "Exit discipline leak",
            "fix": "Tighten exit discipline earlier. Weakness should trigger action before deterioration turns into damage.",
        })

    if late_edit > 0:
        base = late_edit * 3
        impact_score = round(base * loss_multiplier, 1)
        items.append({
            "key": "late_edit",
            "headline": "Stop editing after the market already voted",
            "body": f"{late_edit} archived trade(s) were edited after weakness was already visible.",
            "severity_score": base,
            "impact_score": impact_score,
            "damage_type": "Reactive management leak",
            "fix": "Make earlier decisions. Edits should support a plan, not rescue a broken one.",
        })

    if against_engine > 0:
        base = against_engine * 3
        impact_score = round(base * loss_multiplier, 1)
        items.append({
            "key": "against_engine",
            "headline": "You are fighting the engine too often",
            "body": f"{against_engine} archived trade(s) show against-engine activation behavior.",
            "severity_score": base,
            "impact_score": impact_score,
            "damage_type": "Alignment leak",
            "fix": "Raise the standard for discretionary disagreement. If you fight the system, the proof needs to be stronger.",
        })

    if high_conviction_no_thesis > 0:
        base = high_conviction_no_thesis * 2
        impact_score = round(base * loss_multiplier, 1)
        items.append({
            "key": "high_conviction_no_thesis",
            "headline": "Your conviction needs structure",
            "body": f"{high_conviction_no_thesis} archived trade(s) carried high conviction without a written thesis.",
            "severity_score": base,
            "impact_score": impact_score,
            "damage_type": "Decision structure leak",
            "fix": "Do not allow high conviction without a written reason. Confidence should be documented before risk is taken.",
        })

    if post_loss_creation > 0:
        base = post_loss_creation * 2
        impact_score = round(base * loss_multiplier, 1)
        items.append({
            "key": "post_loss_creation",
            "headline": "Watch emotional re-entry after losses",
            "body": f"{post_loss_creation} archived trade(s) may have been created too soon after a loss.",
            "severity_score": base,
            "impact_score": impact_score,
            "damage_type": "Emotional flow leak",
            "fix": "Slow down after losses. A new trade should come from a setup, not from emotional recoil.",
        })

    items = sorted(
        items,
        key=lambda x: (x["impact_score"], x["severity_score"]),
        reverse=True,
    )

    if not items:
        return {
            "headline": "No major behavior threat is dominating right now.",
            "summary": "Your archived trade set is not showing a loud recurring discipline failure.",
            "top_fix": None,
            "items": [],
            "totals": {
                "archived": archived,
                "wins": wins,
                "losses": losses,
            },
        }

    top = items[0]

    if top["key"] in {"late_edit", "late_weak_close"}:
        summary = "The strongest damage source is trade management after weakness appears."
    elif top["key"] == "against_engine":
        summary = "The strongest damage source is directional disagreement with the system."
    elif top["key"] == "high_conviction_no_thesis":
        summary = "The strongest damage source is confidence without written structure."
    elif top["key"] == "post_loss_creation":
        summary = "The strongest damage source is emotional re-entry after losses."
    else:
        summary = "The strongest damage source is a recurring discipline leak."

    return {
        "headline": "Behavior priority engine is active.",
        "summary": summary,
        "top_fix": top,
        "items": items[:5],
        "totals": {
            "archived": archived,
            "wins": wins,
            "losses": losses,
        },
    }


def analyze_user_trades():
    positions = get_user_positions(include_closed=True)
    archived = [
        p for p in positions
        if str(p.get("status", "")).lower() == "closed"
    ]

    if not archived:
        return {
            "totals": {"archived": 0, "wins": 0, "losses": 0, "flat": 0},
            "direction_counts": {},
            "conviction_counts": {},
            "average_health": 0,
            "insights": ["No archived trades yet."],
            "behavior_summary": {
                "counts": {},
                "cards": ["No archived trades yet."],
            },
            "trades": [],
        }

    wins = 0
    losses = 0
    flat = 0
    total_health = 0
    direction_counts = {}
    conviction_counts = {}
    enriched = []

    for pos in archived:
        outcome = classify_trade_outcome(pos)
        health_score = int((pos.get("health", {}) or {}).get("score", 0) or 0)

        if outcome == "WIN":
            wins += 1
        elif outcome == "LOSS":
            losses += 1
        else:
            flat += 1

        direction = pos.get("direction", "UNKNOWN")
        conviction = pos.get("conviction", "Unknown")
        direction_counts[direction] = direction_counts.get(direction, 0) + 1
        conviction_counts[conviction] = conviction_counts.get(conviction, 0) + 1
        total_health += health_score

        row = dict(pos)
        row["outcome"] = outcome
        row["lesson"] = build_trade_lesson(pos)
        row["behavior_flags"] = build_trade_behavior_flags(pos)
        row["behavior_coaching"] = build_behavior_coaching_line(pos, row["behavior_flags"])
        enriched.append(row)

    avg_health = round(total_health / len(archived), 1)

    insights = []
    if wins > losses:
        insights.append("You are net positive on archived trades, but that does not excuse weak process on the bad ones.")
    elif losses > wins:
        insights.append("Your archived losses are outweighing your wins. Entry quality and alignment need to get stricter.")
    else:
        insights.append("Your results are balanced, which usually means the edge is still too soft or inconsistent.")

    if avg_health < 40:
        insights.append("You tend to close trades after they have already weakened badly. That is a management problem, not just a market problem.")
    elif avg_health > 70:
        insights.append("You are generally exiting from stronger states, which suggests better discipline on closes.")

    behavior_summary = build_behavior_habit_summary(enriched)

    return {
        "totals": {
            "archived": len(archived),
            "wins": wins,
            "losses": losses,
            "flat": flat,
        },
        "direction_counts": direction_counts,
        "conviction_counts": conviction_counts,
        "average_health": avg_health,
        "insights": insights,
        "behavior_summary": behavior_summary,
        "trades": enriched,
    }


def enrich_play(play):
    row = dict(play)
    row["symbol"] = str(row.get("symbol", "")).upper()
    row["entry"] = _safe_float(row.get("entry"))
    row["stop"] = _safe_float(row.get("stop"))
    row["target"] = _safe_float(row.get("target"))
    row["current_price"] = _safe_float(row.get("current_price", row["entry"]))
    row["conviction"] = row.get("conviction", "Medium")
    row["status"] = row.get("status", "Open")
    row["direction"] = determine_direction(row)
    row["health"] = determine_play_health(row)

    market_context = latest_market_context()
    candidate = get_candidate_for_symbol(row["symbol"])

    row["market_context"] = market_context
    row["engine_candidate"] = candidate
    row["system_feedback"] = build_play_feedback(row, market_context, candidate)
    row["system_agreement"] = build_play_agreement(row, market_context, candidate)
    return row


def get_my_plays():
    return [enrich_play(p) for p in load_my_plays()]


def add_play(symbol, entry, stop, target, conviction="Medium", thesis="", notes=""):
    symbol = str(symbol or "").strip().upper()
    if not symbol:
        raise ValueError("Symbol is required.")

    validated = validate_play_inputs(entry, stop, target)
    plays = load_my_plays()

    play = {
        "play_id": build_play_id(symbol),
        "symbol": symbol,
        "entry": validated["entry"],
        "stop": validated["stop"],
        "target": validated["target"],
        "current_price": validated["entry"],
        "conviction": conviction or "Medium",
        "thesis": thesis or "",
        "notes": notes or "",
        "status": "Open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    plays.append(play)
    save_my_plays(plays)
    return enrich_play(play)


def update_play(play_id, symbol=None, entry=None, stop=None, target=None, conviction=None, thesis=None, notes=None, status=None):
    plays = load_my_plays()
    updated = None

    for play in plays:
        if str(play.get("play_id")) != str(play_id):
            continue

        new_symbol = str(symbol or play.get("symbol", "")).strip().upper()
        new_entry = entry if entry not in {None, ""} else play.get("entry")
        new_stop = stop if stop not in {None, ""} else play.get("stop")
        new_target = target if target not in {None, ""} else play.get("target")
        validated = validate_play_inputs(new_entry, new_stop, new_target)

        play["symbol"] = new_symbol
        play["entry"] = validated["entry"]
        play["stop"] = validated["stop"]
        play["target"] = validated["target"]

        if conviction is not None:
            play["conviction"] = conviction
        if thesis is not None:
            play["thesis"] = thesis
        if notes is not None:
            play["notes"] = notes
        if status is not None:
            play["status"] = status

        play["updated_at"] = datetime.now().isoformat()
        updated = play
        break

    save_my_plays(plays)
    return enrich_play(updated) if updated else None


def archive_play(play_id):
    return update_play(play_id, status="Archived")


def get_play(play_id):
    plays = load_my_plays()
    for play in plays:
        if str(play.get("play_id")) == str(play_id):
            return enrich_play(play)
    return None


def add_user_position_from_play(play_id):
    play = get_play(play_id)
    if not play:
        return None

    positions = load_user_positions()
    for pos in positions:
        if str(pos.get("play_id")) == str(play_id) and str(pos.get("status", "Open")).lower() == "open":
            return enrich_user_position(pos)

    position = {
        "position_id": f"POS-{play_id}",
        "play_id": play_id,
        "symbol": play.get("symbol"),
        "entry": play.get("entry"),
        "stop": play.get("stop"),
        "target": play.get("target"),
        "current_price": play.get("current_price"),
        "conviction": play.get("conviction"),
        "thesis": play.get("thesis"),
        "notes": play.get("notes"),
        "status": "Open",
        "opened_at": datetime.now().isoformat(),
    }

    positions.append(position)
    save_user_positions(positions)
    return enrich_user_position(position)


def enrich_user_position(position):
    row = dict(position)
    row["symbol"] = str(row.get("symbol", "")).upper()
    row["entry"] = _safe_float(row.get("entry"))
    row["stop"] = _safe_float(row.get("stop"))
    row["target"] = _safe_float(row.get("target"))
    row["current_price"] = _safe_float(row.get("current_price", row["entry"]))
    row["conviction"] = row.get("conviction", "Medium")
    row["status"] = row.get("status", "Open")
    row["health"] = determine_play_health(row)
    row["direction"] = determine_direction(row)

    market_context = latest_market_context()
    candidate = get_candidate_for_symbol(row.get("symbol"))

    row["market_context"] = market_context
    row["engine_candidate"] = candidate
    row["system_feedback"] = build_play_feedback(row, market_context, candidate)
    row["system_agreement"] = build_play_agreement(row, market_context, candidate)
    return row


def get_user_positions(include_closed=False):
    positions = [enrich_user_position(p) for p in load_user_positions()]
    if include_closed:
        return positions
    return [
        p for p in positions
        if str(p.get("status", "Open")).lower() != "closed"
    ]


def get_user_position(position_id):
    positions = load_user_positions()
    for position in positions:
        if str(position.get("position_id")) == str(position_id):
            return enrich_user_position(position)
    return None


def update_user_position(position_id, stop=None, target=None, notes=None, conviction=None, status=None):
    positions = load_user_positions()
    updated = None

    for position in positions:
        if str(position.get("position_id")) != str(position_id):
            continue

        if stop not in {None, ""}:
            position["stop"] = _safe_float(stop)
        if target not in {None, ""}:
            position["target"] = _safe_float(target)
        if notes is not None:
            position["notes"] = notes
        if conviction is not None:
            position["conviction"] = conviction
        if status is not None:
            position["status"] = status

        updated = position
        break

    save_user_positions(positions)
    return enrich_user_position(updated) if updated else None


def close_user_position(position_id):
    positions = load_user_positions()
    closed = None

    for position in positions:
        if str(position.get("position_id")) != str(position_id):
            continue
        position["status"] = "Closed"
        position["closed_at"] = datetime.now().isoformat()
        closed = position
        break

    save_user_positions(positions)
    return enrich_user_position(closed) if closed else None


def classify_trade_outcome(position):
    entry = _safe_float(position.get("entry"))
    current = _safe_float(position.get("current_price", entry))
    direction = determine_direction(position)

    if not entry:
        return "UNKNOWN"

    if direction == "CALL":
        if current > entry:
            return "WIN"
        if current < entry:
            return "LOSS"
    elif direction == "PUT":
        if current < entry:
            return "WIN"
        if current > entry:
            return "LOSS"

    return "FLAT"


def _agreement_bucket(score):
    score = _safe_int(score)
    if score >= 75:
        return "High"
    if score >= 55:
        return "Moderate"
    if score >= 35:
        return "Mixed"
    return "Low"


def _health_bucket(score):
    score = _safe_int(score)
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Stable"
    if score >= 35:
        return "Weakening"
    return "Broken"


def _safe_upper(value, default="UNKNOWN"):
    text = str(value or "").strip().upper()
    return text if text else default


def _build_pattern_label(outcome, agreement_bucket, conviction, direction, mode, breadth):
    return " | ".join([
        f"{outcome}",
        f"{agreement_bucket} agreement",
        f"{conviction} conviction",
        f"{direction}",
        f"{mode}",
        f"{breadth}",
    ])


def _top_count_item(counts, fallback_label="Not enough data yet."):
    if not counts:
        return {
            "label": fallback_label,
            "count": 0,
        }
    label, count = max(counts.items(), key=lambda item: item[1])
    return {
        "label": label,
        "count": count,
    }


def _build_repeat_and_stop_behaviors(enriched):
    repeat_counts = {}
    stop_counts = {}

    for trade in enriched:
        outcome = trade.get("outcome", "UNKNOWN")
        agreement_bucket = _agreement_bucket((trade.get("system_agreement", {}) or {}).get("score", 0))
        conviction = str(trade.get("conviction", "Unknown"))
        direction = str(trade.get("direction", "UNKNOWN"))
        market_context = trade.get("market_context", {}) or {}
        mode = _safe_upper(market_context.get("mode"))
        breadth = _safe_upper(market_context.get("breadth"))

        label = _build_pattern_label(outcome, agreement_bucket, conviction, direction, mode, breadth)

        if outcome == "WIN":
            repeat_counts[label] = repeat_counts.get(label, 0) + 1
        elif outcome == "LOSS":
            stop_counts[label] = stop_counts.get(label, 0) + 1

    repeat_top = _top_count_item(repeat_counts, "No repeat behavior identified yet.")
    stop_top = _top_count_item(stop_counts, "No stop behavior identified yet.")

    repeat_summary = (
        f"Your most repeatable winning pattern so far is: {repeat_top['label']}."
        if repeat_top["count"] > 0
        else repeat_top["label"]
    )
    stop_summary = (
        f"Your most common losing pattern so far is: {stop_top['label']}."
        if stop_top["count"] > 0
        else stop_top["label"]
    )

    return {
        "repeat": {
            "headline": "What to Repeat",
            "label": repeat_top["label"],
            "count": repeat_top["count"],
            "summary": repeat_summary,
        },
        "stop": {
            "headline": "What to Stop",
            "label": stop_top["label"],
            "count": stop_top["count"],
            "summary": stop_summary,
        },
    }


def _build_condition_summary(enriched):
    condition_counts = {}
    winning_conditions = {}
    losing_conditions = {}

    for trade in enriched:
        market_context = trade.get("market_context", {}) or {}
        regime = _safe_upper(market_context.get("regime"))
        breadth = _safe_upper(market_context.get("breadth"))
        mode = _safe_upper(market_context.get("mode"))

        label = f"{regime} | {breadth} | {mode}"
        condition_counts[label] = condition_counts.get(label, 0) + 1

        outcome = trade.get("outcome", "UNKNOWN")
        if outcome == "WIN":
            winning_conditions[label] = winning_conditions.get(label, 0) + 1
        elif outcome == "LOSS":
            losing_conditions[label] = losing_conditions.get(label, 0) + 1

    most_seen = _top_count_item(condition_counts, "No condition pattern identified yet.")
    best = _top_count_item(winning_conditions, "No best-condition pattern identified yet.")
    worst = _top_count_item(losing_conditions, "No weak-condition pattern identified yet.")

    return {
        "most_seen": most_seen,
        "best": best,
        "worst": worst,
        "summary": [
            f"Most seen market backdrop: {most_seen['label']}." if most_seen["count"] > 0 else most_seen["label"],
            f"Best condition cluster: {best['label']}." if best["count"] > 0 else best["label"],
            f"Weakest condition cluster: {worst['label']}." if worst["count"] > 0 else worst["label"],
        ],
    }


def _build_alignment_summary(enriched):
    high_wins = 0
    high_losses = 0
    low_wins = 0
    low_losses = 0

    for trade in enriched:
        outcome = trade.get("outcome", "UNKNOWN")
        agreement_score = _safe_int((trade.get("system_agreement", {}) or {}).get("score", 0))

        if agreement_score >= 75 and outcome == "WIN":
            high_wins += 1
        elif agreement_score >= 75 and outcome == "LOSS":
            high_losses += 1
        elif agreement_score < 55 and outcome == "WIN":
            low_wins += 1
        elif agreement_score < 55 and outcome == "LOSS":
            low_losses += 1

    if high_wins > high_losses:
        headline = "Alignment is helping when you respect it."
        summary = "Your better trades are showing up when agreement is strong. The system is not random noise for you."
    elif low_losses > low_wins:
        headline = "You are paying for misalignment."
        summary = "A meaningful share of your losses is coming from trades that lacked strong support from the system."
    else:
        headline = "Your alignment edge is still mixed."
        summary = "The system is giving signals, but your results are not yet consistently separating strong alignment from weak alignment."

    return {
        "headline": headline,
        "summary": summary,
        "stats": {
            "high_agreement_wins": high_wins,
            "high_agreement_losses": high_losses,
            "low_agreement_wins": low_wins,
            "low_agreement_losses": low_losses,
        },
    }


def _build_conviction_summary(enriched):
    high_conviction_wins = 0
    high_conviction_losses = 0
    low_conviction_wins = 0
    low_conviction_losses = 0

    for trade in enriched:
        conviction = str(trade.get("conviction", "Unknown")).strip().lower()
        outcome = trade.get("outcome", "UNKNOWN")

        if conviction == "high" and outcome == "WIN":
            high_conviction_wins += 1
        elif conviction == "high" and outcome == "LOSS":
            high_conviction_losses += 1
        elif conviction == "low" and outcome == "WIN":
            low_conviction_wins += 1
        elif conviction == "low" and outcome == "LOSS":
            low_conviction_losses += 1

    if high_conviction_losses > high_conviction_wins:
        headline = "High conviction is sometimes turning into force."
        summary = "Your high-conviction losses suggest confidence is occasionally outrunning alignment."
    elif high_conviction_wins > high_conviction_losses:
        headline = "High conviction is earning its keep."
        summary = "Your stronger-conviction trades are producing enough wins to justify real trust when the setup is there."
    elif low_conviction_wins > low_conviction_losses:
        headline = "You may be under-trusting some valid ideas."
        summary = "Some of your wins are coming from lower-conviction trades, which suggests hesitation may be muting your best instincts."
    else:
        headline = "Your conviction profile is still muddy."
        summary = "Conviction is showing up, but it is not yet clearly separating your better decisions from your weaker ones."

    return {
        "headline": headline,
        "summary": summary,
        "stats": {
            "high_conviction_wins": high_conviction_wins,
            "high_conviction_losses": high_conviction_losses,
            "low_conviction_wins": low_conviction_wins,
            "low_conviction_losses": low_conviction_losses,
        },
    }


def _build_dominant_patterns(enriched):
    winning_patterns = {}
    losing_patterns = {}

    for trade in enriched:
        agreement = trade.get("system_agreement", {}) or {}
        agreement_bucket = _agreement_bucket(agreement.get("score", 0))
        conviction = str(trade.get("conviction", "Unknown"))
        direction = str(trade.get("direction", "UNKNOWN"))
        market_context = trade.get("market_context", {}) or {}
        regime = _safe_upper(market_context.get("regime"))
        breadth = _safe_upper(market_context.get("breadth"))
        mode = _safe_upper(market_context.get("mode"))

        label = (
            f"{direction} | {agreement_bucket} agreement | "
            f"{conviction} conviction | {regime} | {breadth} | {mode}"
        )

        outcome = trade.get("outcome", "UNKNOWN")
        if outcome == "WIN":
            winning_patterns[label] = winning_patterns.get(label, 0) + 1
        elif outcome == "LOSS":
            losing_patterns[label] = losing_patterns.get(label, 0) + 1

    top_win = _top_count_item(winning_patterns, "No dominant winning pattern yet.")
    top_loss = _top_count_item(losing_patterns, "No dominant losing pattern yet.")

    return {
        "winning": {
            "headline": "Dominant Winning Pattern",
            "label": top_win["label"],
            "count": top_win["count"],
        },
        "losing": {
            "headline": "Dominant Losing Pattern",
            "label": top_loss["label"],
            "count": top_loss["count"],
        },
    }


def _build_trade_coaching_summary(enriched, avg_health, wins, losses, flat):
    insights = []

    if wins > losses:
        insights.append("You are net positive on archived trades, but that does not excuse weak process on the bad ones.")
    elif losses > wins:
        insights.append("Your archived losses are outweighing your wins. Entry quality and alignment need to get stricter.")
    else:
        insights.append("Your results are balanced, which usually means the edge is still too soft or inconsistent.")

    if avg_health < 40:
        insights.append("You tend to close trades after they have already weakened badly. That is a management problem, not just a market problem.")
    elif avg_health > 70:
        insights.append("You are generally exiting from stronger states, which suggests better discipline on closes.")

    if flat > 0 and flat >= max(1, wins):
        insights.append("A meaningful chunk of your trade history is not producing clean edge. You may be forcing setups that never really developed.")

    return insights


def build_trade_lesson(position):
    outcome = classify_trade_outcome(position)
    agreement = position.get("system_agreement", {}) or {}
    agreement_score = int(agreement.get("score", 0) or 0)
    direction = position.get("direction", "UNKNOWN")
    conviction = position.get("conviction", "Unknown")
    health = position.get("health", {}) or {}
    health_score = int(health.get("score", 0) or 0)
    market_context = position.get("market_context", {}) or {}
    mode = market_context.get("mode", "UNKNOWN")
    breadth = market_context.get("breadth", "UNKNOWN")
    regime = market_context.get("regime", "UNKNOWN")

    headline = "Needs harder review."
    lesson = "This trade does not yet have enough context attached to judge cleanly."
    tag = "Review"

    if outcome == "WIN" and agreement_score >= 75:
        headline = "You took the hint."
        lesson = (
            f"This trade worked because your {direction} idea was aligned with the system and the environment did not fight you. "
            f"You were not guessing blindly here."
        )
        tag = "Aligned Win"
    elif outcome == "WIN" and agreement_score <


    def build_my_plays_page_summary(plays):
    plays = _ensure_activation_readiness(plays or [])

    total = len(plays)
    ready = 0
    close = 0
    weak = 0
    high_agreement = 0
    high_conviction = 0

    for play in plays:
        bucket = _activation_bucket(play)
        agreement_score = _agreement_score(play)
        conviction = _norm_text(play.get("conviction", "Medium")).lower()

        if bucket == "READY":
            ready += 1
        elif bucket == "CLOSE":
            close += 1
        elif bucket in {"WATCH", "WEAK"}:
            weak += 1

        if agreement_score >= 75:
            high_agreement += 1
        if conviction == "high":
            high_conviction += 1

    if total == 0:
        headline = "No idea flow yet."
        summary = "You do not have enough plays yet for the system to judge your decision quality."
        chip = "Cold Start"
    elif weak > ready:
        headline = "Your idea book is still too soft."
        summary = "You are carrying more weak or watch-only setups than truly ready ideas. Tightening your filter matters more than adding volume."
        chip = "Needs Tightening"
    elif ready > 0:
        headline = "There are real candidates on deck."
        summary = "You have playable setups with enough structure to matter. The goal now is disciplined promotion, not random activation."
        chip = "Constructive"
    else:
        headline = "The book is forming, but still mixed."
        summary = "Some ideas are getting closer, but the edge is not clean enough yet to treat the inventory as sharp."
        chip = "Mixed"

    return {
        "headline": headline,
        "summary": summary,
        "chip": chip,
        "total": total,
        "ready": ready,
        "close": close,
        "weak": weak,
        "high_agreement": high_agreement,
        "high_conviction": high_conviction,
    }


def build_play_detail_summary(play):
    if not play:
        return {
            "headline": "Play not found.",
            "summary": "The requested play could not be loaded.",
            "chip": "Missing",
        }

    readiness = play.get("activation_readiness", {}) or {}
    bucket = _norm_upper(readiness.get("bucket", "UNKNOWN"))
    agreement_score = _agreement_score(play)
    health_score = _health_score(play)

    if bucket == "READY" and agreement_score >= 75:
        headline = "This setup is close to institutional-quality for your system."
        summary = "The structure, agreement, and context are strong enough that activation can be justified if you stay disciplined."
        chip = "Ready"
    elif bucket == "CLOSE":
        headline = "This setup is warming up, but it is not fully earned yet."
        summary = "You may be early if you push this now. Let the system get cleaner confirmation before treating it like a live position."
        chip = "Close"
    elif bucket in {"WATCH", "WEAK"}:
        headline = "This setup is not strong enough yet."
        summary = "The system is telling you this idea still lacks the evidence required for trust. Do not confuse attention with quality."
        chip = "Weak / Watch"
    elif health_score < 35:
        headline = "The setup is already under pressure."
        summary = "This idea is not developing in a way that deserves confidence right now."
        chip = "Under Pressure"
    else:
        headline = "This setup is still developing."
        summary = "The idea is alive, but the edge is not clean enough yet to pretend certainty."
        chip = "Developing"

    return {
        "headline": headline,
        "summary": summary,
        "chip": chip,
    }


def build_my_positions_page_summary(positions):
    positions = positions or []

    total = len(positions)
    strong = 0
    weak = 0
    high_agreement = 0
    under_pressure = 0

    for pos in positions:
        agreement_score = _agreement_score(pos)
        health_score = _health_score(pos)
        label = _norm_upper((pos.get("health", {}) or {}).get("label", ""))

        if agreement_score >= 75 and health_score >= 75:
            strong += 1
        if agreement_score < 55 or health_score < 35:
            weak += 1
        if agreement_score >= 75:
            high_agreement += 1
        if label in {"UNDER PRESSURE", "BROKEN"} or health_score < 35:
            under_pressure += 1

    if total == 0:
        headline = "No live exposure yet."
        summary = "You do not currently have open user positions to manage."
        chip = "Flat"
    elif weak > 0:
        headline = "Your live book needs attention."
        summary = f"{weak} position(s) currently look weak by health or agreement. The goal is faster clarity, not passive hope."
        chip = "Needs Review"
    elif strong > 0:
        headline = "The live book is behaving constructively."
        summary = "You currently have positions that still hold real support. Protect quality and do not over-manage strength."
        chip = "Constructive"
    else:
        headline = "The live book is mixed."
        summary = "You have active exposure, but not enough clean strength yet to call the position layer truly healthy."
        chip = "Mixed"

    return {
        "headline": headline,
        "summary": summary,
        "chip": chip,
        "total": total,
        "strong": strong,
        "weak": weak,
        "high_agreement": high_agreement,
        "under_pressure": under_pressure,
    }


def build_position_detail_summary(position):
    if not position:
        return {
            "headline": "Position not found.",
            "summary": "The requested position could not be loaded.",
            "chip": "Missing",
        }

    agreement_score = _agreement_score(position)
    health_score = _health_score(position)

    if agreement_score >= 75 and health_score >= 75:
        headline = "This position still has real support."
        summary = "The trade is behaving like something the system can justify. Do not ruin a good state with anxious over-management."
        chip = "Strong"
    elif agreement_score < 55 and health_score < 35:
        headline = "This position is weak in both idea quality and live behavior."
        summary = "The environment is not helping and the trade itself is deteriorating. Capital protection matters more than narrative right now."
        chip = "Critical"
    elif health_score < 35:
        headline = "This position is under real pressure."
        summary = "The setup may not be fully dead, but the live state is weak enough that passive management becomes its own mistake."
        chip = "Under Pressure"
    elif agreement_score < 55:
        headline = "This position lacks strong contextual support."
        summary = "Even if the trade is still alive, the system is not giving it high-quality backing."
        chip = "Mixed"
    else:
        headline = "This position is still developing."
        summary = "There is not enough evidence yet to call this either a clean success or a clean failure."
        chip = "Developing"

    return {
        "headline": headline,
        "summary": summary,
        "chip": chip,
    }


def build_trade_analysis_summary(analysis):
    analysis = analysis or {}
    totals = analysis.get("totals", {}) or {}
    wins = _safe_int(totals.get("wins", 0))
    losses = _safe_int(totals.get("losses", 0))
    flat = _safe_int(totals.get("flat", 0))
    behavior_summary = analysis.get("behavior_summary", {}) or {}
    behavior_counts = behavior_summary.get("counts", {}) or {}

    if wins > losses and sum(_safe_int(v) for v in behavior_counts.values()) == 0:
        headline = "Your archived book shows cleaner decision behavior."
        summary = "The trades are not perfect, but there are fewer obvious behavior leaks contaminating the outcomes."
        chip = "Constructive"
    elif losses > wins:
        headline = "The archived book is showing real decision leakage."
        summary = "Losses are outweighing wins, and the focus should be on tightening idea quality, activation quality, and management quality together."
        chip = "Needs Correction"
    elif flat > max(1, wins):
        headline = "Too much energy is producing too little edge."
        summary = "The archived book suggests too many trades are going nowhere, which usually means weak selection or weak follow-through."
        chip = "Soft Edge"
    else:
        headline = "The archived book is mixed."
        summary = "There is signal here, but not yet enough clean separation between strong decisions and weak habits."
        chip = "Mixed"

    return {
        "headline": headline,
        "summary": summary,
        "chip": chip,
    }
