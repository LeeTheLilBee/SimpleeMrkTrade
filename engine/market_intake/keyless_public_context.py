"""One shared, keyless, source-only research context for protected OB rooms.

BLS CPI, Treasury debt and OpenFIGI symbol mapping are fetched server-side,
cached briefly in process RAM, and displayed only as independently sourced,
dated public research. EDGAR stays delegated to the already installed SEC
issuer-research resolver; this route neither re-fetches SEC nor implies a filing
has been fetched. NO brokerage/third-party login, paid source, prices or trading.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
import os
import re
from threading import RLock

from .public_research_sources import (
    OwnerResearchPolicy, PublicReferenceClient, PublicResearchUnavailable,
)
from .treasury_public_context import TreasuryPublicClient, TREASURY_DOCS
from .sec_public_client import SEC_API
from .keyless_soulaana import build_soulaana_source_register, build_soulaana_evidence_brief

BLS_DOCS = "https://www.bls.gov/developers/api_signature.htm"
FIGI_DOCS = "https://www.openfigi.com/api/documentation"
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")
SOURCES = ("sec", "bls", "treasury", "openfigi")
TL_SECONDS = {"bls": 86400, "treasury": 21600, "openfigi": 3600}
BLS_SERIES_META = {
    "CUUR0000SA0": ("CPI-U all items, not seasonally adjusted", "index"),
    "LNS14000000": ("Civilian unemployment rate, seasonally adjusted", "percent"),
    "CES0000000001": ("Total nonfarm payroll employment, seasonally adjusted", "thousands"),
    "WPUFD4": ("Producer Price Index, final demand, not seasonally adjusted", "index"),
}
LABELS = {
    "bls": ("BLS", "Macro panel · CPI / unemployment / payrolls / PPI", "index", BLS_DOCS),
    "treasury": ("US Treasury", "Total public debt outstanding", "USD", TREASURY_DOCS),
    "openfigi": ("OpenFIGI", "US ticker-to-FIGI reference", "FIGI", FIGI_DOCS),
    "sec": ("SEC EDGAR", "Company filings and companyfacts", "research", SEC_API),
}


def enabled_sources_from_environment() -> frozenset[str]:
    if os.environ.get("OB_KEYLESS_RESEARCH_ENABLED") != "1":
        return frozenset()
    # Separate source-by-source owner use/display review. Not an AI-use grant.
    return frozenset(k for k in ("bls", "treasury", "openfigi")
                     if os.environ.get(f"OB_KEYLESS_{k.upper()}_USE_REVIEWED") == "1"
                     and os.environ.get(f"OB_KEYLESS_{k.upper()}_OWNER_DISPLAY_REVIEWED") == "1")


def soulaana_sources_from_environment(enabled: frozenset[str]) -> frozenset[str]:
    """Explicit AI/content review; owner-display flags alone never authorize it."""
    if os.environ.get("OB_KEYLESS_SOULAANA_CONTENT_ENABLED") != "1":
        return frozenset()
    return frozenset(
        key for key in ("bls", "treasury", "openfigi")
        if key in enabled and os.environ.get(
            f"OB_KEYLESS_{key.upper()}_AI_USE_REVIEWED"
        ) == "1"
    )


def edgar_delegated_from_environment() -> bool:
    return (os.environ.get("OB_SEC_PUBLIC_RESEARCH_ENABLED") == "1"
            and os.environ.get("OB_SEC_PUBLIC_USE_REVIEWED") == "1"
            and os.environ.get("OB_SEC_OWNER_DISPLAY_REVIEWED") == "1"
            and bool(os.environ.get("OB_SEC_CONTACT_EMAIL")))


class KeylessPublicContext:
    """Bounded shared context; no background process or fetch during construction.

    The service is composed once at Tower startup. It serializes first fetches to
    prevent a wave of room loads from consuming a whole daily free BLS quota.
    Caches are process-local and not a data warehouse, signal or live feed.
    """
    def __init__(self, *, enabled: frozenset[str] = frozenset(),
                 sec_delegated: bool = False, ai_sources: frozenset[str] = frozenset(),
                 reference=None, treasury=None, now=None):
        if not isinstance(enabled, frozenset) or not enabled <= frozenset(SOURCES):
            raise ValueError("Exact server-controlled keyless source allowlist required")
        if (type(ai_sources) is not frozenset
                or not ai_sources <= frozenset({"bls", "treasury", "openfigi"})
                or not ai_sources <= enabled):
            raise ValueError("independently reviewed source/content grants required")
        self.enabled = enabled
        self.ai_sources = ai_sources
        self.sec_delegated = sec_delegated is True
        policy = OwnerResearchPolicy(
            source_use_reviewed=bool(enabled),
            owner_display_reviewed=bool(enabled),
            ai_use_reviewed=bool(ai_sources),
            reviewed_sources=enabled,
            ai_reviewed_sources=ai_sources,
        )
        self.reference = reference or PublicReferenceClient(policy)
        self.treasury = treasury or TreasuryPublicClient(policy)
        self._clock = now or (lambda: datetime.now(timezone.utc))
        self._lock = RLock()
        self._cache = {}
        self._figi_attempts = deque(maxlen=5)

    def _row(self, key: str, state: str, *, value=None, period=None,
             fetched_at=None, symbol=None, previous_period=None,
             previous_value=None, source_reference=None, series=None) -> dict:
        provider, label, unit, reference = LABELS[key]
        return {
            "source": key, "provider": provider, "label": label,
            "state": state, "value": value, "period": period,
            # These fields remain separate from publication/release times.
            "previous_period": previous_period, "previous_value": previous_value,
            "unit": unit, "retrieved_at": fetched_at,
            "symbol": symbol if key == "openfigi" else None,
            "source_reference": source_reference or reference,
            "series": series if key == "bls" else None,
            "historical_or_reference_only": True,
            "quote_eligible": False, "trading_authorized": False,
            "ai_use_approved": (key in self.ai_sources and state == "SOURCE_BOUND"),
        }

    def _load(self, key: str, symbol: str | None, now: datetime) -> dict:
        if key == "bls":
            cpi = self.reference.bls_v1("CUUR0000SA0")
            panel = []
            for series_id, (label, unit) in BLS_SERIES_META.items():
                try:
                    obs = cpi if series_id == "CUUR0000SA0" else self.reference.bls_v2(series_id)
                except PublicResearchUnavailable:
                    panel.append({
                        "series_id": series_id, "label": label, "unit": unit,
                        "state": "SOURCE_HOLD", "value": None, "period": None,
                        "previous_period": None, "previous_value": None,
                        "source_reference": (
                            cpi.source_reference if series_id == "CUUR0000SA0"
                            else "https://www.bls.gov/developers/api_signature_v2.htm"
                        ),
                    })
                    continue
                panel.append({
                    "series_id": series_id, "label": label, "unit": unit,
                    "state": "SOURCE_BOUND", "value": obs.value, "period": obs.period,
                    "previous_period": obs.previous_period,
                    "previous_value": obs.previous_value,
                    "source_reference": (
                        obs.source_reference
                        if series_id != "CUUR0000SA0" or obs.product == "OFFICIAL_BULK_CPI"
                        else BLS_DOCS
                    ),
                })
            return self._row(key, "SOURCE_BOUND", value=cpi.value,
                             period=cpi.period, fetched_at=cpi.fetched_at.isoformat(),
                             previous_period=cpi.previous_period,
                             previous_value=cpi.previous_value,
                             source_reference=(cpi.source_reference if
                                 cpi.product == "OFFICIAL_BULK_CPI" else None),
                             series=panel)
        if key == "treasury":
            obs = self.treasury.latest_public_debt()
            return self._row(key, "SOURCE_BOUND", value=obs.value,
                             period=obs.period, fetched_at=obs.fetched_at.isoformat(),
                             previous_period=obs.previous_period,
                             previous_value=obs.previous_value)
        if key == "openfigi" and symbol is not None:
            while self._figi_attempts and (now - self._figi_attempts[0]).total_seconds() >= 60:
                self._figi_attempts.popleft()
            if len(self._figi_attempts) >= 5:
                return self._row(key, "LOCAL_QUOTA_HOLD", symbol=symbol)
            self._figi_attempts.append(now)
            obs = self.reference.openfigi_ticker(symbol) # no API key
            return self._row(key, "SOURCE_BOUND" if obs.status == "MATCH" else obs.status,
                             value=obs.figi if obs.status == "MATCH" else None,
                             fetched_at=obs.fetched_at.isoformat(), symbol=symbol)
        return self._row(key, "SYMBOL_REQUIRED", symbol=symbol)

    def _one(self, key: str, symbol: str | None, now: datetime) -> dict:
        if key not in self.enabled:
            # Never retrieve a cached value after review is revoked.
            self._cache.pop((key, symbol if key == "openfigi" else None), None)
            return self._row(key, "REVIEW_HOLD", symbol=symbol)
        if key == "openfigi" and symbol is None:
            return self._row(key, "SYMBOL_REQUIRED")
        cache_key = (key, symbol if key == "openfigi" else None)
        cached = self._cache.get(cache_key)
        if cached and cached[0] > now:
            return dict(cached[1])
        try:
            result = self._load(key, symbol, now)
        except (PublicResearchUnavailable, ValueError, TypeError, KeyError, OverflowError):
            result = self._row(key, "SOURCE_HOLD", symbol=symbol)
        lifetime = TL_SECONDS[key] if result["state"] in {"SOURCE_BOUND", "NOT_FOUND", "AMBIGUOUS_HOLD"} else 300
        if len(self._cache) >= 40 and cache_key not in self._cache:
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = (now + timedelta(seconds=lifetime), dict(result))
        return result

    def snapshot(self, *, symbol: str | None = None) -> dict:
        if symbol is not None and (not isinstance(symbol, str) or not SYMBOL.fullmatch(symbol)
                                   or ".." in symbol):
            raise ValueError("A valid exact uppercase ticker is required")
        with self._lock:
            now = self._clock()
            if now.tzinfo is None or now.utcoffset() is None:
                raise ValueError("UTC-aware source clock required")
            rows = [self._row(
                "sec", "DELEGATED_ISSUER_RESEARCH" if self.sec_delegated else "REVIEW_HOLD",
                symbol=symbol,
            )]
            rows.extend(self._one(key, symbol, now) for key in ("bls", "treasury", "openfigi"))
        result = {
            "schema": "OB_KEYLESS_PUBLIC_CONTEXT_V1",
            "as_of": now.isoformat(),
            "symbol": symbol,
            "sources": rows,
            "source_only": True, "context_only": True,
            "prices_attached": False, "options_chain_attached": False,
            "live_quote_verified": False, "feeds_connected": False,
            "candidate_admitted": False, "broker_execution_authorized": False,
            "ai_input_approved": False,
            "sec_data_in_this_snapshot": False,
            "sec_note": "SEC issuer filings use the existing separate reviewed symbol-research corridor; no filing receipt is claimed here.",
            "public_business_auth_independent": True,
        }
        # Soulaana sees an independent, tightly limited source-status handoff,
        # never the provider values or raw text and never a trading signal.
        result["soulaana_source_register"] = build_soulaana_source_register(result)
        # Independent evidence handoff: only reviewed BLS/Treasury/FIGI
        # observations. No automatic model call, SEC content or broker feed.
        result["soulaana_evidence_brief"] = build_soulaana_evidence_brief(
            result, approved_sources=self.ai_sources,
        )
        return result


def from_environment() -> KeylessPublicContext:
    enabled = enabled_sources_from_environment()
    return KeylessPublicContext(
        enabled=enabled,
        ai_sources=soulaana_sources_from_environment(enabled),
        sec_delegated=edgar_delegated_from_environment(),
    )
