from engine.notifications import push_notification

def notify_trade_approved(trade):
    score = trade.get("score", 0)
    symbol = trade.get("symbol")
    strategy = trade.get("strategy")
    confidence = trade.get("confidence", "NONE")

    if score >= 220:
        push_notification(
            title="High Conviction Trade",
            message=f"{symbol} approved as {strategy} with elite score {score} and confidence {confidence}.",
            level="success",
            link="/premium-analysis",
            members_only=True,
            min_tier="Pro",
            category="premium"
        )
    elif score >= 120:
        push_notification(
            title="Approved Trade",
            message=f"{symbol} approved as {strategy} with premium score {score}.",
            level="info",
            link="/signals",
            members_only=True,
            min_tier="Starter",
            category="signal"
        )

def notify_trade_risk(symbol, reason):
    push_notification(
        title="Risk Alert",
        message=f"{symbol} risk condition triggered: {reason}.",
        level="warning",
        link="/positions",
        members_only=True,
        min_tier="Pro",
        category="risk"
    )

def notify_trade_closed(symbol, reason):
    push_notification(
        title="Trade Closed",
        message=f"{symbol} was closed: {reason}.",
        level="warning",
        link="/closed-trades",
        members_only=True,
        min_tier="Starter",
        category="risk"
    )

def notify_trade_edge(symbol, notes):
    push_notification(
        title="Edge Detected",
        message=f"{symbol}: {' | '.join(notes[:3])}",
        level="info",
        link="/why-this-trade",
        members_only=True,
        min_tier="Pro",
        category="premium"
    )
