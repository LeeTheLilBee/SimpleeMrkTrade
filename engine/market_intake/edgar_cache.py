"""Checked offline SEC EDGAR snapshot reader and opt-in Tower research resolver.

This is *not* a network client or a source of market prices. A specific official
CIK and checksum-matching provenance receipt must match every read. It is
designed for backend owner-authorized integration, not a public query endpoint.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from .contracts import SourceRights, _aware, clean_symbol
from .edgar_research import EdgarResearchBundle, build_edgar_research
from .fundamental_research import FundamentalRights
from .universe import SymbolRow

MAX_FILE_BYTES=32_000_000
METADATA_SKEW_SECONDS=120


def read_sec_cache(*,root:Path,cik:str,kind:str)->tuple[dict,datetime]:
    if not isinstance(root,Path):
        raise TypeError("EDGAR cache root must be an explicit Path")
    if not isinstance(cik,str) or len(cik)!=10 or not cik.isdigit():
        raise ValueError("exact padded CIK required")
    if kind not in {"submissions","companyfacts"}:
        raise ValueError("only supported reviewed SEC product")
    suffix="" if kind=="submissions" else ".companyfacts"
    name=f"CIK{cik}{suffix}.json"
    url=(f"https://data.sec.gov/submissions/CIK{cik}.json" if kind=="submissions"
         else f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    path=root/name
    meta_path=root/f"{name}.http-metadata.json"
    if path.is_symlink() or meta_path.is_symlink():
        raise ValueError("untrusted EDGAR cache symlink")
    raw=path.read_bytes()
    if not raw or len(raw)>MAX_FILE_BYTES:
        raise ValueError("SEC snapshot size invalid")
    meta=json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(meta,dict) or meta.get("url")!=url or (
        meta.get("source_type")!="PUBLIC_SEC_REFERENCE_NOT_QUOTE" or
        meta.get("sha256")!=sha256(raw).hexdigest()):
        raise ValueError("SEC provenance URL or cached digest invalid")
    at=datetime.fromisoformat(str(meta.get("retrieved_at","")).replace("Z","+00:00"))
    _aware(at,"SEC snapshot receipt")
    if at>datetime.now(timezone.utc)+timedelta(seconds=METADATA_SKEW_SECONDS):
        raise ValueError("future SEC snapshot receipt")
    payload=json.loads(raw)
    if not isinstance(payload,dict) or isinstance(payload.get("cik"),bool) or (
        str(payload.get("cik")).zfill(10)!=cik):
        raise ValueError("SEC cached issuer mismatch")
    if kind=="submissions" and not isinstance(payload.get("filings"),dict):
        raise ValueError("SEC submissions missing")
    if kind=="companyfacts" and not isinstance(payload.get("facts"),dict):
        raise ValueError("SEC financial concepts missing")
    return payload,at


def checked_cached_research(*,identity:SymbolRow,root:Path,
                            event_rights:SourceRights,
                            fundamental_rights:FundamentalRights,
                            at:datetime|None=None)->EdgarResearchBundle:
    if not identity.sec_cik:
        raise ValueError("directory/SEC issuer identity not cross-referenced")
    submissions,sub_at=read_sec_cache(root=root,cik=identity.sec_cik,kind="submissions")
    facts,facts_at=read_sec_cache(root=root,cik=identity.sec_cik,kind="companyfacts")
    captured=max(sub_at,facts_at)
    # A snapshot must not be silently recast as newer at request time.
    if at is not None:
        _aware(at,"owner research time")
        if at<captured:raise ValueError("research time precedes source evidence")
    return build_edgar_research(identity=identity,submissions=submissions,
        companyfacts=facts,received_at=captured,event_rights=event_rights,
        fundamental_rights=fundamental_rights)


def make_owner_edgar_resolver(*,identities:Mapping[str,SymbolRow],root:Path,
                              event_rights:SourceRights,
                              fundamental_rights:FundamentalRights):
    """Create a read-only resolver to inject into Tower's pre-existing guard.

    Caller, not this module, must vet the identity registry and rights against
    the actual owner/provider policy. No connection is configured automatically.
    """
    if not isinstance(identities,Mapping) or not isinstance(root,Path):
        raise ValueError("trusted symbol registry and dedicated cache path required")
    approved=dict(identities)
    for symbol,row in approved.items():
        if not isinstance(row,SymbolRow) or row.symbol!=clean_symbol(symbol):
            raise ValueError("invalid authoritative symbol registry")
    def resolver(room:str,symbol:str):
        if room not in {"symbol_page","market_map","trade_center","review_center"}:
            raise ValueError("unapproved room")
        symbol=clean_symbol(symbol)
        if symbol not in approved:
            return None
        try:
            return checked_cached_research(identity=approved[symbol],root=root,
                event_rights=event_rights,
                fundamental_rights=fundamental_rights).inputs
        except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError):
            # Tower will hide unavailable source rather than inject made-up facts.
            return None
    return resolver
