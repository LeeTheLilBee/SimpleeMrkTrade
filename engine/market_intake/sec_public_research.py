"""Official SEC ticker -> submissions -> companyfacts -> OB research.

Opt-in read-only backend resolver. Public EDGAR data is company research:
never a stock/option quote, signal, recommendation, position or order. SEC
ticker/CIK association is a research identity, not an independent Nasdaq listing.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os

from .contracts import SourceRights, clean_symbol
from .fundamental_research import FundamentalRights, parse_companyfacts
from .sec_events import parse_sec_submissions
from .sec_public_client import EDGARPublicClient, SECResearchUnavailable, SEC_API, SEC_TICKERS
from .symbol_research import SymbolResearchInputs
from .universe import SymbolRow, parse_sec_ticker_exchange


@dataclass(frozen=True)
class SECResearchPolicy:
    reviewed_at: datetime
    owner_display_reviewed: bool
    ai_explanation_reviewed: bool = False

    def __post_init__(self):
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("SEC policy review requires timestamp")
        if self.owner_display_reviewed is not True:
            raise ValueError("Explicit owner-display review is required")


class SECOfficialResearchResolver:
    """Only exact official ticker/CIK associations can produce an issuer record."""

    def __init__(self, client: EDGARPublicClient, policy: SECResearchPolicy):
        if not isinstance(client, EDGARPublicClient) or not isinstance(policy, SECResearchPolicy):
            raise TypeError("Reviewed official SEC client and research policy required")
        self.client = client
        self.policy = policy

    def __call__(self, room: str, symbol: str) -> SymbolResearchInputs | None:
        if room not in {"market_map", "symbol_page", "trade_center", "review_center"}:
            return None
        symbol = clean_symbol(symbol)
        directory, directory_received_at = self.client.ticker_directory()
        tickers = parse_sec_ticker_exchange(json.dumps(directory, separators=(",", ":")))
        match = tickers.get(symbol)
        if match is None:
            return None  # No guessed company; an absent ticker cannot be researched.
        cik, name, exchange = match
        if not cik.isdigit() or len(cik) != 10 or not name.strip() or not exchange.strip():
            raise SECResearchUnavailable("SEC_IDENTITY_UNVERIFIED")
        if self.policy.reviewed_at > directory_received_at:
            raise SECResearchUnavailable("SEC_POLICY_TIME_INVALID")

        submissions, submissions_received_at = self.client.submissions(cik)
        facts_payload, facts_received_at = self.client.companyfacts(cik)
        snapshot_at = datetime.now(timezone.utc)
        if str(submissions.get("cik", "")).zfill(10) != cik:
            raise SECResearchUnavailable("SEC_SUBMISSIONS_IDENTITY_MISMATCH")

        identity = SymbolRow(
            symbol=symbol, security_name=name, exchange=exchange,
            source_file=SEC_TICKERS, directory_observed_at=directory_received_at,
            sec_cik=cik, sec_name=name,
            identity_status="SEC_OFFICIAL_TICKER_CIK_ASSOCIATION_ONLY",
        )
        # The accepted timestamps must be independent SEC submissions evidence,
        # not the companyfacts filed date or the time OB downloaded the response.
        recent = submissions.get("filings", {}).get("recent", {})
        keys = ("accessionNumber", "acceptanceDateTime")
        if not isinstance(recent, dict) or any(not isinstance(recent.get(k), list) for k in keys):
            raise SECResearchUnavailable("SEC_ACCEPTANCE_EVIDENCE_MISSING")
        if len(recent["accessionNumber"]) != len(recent["acceptanceDateTime"]):
            raise SECResearchUnavailable("SEC_ACCEPTANCE_EVIDENCE_MALFORMED")
        accepted: dict[str, datetime] = {}
        for accession, raw_time in zip(recent["accessionNumber"], recent["acceptanceDateTime"]):
            if not isinstance(accession, str) or not isinstance(raw_time, str):
                continue
            try:
                dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            except ValueError:
                continue
            if dt.tzinfo is None or dt.utcoffset() is None or dt > snapshot_at:
                continue
            if accession in accepted and accepted[accession] != dt:
                raise SECResearchUnavailable("SEC_ACCESSION_CONFLICT")
            accepted[accession] = dt

        event_rights = SourceRights(
            source_id="sec-edgar", upstream_family="SEC-EDGAR",
            permission_reference=SEC_API, verified_at=self.policy.reviewed_at,
            internal_research=True, automated_non_display=True,
            owner_display=self.policy.owner_display_reviewed,
            entitled_instruments=frozenset({"event"}),
            real_time_entitled=False, invitee_display=False, redistribution=False,
        )
        events = parse_sec_submissions(
            json.dumps(submissions, separators=(",", ":")),
            universe={symbol: identity}, received_at=submissions_received_at,
            max_items_per_issuer=20,
        )
        # Reject future-dated or unproven issuer events rather than poisoning a
        # legitimate current research record with a future filing timestamp.
        events = [event for event in events if event.evidence.observed_at <= snapshot_at]
        # A missing accepted accession in the bounded/current submissions list
        # causes the fact to be skipped by parse_companyfacts, never backdated.
        financial_rights = FundamentalRights(
            source_id="sec-edgar", reference=SEC_API,
            reviewed_at=self.policy.reviewed_at, internal_research=True,
            owner_display=self.policy.owner_display_reviewed,
            ai_explanation=self.policy.ai_explanation_reviewed,
            retention=False,
        )
        facts = parse_companyfacts(
            facts_payload, cik=cik, accepted_accessions=accepted,
            rights=financial_rights, reviewed_at=facts_received_at,
            max_facts=200,
        )
        return SymbolResearchInputs(
            identity=identity, captured_at=snapshot_at,
            financial_facts=facts, financial_rights=financial_rights,
            issuer_events=tuple(events),
            event_rights={"sec-edgar": event_rights},
        )


def sec_owner_resolver_from_environment() -> SECOfficialResearchResolver | None:
    """Default OFF. Missing explicit review/contact refuses enabled startup.

    Operator-provided settings, not browser/session/query-string values:
      OB_SEC_PUBLIC_RESEARCH_ENABLED=1
      OB_SEC_CONTACT_EMAIL=real monitored contact
      OB_SEC_PUBLIC_USE_REVIEWED=1
      OB_SEC_OWNER_DISPLAY_REVIEWED=1
      OB_SEC_AI_EXPLANATION_REVIEWED=1 (optional; otherwise no facts in AI brief)
    """
    if os.environ.get("OB_SEC_PUBLIC_RESEARCH_ENABLED") != "1":
        return None
    if os.environ.get("OB_SEC_PUBLIC_USE_REVIEWED") != "1":
        raise ValueError("SEC public source use requires an operator rights review")
    if os.environ.get("OB_SEC_OWNER_DISPLAY_REVIEWED") != "1":
        raise ValueError("SEC owner-display use must be independently reviewed")
    email = os.environ.get("OB_SEC_CONTACT_EMAIL", "")
    client = EDGARPublicClient(email)
    policy = SECResearchPolicy(
        reviewed_at=datetime.now(timezone.utc), owner_display_reviewed=True,
        ai_explanation_reviewed=os.environ.get("OB_SEC_AI_EXPLANATION_REVIEWED") == "1",
    )
    return SECOfficialResearchResolver(client, policy)
