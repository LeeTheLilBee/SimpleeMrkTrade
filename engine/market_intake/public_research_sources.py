"""Opt-in, backend-only public reference sources for OB's Market Data Desk.

These observations are *not* real-time equity/option prices, trading signals, or
feed-entitlement evidence. No network requests occur on import or in Tower views.
Caller must pass separately reviewed owner-use policy before any fetch. No storage.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import re
from typing import Callable
from urllib.parse import urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.error import HTTPError, URLError


BLS_DOCS = "https://www.bls.gov/developers/"
BEA_DOCS = "https://apps.bea.gov/api/signup/"
FIGI_DOCS = "https://www.openfigi.com/api/documentation"
_BLS = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
# Official no-key download for the same exact all-items CPI-U series; never a
# third-party relabel or stale bundled fixture.
BLS_BULK_CPI = "https://download.bls.gov/pub/time.series/cu/cu.data.1.AllItems"
_BLS_BULK_MAX_BYTES = 5_000_000
_BEA = "https://apps.bea.gov/api/data/"
_FIGI = "https://api.openfigi.com/v3/mapping"
_SERIES = re.compile(r"^[A-Z0-9_-]{3,45}$")
_SYMBOL = re.compile(r"^[A-Z0-9][A-Z0-9.-]{0,15}$")
_KEY = re.compile(r"^[A-Za-z0-9-]{10,120}$")
_MAX_BYTES = 1_000_000


class PublicResearchUnavailable(ValueError):
    """Redacted source error: do not echo vendor responses, URLs or keys."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _default_open(request: Request, timeout: int):
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


@dataclass(frozen=True)
class OwnerResearchPolicy:
    source_use_reviewed: bool = False
    owner_display_reviewed: bool = False
    ai_use_reviewed: bool = False
    # No global rights inheritance: each provider must be reviewed separately.
    reviewed_sources: frozenset[str] = frozenset()
    ai_reviewed_sources: frozenset[str] = frozenset()

    def ai_allowed(self, source: str) -> bool:
        return (self.ai_use_reviewed is True
                and type(self.ai_reviewed_sources) is frozenset
                and source in self.reviewed_sources
                and source in self.ai_reviewed_sources)

    def require(self, source: str) -> None:
        if (self.source_use_reviewed is not True
            or self.owner_display_reviewed is not True
            or type(self.reviewed_sources) is not frozenset
            or source not in self.reviewed_sources):
            raise PublicResearchUnavailable("OWNER_SOURCE_REVIEW_REQUIRED")


@dataclass(frozen=True)
class PublicObservation:
    provider: str
    product: str
    series_id: str
    period: str
    value: str
    fetched_at: datetime
    source_reference: str
    # Retrieval time is not a source publication/release time.
    release_at: None = None
    current_quote_eligible: bool = False
    candidate_admitted: bool = False
    broker_execution_authorized: bool = False
    ai_use_approved: bool = False
    # Optional earlier official observation from the same response. Both
    # source periods survive; retrieval time is never treated as release time.
    previous_period: str | None = None
    previous_value: str | None = None


@dataclass(frozen=True)
class IdentifierObservation:
    provider: str
    ticker: str
    status: str
    figi: str | None
    fetched_at: datetime
    source_reference: str = FIGI_DOCS
    current_quote_eligible: bool = False
    company_identity_verified: bool = False
    broker_execution_authorized: bool = False


