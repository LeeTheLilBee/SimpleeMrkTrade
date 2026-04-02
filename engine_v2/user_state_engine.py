from typing import Dict


def detect_user_state(user_data: Dict) -> Dict:
    trades = user_data.get("recent_trades", 0)
    views = user_data.get("page_views", 0)

    if trades > 10:
        state = "overtrading"
    elif views > 20 and trades == 0:
        state = "hesitating"
    else:
        state = "normal"

    return {
        "user_state": state
    }
