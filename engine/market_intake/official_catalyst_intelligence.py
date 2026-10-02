"""Official research provenance, in-process change tracking and Soulaana triage.

No network, cross-source causal inference, issuer matching, stock/option quote,
provider entitlement, candidate ranking or execution. All public timeline
details originate solely from individually AI-reviewed, validated radar rows.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re

from .official_catalyst_sources import REFERENCES

SOURCE_ORDER = ("federal_register", "cftc", "eia", "world_bank", "nws")
PERIOD_KIND = {
    "federal_register": "document_publication_date",
    "cftc": "report_as_of_date",
    "eia": "series_observation_period",
    "world_bank": "annual_observation_year",
    "nws": "alert_effective_time",
}
SOURCE_CADENCE = {
    "federal_register": "event-driven",
    "cftc": "weekly",
    "eia": "weekly",
    "world_bank": "annual",
    "nws": "event-driven",
}
CHANGES = frozenset({
    "FIRST_OBSERVED_IN_PROCESS",
    "UNCHANGED_SINCE_LAST_VERIFIED_FETCH",
    "CHANGED_SINCE_LAST_VERIFIED_FETCH",
})
PERMITTED_STATES = frozenset({
    "SOURCE_BOUND", "NO_PUBLICATION", "REVIEW_HOLD", "KEY_REQUIRED", "SOURCE_HOLD",
})
MAX_TIMELINE = 12


def _event_identity(source: str, fact: dict) -> str:
    """A stable publisher/series period identity, not an inferred ticker."""
    if source == "federal_register":
        identity = fact.get("id")
        if not isinstance(identity, str) or not re.fullmatch(r"20[0-9]{2}-[0-9]{4,6}", identity):
            raise ValueError("PROVENANCE_ID_HOLD")
        return identity
    if source == "nws":
        identity = fact.get("reference")
        if (not isinstance(identity, str) or len(identity) > 340 or
                not re.fullmatch(r"https://(?:api|alerts)\.weather\.gov/alerts/[A-Za-z0-9/:._?=%-]{1,220}",
                                 identity)):
            raise ValueError("PROVENANCE_ID_HOLD")
        return identity
    if source in {"eia", "world_bank"}:
        category = {"eia": "CRUDE_STOCKS_SERIES", "world_bank": "ANNUAL_GDP_USD"}[source]
        if fact.get("category") != category:
            raise ValueError("PROVENANCE_ID_HOLD")
        return category + ":" + _period(source, fact.get("period"))
    if source == "cftc":
        if fact.get("category") != "TFF_FUTURES_ONLY":
            raise ValueError("PROVENANCE_ID_HOLD")
        name = fact.get("title")
        if not isinstance(name, str) or not re.fullmatch(r"[\w ,.&()/'-]{1,160}", name):
            raise ValueError("PROVENANCE_ID_HOLD")
        return name + ":" + _period(source, fact.get("period"))
    raise ValueError("PROVENANCE_SOURCE_HOLD")


def _period(source: str, value: object) -> str:
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError("PROVENANCE_PERIOD_HOLD")
    if source == "world_bank":
        if not re.fullmatch(r"20[0-9]{2}", value):
            raise ValueError("PROVENANCE_PERIOD_HOLD")
    elif source == "nws":
        try:
            at = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if at.tzinfo is None or at.utcoffset() is None:
                raise ValueError()
        except ValueError:
            raise ValueError("PROVENANCE_PERIOD_HOLD") from None
    elif not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("PROVENANCE_PERIOD_HOLD")
    return value


def _validated_fact(source: str, fact: dict):
    if source not in SOURCE_ORDER or not isinstance(fact, dict):
        raise ValueError("PROVENANCE_FACT_HOLD")
    _event_identity(source, fact)
    _period(source, fact.get("period"))
    title, ref = fact.get("title"), fact.get("reference")
    if (not isinstance(title, str) or not title or len(title) > 250 or
            not isinstance(ref, str) or not ref or len(ref) > 340):
        raise ValueError("PROVENANCE_FACT_HOLD")
    if source == "federal_register":
        expected = (ref == "https://www.federalregister.gov/d/" + fact["id"] or
                    bool(re.fullmatch(
                        r"https://www\.federalregister\.gov/documents/20[0-9]{2}/"
                        r"[0-9]{2}/[0-9]{2}/" + re.escape(fact["id"]) + r"/[a-z0-9-]{1,200}",
                        ref)))
        if fact.get("stage") not in {"Rule", "Proposed Rule", "Notice"} or not expected:
            raise ValueError("PROVENANCE_REFERENCE_HOLD")
    elif source == "nws":
        if fact.get("category") != "ACTIVE_GA_ALERT":
            raise ValueError("PROVENANCE_REFERENCE_HOLD")
    elif ref != REFERENCES[source]:
        raise ValueError("PROVENANCE_REFERENCE_HOLD")
    if source == "cftc":
        for name in ("leveraged_long", "leveraged_short", "leveraged_net"):
            _decimal(fact.get(name))
        if (_decimal(fact["leveraged_long"]) - _decimal(fact["leveraged_short"])
                != _decimal(fact["leveraged_net"])):
            raise ValueError("PROVENANCE_VALUE_HOLD")
    if source in {"eia", "world_bank"}:
        _decimal(fact.get("value"))


def _decimal(x):
    if not isinstance(x, str) or len(x) > 75:
        raise ValueError("PROVENANCE_VALUE_HOLD")
    try:
        value = Decimal(x)
    except InvalidOperation:
        raise ValueError("PROVENANCE_VALUE_HOLD") from None
    if not value.is_finite() or abs(value) > Decimal("1e24"):
        raise ValueError("PROVENANCE_VALUE_HOLD")
    return value


class RevisionLedger:
    """Tiny RAM-only source fingerprints; not a durable revision archive.

    Changed means changed compared with the LAST successfully fetched identical
    source/event identity observed in THIS process; it does not prove the
    publisher issued a formal revised release. Cached reads are not new checks.
    """

    def __init__(self, *, max_entries: int = 120):
        if type(max_entries) is not int or not 5 <= max_entries <= 500:
            raise ValueError("Bounded fingerprint history required")
        self._known: dict[tuple[str, str], str] = {}
        self.max_entries = max_entries

    def clear(self, source: str):
        if source not in SOURCE_ORDER:
            raise ValueError("Unknown source")
        for key in tuple(self._known):
            if key[0] == source:
                del self._known[key]

    def record(self, source: str, facts: list[dict]) -> list[str]:
        if (source not in SOURCE_ORDER or not isinstance(facts, list) or
                len(facts) > 3):
            raise ValueError("PROVENANCE_ROW_HOLD")
        proposals: list[tuple[tuple[str, str], str]] = []
        keys = set()
        for fact in facts:
            _validated_fact(source, fact)
            key = (source, _event_identity(source, fact))
            if key in keys:
                raise ValueError("PROVENANCE_DUPLICATE_HOLD")
            keys.add(key)
            # Store no raw provider values: hashes of normalized, validated
            # source facts only. No URLs/values/credentials in persistent storage.
            digest = sha256(json.dumps(
                fact, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            ).encode("utf-8")).hexdigest()
            proposals.append((key, digest))
        result = []
        for key, digest in proposals:
            before = self._known.get(key)
            result.append("FIRST_OBSERVED_IN_PROCESS" if before is None else (
                "UNCHANGED_SINCE_LAST_VERIFIED_FETCH" if before == digest else
                "CHANGED_SINCE_LAST_VERIFIED_FETCH"))
        # Atomic with respect to validation: never mutate ledger after partial
        # malformed payload; caller's existing RLock protects concurrent requests.
        for key, digest in proposals:
            self._known.pop(key, None)
            self._known[key] = digest
        while len(self._known) > self.max_entries:
            del self._known[next(iter(self._known))]
        return result


def _sort_period(source, period):
    if source == "world_bank":
        return period + "-01-01T00:00:00+00:00"
    if source != "nws":
        return period + "T00:00:00+00:00"
    return datetime.fromisoformat(period.replace("Z", "+00:00")).astimezone(
        timezone.utc).isoformat()


def _period_comparisons(source, facts):
    # Never compare unrelated CFTC markets or an effective weather timestamp
    # with publication time. Only exact fixed series with matching units.
    if source not in {"eia", "world_bank"} or len(facts) < 2:
        return []
    latest, earlier = sorted(facts, key=lambda x: x["period"], reverse=True)[:2]
    if latest["period"] == earlier["period"] or latest["category"] != earlier["category"]:
        raise ValueError("COMPARISON_IDENTITY_HOLD")
    change = _decimal(latest["value"]) - _decimal(earlier["value"])
    return [{
        "source": source,
        "series": latest["category"],
        "later_period": latest["period"], "earlier_period": earlier["period"],
        "later_value": latest["value"], "earlier_value": earlier["value"],
        "difference_in_source_units": str(change),
        "direction": "UP" if change > 0 else "DOWN" if change < 0 else "UNCHANGED",
        "source_reference": REFERENCES[source],
        "research_only": True, "causality_claimed": False,
        "quote_verified": False,
    }]


def build_intelligence(rows, *, approved_sources, as_of):
    """Project bounded, rights-filtered provenance from same protected snapshot.

    Source health may show an allowed owner's source state. Event contents,
    comparisons and explanations appear ONLY for separately AI-reviewed sources.
    """
    if (not isinstance(as_of, datetime) or as_of.tzinfo is None or
            as_of.utcoffset() is None or
            not isinstance(rows, list) or len(rows) != 6 or
            type(approved_sources) is not frozenset or
            not approved_sources <= set(SOURCE_ORDER)):
        raise ValueError("INTELLIGENCE_CONTRACT_HOLD")
    if [r.get("source") for r in rows] != list(SOURCE_ORDER) + ["sec_edgar"]:
        raise ValueError("INTELLIGENCE_SOURCE_ORDER_HOLD")
    health = []
    timeline, comparisons = [], []
    for row in rows[:5]:
        source, state = row["source"], row.get("state")
        if (state not in PERMITTED_STATES or row.get("source_reference") != REFERENCES[source]
                or not isinstance(row.get("facts"), list)
                or len(row["facts"]) > 3 or
                row.get("quote_eligible") is not False or
                row.get("execution_authorized") is not False):
            raise ValueError("INTELLIGENCE_SOURCE_HOLD")
        facts = row["facts"]
        if state != "SOURCE_BOUND" and facts:
            raise ValueError("INTELLIGENCE_HELD_CONTENT_HOLD")
        if source in approved_sources and state == "SOURCE_BOUND":
            if row.get("ai_use_approved") is not True:
                raise ValueError("INTELLIGENCE_AI_RIGHTS_HOLD")
        elif row.get("ai_use_approved") is not False:
            raise ValueError("INTELLIGENCE_AI_RIGHTS_HOLD")
        health.append({
            "source": source, "state": state,
            "period_kind": PERIOD_KIND[source], "publication_cadence": SOURCE_CADENCE[source],
            "latest_source_period": max((f["period"] for f in facts), default=None),
            "retrieved_at": row.get("retrieved_at") if state in {"SOURCE_BOUND", "NO_PUBLICATION"} else None,
            "cache_hit": row.get("cache_hit") is True,
            "validated_record_count": len(facts) if state == "SOURCE_BOUND" else 0,
            "soulaana_content_approved": row.get("ai_use_approved") is True,
            "source_reference": REFERENCES[source],
            "original_content_not_substituted": True,
        })
        if row.get("ai_use_approved") is not True:
            continue
        markers = row.get("change_markers")
        if not isinstance(markers, list) or len(markers) != len(facts):
            raise ValueError("INTELLIGENCE_REVISION_HOLD")
        for fact, change in zip(facts, markers):
            _validated_fact(source, fact)
            if change not in CHANGES:
                raise ValueError("INTELLIGENCE_REVISION_HOLD")
            timeline.append({
                "source": source, "label": row["label"],
                "title": fact["title"], "source_period": _period(source, fact["period"]),
                "period_kind": PERIOD_KIND[source], "original_reference": fact["reference"],
                "change_since_last_verified_fetch": change,
                "retrieved_at": row["retrieved_at"],
                "research_only": True, "issuer_identity_proven": False,
                "quote_verified": False, "trade_causality_claimed": False,
            })
        comparisons.extend(_period_comparisons(source, facts))
    sec = rows[5]
    if (sec.get("state") != "EXISTING_PROTECTED_CORRIDOR" or
            sec.get("facts") != [] or sec.get("ai_use_approved") is not False):
        raise ValueError("INTELLIGENCE_SEC_DELEGATION_HOLD")
    health.append({
        "source": "sec_edgar", "state": "EXISTING_PROTECTED_CORRIDOR",
        "period_kind": None, "publication_cadence": "filing-driven",
        "latest_source_period": None, "retrieved_at": None, "cache_hit": False,
        "validated_record_count": 0, "soulaana_content_approved": False,
        "source_reference": sec["source_reference"],
        "original_content_not_substituted": True,
    })
    timeline.sort(key=lambda x: (
        _sort_period(x["source"], x["source_period"]), x["source"], x["title"],
    ), reverse=True)
    timeline = timeline[:MAX_TIMELINE]
    # Future scanner/issuer/quote/risk phases must supply independent actual
    # reviewed receipts. Publisher context alone never creates finalists.
    count = sum(r["soulaana_content_approved"] for r in health)
    return {
        "schema": "OB_SOULAANA_PROVENANCE_TRIAGE_V1",
        "as_of": as_of.isoformat(),
        "source_health": health,
        "event_timeline": timeline, "timeline_count": len(timeline),
        "series_comparisons": comparisons, "comparison_count": len(comparisons),
        "research_state": "REVIEWED_CONTEXT_AVAILABLE" if count else "NO_AI_REVIEWED_CONTEXT",
        "source_families_with_reviewed_content": count,
        "selection_readiness": {
            "state": "SOURCE_CONTEXT_ONLY",
            "official_context_present": bool(count),
            "issuer_identity_verified_in_this_corridor": False,
            "live_equity_quote_verified_in_this_corridor": False,
            "licensed_option_chain_verified_in_this_corridor": False,
            "contract_liquidity_verified_in_this_corridor": False,
            "capital_and_risk_policy_verified_in_this_corridor": False,
            "candidate_shortlist_authorized": False,
            "owner_review_required": True,
            "next_evidence": [
                "Match specific issuers through independently reviewed SEC/identifier evidence.",
                "Attach independently entitled current underlying and options quotes.",
                "Verify options liquidity, risk limits, capital policy and owner review.",
            ],
        },
        "revision_note": (
            "Changed means compared with a previous successful fetch of the same "
            "source identity in this single process. It does not prove a publisher "
            "formally issued a revision; an empty or held source never confirms "
            "that earlier records were withdrawn."
        ),
        "retrieval_not_publication": True,
        "independent_upstream_families_not_reseller_count": True,
        "external_model_called": False,
        "cross_source_causality_claimed": False,
        "price_or_option_data_attached": False,
        "ranking_performed": False,
        "execution_authorized": False,
    }
