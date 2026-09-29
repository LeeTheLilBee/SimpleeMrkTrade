"""OBSCAN006-010: deterministic symbol-directory import and identity reconciliation.

These are metadata, NOT executable/optionable assertions or live stock prices.
Network retrieval is intentionally absent; the importer accepts an approved local file.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from typing import Iterable, Mapping

from .contracts import _aware, clean_symbol

NASDAQ_COLUMNS = {"Symbol", "Security Name", "Test Issue"}
OTHER_COLUMNS = {"ACT Symbol", "Security Name", "Test Issue", "Exchange"}


@dataclass(frozen=True)
class SymbolRow:
    symbol: str
    security_name: str
    exchange: str
    source_file: str
    directory_observed_at: datetime
    nasdaq_test_issue: bool = False
    sec_cik: str | None = None
    sec_name: str | None = None
    identity_status: str = "DIRECTORY_ONLY"
    price_state: str = "UNAVAILABLE"
    optionability_state: str = "UNVERIFIED"

    def __post_init__(self) -> None:
        clean_symbol(self.symbol)
        _aware(self.directory_observed_at, "directory_observed_at")


def parse_nasdaq_directory(contents: str, *, directory: str,
                           observed_at: datetime) -> list[SymbolRow]:
    """Parse Nasdaq Trader nasdaqlisted.txt or otherlisted.txt; no implicit terms grant."""
    _aware(observed_at, "observed_at")
    required = NASDAQ_COLUMNS if directory == "nasdaqlisted.txt" else (
        OTHER_COLUMNS if directory == "otherlisted.txt" else None)
    if required is None:
        raise ValueError("unsupported directory")
    if not isinstance(contents, str) or len(contents) > 15_000_000:
        raise ValueError("invalid directory text")
    lines = contents.splitlines()
    if not lines or not required.issubset(set(lines[0].split("|"))):
        raise ValueError("missing official directory header")
    headers = lines[0].split("|")
    indices = {h: i for i, h in enumerate(headers)}
    result: dict[str, SymbolRow] = {}
    for line in lines[1:]:
        if not line or line.startswith("File Creation Time:"):
            continue
        parts = line.split("|")
        if len(parts) < len(headers):
            raise ValueError("truncated directory row")
        val = lambda col: parts[indices[col]].strip()
        if val("Test Issue") == "Y":
            continue
        if val("Test Issue") != "N":
            raise ValueError("unrecognized test-issue flag")
        try:
            symbol = clean_symbol(val("Symbol" if directory == "nasdaqlisted.txt" else "ACT Symbol"))
        except ValueError:
            # Preserve exclusion for unsupported instruments; do not convert them to a different symbol.
            continue
        if symbol in result:
            raise ValueError("duplicate symbol inside directory; requires identity review")
        result[symbol] = SymbolRow(
            symbol=symbol, security_name=val("Security Name"),
            exchange="NASDAQ" if directory == "nasdaqlisted.txt" else val("Exchange"),
            source_file=directory, directory_observed_at=observed_at)
    return sorted(result.values(), key=lambda row: row.symbol)


def parse_sec_ticker_exchange(contents: str) -> dict[str, tuple[str, str, str]]:
    """Accept SEC company_tickers_exchange.json's fields+data form; label as cross-reference."""
    data = json.loads(contents)
    if not isinstance(data, dict) or not isinstance(data.get("fields"), list) or not isinstance(data.get("data"), list):
        raise ValueError("expected SEC company_tickers_exchange.json shape")
    fields = data["fields"]
    required = ("cik", "name", "ticker", "exchange")
    if any(field not in fields for field in required):
        raise ValueError("SEC cross-reference fields missing")
    idx = [fields.index(field) for field in required]
    result: dict[str, tuple[str, str, str]] = {}
    for row in data["data"]:
        if not isinstance(row, list) or len(row) != len(fields):
            raise ValueError("truncated SEC ticker row")
        try:
            symbol = clean_symbol(str(row[idx[2]]))
        except ValueError:
            continue
        value = (str(row[idx[0]]).zfill(10), str(row[idx[1]]), str(row[idx[3]]))
        if symbol in result and result[symbol] != value:
            raise ValueError("SEC ticker collision requires manual mapping")
        result[symbol] = value
    return result


def reconcile_symbol_universe(nasdaq: Iterable[SymbolRow], other: Iterable[SymbolRow],
                              sec: Mapping[str, tuple[str, str, str]] | None = None) -> dict[str, SymbolRow]:
    """The SEC cannot add an unlisted security or prove that a directory ticker is optionable."""
    sec = sec or {}
    rows: dict[str, SymbolRow] = {}
    for record in [*nasdaq, *other]:
        if record.symbol in rows:
            raise ValueError("cross-directory duplicate must be reviewed, not silently overwritten")
        cik, company, exchange = sec.get(record.symbol, (None, None, None))
        from dataclasses import replace
        rows[record.symbol] = replace(
            record, sec_cik=cik, sec_name=company,
            identity_status="CROSS_REFERENCED" if cik and exchange else "DIRECTORY_ONLY")
    return rows


def diff_directory(previous: Mapping[str, SymbolRow], current: Mapping[str, SymbolRow]) -> dict[str, tuple[str, ...]]:
    """Changes are research leads requiring review; removed ≠ delisted without confirmation."""
    old, new = set(previous), set(current)
    changed = tuple(sorted(sym for sym in old & new if
        (previous[sym].security_name, previous[sym].exchange, previous[sym].sec_cik) !=
        (current[sym].security_name, current[sym].exchange, current[sym].sec_cik)))
    return {"newly_seen": tuple(sorted(new-old)), "not_in_latest_file": tuple(sorted(old-new)),
            "identity_changed": changed}


def directory_snapshot(rows: Mapping[str, SymbolRow]) -> dict[str, object]:
    return {
        "schema": "OB_SYMBOL_UNIVERSE_V1",
        "symbols": len(rows),
        "current_price_provided": False,
        "option_contract_prices_provided": False,
        "listing_truth": "directory metadata as observed; removal does not prove delisting",
        "identity_review_required": sum(x.identity_status != "CROSS_REFERENCED" for x in rows.values()),
    }
