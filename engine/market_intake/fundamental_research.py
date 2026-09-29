"""OBINTEL011-016: exact-CIK SEC company facts with acceptance-time evidence.

This parser consumes *reviewed offline* SEC companyfacts JSON plus an independent
exact-accession acceptance timestamp map, e.g. from official submissions. It has
no HTTP client and makes no assumption that SEC filing date equals availability
time. Raw GAAP concepts are not collapsed into fabricated comparable ratios.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Mapping
import re

from .contracts import _aware

ACCESSION=re.compile(r"^\d{10}-\d{2}-\d{6}$")
CONCEPT_UNITS={
    "Assets":"USD", "Liabilities":"USD", "StockholdersEquity":"USD",
    "CashAndCashEquivalentsAtCarryingValue":"USD", "NetIncomeLoss":"USD",
    "Revenues":"USD", "RevenueFromContractWithCustomerExcludingAssessedTax":"USD",
    "EarningsPerShareDiluted":"USD/shares",
}
FORMS={"10-K","10-Q","10-K/A","10-Q/A","20-F","20-F/A"}


@dataclass(frozen=True)
class FundamentalRights:
    source_id: str
    reference: str
    reviewed_at: datetime
    internal_research: bool = False
    owner_display: bool = False
    ai_explanation: bool = False
    retention: bool = False
    expires_at: datetime | None = None

    def __post_init__(self):
        _aware(self.reviewed_at,"fundamentals rights approval")
        if not self.source_id.strip() or not self.reference.strip():
            raise ValueError("source and terms reference required")
        if self.expires_at is not None:
            _aware(self.expires_at,"expiry")
            if self.expires_at <= self.reviewed_at: raise ValueError("invalid expiry")

    def allowed_at(self,now:datetime)->bool:
        _aware(now,"fundamental research time")
        return (self.internal_research and self.reviewed_at <= now and
                (self.expires_at is None or now < self.expires_at))


@dataclass(frozen=True)
class CompanyFact:
    cik: str
    accession: str
    concept: str
    unit: str
    value: float
    fiscal_end: date
    accepted_at: datetime
    form: str
    provenance_reference: str

    def __post_init__(self):
        if not self.cik.isdigit() or len(self.cik)!=10 or not ACCESSION.fullmatch(self.accession):
            raise ValueError("exact issuer and accession identity required")
        if self.concept not in CONCEPT_UNITS or CONCEPT_UNITS[self.concept] != self.unit:
            raise ValueError("unsupported unnormalized GAAP fact")
        if self.form not in FORMS:raise ValueError("supported SEC form required")
        if not isinstance(self.fiscal_end,date) or isinstance(self.fiscal_end,datetime):
            raise ValueError("actual fiscal period end required")
        if type(self.value) not in {int,float} or not isfinite(self.value):
            raise ValueError("finite SEC numeric fact required")
        _aware(self.accepted_at,"SEC filing acceptance")
        if self.accepted_at.date()<self.fiscal_end:
            raise ValueError("acceptance predates reported fiscal end")
        if not self.provenance_reference.startswith("https://www.sec.gov/Archives/edgar/data/"):
            raise ValueError("official accession source required")


def parse_companyfacts(payload: Mapping[str,object], *, cik: str,
                       accepted_accessions: Mapping[str,datetime],
                       rights: FundamentalRights, reviewed_at: datetime,
                       max_facts: int = 200) -> tuple[CompanyFact,...]:
    """Fail-closed selected concept extraction, bound to independent acceptance times."""
    _aware(reviewed_at,"source receipt")
    if not rights.allowed_at(reviewed_at) or rights.source_id!="sec-edgar":
        raise ValueError("SEC fundamentals rights not reviewed")
    if type(max_facts) is not int or not 1<=max_facts<=1000:
        raise ValueError("bounded fact intake required")
    if not isinstance(cik,str) or not cik.isdigit() or len(cik)!=10:
        raise ValueError("exact ten-digit CIK required")
    raw_cik=payload.get("cik")
    if isinstance(raw_cik,bool) or str(raw_cik).zfill(10)!=cik:
        raise ValueError("SEC companyfacts issuer differs from reviewed CIK")
    us_gaap=payload.get("facts",{}).get("us-gaap",{}) if isinstance(payload.get("facts"),dict) else {}
    if not isinstance(us_gaap,dict):raise ValueError("SEC us-gaap facts malformed")
    facts: list[CompanyFact]=[]
    seen=set()
    for concept, unit in CONCEPT_UNITS.items():
        node=us_gaap.get(concept)
        if not isinstance(node,dict):continue
        values=node.get("units",{})
        if not isinstance(values,dict) or not isinstance(values.get(unit),list):continue
        for item in values[unit][:500]:
            if not isinstance(item,dict):continue
            accession=item.get("accn")
            if not isinstance(accession,str) or not ACCESSION.fullmatch(accession):continue
            accepted=accepted_accessions.get(accession)
            if not isinstance(accepted,datetime):continue
            _aware(accepted,"independent SEC acceptance")
            if accepted>reviewed_at:continue
            if item.get("form") not in FORMS:continue
            try:
                end=date.fromisoformat(str(item["end"]))
                filed=date.fromisoformat(str(item["filed"]))
            except (ValueError,KeyError,TypeError):continue
            if filed>accepted.date():continue
            value=item.get("val")
            if type(value) not in {int,float} or not isfinite(value):continue
            unique=(accession,concept,unit,end)
            if unique in seen:continue
            seen.add(unique)
            url=(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                 f"{accession.replace('-','')}/{accession.replace('-','')}-index.html")
            try:
                facts.append(CompanyFact(cik,accession,concept,unit,float(value),end,
                                         accepted,item["form"],url))
            except ValueError:continue
    facts.sort(key=lambda x:(x.accepted_at,x.accession,x.concept,x.fiscal_end))
    return tuple(facts[-max_facts:])


def fundamental_context(*, cik: str, facts: tuple[CompanyFact,...],
                        rights: FundamentalRights, as_of: datetime) -> dict[str,object]:
    _aware(as_of,"research cut-off")
    if not rights.allowed_at(as_of) or rights.owner_display is not True:
        raise ValueError("fundamental research/owner-display permission expired or absent")
    eligible=[x for x in facts if x.cik==cik and x.accepted_at <= as_of]
    latest:dict[str,CompanyFact]={}
    for row in eligible:
        old=latest.get(row.concept)
        if old is None or (row.fiscal_end,row.accepted_at) > (old.fiscal_end,old.accepted_at):
            latest[row.concept]=row
    # Compare only exact year-end, point-in-time balance-sheet concepts. Do NOT
    # treat reported revenue/earnings values as annual without their start/length
    # metadata; SEC filings may also report quarterly and year-to-date facts.
    point_in_time={"Assets","Liabilities","StockholdersEquity",
                   "CashAndCashEquivalentsAtCarryingValue"}
    comparisons=[]
    for concept in sorted(point_in_time):
        periods={}
        for row in eligible:
            if row.concept!=concept or row.form not in {"10-K","10-K/A"}:continue
            previous=periods.get(row.fiscal_end)
            if previous is None or row.accepted_at>previous.accepted_at:
                periods[row.fiscal_end]=row
        years=sorted(periods.values(),key=lambda row:row.fiscal_end)
        if len(years)<2:continue
        older,newer=years[-2:]
        spacing=(newer.fiscal_end-older.fiscal_end).days
        if not 300<=spacing<=430 or older.value==0:continue
        comparisons.append({
            "concept":concept,"unit":newer.unit,
            "earlier_fiscal_end":older.fiscal_end.isoformat(),
            "later_fiscal_end":newer.fiscal_end.isoformat(),
            "earlier_value":older.value,"later_value":newer.value,
            "reported_change_pct":(newer.value-older.value)/abs(older.value)*100,
            "earlier_source":older.provenance_reference,
            "later_source":newer.provenance_reference,
            "retrospective_only":True,"revisions_as_of":as_of.isoformat(),
        })
    # Preserve form, GAAP concept, period and original SEC citation for each fact.
    return {"schema":"OB_SEC_FUNDAMENTALS_CONTEXT_V1","cik":cik,
            "as_of":as_of.isoformat(),"source_id":rights.source_id,
            "state":"SOURCE_BOUND" if latest else "NO_VERIFIED_FACTS",
            "reported_concepts":[{
                "concept":v.concept,"value":v.value,"units":v.unit,
                "fiscal_end":v.fiscal_end.isoformat(),"accepted_at":v.accepted_at.isoformat(),
                "accession":v.accession,"form":v.form,"reference":v.provenance_reference,
            } for v in sorted(latest.values(),key=lambda x:x.concept)],
            "raw_concepts_not_normalized":True,
            "year_end_balance_sheet_comparisons":comparisons,
            "comparisons_are_unadjusted_retrospective_facts":True,
            "historical_context_only":True,"quote_eligible":False,
            "signal_eligible":False,"execution_authorized":False,
            "ai_explanation_allowed":rights.ai_explanation,
            "owner_display_allowed":rights.owner_display}
