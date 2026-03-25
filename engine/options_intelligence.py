from math import fabs
from datetime import datetime


def _safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def _days_to_expiry(expiry):
    try:
        exp = datetime.fromisoformat(str(expiry))
        now = datetime.now()
        return max(0, (exp - now).days)
    except Exception:
        return 0


def determine_trade_intent(trade):
    score = float(trade.get("score", 0) or 0)
    atr = float(trade.get("atr", 0) or 0)

    if score >= 200:
        return "EXPLOSIVE"
    if score >= 170:
        return "MOMENTUM"
    if atr >= 5:
        return "MOMENTUM"
    return "GRIND"


def contract_quality_score(option, stock_price, strategy, trade=None):
    strike = _safe_float(option.get("strike"))
    volume = _safe_float(option.get("volume"))
    oi = _safe_float(option.get("openInterest"))
    expiry = option.get("expiry")
    option_type = str(option.get("type", "")).upper()
    bid = _safe_float(option.get("bid"))
    ask = _safe_float(option.get("ask"))
    spread = abs(ask - bid) if bid or ask else _safe_float(option.get("bidAskSpread"))

    score = 0
    notes = []

    dte = _days_to_expiry(expiry)
    intent = determine_trade_intent(trade or {})

    if strategy == "CALL" and option_type == "CALL":
        score += 10
        notes.append("Contract type matches bullish thesis.")
    elif strategy == "PUT" and option_type == "PUT":
        score += 10
        notes.append("Contract type matches bearish thesis.")
    else:
        notes.append("Contract type does not match the thesis.")
        return 0, notes

    # Expiry scoring by trade intent
    if intent == "EXPLOSIVE":
        if 3 <= dte <= 10:
            score += 30
            notes.append("Short-dated contract fits explosive move.")
        elif 11 <= dte <= 21:
            score += 12
            notes.append("Expiry is usable but slower than ideal for explosive setup.")
        else:
            score -= 5
            notes.append("Expiry is not ideal for an explosive setup.")
    elif intent == "MOMENTUM":
        if 7 <= dte <= 21:
            score += 25
            notes.append("Expiry aligns with momentum window.")
        elif 22 <= dte <= 35:
            score += 12
            notes.append("Expiry is workable for momentum.")
        else:
            score += 5
            notes.append("Expiry is usable but not ideal for momentum.")
    else:  # GRIND
        if 14 <= dte <= 45:
            score += 25
            notes.append("Longer expiry supports slower grind setup.")
        elif 7 <= dte <= 13:
            score += 10
            notes.append("Expiry is a bit tight for a grind setup.")
        else:
            score += 5
            notes.append("Expiry is not ideal for a grind setup.")

    # Liquidity scoring
    if volume >= 2000:
        score += 25
        notes.append("Strong liquidity.")
    elif volume >= 500:
        score += 15
        notes.append("Good liquidity.")
    elif volume >= 100:
        score += 5
        notes.append("Thin liquidity.")
    else:
        score -= 10
        notes.append("Very weak liquidity.")

    if oi >= 2000:
        score += 25
        notes.append("Open interest is very strong.")
    elif oi >= 500:
        score += 15
        notes.append("Open interest is solid.")
    elif oi >= 100:
        score += 5
        notes.append("Open interest is thin.")
    else:
        score -= 10
        notes.append("Open interest is very weak.")

    # Spread scoring
    if spread <= 0:
        notes.append("Spread unavailable.")
    elif spread <= 0.05:
        score += 20
        notes.append("Very tight spread.")
    elif spread <= 0.10:
        score += 12
        notes.append("Tight spread.")
    elif spread <= 0.25:
        score += 5
        notes.append("Acceptable spread.")
    else:
        score -= 10
        notes.append("Wide spread reduces execution quality.")

    # Strike distance scoring by trade intent
    if stock_price > 0 and strike > 0:
        distance_pct = fabs(strike - stock_price) / stock_price

        if intent == "EXPLOSIVE":
            if distance_pct <= 0.02:
                score += 25
                notes.append("Tight strike for fast explosive move.")
            elif distance_pct <= 0.05:
                score += 10
                notes.append("Slightly wide for explosive move.")
            else:
                score -= 5
                notes.append("Too far from price for explosive setup.")

        elif intent == "MOMENTUM":
            if distance_pct <= 0.04:
                score += 20
                notes.append("Well-positioned strike for momentum.")
            elif distance_pct <= 0.08:
                score += 10
                notes.append("Acceptable strike for momentum.")
            else:
                score += 2
                notes.append("Wide strike reduces efficiency.")

        else:  # GRIND
            if distance_pct <= 0.06:
                score += 20
                notes.append("Strike allows slower progression.")
            else:
                score += 5
                notes.append("Far strike reduces probability of payoff.")

    option["trade_intent"] = intent
    option["dte"] = dte
    option["bidAskSpread"] = spread

    return int(score), notes


def choose_best_option(option_chain, stock_price, strategy, trade=None):
    best = None
    best_score = -1
    best_notes = []

    for option in option_chain or []:
        score, notes = contract_quality_score(option, stock_price, strategy, trade=trade)
        option["contract_score"] = score
        option["contract_notes"] = notes

        if score > best_score:
            best = option
            best_score = score
            best_notes = notes

    return best, best_score, best_notes


def option_is_executable(option, min_score=60):
    if not option:
        return False, "no_option_contract"

    score = _safe_float(option.get("contract_score"))
    volume = _safe_float(option.get("volume"))
    oi = _safe_float(option.get("openInterest"))
    spread = _safe_float(option.get("bidAskSpread"))

    if score < min_score:
        return False, "contract_score_too_low"
    if volume < 50:
        return False, "volume_too_thin"
    if oi < 50:
        return False, "open_interest_too_thin"
    if spread and spread > 0.10:
        return False, "spread_too_wide"

    return True, "ok"


def explain_option_choice(option):
    if not option:
        return ["No suitable option contract was selected."]

    notes = list(option.get("contract_notes", []))
    intent = option.get("trade_intent", "UNKNOWN")
    score = option.get("contract_score", 0)
    dte = option.get("dte", "N/A")
    strike = option.get("strike", "N/A")

    polished = [
        f"This contract was chosen for a {intent.lower()} setup.",
        f"The strike selection centers around {strike} and is aligned with the expected move profile.",
        f"Time to expiry is {dte} day(s), which fits the trade structure the system is trying to express.",
    ]

    polished.extend(notes)
    polished.append(
        f"Final contract score: {score}, combining expiry fit, liquidity quality, spread quality, and strike alignment."
    )
    return polished
