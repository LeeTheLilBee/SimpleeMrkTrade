"""OBINTEL028: source-reference memory and deterministic Soulaana research brief.

This is an in-memory rehearsal ledger of NON-PRICE metadata, not a persistent
data store. It refuses unsupported retention and never records a broker action,
financial values, raw quote, account secret or feed token. A real durable ledger
would require Tower owner authorization and Archive Vault retention decisions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json

from .contracts import _aware
from .symbol_research import SymbolResearchInputs
from .research_bridge import project_research


@dataclass(frozen=True)
class ResearchMemoryReceipt:
    receipt_id: str
    symbol: str
    observed_at: str
    evidence_digest: str
    source_references: tuple[str,...]
    state: str = "RESEARCH_MEMORY_METADATA_ONLY"
    can_admit_candidate: bool = False
    can_authorize_order: bool = False


class ResearchReferenceLedger:
    """Memory for tested research *references* only; no raw vendor data retention."""

    def __init__(self):
        self._receipts:dict[str,ResearchMemoryReceipt]={}
        self._latest:dict[str,datetime]={}

    def append(self, inputs:SymbolResearchInputs, *, receipt_id:str) -> ResearchMemoryReceipt:
        if not isinstance(receipt_id,str) or not receipt_id.strip() or len(receipt_id)>100:
            raise ValueError("nonblank bounded owner audit receipt required")
        if receipt_id in self._receipts:
            raise ValueError("duplicate memory receipt")
        if inputs.history is not None and not inputs.history.rights.retention_allowed:
            raise ValueError("historical feed retention was not separately permitted")
        if inputs.financial_facts and (
            inputs.financial_rights is None or not inputs.financial_rights.retention):
            raise ValueError("fundamental record retention not reviewed")
        # Event references are intentionally excluded because SourceRights does not
        # grant persistence rights. A real Archive Vault integration must separately
        # assess retention before accepting an issuer-event artifact.
        refs=[inputs.identity.source_file]
        if inputs.history is not None:
            refs.append(inputs.history.snapshot_reference)
        if inputs.financial_facts:
            refs.extend(row.provenance_reference for row in inputs.financial_facts)
        refs=sorted(set(refs))
        if any(not isinstance(ref,str) or not ref.strip() or len(ref)>500 for ref in refs):
            raise ValueError("bounded non-secret source references required")
        previous=self._latest.get(inputs.identity.symbol)
        if previous is not None and inputs.captured_at <= previous:
            raise ValueError("research memory must move forward in event time")
        content=json.dumps({"symbol":inputs.identity.symbol,
                            "source_references":refs,
                            "captured_at":inputs.captured_at.isoformat()},
                           sort_keys=True,separators=(",",":"))
        item=ResearchMemoryReceipt(receipt_id,inputs.identity.symbol,inputs.captured_at.isoformat(),
                                   sha256(content.encode("utf-8")).hexdigest(),tuple(refs))
        self._receipts[receipt_id]=item
        self._latest[inputs.identity.symbol]=inputs.captured_at
        return item

    def get(self,receipt_id:str)->ResearchMemoryReceipt|None:
        return self._receipts.get(receipt_id)

    def forget_runtime(self)->None:
        """Process stop / revocation clears transient references without fallback."""
        self._receipts.clear()
        self._latest.clear()


def soulaana_research_brief(packet:dict)->dict[str,object]:
    """A deterministic translation of permission-filtered evidence, never an AI-created fact."""
    view=project_research(packet,"soulaana")
    history=view["history"]
    facts=view["fundamentals"]
    events=view["issuer_events"]
    scanner=view["market_sources"]
    sections=[]
    if history["state"]=="SOURCE_BOUND_HISTORY":
        sections.append("Reviewed completed-session price history is available, not a live quote.")
    elif history["state"]=="EXPLANATION_RIGHTS_HOLD":
        sections.append("Historical feed terms do not allow assistant explanation of its values.")
    else:
        sections.append("Verified historical price context is unavailable.")
    if facts["state"]=="SOURCE_BOUND":
        sections.append("SEC reported concepts are issuer-bound and retain their fiscal periods and citations.")
    elif facts["state"]=="EXPLANATION_RIGHTS_HOLD":
        sections.append("Financial-source AI-use permission is not approved.")
    else:
        sections.append("Issuer financial concepts remain unavailable or under review.")
    if events:
        sections.append(f"{len(events)} source-cited issuer event(s) are available as research leads.")
    if scanner["scanner_state"]=="AI_SOURCE_RIGHTS_HOLD":
        sections.append("Issuer-event and current-source AI-use rights are not established; source details are withheld.")
    elif scanner["scanner_state"]=="CONFLICT_HOLD":
        sections.append("Independent price evidence disagrees. Research remains on hold.")
    elif not scanner["equity_sources"]:
        sections.append("No approved current underlying quote is attached to this research brief.")
    else:
        sections.append("Current scanner source IDs are present; broker execution proof is separate.")
    return {
        "schema":"OB_SOULAANA_SOURCE_RESEARCH_BRIEF_V1",
        "symbol":view["symbol"],"as_of":view["as_of"],
        "statements":sections,
        "source_event_references":[e.get("reference") for e in events],
        "historical_source_reference":history.get("snapshot_reference"),
        "next_useful_action":"Inspect cited source evidence and existing OB gates before changing a candidate.",
        "generated_explanations_not_factual_sources":True,
        "can_grant_data_rights":False,"can_authorize_trading":False,
        "can_override_tower":False,
    }
