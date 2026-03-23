import os
import sys
import json
from pathlib import Path

# 🔥 FIX IMPORT PATH (CRITICAL)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.ticker_universe import flattened_ticker_list, sector_map


def bootstrap_signals(output_path="data/signals.json"):
    tickers = flattened_ticker_list()
    sectors = sector_map()

    seeded = []
    base_score = 210

    for i, ticker in enumerate(tickers):
        score = max(45, base_score - (i * 3))

        if score >= 180:
            confidence = "HIGH"
            opinion = "High-conviction setup with strong alignment."
        elif score >= 130:
            confidence = "MEDIUM"
            opinion = "Developing setup with meaningful support."
        else:
            confidence = "LOW"
            opinion = "Early setup worth monitoring."

        seeded.append(
            {
                "symbol": ticker,
                "score": score,
                "confidence": confidence,
                "company_name": ticker,
                "opinion": opinion,
                "timestamp": "2026-03-21T15:00:00",
                "sector": sectors.get(ticker, "General"),
                "setup_type": "Continuation" if i % 3 == 0 else ("Breakout" if i % 3 == 1 else "Pullback")
            }
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(seeded, f, indent=2)

    return seeded


if __name__ == "__main__":
    data = bootstrap_signals()
    print(f"Bootstrapped {len(data)} signals.")
