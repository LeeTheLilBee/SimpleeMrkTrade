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
from xml.etree import ElementTree as ET
from urllib.error import HTTPError, URLError
from urllib.request import Request

from .public_research_sources import (
    OwnerResearchPolicy, PublicObservation, PublicResearchUnavailable,
    _default_open,
)

TREASURY_DOCS = "https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/"
TREASURY_RATE_DOCS = "https://home.treasury.gov/treasury-daily-interest-rate-xml-feed"
_TREASURY_RATE_BASE = (
    "https://home.treasury.gov/resource-center/data-chart-center/"
    "interest-rates/pages/xml"
)
_RATE_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
    "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
}
_NOMINAL_FIELDS = {
    "2Y": "BC_2YEAR", "5Y": "BC_5YEAR",
    "10Y": "BC_10YEAR", "30Y": "BC_30YEAR",
}
_REAL_FIELDS = {
    "5Y": "TC_5YEAR", "10Y": "TC_10YEAR", "30Y": "TC_30YEAR",
}
TREASURY_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
    "v2/accounting/od/debt_to_penny"
    "?fields=record_date,tot_pub_debt_out_amt"
    "&sort=-record_date&format=json&page[number]=1&page[size]=2"
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAX_RESPONSE_BYTES = 80_000
_MAX_RATE_RESPONSE_BYTES = 700_000


