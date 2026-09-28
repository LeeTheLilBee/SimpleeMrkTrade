"""Simplee first-party scanner — common, strictly non-trading observation contract.

Macro-context observations cannot satisfy the canonical OB market-price source
contract: there are no stock/option quotes, candidates, broker positions or orders.
All observation dates are source-provided, never generated at collection time.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
import re

SCHEMA = "SIMPLEE_MARKET_SCANNER_MACRO_V1"
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Observation:
    source: str
    series_id: str
    title: str
    region: str
    period: str
    value: str
    units: str
    cadence: str
    source_url: str
    license_status: str
    collected_at: str
    vintage_start: Optional[str] = None
    vintage_end: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "series_id": self.series_id,
            "title": self.title,
            "region": self.region,
            "period": self.period,
            "value": self.value,
            "units": self.units,
            "cadence": self.cadence,
            "source_url": self.source_url,
            "license_status": self.license_status,
            "collected_at": self.collected_at,
            "vintage_start": self.vintage_start,
            "vintage_end": self.vintage_end,
            "ob_market_quote_eligible": False,
            "ob_options_chain_eligible": False,
            "ob_live_signal_eligible": False,
        }


def iso_period(raw: object, *, annual_allowed: bool = False) -> str:
    value = str(raw or "").strip()
    if annual_allowed and re.fullmatch(r"\d{4}", value):
        value += "-01-01"
    if not _DATE.fullmatch(value):
        raise ValueError("Source period missing or malformed")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid source period") from exc
    return value


def decimal_value(raw: object) -> str:
    if raw is None or isinstance(raw, bool) or str(raw).strip() in ("", "."):
        raise ValueError("Missing source observation; no zero substitution")
    try:
        num = Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Non-numeric source observation") from exc
    if not num.is_finite():
        raise ValueError("Non-finite source observation")
    return str(num)


def collection_time(raw: datetime) -> str:
    if not isinstance(raw, datetime) or raw.tzinfo is None or raw.utcoffset() is None:
        raise ValueError("Collection time must be timezone-aware")
    return raw.isoformat()


def macro_envelope(observations: list[Observation], *, status: str, reason: str = "") -> dict:
    if status not in {"source_observed", "not_configured", "license_review_required",
                      "source_unavailable", "invalid_source"}:
        raise ValueError("Unknown macro source state")
    return {
        "schema": SCHEMA,
        "kind": "macro_context_only",
        "status": status,
        "reason": reason,
        "observations": [row.to_dict() for row in observations] if status == "source_observed" else [],
        "market_quotes": [],
        "option_chains": [],
        "signals": [],
        "positions": [],
        "candidates": [],
        "manual_live_queue": [],
        "current_market_data_eligible": False,
        "ai_assistant_input_eligible": False,  # FRED API terms prohibit AI/ML use absent express permission.
        "persistent_cache_eligible": False,
        "reuse_scope": "ephemeral_human_reference_only_pending_terms_review",
        "can_authorize_order": False,
    }
