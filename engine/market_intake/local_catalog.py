"""Zero-network symbol catalog ingestion. Run from repo root after approved downloads.

Example:
 python -m engine.market_intake.local_catalog \
   --nasdaq path/to/nasdaqlisted.txt --other path/to/otherlisted.txt \
   --sec path/to/company_tickers_exchange.json

No provider request, API key, webhook, live quote, or permanent server is started.
Output is a metadata snapshot printed to stdout, NOT data/market_universe.json.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .sec_events import parse_sec_submissions
from .universe import (directory_snapshot, parse_nasdaq_directory,
                       parse_sec_ticker_exchange, reconcile_symbol_universe)


def run(nasdaq_file: Path, other_file: Path, sec_file: Path | None = None,
        submission_files: tuple[Path, ...] = ()) -> dict[str, object]:
    timestamp = datetime.now(timezone.utc)
    first = parse_nasdaq_directory(nasdaq_file.read_text(encoding="utf-8"),
                                   directory="nasdaqlisted.txt", observed_at=timestamp)
    second = parse_nasdaq_directory(other_file.read_text(encoding="utf-8"),
                                    directory="otherlisted.txt", observed_at=timestamp)
    sec = parse_sec_ticker_exchange(sec_file.read_text(encoding="utf-8")) if sec_file else None
    rows = reconcile_symbol_universe(first, second, sec)
    extracted = []
    for file in submission_files:
        extracted.extend(parse_sec_submissions(file.read_text(encoding="utf-8"),
                      universe=rows, received_at=timestamp))
    # Extraction is not automatic entitlement or proof the filing was newly published.
    filing_samples = [{"symbol": e.evidence.symbol, "form": e.headline,
                       "accepted_at": e.evidence.observed_at.isoformat(),
                       "source": e.evidence.source_id,
                       "reference": e.reference_url,
                       "gate": "SOURCE_RIGHTS_REVIEW_REQUIRED"}
                      for e in extracted[:12]]
    return {**directory_snapshot(rows), "filing_events_extracted": len(extracted),
            "filing_samples": filing_samples,
            "retrieved_from_local_files_at": timestamp.isoformat(),
            "directory_source_files": [nasdaq_file.name, other_file.name],
            "sec_cross_reference_provided": sec_file is not None,
            "research_only": True, "source_license_review_required": True,
            "not_promoted_to_active_ob_engine": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nasdaq", required=True, type=Path)
    parser.add_argument("--other", required=True, type=Path)
    parser.add_argument("--sec", type=Path)
    parser.add_argument("--submissions", type=Path, nargs="*", default=[])
    args = parser.parse_args()
    print(json.dumps(run(args.nasdaq, args.other, args.sec, tuple(args.submissions)), indent=2))


if __name__ == "__main__":
    main()
