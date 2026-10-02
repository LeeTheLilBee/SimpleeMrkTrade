"""SEC EDGAR -> existing Observatory Symbol Intelligence source adapter.

Accepts bounded, official *already fetched* submissions and companyfacts JSON.
Only directory+SEC cross-referenced identities enter the research record. Rights
are injected after independent use review, never inferred from public access.

No HTTP, broker API, options/equity quote, intraday filing-trigger proof,
candidate admission, return prediction or trading mode permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from typing import Mapping

from .contracts import SourceRights, _aware
from .fundamental_research import FundamentalRights, CompanyFact, parse_companyfacts
from .sec_events import parse_sec_submissions
from .symbol_research import SymbolResearchInputs, symbol_research_snapshot
from .universe import SymbolRow

_CIK = re.compile(r"^\d{10}$")
_ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")
_FORMS = frozenset({"8-K","8-K/A","10-K","10-K/A","10-Q","10-Q/A",
                    "20-F","20-F/A","6-K","S-1","S-1/A","DEF 14A"})
_SOURCE_LIMIT = 32_000_000


def _official_cik(data: Mapping[str, object], label: str) -> str:
    if not isinstance(data, dict):
        raise ValueError(f"{label}: expected official SEC JSON object")
    raw = data.get("cik")
    if isinstance(raw, bool) or not isinstance(raw, (int,str)):
        raise ValueError(f"{label}: CIK missing")
    cik = str(raw)
    if not cik.isdigit() or len(cik)>10:
        raise ValueError(f"{label}: malformed SEC CIK")
    return cik.zfill(10)


def _recent_rows(submissions: Mapping[str,object]) -> list[tuple[str,str,datetime,str,int]]:
    filings = submissions.get("filings")
    recent = filings.get("recent") if isinstance(filings,dict) else None
    if not isinstance(recent,dict):
        raise ValueError("SEC filings.recent arrays missing")
    keys=("accessionNumber","form","acceptanceDateTime","primaryDocument")
    arrays=[recent.get(k) for k in keys]
    if any(not isinstance(a,list) for a in arrays) or len({len(a) for a in arrays})!=1:
        raise ValueError("SEC parallel submission columns missing or unaligned")
    if len(arrays[0])>20000:
        raise ValueError("SEC recent filing array exceeds bounded intake")
    result=[]
    for i,parts in enumerate(zip(*arrays)):
        accession,form,time_raw,document=parts
        if not isinstance(accession,str) or not _ACCESSION.fullmatch(accession):
            continue
        if not isinstance(form,str) or len(form)>30 or not form.strip():
            continue
        try:
            accepted=datetime.fromisoformat(str(time_raw).replace("Z","+00:00"))
            _aware(accepted,"source-reported SEC acceptance time")
        except (TypeError,ValueError):
            continue
        result.append((accession,form,accepted,str(document),i))
    return result


def acceptance_evidence(submissions: Mapping[str,object], *, received_at:datetime
                        ) -> tuple[dict[str,datetime],tuple[str,...]]:
    """Source-reported dates only: no false claims of raw-header verification.

    The SEC's source JSON acceptance timestamp is never converted from a
    filing-date string. A disputed/inconsistent accession is excluded entirely.
    """
    _aware(received_at,"SEC receipt")
    result={}
    conflicts=set()
    for accession,_,stamp,_,_ in _recent_rows(submissions):
        if stamp > received_at:
            conflicts.add(accession) # future/clock inconsistency remains HOLD
            result.pop(accession,None)
            continue
        if accession in conflicts:
            continue
        if accession in result and result[accession]!=stamp:
            conflicts.add(accession)
            result.pop(accession,None)
            continue
        result[accession]=stamp
    return result,tuple(sorted(conflicts))


@dataclass(frozen=True)
class EdgarResearchBundle:
    inputs: SymbolResearchInputs
    accepted_accessions: int
    filings: int
    selected_facts: int
    source_reference: str
    historical_filing_coverage: str
    timestamp_assurance: str = "SEC_JSON_REPORTED_NOT_RAW_HEADER_VERIFIED"
    source_receipts: tuple[tuple[str,str], ...] = ()
    source_is_equity_quote: bool = False
    source_is_option_quote: bool = False
    candidate_admitted: bool = False
    execution_authorized: bool = False

    def owner_snapshot(self) -> dict[str,object]:
        return symbol_research_snapshot(self.inputs,as_of=self.inputs.captured_at)

    def status(self) -> dict[str,object]:
        return {"schema":"OB_EDGAR_RESEARCH_INTAKE_V1",
                "symbol":self.inputs.identity.symbol,
                "cik":self.inputs.identity.sec_cik,
                "source_reference":self.source_reference,
                "as_of":self.inputs.captured_at.isoformat(),
                "verified_accessions":self.accepted_accessions,
                "filings_selected":self.filings,
                "financial_facts_selected":self.selected_facts,
                "coverage":self.historical_filing_coverage,
                "timestamp_assurance":self.timestamp_assurance,
                "cache_receipts":dict(self.source_receipts),
                "cache_receipts_not_live_feed":True,
                "current_equity_quote":False,
                "current_option_quote":False,
                "execution_authorized":False}


def build_edgar_research(*, identity:SymbolRow,
                         submissions:Mapping[str,object],
                         companyfacts:Mapping[str,object],
                         received_at:datetime,
                         event_rights:SourceRights,
                         fundamental_rights:FundamentalRights,
                         max_events:int=60,max_facts:int=200)->EdgarResearchBundle:
    _aware(received_at,"EDGAR source receipt")
    if identity.identity_status!="CROSS_REFERENCED" or not identity.sec_cik or (
        not _CIK.fullmatch(identity.sec_cik)) or identity.directory_observed_at>received_at:
        raise ValueError("directory+SEC independently cross-referenced identity required")
    cik=identity.sec_cik
    if _official_cik(submissions,"submissions")!=cik or _official_cik(companyfacts,"companyfacts")!=cik:
        raise ValueError("SEC issuer CIK differs from directory-cross-referenced symbol")
    if not 1<=max_events<=100 or not 1<=max_facts<=1000:
        raise ValueError("bounded EDGAR fact/event selection required")
    if (event_rights.source_id!="sec-edgar" or event_rights.upstream_family!="SEC-EDGAR"
        or not event_rights.reviewed_for_scan() or event_rights.verified_at>received_at
        or event_rights.expires_at is not None and received_at>=event_rights.expires_at
        or "event" not in event_rights.entitled_instruments or not event_rights.owner_display):
        raise ValueError("reviewed SEC owner-event permissions required")
    if (fundamental_rights.source_id!="sec-edgar" or
        not fundamental_rights.owner_display or
        not fundamental_rights.allowed_at(received_at)):
        raise ValueError("reviewed SEC financial research and owner display required")
    rows=_recent_rows(submissions)
    accepted,conflicts=acceptance_evidence(submissions,received_at=received_at)
    recent=submissions["filings"]["recent"]
    # Keep SEC column alignment by filtering whole rows together, never one column
    # independently. Top recent filings of interest; facts still join against all
    # accepted accessions in the official recent submission snapshot.
    selected=[i for accession,form,_,_,i in rows
              if form in _FORMS and accession in accepted][:max_events]
    narrow={**submissions,"filings":{"recent":{
        key:[values[i] for i in selected] for key,values in recent.items()
        if isinstance(values,list) and len(values)==len(recent["accessionNumber"])
    }}}
    # parse_sec_submissions uses the actual official primary-document and source
    # acceptance value; unverified timestamps are not invented.
    filing_events=parse_sec_submissions(json.dumps(narrow),universe={identity.symbol:identity},
                                        received_at=received_at,max_items_per_issuer=max_events)
    filing_events=[x for x in filing_events
                   if x.evidence.observation_id.split(":")[2] in accepted]
    facts=parse_companyfacts(companyfacts,cik=cik,accepted_accessions=accepted,
                             rights=fundamental_rights,reviewed_at=received_at,
                             max_facts=max_facts)
    inputs=SymbolResearchInputs(
        identity=identity,captured_at=received_at,
        financial_facts=facts,financial_rights=fundamental_rights,
        issuer_events=tuple(filing_events),event_rights={"sec-edgar":event_rights})
    older=submissions.get("filings",{}).get("files",[])
    return EdgarResearchBundle(
        inputs=inputs,accepted_accessions=len(accepted),filings=len(filing_events),
        selected_facts=len(facts),
        source_reference=f"https://data.sec.gov/submissions/CIK{cik}.json",
        historical_filing_coverage=(
            "RECENT_ONLY_OLDER_PAGES_NOT_IMPORTED" if older else
            "RECENT_ENDPOINT_ONLY_NO_FULL_HISTORY_ASSERTION"))
