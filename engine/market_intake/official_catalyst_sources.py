"""Bounded first-party catalyst adapters, never stock or option quote feeds.

Each adapter fetches exactly one fixed approved source/API product, validates its
publication shape and returns a small source-native fact. No third-party articles,
HTML scraping, streaming, broker, user-supplied URL or inferred trading authority.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

FEDERAL_REGISTER = ("https://www.federalregister.gov/api/v1/documents.json?"
                    "per_page=3&order=newest&conditions%5Bagencies%5D%5B%5D="
                    "securities-and-exchange-commission")
CFTC = ("https://publicreporting.cftc.gov/resource/gpe5-46if.json?"
        "%24limit=5&%24order=report_date_as_yyyy_mm_dd%20DESC")
NWS = "https://api.weather.gov/alerts/active?area=GA"
WORLD_BANK = ("https://api.worldbank.org/v2/country/US/indicator/"
              "NY.GDP.MKTP.CD?format=json&per_page=4")
WORLD_BANK_METADATA = ("https://api.worldbank.org/v2/indicator/"
                       "NY.GDP.MKTP.CD?format=json")
EIA = "https://api.eia.gov/v2/seriesid/PET.WCESTUS1.W"
REFERENCES = {
    "federal_register": "https://www.federalregister.gov/developers/documentation/api/v1",
    "cftc": "https://publicreporting.cftc.gov/stories/s/r4w3-av2u",
    "eia": "https://www.eia.gov/opendata/",
    "world_bank": "https://data.worldbank.org/indicator/NY.GDP.MKTP.CD",
    "nws": "https://www.weather.gov/documentation/services-web-api",
}
ALLOWED = frozenset({FEDERAL_REGISTER, CFTC, NWS, WORLD_BANK, WORLD_BANK_METADATA})
MAX_BYTES = 512_000


class SourceHold(ValueError):
    """A real source receipt is absent/invalid; caller must never invent one."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _text(value, maximum=140):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise SourceHold("SOURCE_SHAPE_HOLD")
    # The source text is not executable and must be rendered via textContent.
    if any(ord(ch) < 32 and ch not in "\t\n" for ch in value):
        raise SourceHold("SOURCE_SHAPE_HOLD")
    return value.strip()


def _date(value):
    try:
        day = date.fromisoformat(_text(value, 10))
    except (TypeError, ValueError):
        raise SourceHold("SOURCE_DATE_HOLD") from None
    if day > datetime.now(timezone.utc).date():
        raise SourceHold("SOURCE_DATE_HOLD")
    return day.isoformat()


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise SourceHold("SOURCE_VALUE_HOLD")
    try:
        n = Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        raise SourceHold("SOURCE_VALUE_HOLD") from None
    if not n.is_finite() or abs(n) > Decimal("1e24"):
        raise SourceHold("SOURCE_VALUE_HOLD")
    return str(n)


