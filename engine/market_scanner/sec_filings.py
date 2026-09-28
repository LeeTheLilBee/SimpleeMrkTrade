"""OBDATA016: SEC EDGAR filings context, never stock-price or broker evidence.

Official JSON submissions endpoint. No unauthenticated HTML scraping; caller
is responsible for a truthful descriptive User-Agent, host allowlist, bounded
request budget, timeout and fair access. There is deliberately no network I/O
here; the parser receives a response from the separately approved transport.
"""
from __future__ import annotations

from datetime import date
from typing import Mapping
import re

SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
TYPES = {"10-K", "10-Q", "8-K", "20-F", "6-K", "40-F"}
SAFE_ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")


def submissions_url(cik: int) -> str:
    if type(cik) is not int or cik <= 0 or cik > 9_999_999_999:
        raise ValueError("Valid official numeric CIK required")
    return SEC_SUBMISSIONS.format(cik=cik)


def filing_context(*, cik: int, payload: Mapping | None,
                   access_policy_verified: bool, owner_use_permitted: bool) -> dict:
    """Parse previously obtained issuer submission JSON; no quote synthesis."""
    status = {
        "schema": "OBDATA016_SEC_CONTEXT_V1",
        "kind": "public_filing_research",
        "cik": cik,
        "source": submissions_url(cik),
        "status": "HOLD", "reason": "",
        "filings": [],
        "market_quotes": [], "options_chains": [], "positions": [],
        "manual_live_queue": [], "trading_authorized": False,
    }
    if not access_policy_verified or not owner_use_permitted:
        status["reason"] = "SEC fair-access identity/use policy not verified"
        return status
    if not isinstance(payload, Mapping) or str(payload.get("cik", "")).lstrip("0") != str(cik):
        status["reason"] = "Missing or mismatched SEC issuer response"
        return status
    recent = payload.get("filings", {}).get("recent") if isinstance(payload.get("filings"), Mapping) else None
    if not isinstance(recent, Mapping):
        status["reason"] = "Missing official recent filing entries"
        return status
    keys = ("accessionNumber", "filingDate", "form", "primaryDocument")
    if any(not isinstance(recent.get(key), list) for key in keys):
        status["reason"] = "Malformed official filing columns"
        return status
    if len({len(recent[key]) for key in keys}) != 1:
        status["reason"] = "Filing metadata columns are not aligned"
        return status
    out = []
    for accession, filing_day, form, primary in zip(*(recent[key] for key in keys)):
        if form not in TYPES or not isinstance(accession, str) or not SAFE_ACCESSION.fullmatch(accession):
            continue
        try:
            day = date.fromisoformat(str(filing_day))
        except ValueError:
            continue
        if not isinstance(primary, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,130}", primary):
            continue
        out.append({
            "form": form,
            "accession_number": accession,
            "filing_date": day.isoformat(),
            "cik": cik,
            "official_source": status["source"],
            "research_only": True,
            "provider_quote_as_of": None,
        })
        if len(out) >= 12:
            break
    status["status"] = "SOURCE_OBSERVED" if out else "NO_ELIGIBLE_FILINGS"
    status["filings"] = out
    status["reason"] = ("Official company filing metadata; not an intraday market observation"
                        if out else "No eligible recent filings")
    return status
