"""Strict deterministic fingerprint for Official Catalyst Radar snapshots.

Validation lives beside the source contract; transport/replay/session logic does
not. The resulting digest can safely drive ObservatoryEventHub invalidations
without placing public-source facts on the WebSocket.
"""
from __future__ import annotations

from hashlib import sha256
import json

SOURCES = ("federal_register", "cftc", "eia", "world_bank", "nws", "sec_edgar")


def official_catalyst_fingerprint(packet):
    if (
        not isinstance(packet, dict)
        or packet.get("schema") != "OB_OFFICIAL_CATALYST_RADAR_V1"
        or packet.get("prices_attached") is not False
        or packet.get("broker_execution_authorized") is not False
    ):
        raise ValueError("CATALYST_FINGERPRINT_PACKET_HOLD")
    rows = packet.get("sources")
    if (
        not isinstance(rows, list)
        or len(rows) != len(SOURCES)
        or tuple(row.get("source") for row in rows) != SOURCES
    ):
        raise ValueError("CATALYST_FINGERPRINT_PACKET_HOLD")

    projection = []
    for row in rows:
        state = row.get("state")
        if (
            state not in {
                "SOURCE_BOUND", "NO_PUBLICATION", "REVIEW_HOLD", "SOURCE_HOLD",
                "KEY_REQUIRED", "EXISTING_PROTECTED_CORRIDOR",
            }
            or row.get("quote_eligible") is not False
            or row.get("execution_authorized") is not False
            or not isinstance(row.get("facts"), list)
            or len(row["facts"]) > 3
        ):
            raise ValueError("CATALYST_FINGERPRINT_PACKET_HOLD")
        if (
            row["source"] == "sec_edgar"
            and (state != "EXISTING_PROTECTED_CORRIDOR" or row["facts"])
        ):
            raise ValueError("CATALYST_FINGERPRINT_PACKET_HOLD")
        if state != "SOURCE_BOUND" and row["facts"]:
            raise ValueError("CATALYST_FINGERPRINT_PACKET_HOLD")
        projection.append({
            "source": row["source"],
            "state": state,
            "facts": row["facts"],
            "ai_use_approved": row.get("ai_use_approved") is True,
        })

    return sha256(json.dumps(
        projection,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")).hexdigest()