class PublicReferenceClient:
    """Short-lived, bounded public-source pulls. No cache or HTTP in constructor.

    Injected opener in tests receives a urllib Request and timeout. Only the
    three fixed official endpoints below are reachable. No redirect following.
    """

    def __init__(self, policy: OwnerResearchPolicy, *, opener: Callable | None = None):
        if not isinstance(policy, OwnerResearchPolicy):
            raise TypeError("explicit owner research policy required")
        self.policy = policy
        self._opener = opener or _default_open

    def _json(self, url: str, *, source: str, method: str = "GET",
              body: bytes | None = None, headers: dict[str, str] | None = None):
        self.policy.require(source)
        valid = (
            source == "bls" and method == "GET" and body is None
            and re.fullmatch(re.escape(_BLS) + r"[A-Z0-9_-]{3,45}", url) is not None
        ) or (
            source == "bea" and method == "GET" and body is None
            and url.startswith(_BEA + "?")
        ) or (
            source == "openfigi" and method == "POST" and url == _FIGI
            and isinstance(body, bytes)
        )
        if not valid:
            raise PublicResearchUnavailable("SOURCE_ENDPOINT_NOT_ALLOWED")
        req = Request(url, data=body, headers=headers or {"Accept": "application/json"},
                      method=method)
        try:
            with self._opener(req, timeout=8) as response:
                raw = response.read(_MAX_BYTES + 1)
            if len(raw) > _MAX_BYTES:
                raise PublicResearchUnavailable("SOURCE_RESPONSE_TOO_LARGE")
            value = json.loads(raw)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise PublicResearchUnavailable("SOURCE_TRANSPORT_HOLD") from None
        except (UnicodeError, json.JSONDecodeError):
            raise PublicResearchUnavailable("SOURCE_JSON_INVALID") from None
        if not isinstance(value, (dict, list)):
            raise PublicResearchUnavailable("SOURCE_JSON_INVALID")
        return value, datetime.now(timezone.utc)

    @staticmethod
    def _number(value) -> str:
        if not isinstance(value, str):
            raise PublicResearchUnavailable("SOURCE_VALUE_INVALID")
        try:
            number = Decimal(value.replace(",", ""))
        except InvalidOperation:
            raise PublicResearchUnavailable("SOURCE_VALUE_INVALID") from None
        if not number.is_finite():
            raise PublicResearchUnavailable("SOURCE_VALUE_INVALID")
        return str(number)

    def _bls_official_bulk_cpi(self, series_id: str) -> PublicObservation:
        """Independent official BLS flat-file fallback for exact CPI-U all-items.

        API REQUEST_NOT_PROCESSED is not a valid observation. Use only this
        fixed official endpoint, no redirects, no provider login, bounded bytes,
        exact series, two date-ordered monthly values, honest source URL.
        """
        self.policy.require("bls")
        if series_id != "CUUR0000SA0":
            raise PublicResearchUnavailable("BLS_BULK_SERIES_NOT_SUPPORTED")
        request = Request(BLS_BULK_CPI, method="GET", headers={
            "Accept": "text/plain", "Accept-Encoding": "identity",
        })
        try:
            with self._opener(request, timeout=12) as response:
                if (getattr(response, "status", 200) != 200 or
                        getattr(response, "geturl", lambda: BLS_BULK_CPI)() != BLS_BULK_CPI):
                    raise PublicResearchUnavailable("BLS_BULK_TRANSPORT_HOLD")
                raw = response.read(_BLS_BULK_MAX_BYTES + 1)
            if len(raw) > _BLS_BULK_MAX_BYTES:
                raise PublicResearchUnavailable("BLS_BULK_TOO_LARGE")
            lines = raw.decode("utf-8-sig").splitlines()
            if not lines or [s.strip() for s in lines[0].split("\t")][:4] != [
                "series_id", "year", "period", "value"
            ]:
                raise PublicResearchUnavailable("BLS_BULK_SHAPE_HOLD")
            selected = {}
            now = datetime.now(timezone.utc)
            for line in lines[1:]:
                fields = [s.strip() for s in line.split("\t")]
                if not fields or fields[0] != series_id:
                    continue
                if len(fields) < 4:
                    raise PublicResearchUnavailable("BLS_BULK_SHAPE_HOLD")
                year, month, value = fields[1:4]
                if not re.fullmatch(r"(?:19|20)\d{2}", year) or not re.fullmatch(r"M(?:0[1-9]|1[0-2])", month):
                    # Do not treat the separately published annual average M13
                    # or semiannual S## as a monthly CPI point.
                    if month == "M13" or re.fullmatch(r"S0[1-3]", month):
                        continue
                    raise PublicResearchUnavailable("BLS_BULK_SHAPE_HOLD")
                if (int(year), int(month[1:])) > (now.year, now.month):
                    raise PublicResearchUnavailable("BLS_BULK_FUTURE_HOLD")
                number = self._number(value)
                if Decimal(number) <= 0 or (year, month) in selected:
                    raise PublicResearchUnavailable("BLS_BULK_SHAPE_HOLD")
                selected[(year, month)] = number
            if len(selected) < 2:
                raise PublicResearchUnavailable("BLS_BULK_SHAPE_HOLD")
            latest, previous = sorted(selected, reverse=True)[:2]
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError):
            raise PublicResearchUnavailable("BLS_BULK_TRANSPORT_HOLD") from None
        return PublicObservation(
            "BLS", "OFFICIAL_BULK_CPI", series_id,
            "-".join(latest), selected[latest], now, BLS_BULK_CPI,
            ai_use_approved=self.policy.ai_allowed("bls"),
            previous_period="-".join(previous), previous_value=selected[previous],
        )

    def bls_v1(self, series_id: str) -> PublicObservation:
        """Unregistered BLS v1: historical publication, not live market time."""
        if not isinstance(series_id, str) or not _SERIES.fullmatch(series_id):
            raise PublicResearchUnavailable("BLS_SERIES_INVALID")
        try:
            payload, fetched = self._json(_BLS + series_id, source="bls")
        except PublicResearchUnavailable as exc:
            if str(exc) == "SOURCE_TRANSPORT_HOLD" and series_id == "CUUR0000SA0":
                return self._bls_official_bulk_cpi(series_id)
            raise
        if (isinstance(payload, dict) and
                payload.get("status") in {"REQUEST_NOT_PROCESSED", "REQUEST_FAILED"} and
                series_id == "CUUR0000SA0"):
            return self._bls_official_bulk_cpi(series_id)
        try:
            if payload["status"] != "REQUEST_SUCCEEDED":
                raise ValueError()
            results = payload["Results"]
            # BLS documentation contains BOTH legitimate wrappers: its v1
            # signature sample shows a singleton Results list, while its
            # Python v1 example reads Results as an object with "series".
            # Accept exactly these two documented envelopes, no loose coercion.
            if isinstance(results, list):
                if len(results) != 1 or not isinstance(results[0], dict):
                    raise ValueError()
                group = results[0]
            elif isinstance(results, dict):
                group = results
            else:
                raise ValueError()
            series = group["series"]
            if (not isinstance(series, list) or len(series) != 1
                    or not isinstance(series[0], dict)
                    or series[0].get("seriesID") != series_id):
                raise ValueError()
            rows = series[0]["data"]
            if not isinstance(rows, list):
                raise ValueError()
            valid = [r for r in rows if isinstance(r, dict) and re.fullmatch(r"(?:M(?:0[1-9]|1[0-2])|Q0[1-4]|A01)",
                     str(r.get("period", ""))) and re.fullmatch(r"\d{4}", str(r.get("year", "")))]
            latest = max(valid, key=lambda r: (r["year"], r["period"]))
            number = self._number(latest["value"])
            latest_key = (latest["year"], latest["period"])
            earlier = sorted((r for r in valid if (r["year"], r["period"]) < latest_key),
                             key=lambda r: (r["year"], r["period"]), reverse=True)
            previous_period = previous_value = None
            for candidate in earlier:
                try:
                    candidate_value = self._number(candidate["value"])
                except (PublicResearchUnavailable, KeyError, TypeError):
                    continue
                previous_period = candidate["year"] + "-" + candidate["period"]
                previous_value = candidate_value
                break
        except (TypeError, KeyError, IndexError, ValueError) as exc:
            raise PublicResearchUnavailable("BLS_SOURCE_SHAPE_HOLD") from None
        return PublicObservation("BLS", "PUBLIC_V1", series_id,
                                 f'{latest["year"]}-{latest["period"]}', number,
                                 fetched, BLS_DOCS,
                                 ai_use_approved=self.policy.ai_allowed("bls"),
                                 previous_period=previous_period, previous_value=previous_value)

    def bea_nipa(self, api_key: str, *, table: str = "T10105", frequency: str = "Q",
                 line_number: str = "1") -> PublicObservation:
        """Keyed no-cost BEA NIPA inquiry; exact table/line labels preserved.

        The caller must supply a separately registered BEA key. We don't infer
        that table/line is an investment signal or that retrieval time is release.
        """
        if not isinstance(api_key, str) or not _KEY.fullmatch(api_key):
            raise PublicResearchUnavailable("BEA_KEY_NOT_CONFIGURED")
        if (not isinstance(table, str) or not re.fullmatch(r"T[0-9]{4,8}", table)
            or not isinstance(frequency, str) or frequency not in {"A", "Q"}):
            raise PublicResearchUnavailable("BEA_QUERY_INVALID")
        if not isinstance(line_number, str) or not re.fullmatch(r"[1-9][0-9]{0,2}", line_number):
            raise PublicResearchUnavailable("BEA_QUERY_INVALID")
        params = urlencode(dict(UserID=api_key, method="GetData", datasetname="NIPA",
                              TableName=table, Frequency=frequency,
                              Year="LAST5", ResultFormat="JSON"))
        payload, fetched = self._json(_BEA + "?" + params, source="bea")
        try:
            results = payload["BEAAPI"]["Results"]
            rows = results["Data"]
            matching = [r for r in rows if isinstance(r, dict) and str(r.get("LineNumber")) == line_number and
                        re.fullmatch(r"\d{4}(?:Q[1-4])?", str(r.get("TimePeriod", "")))]
            latest = max(matching, key=lambda r: r["TimePeriod"])
            number = self._number(latest["DataValue"])
        except (TypeError, KeyError, IndexError, ValueError):
            raise PublicResearchUnavailable("BEA_SOURCE_SHAPE_HOLD") from None
        return PublicObservation("BEA", "NIPA", f"{table}:{frequency}:{line_number}",
                                 latest["TimePeriod"], number, fetched, BEA_DOCS,
                                 ai_use_approved=self.policy.ai_allowed("bea"))

    def openfigi_ticker(self, ticker: str, *, api_key: str | None = None
                        ) -> IdentifierObservation:
        """Reference mapping, never independent company or real-time quote proof.

        Ambiguous provider output is held, not coerced into an arbitrary FIGI.
        """
        if not isinstance(ticker, str) or not _SYMBOL.fullmatch(ticker):
            raise PublicResearchUnavailable("FIGI_SYMBOL_INVALID")
        if api_key is not None and (not isinstance(api_key, str) or
                                    not re.fullmatch(r"[A-Za-z0-9_-]{10,120}", api_key)):
            raise PublicResearchUnavailable("FIGI_KEY_INVALID")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if api_key:
            headers["X-OPENFIGI-APIKEY"] = api_key
        body = json.dumps([{"idType": "TICKER", "idValue": ticker, "exchCode": "US"}]).encode()
        payload, fetched = self._json(_FIGI, source="openfigi", method="POST", body=body, headers=headers)
        if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
            raise PublicResearchUnavailable("FIGI_SOURCE_SHAPE_HOLD")
        if "error" in payload[0] or "data" not in payload[0]:
            raise PublicResearchUnavailable("FIGI_SOURCE_SHAPE_HOLD")
        matches = payload[0]["data"]
        if not isinstance(matches, list):
            raise PublicResearchUnavailable("FIGI_SOURCE_SHAPE_HOLD")
        eligible = [r["figi"] for r in matches if isinstance(r, dict) and
                    r.get("ticker") == ticker and isinstance(r.get("figi"), str) and
                    re.fullmatch(r"BBG[A-Z0-9]{9}", r["figi"])]
        state = "MATCH" if len(eligible) == 1 and len(matches) == 1 else (
            "NOT_FOUND" if not matches else "AMBIGUOUS_HOLD")
        return IdentifierObservation("OpenFIGI", ticker, state,
                                     eligible[0] if state == "MATCH" else None, fetched)
