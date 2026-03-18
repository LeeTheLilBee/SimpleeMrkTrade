from engine.watchlist_rotation import build_rotating_watchlist

def get_watchlist():
    return build_rotating_watchlist(limit=20)