class OfficialCatalystClient:
    def __init__(self, *, opener=None, user_agent="Simplee-Observatory/1 (simpleeuniverse@gmail.com)"):
        self._opener = opener or build_opener(_NoRedirect()).open
        self._agent = _text(user_agent, 170)

    def _json(self, url, *, key=None):
        if url not in ALLOWED and not (url.startswith(EIA + "?") and key is not None):
            raise SourceHold("SOURCE_URL_HOLD")
        headers = {"Accept": "application/json", "User-Agent": self._agent}
        req = Request(url, headers=headers, method="GET")
        try:
            with self._opener(req, timeout=8) as response:
                if getattr(response, "status", 200) != 200 or response.geturl() != url:
                    raise SourceHold("SOURCE_TRANSPORT_HOLD")
                raw = response.read(MAX_BYTES + 1)
        except (HTTPError, URLError, OSError, TimeoutError):
            raise SourceHold("SOURCE_TRANSPORT_HOLD") from None
        if len(raw) > MAX_BYTES:
            raise SourceHold("SOURCE_TOO_LARGE")
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError):
            raise SourceHold("SOURCE_JSON_HOLD") from None

    def federal_register(self):
        data = self._json(FEDERAL_REGISTER)
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            raise SourceHold("SOURCE_SHAPE_HOLD")
        facts = []
        for x in data["results"][:3]:
            if not isinstance(x, dict) or x.get("type") not in {"Rule", "Proposed Rule", "Notice"}:
                continue
            number = _text(x.get("document_number"), 30)
            if not re.fullmatch(r"20\d{2}-\d{4,6}", number):
                raise SourceHold("SOURCE_ID_HOLD")
            link = x.get("html_url")
            if link != "https://www.federalregister.gov/d/" + number:
                # Official canonical URL, never accept vendor-supplied offsite URLs.
                raise SourceHold("SOURCE_URL_HOLD")
            facts.append({
                "title": _text(x.get("title"), 250),
                "stage": x["type"], "period": _date(x.get("publication_date")),
                "reference": link, "id": number,
            })
        if not facts:
            return {"state": "NO_PUBLICATION", "facts": []}
        return {"state": "SOURCE_BOUND", "facts": facts}

    def cftc(self):
        data = self._json(CFTC)
        if not isinstance(data, list):
            raise SourceHold("SOURCE_SHAPE_HOLD")
        facts = []
        for x in data[:5]:
            if not isinstance(x, dict):
                raise SourceHold("SOURCE_SHAPE_HOLD")
            report = _text(x.get("report_date_as_yyyy_mm_dd"), 27)[:10]
            market = _text(x.get("market_and_exchange_names"), 160)
            if not re.fullmatch(r"[\w ,.&()/'-]{1,160}", market):
                raise SourceHold("SOURCE_SHAPE_HOLD")
            facts.append({"title": market, "period": _date(report),
                          "category": "TFF_FUTURES_ONLY", "reference": REFERENCES["cftc"]})
        if not facts:
            return {"state": "NO_PUBLICATION", "facts": []}
        return {"state": "SOURCE_BOUND", "facts": facts[:3]}

    def nws(self):
        data = self._json(NWS)
        if not isinstance(data, dict) or not isinstance(data.get("features"), list):
            raise SourceHold("SOURCE_SHAPE_HOLD")
        facts = []
        for x in data["features"][:3]:
            if not isinstance(x, dict) or not isinstance(x.get("properties"), dict):
                raise SourceHold("SOURCE_SHAPE_HOLD")
            p = x["properties"]
            if p.get("status") != "Actual":
                continue
            title = _text(p.get("event"), 130)
            effective = _text(p.get("effective"), 40)
            try:
                at = datetime.fromisoformat(effective.replace("Z", "+00:00"))
                if at.tzinfo is None or at.utcoffset() is None:
                    raise ValueError()
            except ValueError:
                raise SourceHold("SOURCE_DATE_HOLD") from None
            link = p.get("@id") or p.get("id")
            if not (isinstance(link, str) and
                    (link.startswith("https://api.weather.gov/alerts/") or
                     link.startswith("https://alerts.weather.gov/")) and
                    len(link) < 250):
                raise SourceHold("SOURCE_URL_HOLD")
            facts.append({"title": title, "period": at.isoformat(),
                          "reference": link, "category": "ACTIVE_GA_ALERT"})
        return {"state": "SOURCE_BOUND", "facts": facts}

    def world_bank(self):
        # Do not promote arbitrary World Bank indicators or third-party data.
        meta = self._json(WORLD_BANK_METADATA)
        if (not isinstance(meta, list) or len(meta) != 2 or
                not isinstance(meta[1], list) or len(meta[1]) != 1 or
                not isinstance(meta[1][0], dict) or
                meta[1][0].get("id") != "NY.GDP.MKTP.CD" or
                not isinstance(meta[1][0].get("source"), dict) or
                str(meta[1][0]["source"].get("id")) != "2"):
            raise SourceHold("WORLD_BANK_METADATA_HOLD")
        data = self._json(WORLD_BANK)
        if not isinstance(data, list) or len(data) != 2 or not isinstance(data[1], list):
            raise SourceHold("SOURCE_SHAPE_HOLD")
        facts = []
        for x in data[1][:4]:
            if not isinstance(x, dict) or not isinstance(x.get("indicator"), dict):
                raise SourceHold("SOURCE_SHAPE_HOLD")
            if (x["indicator"].get("id") != "NY.GDP.MKTP.CD" or
                    x.get("countryiso3code") != "USA"):
                raise SourceHold("SOURCE_ID_HOLD")
            if x.get("value") is not None:
                facts.append({"title": "US GDP, current USD", "period": _date(x.get("date") + "-01-01")
                              [:4], "value": _number(x["value"]),
                              "reference": REFERENCES["world_bank"], "category": "ANNUAL_GDP_USD"})
        if not facts:
            return {"state": "NO_PUBLICATION", "facts": []}
        facts.sort(key=lambda x: x["period"], reverse=True)
        return {"state": "SOURCE_BOUND", "facts": facts[:2]}

    def eia(self, key):
        key = _text(key, 110)
        if not re.fullmatch(r"[A-Za-z0-9]{12,110}", key):
            raise SourceHold("EIA_KEY_HOLD")
        url = EIA + "?" + urlencode({"api_key": key})
        data = self._json(url, key=key)
        response = data.get("response") if isinstance(data, dict) else None
        rows = response.get("data") if isinstance(response, dict) else None
        if not isinstance(rows, list):
            raise SourceHold("SOURCE_SHAPE_HOLD")
        facts = []
        for x in rows[:4]:
            if not isinstance(x, dict):
                raise SourceHold("SOURCE_SHAPE_HOLD")
            # v2 seriesid data must identify its value/period; ambiguous
            # responses remain held until a real key and source shape verified.
            value = x.get("value")
            period = x.get("period")
            if value is not None:
                if not isinstance(period, str) or not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", period):
                    raise SourceHold("SOURCE_DATE_HOLD")
                facts.append({"title": "US commercial crude inventories",
                              "period": _date(period), "value": _number(value),
                              "reference": REFERENCES["eia"], "category": "CRUDE_STOCKS_SERIES"})
        if not facts:
            return {"state": "NO_PUBLICATION", "facts": []}
        facts.sort(key=lambda x: x["period"], reverse=True)
        return {"state": "SOURCE_BOUND", "facts": facts[:2]}
