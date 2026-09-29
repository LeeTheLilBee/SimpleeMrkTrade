"""Commercial-reuse-reviewed, source-only Market Catalyst Radar for Soulaana.

This is a separate protected research lane beside existing keyless and EDGAR
rooms. It DOES NOT install a quote feed, trade candidate, market scanner or
external model. All five sources start OFF until four independent reviewed
source-specific permissions are present; World Bank needs an indicator license
review, EIA needs its free key. A source may be owner visible without AI access.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import RLock
import os
import re

from .official_catalyst_sources import OfficialCatalystClient, SourceHold, REFERENCES

SOURCES = ("federal_register", "cftc", "eia", "world_bank", "nws")
TTL = {"federal_register": 3600, "cftc": 21600, "eia": 21600,
       "world_bank": 86400, "nws": 600}
LABELS = {
    "federal_register": "Federal Register · SEC agency documents",
    "cftc": "CFTC · Traders in Financial Futures, futures only",
    "eia": "EIA · weekly U.S. commercial crude inventories",
    "world_bank": "World Bank · US annual GDP, current USD",
    "nws": "NWS · actual active Georgia alerts",
}
MEANING = {
    "federal_register": ("Officially published SEC-related rulemaking or notices. "
                         "A proposed rule is not a final rule or an effective regulation."),
    "cftc": ("A reported TFF futures-only contract market, NOT a live options chain "
             "or proof of any particular trader's position."),
    "eia": ("A dated source-reported crude inventory observation, not an oil-price "
            "quote or a forecast."),
    "world_bank": ("Annual U.S. GDP at current USD from the licensed World Development "
                   "Indicators series, not CPI or real-time GDP."),
    "nws": ("An actual weather alert in the selected Georgia area. An empty snapshot "
            "is not a promise that conditions are safe."),
}


def reviewed_sources(environ=None):
    env = environ if environ is not None else os.environ
    if env.get("OB_CATALYST_RADAR_ENABLED") != "1":
        return frozenset()
    enabled = set()
    for source in SOURCES:
        prefix = "OB_CATALYST_" + source.upper() + "_"
        if all(env.get(prefix + suffix) == "1" for suffix in (
                "COMMERCIAL_REUSE_REVIEWED", "AUTOMATED_USE_REVIEWED",
                "OWNER_DISPLAY_REVIEWED")):
            if source == "world_bank" and env.get(
                    "OB_CATALYST_WORLD_BANK_GDP_LICENSE_REVIEWED") != "1":
                continue
            enabled.add(source)
    return frozenset(enabled)


def reviewed_soulaana_sources(enabled, environ=None):
    env = environ if environ is not None else os.environ
    if env.get("OB_CATALYST_SOULAANA_ENABLED") != "1":
        return frozenset()
    return frozenset(x for x in enabled if
                     env.get("OB_CATALYST_" + x.upper() +
                             "_SOULAANA_CONTENT_REVIEWED") == "1")


def _public_row(source, state, facts=None, retrieved_at=None):
    if source not in SOURCES:
        raise ValueError("Unknown official source")
    return {
        "source": source, "label": LABELS[source], "state": state,
        "source_reference": REFERENCES[source], "facts": list(facts or ()),
        "retrieved_at": retrieved_at, "source_only": True,
        "quote_eligible": False, "option_chain": False,
        "candidate_admitted": False, "execution_authorized": False,
        "ai_use_approved": False,
    }


def translate_for_soulaana(row, *, approved):
    """Derive bounded, factual source explanations only from a permitted row."""
    source = row["source"]
    if source not in SOURCES or row.get("source_reference") != REFERENCES.get(source):
        raise ValueError("SOULAANA_REFERENCE_HOLD")
    if not approved or row["state"] != "SOURCE_BOUND":
        return None
    facts = row["facts"]
    if not isinstance(facts, list) or len(facts) > 3:
        raise ValueError("SOULAANA_SOURCE_HOLD")
    explanations = []
    if not facts:
        if source != "nws":
            raise ValueError("SOULAANA_SOURCE_HOLD")
        explanations.append("No actual active Georgia alerts appeared in this specific API response.")
    for fact in facts:
        if (not isinstance(fact, dict) or not isinstance(fact.get("title"), str)
                or not isinstance(fact.get("period"), str)
                or not isinstance(fact.get("reference"), str)
                or len(fact["title"]) > 250 or len(fact["period"]) > 40):
            raise ValueError("SOULAANA_SOURCE_HOLD")
        if source == "federal_register":
            valid_fact_reference = (fact["reference"].startswith(
                "https://www.federalregister.gov/d/") or fact["reference"].startswith(
                "https://www.federalregister.gov/documents/"))
        elif source == "nws":
            valid_fact_reference = (fact["reference"].startswith(
                "https://api.weather.gov/alerts/") or fact["reference"].startswith(
                "https://alerts.weather.gov/"))
        else:
            valid_fact_reference = fact["reference"] == REFERENCES[source]
        if not valid_fact_reference or len(fact["reference"]) > 340:
            raise ValueError("SOULAANA_REFERENCE_HOLD")
        if source in ("federal_register", "cftc", "nws"):
            if source == "federal_register":
                explanations.append(fact["stage"] + " published " +
                                    fact["period"] + ": " + fact["title"] + ".")
            elif source == "cftc":
                # These counts belong to a CFTC reporting category; a positive
                # net is arithmetic, NOT a prediction of the next price move.
                long_count, short_count, net_count = (
                    fact.get("leveraged_long"), fact.get("leveraged_short"),
                    fact.get("leveraged_net"))
                if not all(isinstance(x, str) and len(x) <= 55 for x in (
                        long_count, short_count, net_count)):
                    raise ValueError("SOULAANA_SOURCE_HOLD")
                explanations.append(
                    "TFF futures-only report " + fact["period"] + ": " +
                    fact["title"] + ". Leveraged money long " + long_count +
                    ", short " + short_count + ", net " + net_count +
                    " contracts (long minus short).")
            else:
                explanations.append("NWS actual alert effective " + fact["period"] +
                                    ": " + fact["title"] + ".")
        else:
            if not isinstance(fact.get("value"), str):
                raise ValueError("SOULAANA_SOURCE_HOLD")
            explanations.append(fact["title"] + ": " + fact["value"] +
                                " (source period " + fact["period"] + ").")
    return {
        "source": source, "source_reference": row["source_reference"],
        "source_periods": [f["period"] for f in facts],
        "factual_findings": explanations,
        "how_to_interpret": MEANING[source],
        "retrieved_at": row["retrieved_at"], "source_specific_ai_reviewed": True,
        "external_model_called": False, "forecast_claimed": False,
        "causality_claimed": False, "quote_verified": False,
        "execution_authorized": False,
    }


class OfficialCatalystRadar:
    def __init__(self, *, enabled=frozenset(), ai_sources=frozenset(),
                 client=None, eia_key=None, now=None):
        if (type(enabled) is not frozenset or not enabled <= set(SOURCES)
                or type(ai_sources) is not frozenset or not ai_sources <= enabled):
            raise ValueError("Independently reviewed source gates are required")
        self.enabled = enabled
        self.ai_sources = ai_sources
        self.client = client or OfficialCatalystClient()
        self.eia_key = eia_key
        self._clock = now or (lambda: datetime.now(timezone.utc))
        self._lock = RLock()
        self._cache = {}

    def _fetch(self, source):
        if source == "eia":
            if not self.eia_key:
                return "KEY_REQUIRED", []
            item = self.client.eia(self.eia_key)
        else:
            item = getattr(self.client, source)()
        if (not isinstance(item, dict) or
                item.get("state") not in {"SOURCE_BOUND", "NO_PUBLICATION"} or
                not isinstance(item.get("facts"), list) or
                len(item["facts"]) > 3):
            raise SourceHold("SOURCE_SHAPE_HOLD")
        return item["state"], item["facts"]

    def snapshot(self):
        with self._lock:
            now = self._clock()
            if now.tzinfo is None or now.utcoffset() is None:
                raise ValueError("Source clock must be timezone-aware")
            rows = []
            for source in SOURCES:
                if source not in self.enabled:
                    self._cache.pop(source, None)
                    rows.append(_public_row(source, "REVIEW_HOLD"))
                    continue
                cached = self._cache.get(source)
                if cached and cached[0] > now:
                    row = dict(cached[1])
                    row["facts"] = [dict(x) for x in row["facts"]]
                else:
                    try:
                        state, facts = self._fetch(source)
                        row = _public_row(source, state, facts, now.isoformat())
                    except (SourceHold, ValueError, KeyError, TypeError, OverflowError):
                        row = _public_row(source, "SOURCE_HOLD")
                    ttl = TTL[source] if row["state"] in {"SOURCE_BOUND", "NO_PUBLICATION"} else 300
                    self._cache[source] = (now + timedelta(seconds=ttl), row)
                row["ai_use_approved"] = (
                    source in self.ai_sources and row["state"] == "SOURCE_BOUND"
                )
                rows.append(row)
            # SEC is intentionally a link to the pre-existing reviewed issuer
            # corridor, not a fake sixth source fetch or duplicated rate budget.
            rows.append({
                "source": "sec_edgar", "label": "SEC EDGAR · existing Symbol Research",
                "state": "EXISTING_PROTECTED_CORRIDOR",
                "source_reference": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
                "facts": [], "ai_use_approved": False,
                "note": "Use the current protected Symbol Research corridor for independently reviewed SEC filings.",
                "source_only": True, "quote_eligible": False,
                "candidate_admitted": False, "execution_authorized": False,
            })
            reviewed = [translate_for_soulaana(row, approved=True) for row in rows[:-1]
                        if row["ai_use_approved"]]
        return {
            "schema": "OB_OFFICIAL_CATALYST_RADAR_V1",
            "as_of": now.isoformat(), "sources": rows,
            "soulaana": {
                "schema": "OB_SOULAANA_OFFICIAL_CATALYST_V1",
                "channel": "OFFICIAL_REVIEWED_CATALYSTS",
                "observations": reviewed, "observation_count": len(reviewed),
                "source_specific_ai_review_only": True,
                "interpretation": ("Each note translates a source publication separately. "
                                   "No cross-source causation, automated trading signal "
                                   "or inferred company/option price follows."),
                "external_model_called": False, "blanket_ai_authority": False,
                "forecast_claimed": False, "quote_verified": False,
                "candidate_admitted": False, "broker_execution_authorized": False,
            },
            "source_only": True, "context_only": True,
            "prices_attached": False, "options_chain_attached": False,
            "live_quote_verified": False, "candidate_admitted": False,
            "broker_execution_authorized": False,
            "paid_resources": False, "background_polling": False,
        }


def from_environment():
    enabled = reviewed_sources()
    return OfficialCatalystRadar(
        enabled=enabled, ai_sources=reviewed_soulaana_sources(enabled),
        eia_key=os.environ.get("OB_CATALYST_EIA_API_KEY") or None,
    )
