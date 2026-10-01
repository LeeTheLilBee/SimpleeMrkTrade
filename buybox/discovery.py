"""Universal discovery: explicit sources, normalization, cautious duplicate suggestions.

Never merges opportunities automatically on uncertain seller/listing similarity.
"""
from __future__ import annotations
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from decimal import Decimal
from .registry import get_vertical

TRACKING = {"utm_source","utm_medium","utm_campaign","utm_content","utm_term",
            "fbclid","gclid","msclkid"}

def canonical_url(url):
    if not url:
        return None
    parsed = urlsplit(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    query = [(k,v) for k,v in parse_qsl(parsed.query, keep_blank_values=True)
             if k.lower() not in TRACKING]
    return urlunsplit((parsed.scheme.lower(),parsed.netloc.lower(),
                       parsed.path.rstrip("/") or "/", urlencode(sorted(query)), ""))

def fingerprint(opportunity):
    """Conservative identity tokens; not an authoritative ownership match."""
    location = opportunity.get("location") or {}
    return {
        "vertical": opportunity["vertical"],
        "source_urls": frozenset(
            filter(None,(canonical_url(s.get("url")) for s in opportunity.get("sources",[])
                         if isinstance(s,dict)))),
        "name": " ".join(opportunity["name"].casefold().split()),
        "postal_code": str(location.get("postal_code") or "").casefold(),
        "seller_reference": str(opportunity.get("seller_reference") or "").strip().casefold(),
    }

def duplicate_candidates(opportunity, existing):
    own = fingerprint(opportunity)
    results=[]
    for other in existing:
        if opportunity["id"] == other["id"] or opportunity["vertical"]!=other["vertical"]:
            continue
        candidate = fingerprint(other)
        matching_urls = own["source_urls"] & candidate["source_urls"]
        if matching_urls:
            results.append({"id":other["id"],"reason":"EXACT_SOURCE_URL",
                            "confidence":"HIGH","auto_merge":False})
        elif own["seller_reference"] and own["seller_reference"]==candidate["seller_reference"]:
            results.append({"id":other["id"],"reason":"MATCHING_SELLER_REFERENCE",
                            "confidence":"REVIEW","auto_merge":False})
        elif own["name"] and own["name"]==candidate["name"] and own["postal_code"] and own["postal_code"]==candidate["postal_code"]:
            results.append({"id":other["id"],"reason":"NAME_AND_POSTAL_CODE",
                            "confidence":"REVIEW","auto_merge":False})
    return results

def filter_opportunities(opportunities, *, vertical=None, query="", max_price=None,
                         judgment=None, min_evidence_confidence=None, evaluator=None):
    if vertical is not None:
        get_vertical(vertical)
    needle=query.casefold().strip()
    maxp=Decimal(str(max_price)) if max_price is not None else None
    found=[]
    for op in opportunities:
        if vertical is not None and op["vertical"]!=vertical:
            continue
        if needle and needle not in (op["name"]+" "+str(op.get("location") or {})).casefold():
            continue
        if maxp is not None:
            if op.get("asking_price") is None or Decimal(str(op["asking_price"])) > maxp:
                continue
        evaluation=evaluator(op) if evaluator and (judgment is not None or min_evidence_confidence is not None) else None
        if judgment is not None and (not evaluation or evaluation["judgment"]!=judgment):
            continue
        if min_evidence_confidence is not None and (not evaluation or evaluation["evidence"]["confidence_percent"] < min_evidence_confidence):
            continue
        found.append(op)
    return found

def card(opportunity, evaluation):
    manifest=get_vertical(opportunity["vertical"])
    return {"id":opportunity["id"],"title":opportunity["name"],
            "vertical":opportunity["vertical"],"vertical_label":manifest["label"],
            "location":opportunity.get("location"),"asking_price":opportunity.get("asking_price"),
            "judgment":evaluation["judgment"],
            "evidence_confidence":evaluation["evidence"]["confidence_percent"],
            "financials":evaluation["financials"],
            "top_risk":evaluation["findings"][0]["reason"] if evaluation["findings"] else None,
            "readiness":evaluation["teller_readiness"],
            "metrics":{k:opportunity.get("metrics",{}).get(k) for k in manifest["metrics"]
                       if k in opportunity.get("metrics",{})}}