class TreasuryPublicClient:
    """Inject a transport for offline tests; live transport forbids redirects."""
    def __init__(self, policy: OwnerResearchPolicy, *, opener=None):
        if not isinstance(policy, OwnerResearchPolicy):
            raise TypeError("Independent owner source-use/display policy required")
        self.policy = policy
        self._open = opener or _default_open

    def _rate_feed(self, dataset: str, fields: dict[str, str]) -> list[dict]:
        if dataset not in {"daily_treasury_yield_curve", "daily_treasury_real_yield_curve"}:
            raise PublicResearchUnavailable("TREASURY_RATE_DATASET_HOLD")
        year = datetime.now(timezone.utc).year
        url = (
            _TREASURY_RATE_BASE + "?data=" + dataset
            + "&field_tdr_date_value=" + str(year)
        )
        req = Request(url, method="GET", headers={
            "Accept": "application/xml,text/xml", "Accept-Encoding": "identity",
        })
        try:
            with self._open(req, timeout=8) as response:
                raw = response.read(_MAX_RATE_RESPONSE_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError):
            raise PublicResearchUnavailable("TREASURY_RATE_TRANSPORT_HOLD") from None
        if len(raw) > _MAX_RATE_RESPONSE_BYTES:
            raise PublicResearchUnavailable("TREASURY_RATE_RESPONSE_TOO_LARGE")
        if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
            raise PublicResearchUnavailable("TREASURY_RATE_XML_HOLD")
        try:
            root = ET.fromstring(raw)
            parsed = []
            for entry in root.findall("atom:entry", _RATE_NS):
                props = entry.find("atom:content/m:properties", _RATE_NS)
                if props is None:
                    continue
                stamp = props.findtext("d:NEW_DATE", default="", namespaces=_RATE_NS)
                if not isinstance(stamp, str) or not re.fullmatch(
                        r"20\d{2}-\d{2}-\d{2}T00:00:00", stamp):
                    continue
                period = stamp[:10]
                measured = date.fromisoformat(period)
                if measured > datetime.now(timezone.utc).date() + timedelta(days=1):
                    continue
                values = {}
                valid = True
                for label, tag in fields.items():
                    raw_value = props.findtext("d:" + tag, default="", namespaces=_RATE_NS)
                    try:
                        number = Decimal(str(raw_value))
                    except (InvalidOperation, TypeError, ValueError):
                        valid = False
                        break
                    if not number.is_finite() or number <= Decimal("-20") or number >= Decimal("30"):
                        valid = False
                        break
                    values[label] = str(number)
                if valid:
                    parsed.append({"date": period, "yields_percent": values})
            parsed.sort(key=lambda row: row["date"], reverse=True)
            if len(parsed) < 2 or parsed[0]["date"] <= parsed[1]["date"]:
                raise ValueError()
            return parsed[:2]
        except (ET.ParseError, KeyError, TypeError, ValueError, InvalidOperation, UnicodeError):
            raise PublicResearchUnavailable("TREASURY_RATE_SOURCE_SHAPE_HOLD") from None

    def latest_rates_context(self) -> dict:
        """Official daily nominal/real Treasury curves plus bounded derived context.

        Values are end-of-day par-yield observations, not intraday executable
        prices. Breakeven is a simple nominal-minus-real approximation and is
        labelled as such; it is not CPI or a forecast.
        """
        self.policy.require("treasury")
        nominal = self._rate_feed("daily_treasury_yield_curve", _NOMINAL_FIELDS)
        real = self._rate_feed("daily_treasury_real_yield_curve", _REAL_FIELDS)
        latest, previous = nominal[0], nominal[1]
        latest_2y = Decimal(latest["yields_percent"]["2Y"])
        latest_10y = Decimal(latest["yields_percent"]["10Y"])
        previous_2y = Decimal(previous["yields_percent"]["2Y"])
        previous_10y = Decimal(previous["yields_percent"]["10Y"])
        spread = (latest_10y - latest_2y) * Decimal("100")
        prior_spread = (previous_10y - previous_2y) * Decimal("100")
        curve_delta = spread - prior_spread
        derived = {
            "two_year_change_bp": str(
                ((latest_2y - previous_2y) * Decimal("100")).quantize(Decimal("0.1"))
            ),
            "ten_year_change_bp": str(
                ((latest_10y - previous_10y) * Decimal("100")).quantize(Decimal("0.1"))
            ),
            "thirty_year_change_bp": str(
                ((Decimal(latest["yields_percent"]["30Y"])
                  - Decimal(previous["yields_percent"]["30Y"])) * Decimal("100"))
                .quantize(Decimal("0.1"))
            ),
            "two_ten_spread_bp": str(spread.quantize(Decimal("0.1"))),
            "previous_two_ten_spread_bp": str(prior_spread.quantize(Decimal("0.1"))),
            "curve_shape": (
                "INVERTED" if spread < Decimal("-5") else
                "POSITIVE" if spread > Decimal("5") else "NEAR_FLAT"
            ),
            "curve_change": (
                "STEEPENED" if curve_delta > Decimal("2") else
                "FLATTENED" if curve_delta < Decimal("-2") else "LITTLE_CHANGED"
            ),
            "breakeven_is_simple_approximation": True,
        }
        real_latest, real_previous = real[0], real[1]
        derived["real_ten_year_change_bp"] = str(
            ((Decimal(real_latest["yields_percent"]["10Y"])
              - Decimal(real_previous["yields_percent"]["10Y"])) * Decimal("100"))
            .quantize(Decimal("0.1"))
        )
        if real_latest["date"] == latest["date"]:
            breakeven = (
                Decimal(latest["yields_percent"]["10Y"])
                - Decimal(real_latest["yields_percent"]["10Y"])
            )
            derived["ten_year_breakeven_percent"] = str(
                breakeven.quantize(Decimal("0.01"))
            )
            derived["breakeven_date"] = latest["date"]
        else:
            derived["ten_year_breakeven_percent"] = None
            derived["breakeven_date"] = None
        if real_previous["date"] == previous["date"]:
            prior_breakeven = (
                Decimal(previous["yields_percent"]["10Y"])
                - Decimal(real_previous["yields_percent"]["10Y"])
            )
            derived["previous_ten_year_breakeven_percent"] = str(
                prior_breakeven.quantize(Decimal("0.01"))
            )
            derived["breakeven_change_bp"] = str(
                ((breakeven - prior_breakeven) * Decimal("100"))
                .quantize(Decimal("0.1"))
            ) if derived["ten_year_breakeven_percent"] is not None else None
        else:
            derived["previous_ten_year_breakeven_percent"] = None
            derived["breakeven_change_bp"] = None
        return {
            "state": "SOURCE_BOUND",
            "source": "US Treasury",
            "product": "DAILY_PAR_YIELD_CURVES",
            "source_reference": TREASURY_RATE_DOCS,
            "nominal": {
                "date": latest["date"],
                "yields_percent": latest["yields_percent"],
                "previous_date": previous["date"],
                "previous_yields_percent": previous["yields_percent"],
            },
            "real": {
                "date": real_latest["date"],
                "yields_percent": real_latest["yields_percent"],
                "previous_date": real[1]["date"],
                "previous_yields_percent": real[1]["yields_percent"],
            },
            "derived": derived,
            "market_data_character": "OFFICIAL_DAILY_CLOSE_INDICATIVE_BID_DERIVED",
            "intraday": False,
            "executable_quote": False,
            "broker_execution_authorized": False,
        }

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
