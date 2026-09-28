"""First-party FRED + Our World in Data context adapters.

No outbound I/O on import. Caller provides an audited HTTPS transport and an
explicit per-series/per-chart owner license clearance. No API key is written
into responses, exceptions, logs or rendered URLs. Never use these responses
as intraday stock/option quotes or as trading authorizations.
"""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from urllib.parse import urlencode
from typing import Callable, Mapping

from engine.market_scanner.source_contract import (
    Observation, collection_time, decimal_value, iso_period, macro_envelope,
)

FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations"
OWID_BASE = "https://ourworldindata.org/grapher/"
FRED_SERIES = {
    "DGS2": ("Two-year Treasury constant maturity", "percent", "daily"),
    "DGS10": ("Ten-year Treasury constant maturity", "percent", "daily"),
    "FEDFUNDS": ("Effective federal funds rate", "percent", "monthly"),
    "CPIAUCSL": ("Consumer Price Index", "index", "monthly"),
    "UNRATE": ("Unemployment rate", "percent", "monthly"),
}
_SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fred_observations(*, series_id: str, api_key: str | None,
                      permission_approved: bool,
                      get_json: Callable[[str], dict] | None,
                      collected_at: datetime) -> dict:
    """FRED V1 server-only macro fetch. Permission is specific to THIS series."""
    if series_id not in FRED_SERIES:
        return macro_envelope([], status="invalid_source", reason="Series is not in scanner allowlist")
    if not permission_approved:
        return macro_envelope([], status="license_review_required",
                              reason="Owner/series reuse approval not recorded")
    if not api_key or not re.fullmatch(r"[a-z0-9]{32}", api_key):
        return macro_envelope([], status="not_configured", reason="Server FRED API key unavailable")
    if get_json is None:
        return macro_envelope([], status="not_configured", reason="Approved server transport unavailable")
    url = FRED_ENDPOINT + "?" + urlencode({
        "series_id": series_id, "api_key": api_key, "file_type": "json",
        "sort_order": "desc", "limit": 4,
    })
    try:
        response = get_json(url)
        if not isinstance(response, dict) or not isinstance(response.get("observations"), list):
            raise ValueError("Malformed provider observations")
        rows = []
        for raw in response["observations"]:
            if not isinstance(raw, dict):
                continue
            try:
                period = iso_period(raw.get("date"))
                value = decimal_value(raw.get("value"))
                vintage_start = iso_period(raw["realtime_start"]) if raw.get("realtime_start") else None
                vintage_end = iso_period(raw["realtime_end"]) if raw.get("realtime_end") else None
            except ValueError:
                continue
            label, units, cadence = FRED_SERIES[series_id]
            rows.append(Observation(
                source="FRED", series_id=series_id, title=label,
                region="US", period=period, value=value, units=units, cadence=cadence,
                source_url="https://fred.stlouisfed.org/series/" + series_id,
                license_status="approved_for_specified_owner_context_only",
                collected_at=collection_time(collected_at),
                vintage_start=vintage_start, vintage_end=vintage_end,
            ))
        if not rows:
            return macro_envelope([], status="source_unavailable", reason="No valid provider observation")
        return macro_envelope(rows[:4], status="source_observed")
    except Exception:
        # Never leak an exception that could contain the api_key embedded in the FRED URL.
        return macro_envelope([], status="source_unavailable",
                              reason="FRED provider request or validation failed")


def owid_observations(*, slug: str, column: str, entity_code: str,
                      chart_approved: bool, third_party_license_approved: bool,
                      get_csv: Callable[[str], str] | None,
                      get_json: Callable[[str], dict] | None,
                      collected_at: datetime) -> dict:
    """Only an owner-approved OWID chart/metric/entity; source chronology is preserved."""
    if not _SAFE_SLUG.fullmatch(slug or "") or not column or not re.fullmatch(r"[A-Z0-9_]{2,12}", entity_code or ""):
        return macro_envelope([], status="invalid_source", reason="Invalid approved chart request")
    if not chart_approved or not third_party_license_approved:
        return macro_envelope([], status="license_review_required",
                              reason="Chart and underlying third-party licensing must be reviewed separately")
    if get_csv is None or get_json is None:
        return macro_envelope([], status="not_configured", reason="Server OWID transport unavailable")
    page = OWID_BASE + slug
    try:
        metadata = get_json(page + ".metadata.json")
        csv_text = get_csv(page + ".csv")
        if not isinstance(metadata, dict) or not isinstance(csv_text, str):
            raise ValueError("Malformed OWID provider response")
        chart = metadata.get("chart")
        columns = metadata.get("columns")
        if not isinstance(chart, dict) or not isinstance(columns, dict):
            raise ValueError("Missing OWID citation/columns")
        details = columns.get(column)
        citation = chart.get("citation")
        if not isinstance(details, dict) or not isinstance(citation, str) or not citation.strip():
            raise ValueError("Unattributed or wrong OWID metric")
        units = details.get("unit")
        if not isinstance(units, str) or not units.strip():
            raise ValueError("Missing OWID units")
        reader = csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames or column not in reader.fieldnames or "Code" not in reader.fieldnames:
            raise ValueError("Metric not in chart CSV")
        field = "Day" if "Day" in reader.fieldnames else "Year" if "Year" in reader.fieldnames else None
        if not field:
            raise ValueError("No observation date column")
        rows = []
        for row in reader:
            if row.get("Code") != entity_code:
                continue
            try:
                period = iso_period(row.get(field), annual_allowed=field == "Year")
                value = decimal_value(row.get(column))
            except ValueError:
                continue
            rows.append(Observation(
                source="Our World in Data", series_id=slug + ":" + column,
                title=str(details.get("titleShort") or column)[:150],
                region=entity_code, period=period, value=value, units=units.strip(),
                cadence="daily" if field == "Day" else "annual",
                source_url=page, license_status="chart_and_underlying_source_reviewed_for_owner_context_only",
                collected_at=collection_time(collected_at),
            ))
        if not rows:
            return macro_envelope([], status="source_unavailable", reason="No valid observations for selected entity")
        rows.sort(key=lambda o: o.period, reverse=True)
        env = macro_envelope(rows[:4], status="source_observed")
        env["attribution"] = "Our World in Data; " + citation.strip()[:600]
        env["metadata_url"] = page + ".metadata.json"
        return env
    except Exception:
        return macro_envelope([], status="source_unavailable", reason="OWID provider data or citation validation failed")
