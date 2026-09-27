"""OBSIM076–080: read-only owner-downloadable synthetic report chain.

A finalized owner-initiated export is an evidence copy, not server durability,
source/provider authentication, owner clearance, real balances or session recovery.
This module accepts only accepted ephemeral report material and independently
checks every stored report hash, sequence and final link before packaging it.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import json

from web.ob_multi_simulation_harness import stable_hash

SCHEMA = "OBSIM_OWNER_EPHEMERAL_FINAL_EVIDENCE_V1"
MAX_TICKS = 120
REQUIRED_FALSE = (
    "broker_submission", "capital_movement", "manual_live_unlock",
    "hybrid_unlock", "automated_unlock", "winner_selected",
)


def _dict(value: object, name: str) -> dict[str, object]:
    if type(value) is not dict:
        raise ValueError(name + " must be an exact evidence object")
    return value


def _safe_row(value: object, expected: int, session_id: str) -> dict[str, object]:
    row = _dict(value, "tick")
    material = {key: content for key, content in row.items() if key != "report_hash"}
    if (
        row.get("session_id") != session_id
        or type(row.get("sequence")) is not int or row["sequence"] != expected
        or row.get("report_hash") != stable_hash(material)
        or row.get("source_kind") != "SYNTHETIC"
        or row.get("source_provider_authenticated") is not False
        or row.get("source_claim_verified") is not False
        or row.get("simulation_only") is not True
        or any(row.get(flag, False) is not False for flag in REQUIRED_FALSE)
        or type(row.get("lanes")) is not dict
        or set(row["lanes"]) != {"CONTROL", "INTEGRATED", "EXPERIMENTAL"}
    ):
        raise ValueError("ephemeral tick integrity/scope rejected")
    return row


def build_finalized_owner_evidence_packet(
    session_id: str, reports: Sequence[dict[str, object]],
    final: Mapping[str, object] | None,
) -> dict[str, object]:
    """Reverify exact closed synthetic chain; never include browser/Tower tokens."""
    if not isinstance(session_id, str) or not session_id.startswith("OB-WEB-"):
        raise ValueError("only a hosted proof/demo rehearsal can be exported")
    if (not isinstance(reports, (tuple, list))
            or len(reports) > MAX_TICKS or type(final) is not dict):
        raise ValueError("finalized report-only evidence required")
    verified = [_safe_row(row, i, session_id) for i, row in enumerate(reports, 1)]
    final_material = {key: content for key, content in final.items() if key != "report_hash"}
    if (
        final.get("session_id") != session_id
        or final.get("report_hash") != stable_hash(final_material)
        or type(final.get("total_ticks")) is not int
        or final["total_ticks"] != len(verified)
        or final.get("last_report_hash") != (
            verified[-1]["report_hash"] if verified else None
        )
        or final.get("lanes") != (verified[-1]["lanes"] if verified else final.get("lanes"))
        or final.get("simulation_only") is not True
        or final.get("broker_submission") is not False
        or final.get("capital_movement") is not False
    ):
        raise ValueError("ephemeral terminal evidence integrity rejected")
    content = {
        "schema_version": SCHEMA,
        "report_state": "OWNER_DOWNLOADED_FINALIZED_REPORT_ONLY",
        "session_id": session_id,
        "source_kind": "SYNTHETIC",
        "account_key": "PROOF-DEMO",
        "fictional_starting_units": 10000,
        "source_provider_authenticated": False,
        "tower_issuer_receipt_exported": False,
        "broker_or_capital_authenticated": False,
        "manual_live_authorized": False,
        "broker_submission": False,
        "capital_movement": False,
        "durable_server_archive": False,
        "server_restart_recovery": False,
        "this_is_a_third_party_attestation": False,
        "tick_count": len(verified),
        "reports": verified,
        "final": final,
    }
    # Round-trip to detach the owner-facing copy from volatile mutable rows.
    clean = json.loads(json.dumps(content, allow_nan=False, sort_keys=True))
    return {**clean, "packet_hash": stable_hash(clean)}


def verify_downloaded_owner_evidence_packet(packet: object) -> dict[str, object]:
    """Offline recomputation; integrity only, NOT an authenticated signature."""
    value = _dict(packet, "downloaded packet")
    stated = value.get("packet_hash")
    material = {key: content for key, content in value.items() if key != "packet_hash"}
    if (
        set(value) != {
            "schema_version", "report_state", "session_id", "source_kind",
            "account_key", "fictional_starting_units",
            "source_provider_authenticated", "tower_issuer_receipt_exported",
            "broker_or_capital_authenticated", "manual_live_authorized",
            "broker_submission", "capital_movement",
            "durable_server_archive", "server_restart_recovery",
            "this_is_a_third_party_attestation", "tick_count",
            "reports", "final", "packet_hash",
        }
        or value.get("schema_version") != SCHEMA
        or value.get("report_state") != "OWNER_DOWNLOADED_FINALIZED_REPORT_ONLY"
        or type(stated) is not str or stated != stable_hash(material)
    ):
        raise ValueError("downloaded packet format/hash rejected")
    expected = build_finalized_owner_evidence_packet(
        value["session_id"], value["reports"], value["final"],
    )
    if expected != value:
        raise ValueError("downloaded packet content/source boundary rejected")
    return {
        "state": "VALID_LOCAL_INTEGRITY_ONLY",
        "session_id": value["session_id"],
        "tick_count": value["tick_count"],
        "final_report_hash": value["final"]["report_hash"],
        "packet_hash": value["packet_hash"],
        "broker_or_provider_authenticated": False,
        "tower_permission_issued": False,
        "manual_live_authorized": False,
    }
