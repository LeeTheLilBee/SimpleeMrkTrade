
"""Canonical, server-owned hosted release packet provider / TWR101."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import current_app, has_app_context

from tower.hosted_candidate_release_gate import (
    verify_hosted_candidate_release_packet,
)

NO_REVIEWABLE_CANDIDATE = "NO_REVIEWABLE_CANDIDATE"
REVIEWABLE_CANDIDATE = "REVIEWABLE_CANDIDATE"
MAX_PACKET_BYTES = 262144
DEFAULT_MAX_PACKET_AGE_SECONDS = 3600


def _config(name: str, default: Any = None) -> Any:
    if has_app_context() and name in current_app.config:
        return current_app.config[name]
    return os.environ.get(name, default)


def canonical_release_packet_path() -> Path:
    configured = str(_config("TOWER_HOSTED_RELEASE_PACKET_PATH", "") or "").strip()
    if configured:
        return Path(configured).expanduser()
    return (
        Path(__file__).resolve().parents[1]
        / "tower"
        / "data"
        / "hosted_candidate_release_packet.json"
    )


def _expected_candidate_revision() -> str:
    for key in (
        "TOWER_HOSTED_RELEASE_EXPECTED_REVISION",
        "RENDER_GIT_COMMIT",
        "GIT_COMMIT",
        "COMMIT_SHA",
        "SOURCE_VERSION",
    ):
        value = str(_config(key, "") or "").strip().lower()
        if value:
            return value

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            check=False,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.strip().lower()
    except (OSError, subprocess.SubprocessError):
        pass

    return ""


def _packet_age_seconds(created_at: Any) -> float | None:
    try:
        timestamp = datetime.fromisoformat(
            str(created_at or "").strip().replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return None
    if timestamp.tzinfo is None:
        return None
    return (datetime.now(timezone.utc) - timestamp).total_seconds()


def _unavailable(reason: str) -> dict[str, Any]:
    return {
        "status": "tower_hosted_release_candidate_unavailable",
        "candidate_state": NO_REVIEWABLE_CANDIDATE,
        "reviewable": False,
        "reason": reason,
        "packet": None,
        "deployment_authorized": False,
        "promotion_authorized": False,
        "production_promotion_authorized": False,
        "staging_ready_changed": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
    }


def load_canonical_release_packet() -> dict[str, Any]:
    path = canonical_release_packet_path()
    if path.is_symlink():
        return _unavailable("packet_source_symlink_rejected")
    if not path.is_file():
        return _unavailable("packet_source_missing")

    try:
        if path.stat().st_size > MAX_PACKET_BYTES:
            return _unavailable("packet_source_too_large")
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return _unavailable("packet_source_unreadable")

    if not isinstance(payload, Mapping):
        return _unavailable("packet_source_not_mapping")

    packet = payload.get("packet", payload)
    if not isinstance(packet, Mapping):
        return _unavailable("packet_payload_not_mapping")

    verified = verify_hosted_candidate_release_packet(packet)
    if not verified.get("valid"):
        return _unavailable("packet_integrity_invalid")

    expected_revision = _expected_candidate_revision()
    if not expected_revision:
        return _unavailable("expected_candidate_revision_unavailable")

    packet_expected = str(packet.get("expected_revision") or "").strip().lower()
    packet_actual = str(packet.get("actual_revision") or "").strip().lower()
    if packet_expected != expected_revision or packet_actual != expected_revision:
        return _unavailable("packet_candidate_revision_mismatch")

    age_seconds = _packet_age_seconds(packet.get("created_at_utc"))
    if age_seconds is None:
        return _unavailable("packet_timestamp_invalid")

    try:
        maximum_age = int(
            _config(
                "TOWER_HOSTED_RELEASE_MAX_PACKET_AGE_SECONDS",
                DEFAULT_MAX_PACKET_AGE_SECONDS,
            )
        )
    except (TypeError, ValueError):
        return _unavailable("packet_maximum_age_invalid")

    if maximum_age < 1 or age_seconds < -60 or age_seconds > maximum_age:
        return _unavailable("packet_stale_or_future_dated")

    return {
        "status": "tower_hosted_release_candidate_ready",
        "candidate_state": REVIEWABLE_CANDIDATE,
        "reviewable": True,
        "packet": dict(packet),
        "packet_integrity_hash": packet["packet_integrity_hash"],
        "expected_revision": expected_revision,
        "packet_age_seconds": max(0, round(age_seconds)),
        "deployment_authorized": False,
        "promotion_authorized": False,
        "production_promotion_authorized": False,
        "staging_ready_changed": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
    }
