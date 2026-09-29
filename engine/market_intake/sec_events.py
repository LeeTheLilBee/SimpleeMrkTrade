"""SEC public-submissions parser for approved offline input; never a quote or news-price proxy.

Only a directory-resolved CIK can associate a filing with an OB symbol.
Uses SEC acceptanceDateTime with explicit offset; receipt time is never substituted
as an issuer event timestamp. No HTTP and no automatic data-rights grant.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import PurePosixPath
import re
from typing import Mapping

from .contracts import DiscoveryEvent, Observation, _aware
from .universe import SymbolRow

ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")
DOCUMENT = re.compile(r"^[A-Za-z0-9_.-]{1,180}$")


def parse_sec_submissions(contents: str, *, universe: Mapping[str, SymbolRow],
                          received_at: datetime, max_items_per_issuer: int = 20) -> list[DiscoveryEvent]:
    _aware(received_at, "received_at")
    if not 1 <= max_items_per_issuer <= 100:
        raise ValueError("bounded issuer intake required")
    if not isinstance(contents, str) or len(contents) > 20_000_000:
        raise ValueError("unsupported SEC source size")
    data = json.loads(contents)
    if not isinstance(data, dict):
        raise ValueError("expected SEC issuer submissions JSON")
    raw_cik = str(data.get("cik", ""))
    if not raw_cik.isdigit():
        raise ValueError("issuer CIK missing")
    cik = raw_cik.zfill(10)
    matches = [row for row in universe.values() if row.sec_cik == cik]
    if not matches:
        return []  # Never turn an unbound SEC entity into a guessed ticker.
    recent = data.get("filings", {}).get("recent", {})
    keys = ("accessionNumber", "form", "acceptanceDateTime", "primaryDocument")
    if not isinstance(recent, dict) or any(not isinstance(recent.get(k), list) for k in keys):
        raise ValueError("SEC recent-filing arrays missing")
    lengths = [len(recent[k]) for k in keys]
    if len(set(lengths)) != 1:
        raise ValueError("SEC parallel filing arrays have mismatched lengths")
    result = []
    for i in range(min(lengths[0], max_items_per_issuer)):
        accession, form = str(recent["accessionNumber"][i]), str(recent["form"][i])
        if not ACCESSION.fullmatch(accession) or not form.strip():
            continue
        try:
            observed = datetime.fromisoformat(str(recent["acceptanceDateTime"][i]).replace("Z", "+00:00"))
        except ValueError:
            continue
        if observed.tzinfo is None or observed.utcoffset() is None:
            continue  # Ambiguous timestamps are not filled in from receipt time.
        primary = str(recent["primaryDocument"][i])
        if not DOCUMENT.fullmatch(primary) or PurePosixPath(primary).name != primary:
            primary = accession.replace("-", "") + "-index.html"
        url = (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
               f"{accession.replace('-', '')}/{primary}")
        for row in matches:
            obs = Observation(
                observation_id=f"SEC:{cik}:{accession}:{row.symbol}",
                source_id="sec-edgar", upstream_family="SEC-EDGAR",
                symbol=row.symbol, observed_at=observed, received_at=received_at,
                provenance_reference=url, feed_label="unknown", instrument="event")
            result.append(DiscoveryEvent(obs, "filing",
                f"SEC form {form.strip()} accepted for {row.symbol}", url, cik))
    return result
