import json
import os
from pathlib import Path


def load_ticker_universe(path="data/ticker_universe.json"):
    file_path = Path(path)
    if not file_path.exists():
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def flattened_ticker_list(path="data/ticker_universe.json"):
    universe = load_ticker_universe(path)
    ordered = []
    seen = set()

    for bucket_name, tickers in universe.items():
        if not isinstance(tickers, list):
            continue

        for ticker in tickers:
            ticker = str(ticker).upper().strip()
            if not ticker or ticker in seen:
                continue
            seen.add(ticker)
            ordered.append(ticker)

    return ordered


def sector_map(path="data/ticker_universe.json"):
    universe = load_ticker_universe(path)
    mapping = {}

    for bucket_name, tickers in universe.items():
        if not isinstance(tickers, list):
            continue

        label = bucket_name.replace("_", " ").title()
        for ticker in tickers:
            ticker = str(ticker).upper().strip()
            if ticker and ticker not in mapping:
                mapping[ticker] = label

    return mapping
