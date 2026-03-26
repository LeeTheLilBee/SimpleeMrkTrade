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
    row["entry"] = _safe_float(row.get("entry"))
    row["stop"] = _safe_float(row.get("stop"))
    row["target"] = _safe_float(row.get("target"))
    row["current_price"] = _safe_float(row.get("current_price", row["entry"]))
    row["health"] = determine_play_health(row)
    row["direction"] = determine_direction(row)

    market_context = latest_market_context()
    candidate = get_candidate_for_symbol(row.get("symbol"))

    row["market_context"] = market_context
    row["engine_candidate"] = candidate
    row["system_feedback"] = build_play_feedback(row, market_context, candidate)
    row["system_agreement"] = build_play_agreement(row, market_context, candidate)
    return row


def get_user_positions():
    return [enrich_user_position(p) for p in load_user_positions()]


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
