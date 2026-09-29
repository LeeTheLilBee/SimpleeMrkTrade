"""Keyless US Treasury fiscal context. Read-only, official fixed endpoint, no login.

This is *Debt to the Penny*, not the 10-year Treasury yield, a spot quote,
market price, investment signal, or evidence of any licensed securities feed.
All numeric fields originate from Treasury's published dataset at record_date.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request

from .public_research_sources import (
    OwnerResearchPolicy, PublicObservation, PublicResearchUnavailable,
    _default_open,
)

TREASURY_DOCS = "https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/"
TREASURY_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
    "v2/accounting/od/debt_to_penny"
    "?fields=record_date,tot_pub_debt_out_amt"
    "&sort=-record_date&format=json&page[number]=1&page[size]=2"
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAX_RESPONSE_BYTES = 80_000


class TreasuryPublicClient:
    """Inject a transport for offline tests; live transport forbids redirects."""
    def __init__(self, policy: OwnerResearchPolicy, *, opener=None):
        if not isinstance(policy, OwnerResearchPolicy):
            raise TypeError("Independent owner source-use/display policy required")
        self.policy = policy
        self._open = opener or _default_open

    def latest_public_debt(self) -> PublicObservation:
        self.policy.require("treasury")
        req = Request(TREASURY_URL, method="GET", headers={
            "Accept": "application/json", "Accept-Encoding": "identity",
        })
        try:
            with self._open(req, timeout=6) as response:
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError):
            raise PublicResearchUnavailable("TREASURY_TRANSPORT_HOLD") from None
        if len(raw) > _MAX_RESPONSE_BYTES:
            raise PublicResearchUnavailable("TREASURY_RESPONSE_TOO_LARGE")
        try:
            payload = json.loads(raw)
            rows = payload["data"]
            if not isinstance(rows, list) or not 1 <= len(rows) <= 2:
                raise ValueError()
            def valid_record(row):
                if not isinstance(row, dict):
                    raise ValueError()
                period, amount = row["record_date"], row["tot_pub_debt_out_amt"]
                if not isinstance(period, str) or not _DATE.fullmatch(period):
                    raise ValueError()
                measured = date.fromisoformat(period)
                if measured > datetime.now(timezone.utc).date() + timedelta(days=1):
                    raise ValueError()
                if not isinstance(amount, str):
                    raise ValueError()
                value = Decimal(amount.replace(",", ""))
                if not value.is_finite() or value <= 0:
                    raise ValueError()
                return period, str(value)
            period, value = valid_record(rows[0])
            previous_period = previous_value = None
            if len(rows) == 2:
                previous_period, previous_value = valid_record(rows[1])
                if previous_period >= period:
                    raise ValueError()
        except (KeyError, IndexError, TypeError, ValueError, InvalidOperation, UnicodeError):
            raise PublicResearchUnavailable("TREASURY_SOURCE_SHAPE_HOLD") from None
        return PublicObservation(
            "US Treasury", "DEBT_TO_THE_PENNY", "tot_pub_debt_out_amt",
            period, value, datetime.now(timezone.utc), TREASURY_DOCS,
            ai_use_approved=False,
            previous_period=previous_period, previous_value=previous_value,
        )
