
"""Publish genuine hosted-parity release candidates atomically / TWR106-TWR107."""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from tower.hosted_candidate_release_gate import (
    READY_FOR_OWNER_REVIEW,
    build_hosted_candidate_release_packet,
    validate_parity_result,
    verify_hosted_candidate_release_packet,
)
from tower.hosted_owner_release_review import SAFETY_FALSE_FIELDS
from tower.hosted_release_packet_provider import (
    _config,
    _expected_candidate_revision,
    canonical_release_packet_path,
)
from tower.hosted_runtime_parity import normalize_base_url, probe_hosted_runtime


PUBLICATION_SCHEMA = "tower.hosted-release-candidate-publication.v1"
HOSTED_BASE_URL_CONFIG = "TOWER_HOSTED_RELEASE_BASE_URL"
PACKET_STORE_DURABLE_CONFIG = "TOWER_HOSTED_RELEASE_PACKET_STORE_DURABLE"


def _safety() -> dict[str, bool]:
    return {field: False for field in SAFETY_FALSE_FIELDS}


def _failure(reason: str, *, errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": "tower_hosted_release_candidate_publication_denied",
        "published": False,
        "reason": reason,
        "errors": list(errors or []),
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        **_safety(),
    }


def _hosted_runtime() -> bool:
    return bool(_config("RENDER", "") or _config("RENDER_GIT_COMMIT", ""))


def configured_release_base_url() -> str:
    return str(
        _config(HOSTED_BASE_URL_CONFIG, "") or _config("RENDER_EXTERNAL_URL", "")
    ).strip()


def _durable_packet_store_ready() -> bool:
    if not _hosted_runtime():
        return True
    configured_path = str(_config("TOWER_HOSTED_RELEASE_PACKET_PATH", "") or "").strip()
    confirmed = str(_config(PACKET_STORE_DURABLE_CONFIG, "") or "").strip().lower()
    return bool(configured_path and confirmed == "true")


def _atomic_publish(path: Path, envelope: dict[str, Any]) -> None:
    if path.is_symlink() or path.parent.is_symlink():
        raise OSError("packet_publication_symlink_rejected")
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".publish.lock")
    if lock_path.is_symlink():
        raise OSError("packet_publication_lock_symlink_rejected")

    with lock_path.open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        temporary_path = None
        try:
            if path.is_symlink():
                raise OSError("packet_publication_symlink_rejected")
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".tower-release-candidate-",
                suffix=".tmp",
                dir=str(path.parent),
            )
            temporary_path = Path(temporary_name)
            try:
                os.fchmod(descriptor, 0o600)
                encoded = (json.dumps(envelope, indent=2, sort_keys=True) + "\n").encode()
                offset = 0
                while offset < len(encoded):
                    written = os.write(descriptor, encoded[offset:])
                    if written <= 0:
                        raise OSError("packet_publication_incomplete")
                    offset += written
                os.fsync(descriptor)
            finally:
                os.close(descriptor)

            os.replace(temporary_path, path)
            temporary_path = None

            directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _same_candidate_already_published(
    path: Path,
    *,
    revision: str,
    source_host: str,
) -> bool:
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
        packet = existing.get("packet") or {}
        metadata = existing.get("publication") or {}
    except (AttributeError, OSError, TypeError, ValueError):
        return False
    verification = verify_hosted_candidate_release_packet(packet)
    return bool(
        verification.get("valid")
        and packet.get("expected_revision") == revision
        and packet.get("actual_revision") == revision
        and metadata.get("schema_version") == PUBLICATION_SCHEMA
        and metadata.get("genuine_hosted_probe_required") is True
        and metadata.get("source_host") == source_host
    )


def publish_hosted_release_candidate(
    *,
    base_url: str | None = None,
    expected_revision: str | None = None,
) -> dict[str, Any]:
    """Probe real HTTPS identity surfaces; publish only passing sealed parity."""
    if not _durable_packet_store_ready():
        return _failure("packet_durable_storage_not_configured")

    source = str(base_url or configured_release_base_url() or "").strip()
    if not source:
        return _failure("hosted_release_base_url_not_configured")

    try:
        normalized = normalize_base_url(source, allow_http=False)
    except (TypeError, ValueError) as exc:
        return _failure("hosted_release_base_url_invalid", errors=[str(exc)])

    revision = str(expected_revision or _expected_candidate_revision() or "").strip().lower()
    if not revision or revision in {"unknown", "unavailable", "none", "null"}:
        return _failure("expected_candidate_revision_unavailable")

    path = canonical_release_packet_path()
    if path.is_symlink() or path.parent.is_symlink():
        return _failure("packet_publication_symlink_rejected")

    try:
        parity = probe_hosted_runtime(base_url=normalized, expected_revision=revision)
    except Exception as exc:
        return _failure("hosted_runtime_probe_failed", errors=[exc.__class__.__name__])

    validation = validate_parity_result(parity)
    if (
        not validation.get("valid")
        or parity.get("parity_pass") is not True
        or parity.get("status") != "tower_hosted_candidate_parity_pass"
        or str(parity.get("expected_revision") or "").strip().lower() != revision
        or str(parity.get("actual_revision") or "").strip().lower() != revision
    ):
        return _failure(
            "hosted_runtime_parity_failed",
            errors=list(validation.get("errors", [])) + list(parity.get("failures", [])),
        )

    source_host = urlsplit(normalized).netloc
    if _same_candidate_already_published(
        path,
        revision=revision,
        source_host=source_host,
    ):
        return _failure("candidate_revision_already_published")

    envelope = build_hosted_candidate_release_packet(parity)
    packet = envelope.get("packet") or {}
    verification = verify_hosted_candidate_release_packet(packet)
    if (
        not verification.get("valid")
        or packet.get("release_recommendation") != READY_FOR_OWNER_REVIEW
        or packet.get("parity_pass") is not True
    ):
        return _failure("published_candidate_integrity_invalid", errors=verification.get("errors", []))

    envelope["publication"] = {
        "schema_version": PUBLICATION_SCHEMA,
        "published_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_host": source_host,
        "expected_revision": revision,
        "probe_status": parity["status"],
        "genuine_hosted_probe_required": True,
    }
    envelope.update(_safety())

    try:
        _atomic_publish(path, envelope)
        persisted = json.loads(path.read_text(encoding="utf-8"))
        persisted_packet = persisted.get("packet") or {}
        persisted_check = verify_hosted_candidate_release_packet(persisted_packet)
        if (
            not persisted_check.get("valid")
            or persisted_packet.get("packet_integrity_hash") != packet.get("packet_integrity_hash")
        ):
            return _failure("published_candidate_persistence_verification_failed")
    except Exception as exc:
        return _failure("candidate_publication_persistence_failed", errors=[str(exc)])

    return {
        "status": "tower_hosted_release_candidate_published",
        "published": True,
        "candidate_state": "READY_FOR_OWNER_REVIEW",
        "expected_revision": revision,
        "packet_integrity_hash": packet["packet_integrity_hash"],
        "published_at_utc": envelope["publication"]["published_at_utc"],
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        **_safety(),
    }
