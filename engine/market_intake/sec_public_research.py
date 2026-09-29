"""Explicit owner-triggered SEC public-data ingestion into the existing OB research record.

No account, API key, broker feed, trading authority or hosted route. SEC ticker
cross-reference never manufactures an exchange listing. Research permissions
are supplied by a separately reviewed backend policy, not inferred from 200 OK.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Mapping

from .contracts import SourceRights, _aware, clean_symbol
from .fundamental_research import FundamentalRights, parse_companyfacts
from .sec_events import parse_sec_submissions
from .sec_public_client import EDGARPublicClient, SECResearchUnavailable, SEC_API, SEC_ACCESS
from .symbol_research import SymbolResearchInputs, symbol_research_snapshot
from .universe import SymbolRow, parse_sec_ticker_exchange

SEC_SOURCE = "sec-edgar"
MAX_RECENT_ACCESSIONS = 1000


@dataclass(frozen=True)
class EDGARPolicy:
    """Must be approved by a trusted owner/backend process; never set by the UI."""
    reviewed_reference: str
    reviewed_at: datetime
    internal_research_approved: bool
    owner_display_approved: bool
    ai_explanation_approved: bool
    retention_approved: bool = False
    shared_throttle_approved: bool = False

    def __post_init__(self) -> None:
        _aware(self.reviewed_at, "EDGAR review timestamp")
        if self.reviewed_reference not in {SEC_API, SEC_ACCESS}:
            raise ValueError("Official SEC policy reference required")

    def rights(self) -> tuple[FundamentalRights, SourceRights]:
        if not self.internal_research_approved or not self.owner_display_approved:
            raise SECResearchUnavailable("SEC_RIGHTS_REVIEW_PENDING")
        facts = FundamentalRights(
            source_id=SEC_SOURCE,
            reference=self.reviewed_reference,
            reviewed_at=self.reviewed_at,
            internal_research=True,
            owner_display=True,
            ai_explanation=self.ai_explanation_approved,
            retention=self.retention_approved,
        )
        events = SourceRights(
            source_id=SEC_SOURCE,
            upstream_family="SEC-EDGAR",
            permission_reference=self.reviewed_reference,
            verified_at=self.reviewed_at,
            internal_research=True,
            automated_non_display=True,
            owner_display=True,
            entitled_instruments=frozenset({"event"}),
        )
        return facts, events


def accepted_recent_accessions(submissions: dict, *, received_at: datetime,
                               max_recent: int = MAX_RECENT_ACCESSIONS) -> dict[str, datetime]:
    """Use original SEC timestamp, never receipt time as a filing publication date."""
    _aware(received_at, "submissions receipt")
    recent = submissions.get("filings", {}).get("recent", {})
    if not isinstance(recent, dict):
        raise SECResearchUnavailable("SEC_SUBMISSIONS_INVALID")
    keys = ("accessionNumber", "acceptanceDateTime", "form")
    if any(not isinstance(recent.get(k), list) for k in keys):
        raise SECResearchUnavailable("SEC_SUBMISSIONS_INVALID")
    if len({len(recent[k]) for k in keys}) != 1:
        raise SECResearchUnavailable("SEC_SUBMISSIONS_INVALID")
    if not 1 <= max_recent <= MAX_RECENT_ACCESSIONS:
        raise ValueError("Bounded accession window required")
    from .fundamental_research import ACCESSION, FORMS
    result: dict[str, datetime] = {}
    for accession, stamp, form in zip(*(recent[k][:max_recent] for k in keys)):
        if not isinstance(accession, str) or not ACCESSION.fullmatch(accession) or form not in FORMS:
            continue
        try:
            when = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        except ValueError:
            continue
        if when.tzinfo is None or when.utcoffset() is None or when > received_at:
            continue
        prior = result.get(accession)
        if prior is not None and prior != when:
            raise SECResearchUnavailable("SEC_ACCESSION_CONFLICT")
        result[accession] = when
    return result


def exact_sec_identity(directory_row: SymbolRow,
                       sec_index: Mapping[str, tuple[str, str, str]]) -> SymbolRow:
    """Require independently discovered listed symbol, then exact SEC ticker/CIK."""
    symbol = clean_symbol(directory_row.symbol)
    match = sec_index.get(symbol)
    if match is None:
        raise SECResearchUnavailable("SEC_IDENTITY_NOT_MATCHED")
    cik, name, exchange = match
    if not isinstance(cik, str) or len(cik) != 10 or not cik.isdigit() or not name or not exchange:
        raise SECResearchUnavailable("SEC_IDENTITY_INVALID")
    if directory_row.sec_cik is not None and directory_row.sec_cik != cik:
        raise SECResearchUnavailable("SEC_IDENTITY_CONFLICT")
    return replace(directory_row, sec_cik=cik, sec_name=name,
                   identity_status="CROSS_REFERENCED")


class EDGARResearchCollector:
    """Offline-composable owner research. Caller enforces Tower before invocation.

    A separately configured shared org/IP throttle is required before multi-worker
    deployment; one instance by itself limits to <=2 requests/second.
    """

    def __init__(self, client: EDGARPublicClient, policy: EDGARPolicy, *,
                 owner_authorized: bool, single_worker_confirmed: bool = False):
        if not isinstance(client, EDGARPublicClient):
            raise TypeError("Approved SEC transport required")
        if not isinstance(policy, EDGARPolicy):
            raise TypeError("Backend-reviewed SEC policy required")
        if owner_authorized is not True:
            raise SECResearchUnavailable("OWNER_AUTHORIZATION_REQUIRED")
        if not (single_worker_confirmed or policy.shared_throttle_approved):
            raise SECResearchUnavailable("SEC_ORG_RATE_LIMIT_REVIEW_REQUIRED")
        self.client = client
        self.policy = policy
        self.fundamental_rights, self.event_rights = policy.rights()

    def public_ticker_index(self) -> dict[str, tuple[str, str, str]]:
        payload, _ = self.client.ticker_directory()
        return parse_sec_ticker_exchange(__import__("json").dumps(payload))

    def collect_symbol(self, directory_row: SymbolRow,
                       sec_index: Mapping[str, tuple[str, str, str]]) -> SymbolResearchInputs:
        identity = exact_sec_identity(directory_row, sec_index)
        cik = identity.sec_cik
        if cik is None:
            raise SECResearchUnavailable("SEC_IDENTITY_NOT_MATCHED")
        subs, subs_receipt = self.client.submissions(cik)
        if str(subs.get("cik", "")).zfill(10) != cik:
            raise SECResearchUnavailable("SEC_SUBMISSIONS_CIK_CONFLICT")
        facts, facts_receipt = self.client.companyfacts(cik)
        accessions = accepted_recent_accessions(subs, received_at=subs_receipt)
        parsed_facts = parse_companyfacts(
            facts, cik=cik, accepted_accessions=accessions,
            rights=self.fundamental_rights, reviewed_at=facts_receipt,
        )
        events = parse_sec_submissions(
            __import__("json").dumps(subs), universe={identity.symbol: identity},
            received_at=subs_receipt, max_items_per_issuer=20,
        )
        captured = max(subs_receipt, facts_receipt)
        # The SEC data has research authority only, and never supplies a current
        # market price, an option quote, broker identity or an execution grant.
        return SymbolResearchInputs(
            identity=identity, captured_at=captured, financial_facts=parsed_facts,
            financial_rights=self.fundamental_rights, issuer_events=tuple(events),
            event_rights={SEC_SOURCE: self.event_rights},
        )

    def owner_snapshot(self, directory_row: SymbolRow,
                       sec_index: Mapping[str, tuple[str, str, str]]) -> dict[str, object]:
        data = self.collect_symbol(directory_row, sec_index)
        return symbol_research_snapshot(data, as_of=data.captured_at)
