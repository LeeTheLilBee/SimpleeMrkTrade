"""Owner-only hosted release review and append-only decision receipts.

TWR096-TWR100 consume the integrity-sealed packet from TWR091-TWR095.
An owner decision never deploys, promotes, changes STAGING_READY, opens
broker access, moves capital, or unlocks any Observatory live mode.
"""

from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import re
import uuid

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tower.hosted_candidate_release_gate import (
    READY_FOR_OWNER_REVIEW,
    verify_hosted_candidate_release_packet,
)


OWNER_RELEASE_RECEIPT_SCHEMA = (
    "tower.hosted-owner-release-decision-receipt.v1"
)

APPROVE_RELEASE = "APPROVE_RELEASE"

HOLD_RELEASE = "HOLD_RELEASE"

REJECT_RELEASE = "REJECT_RELEASE"

OWNER_RELEASE_DECISIONS = (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
)

GENESIS_RECEIPT_HASH = "GENESIS"

SAFETY_FALSE_FIELDS = (
    "deployment_authorized",
    "promotion_authorized",
    "production_promotion_authorized",
    "staging_ready_changed",
    "broker_submission_authorized",
    "capital_movement_authorized",
    "manual_live_authorized",
    "live_auto_authorized",
)

_REFERENCE_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:@-]{0,127}$"
)

_SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

_SENSITIVE_REASON_PATTERN = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"\b(?:ghp_|gho_|github_pat_|sk_live_|sk_test_)\S+|"
    r"\bBearer\s+\S+|"
    r"\b(?:password|access_token|refresh_token|api_key|"
    r"github_token|client_secret|session_secret)"
    r"\s*[:=]\s*\S+",
    re.IGNORECASE,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _safe_reference(value: Any) -> str:
    reference = str(value or "").strip()
    return reference if _REFERENCE_PATTERN.fullmatch(reference) else ""


def owner_release_session_context() -> dict[str, Any]:
    """Read verified owner authority from the existing Tower session."""

    from flask import has_request_context, session

    from tower.tower_human_login_ob_launch import (
        OWNER_ROLE,
        SESSION_AUTH_TIME,
        SESSION_OWNER_ID,
        SESSION_ROLE,
        owner_session_active,
        step_up_active,
    )

    if not has_request_context():
        return {
            "status": "tower_owner_release_session_unavailable",
            "owner_verified": False,
            "session_active": False,
            "session_fresh": False,
            "step_up_verified": False,
        }

    owner_id = _safe_reference(
        session.get(SESSION_OWNER_ID)
    )

    authenticated_at = str(
        session.get(SESSION_AUTH_TIME) or ""
    ).strip()

    if owner_id and authenticated_at:
        digest = hashlib.sha256(
            f"{owner_id}:{authenticated_at}".encode("utf-8")
        ).hexdigest()
        session_reference = "owner-session-" + digest[:24]
    else:
        session_reference = ""

    owner_active = owner_session_active()
    elevated = step_up_active()

    return {
        "status": "tower_owner_release_session_checked",
        "owner_id": owner_id,
        "owner_session_reference": session_reference,
        "owner_role": session.get(SESSION_ROLE),
        "owner_verified": (
            owner_active
            and session.get(SESSION_ROLE) == OWNER_ROLE
        ),
        "session_active": owner_active,
        "session_fresh": (
            bool(authenticated_at)
            and elevated
        ),
        "step_up_verified": elevated,
    }


def validate_owner_release_context(
    owner_context: Mapping[str, Any],
) -> dict[str, Any]:

    if not isinstance(owner_context, Mapping):
        return {
            "valid": False,
            "errors": ["owner_context_not_mapping"],
        }

    errors = []

    owner_id = _safe_reference(
        owner_context.get("owner_id")
    )

    session_reference = _safe_reference(
        owner_context.get("owner_session_reference")
    )

    if not owner_id:
        errors.append("owner_identity_missing_or_invalid")

    if not session_reference:
        errors.append("owner_session_reference_missing_or_invalid")

    role = str(
        owner_context.get("owner_role") or ""
    ).strip().lower()

    if role != "owner":
        errors.append("owner_role_required")

    for field in (
        "owner_verified",
        "session_active",
        "session_fresh",
        "step_up_verified",
    ):
        if owner_context.get(field) is not True:
            errors.append(f"{field}_required")

    return {
        "valid": not errors,
        "errors": errors,
        "owner_id": owner_id,
        "owner_session_reference": session_reference,
    }


def build_owner_release_review(
    release_packet: Mapping[str, Any],
    *,
    owner_context: Mapping[str, Any],
) -> dict[str, Any]:

    context = validate_owner_release_context(
        owner_context
    )

    verification = verify_hosted_candidate_release_packet(
        release_packet
    )

    errors = list(
        context["errors"]
    )

    if not verification["valid"]:
        errors.extend(
            verification["errors"]
        )

    if errors:
        return {
            "status": "tower_owner_release_review_denied",
            "review_allowed": False,
            "decision_allowed": False,
            "errors": errors,
            **{
                field: False
                for field in SAFETY_FALSE_FIELDS
            },
        }

    ready = (
        release_packet.get("release_recommendation")
        == READY_FOR_OWNER_REVIEW
        and release_packet.get("parity_valid") is True
        and release_packet.get("parity_pass") is True
        and release_packet.get("owner_decision_recorded") is False
        and release_packet.get("expected_revision")
        == release_packet.get("actual_revision")
        and not release_packet.get("failures")
        and not release_packet.get("validation_errors")
    )

    allowed_decisions = [
        HOLD_RELEASE,
        REJECT_RELEASE,
    ]

    if ready:
        allowed_decisions.insert(
            0,
            APPROVE_RELEASE,
        )

    return {
        "status": "tower_owner_release_review_ready",
        "review_allowed": True,
        "decision_allowed": True,
        "approval_allowed": ready,
        "allowed_decisions": allowed_decisions,
        "owner_id": context["owner_id"],
        "owner_session_reference": (
            context["owner_session_reference"]
        ),
        "expected_revision": (
            release_packet.get("expected_revision")
        ),
        "actual_revision": (
            release_packet.get("actual_revision")
        ),
        "entrypoint": (
            release_packet.get("entrypoint")
        ),
        "critical_route_count": (
            release_packet.get("critical_route_count")
        ),
        "release_recommendation": (
            release_packet.get("release_recommendation")
        ),
        "packet_integrity_hash": (
            release_packet.get("packet_integrity_hash")
        ),
        "checks": dict(
            release_packet.get("checks") or {}
        ),
        "failures": list(
            release_packet.get("failures") or []
        ),
        "validation_errors": list(
            release_packet.get("validation_errors") or []
        ),
        "owner_review_required": True,
        "owner_decision_recorded": False,
        **{
            field: False
            for field in SAFETY_FALSE_FIELDS
        },
    }


def _ledger_path(
    explicit_path: str | Path | None = None,
) -> Path:

    if explicit_path is not None:
        return Path(
            explicit_path
        )

    configured = str(
        os.environ.get(
            "TOWER_RELEASE_RECEIPT_LEDGER_PATH",
            "",
        )
    ).strip()

    hosted = bool(
        os.environ.get("RENDER")
        or os.environ.get("RENDER_GIT_COMMIT")
    )

    operator_confirmed = (
        str(
            os.environ.get(
                "TOWER_RELEASE_RECEIPT_STORE_DURABLE",
                "",
            )
        )
        .strip()
        .lower()
        == "true"
    )

    if hosted and (
        not configured
        or not operator_confirmed
    ):
        raise RuntimeError(
            "receipt_durable_storage_not_configured"
        )

    if configured:
        return Path(
            configured
        )

    return (
        Path(__file__).resolve().parents[1]
        / "tower"
        / "data"
        / "hosted_owner_release_decisions.jsonl"
    )


def verify_owner_release_decision_receipt(
    receipt: Mapping[str, Any],
    *,
    previous_receipt_hash: str | None = None,
) -> dict[str, Any]:

    if not isinstance(
        receipt,
        Mapping,
    ):
        return {
            "valid": False,
            "errors": ["receipt_not_mapping"],
        }

    working = dict(
        receipt
    )

    supplied_hash = str(
        working.pop(
            "receipt_integrity_hash",
            "",
        )
        or ""
    )

    computed_hash = _sha256(
        working
    )

    errors = []

    if (
        receipt.get("schema_version")
        != OWNER_RELEASE_RECEIPT_SCHEMA
    ):
        errors.append(
            "receipt_schema_mismatch"
        )

    if (
        receipt.get("decision")
        not in OWNER_RELEASE_DECISIONS
    ):
        errors.append(
            "receipt_decision_invalid"
        )

    if not _safe_reference(
        receipt.get("owner_id")
    ):
        errors.append(
            "receipt_owner_identity_invalid"
        )

    if not _safe_reference(
        receipt.get("owner_session_reference")
    ):
        errors.append(
            "receipt_owner_session_reference_invalid"
        )

    packet_hash = str(
        receipt.get("packet_integrity_hash")
        or ""
    )

    if not _SHA256_PATTERN.fullmatch(
        packet_hash
    ):
        errors.append(
            "receipt_packet_hash_invalid"
        )

    if (
        not supplied_hash
        or not hmac.compare_digest(
            supplied_hash,
            computed_hash,
        )
    ):
        errors.append(
            "receipt_integrity_hash_mismatch"
        )

    if (
        previous_receipt_hash is not None
        and receipt.get("previous_receipt_hash")
        != previous_receipt_hash
    ):
        errors.append(
            "receipt_chain_previous_hash_mismatch"
        )

    if (
        receipt.get("owner_decision_recorded")
        is not True
    ):
        errors.append(
            "receipt_owner_decision_not_recorded"
        )

    for field in SAFETY_FALSE_FIELDS:
        if receipt.get(field) is not False:
            errors.append(
                f"receipt_safety_boundary_open:{field}"
            )

    valid = not errors

    return {
        "status": (
            "tower_owner_release_decision_receipt_valid"
            if valid
            else "tower_owner_release_decision_receipt_invalid"
        ),
        "valid": valid,
        "integrity_valid": (
            bool(supplied_hash)
            and hmac.compare_digest(
                supplied_hash,
                computed_hash,
            )
        ),
        "supplied_hash": supplied_hash,
        "computed_hash": computed_hash,
        "errors": errors,
    }


def _read_and_verify_ledger(
    path: Path,
) -> list[dict[str, Any]]:

    if not path.exists():
        return []

    receipts = []

    previous_hash = (
        GENESIS_RECEIPT_HASH
    )

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    for line_number, line in enumerate(
        lines,
        start=1,
    ):

        if not line.strip():
            raise ValueError(
                f"receipt_ledger_blank_line:{line_number}"
            )

        try:
            receipt = json.loads(
                line
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"receipt_ledger_invalid_json:{line_number}"
            ) from exc

        verification = (
            verify_owner_release_decision_receipt(
                receipt,
                previous_receipt_hash=previous_hash,
            )
        )

        if not verification["valid"]:
            raise ValueError(
                f"receipt_ledger_invalid_receipt:{line_number}"
            )

        receipts.append(
            dict(receipt)
        )

        previous_hash = receipt[
            "receipt_integrity_hash"
        ]

    return receipts


def read_owner_release_decision_receipts(
    *,
    owner_context: Mapping[str, Any],
    ledger_path: str | Path | None = None,
) -> dict[str, Any]:

    context = (
        validate_owner_release_context(
            owner_context
        )
    )

    if not context["valid"]:
        return {
            "status": "tower_owner_release_receipts_denied",
            "receipts": [],
            "errors": context["errors"],
        }

    try:
        receipts = (
            _read_and_verify_ledger(
                _ledger_path(
                    ledger_path
                )
            )
        )
    except Exception as exc:
        return {
            "status": (
                "tower_owner_release_receipts_unavailable"
            ),
            "receipts": [],
            "errors": [str(exc)],
        }

    return {
        "status": "tower_owner_release_receipts_ready",
        "receipts": receipts,
        "receipt_count": len(receipts),
        "chain_valid": True,
    }


def _append_receipt(
    path: Path,
    receipt: dict[str, Any],
) -> None:

    data = (
        _canonical_json(
            receipt
        )
        + "\n"
    ).encode(
        "utf-8"
    )

    descriptor = os.open(
        path,
        os.O_RDWR | os.O_CREAT,
        0o600,
    )

    original_size = os.lseek(
        descriptor,
        0,
        os.SEEK_END,
    )

    try:

        offset = 0

        while offset < len(data):

            written = os.write(
                descriptor,
                data[offset:],
            )

            if written <= 0:
                raise OSError(
                    "receipt_persistence_incomplete"
                )

            offset += written

        os.fsync(
            descriptor
        )

    except Exception:

        try:
            os.ftruncate(
                descriptor,
                original_size,
            )
            os.fsync(
                descriptor
            )
        except OSError:
            pass

        raise

    finally:

        os.close(
            descriptor
        )


def record_owner_release_decision(
    release_packet: Mapping[str, Any],
    *,
    owner_context: Mapping[str, Any],
    decision: str,
    reason: str,
    ledger_path: str | Path | None = None,
    decided_at_utc: str | None = None,
) -> dict[str, Any]:

    review = (
        build_owner_release_review(
            release_packet,
            owner_context=owner_context,
        )
    )

    if not review.get(
        "review_allowed"
    ):
        return {
            "status": "tower_owner_release_decision_denied",
            "recorded": False,
            "errors": review.get(
                "errors",
                [],
            ),
        }

    normalized = str(
        decision
        or ""
    ).strip().upper()

    if (
        normalized
        not in OWNER_RELEASE_DECISIONS
    ):
        return {
            "status": "tower_owner_release_decision_invalid",
            "recorded": False,
            "errors": [
                "owner_release_decision_not_allowed",
            ],
            "allowed_decisions": (
                review["allowed_decisions"]
            ),
        }

    if (
        normalized
        not in review["allowed_decisions"]
    ):
        return {
            "status": "tower_owner_release_approval_blocked",
            "recorded": False,
            "errors": [
                "release_packet_not_eligible_for_approval",
            ],
        }

    clean_reason = str(
        reason
        or ""
    ).strip()

    if (
        not clean_reason
        or len(clean_reason) > 1000
    ):
        return {
            "status": "tower_owner_release_reason_invalid",
            "recorded": False,
            "errors": [
                "owner_decision_reason_required_and_max_1000_chars",
            ],
        }

    if _SENSITIVE_REASON_PATTERN.search(
        clean_reason
    ):
        return {
            "status": "tower_owner_release_reason_rejected",
            "recorded": False,
            "errors": [
                "owner_decision_reason_contains_sensitive_value",
            ],
        }

    try:

        path = _ledger_path(
            ledger_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        lock_path = path.with_name(
            path.name + ".lock"
        )

        with lock_path.open(
            "a",
            encoding="utf-8",
        ) as lock_file:

            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX,
            )

            try:

                existing = (
                    _read_and_verify_ledger(
                        path
                    )
                )

                for saved in existing:

                    if (
                        saved.get("packet_integrity_hash")
                        == review["packet_integrity_hash"]
                    ):
                        return {
                            "status": (
                                "tower_owner_release_decision_already_recorded"
                            ),
                            "recorded": False,
                            "duplicate": True,
                            "receipt": saved,
                        }

                if existing:
                    previous_hash = existing[-1][
                        "receipt_integrity_hash"
                    ]
                else:
                    previous_hash = (
                        GENESIS_RECEIPT_HASH
                    )

                receipt = {
                    "schema_version": (
                        OWNER_RELEASE_RECEIPT_SCHEMA
                    ),
                    "receipt_type": (
                        "TOWER_HOSTED_OWNER_RELEASE_DECISION"
                    ),
                    "receipt_id": (
                        "tower-release-receipt-"
                        + uuid.uuid4().hex
                    ),
                    "decided_at_utc": (
                        decided_at_utc
                        or _utc_now()
                    ),
                    "decision": normalized,
                    "decision_reason": clean_reason,
                    "owner_id": review["owner_id"],
                    "owner_session_reference": (
                        review["owner_session_reference"]
                    ),
                    "expected_revision": (
                        review["expected_revision"]
                    ),
                    "actual_revision": (
                        review["actual_revision"]
                    ),
                    "entrypoint": review["entrypoint"],
                    "release_recommendation": (
                        review["release_recommendation"]
                    ),
                    "packet_integrity_hash": (
                        review["packet_integrity_hash"]
                    ),
                    "previous_receipt_hash": (
                        previous_hash
                    ),
                    "owner_review_required": True,
                    "owner_decision_recorded": True,
                    "separate_release_execution_gate_required": True,
                    **{
                        field: False
                        for field in SAFETY_FALSE_FIELDS
                    },
                }

                receipt[
                    "receipt_integrity_hash"
                ] = _sha256(
                    receipt
                )

                _append_receipt(
                    path,
                    receipt,
                )

                persisted = (
                    _read_and_verify_ledger(
                        path
                    )
                )

                if (
                    not persisted
                    or persisted[-1][
                        "receipt_integrity_hash"
                    ]
                    != receipt[
                        "receipt_integrity_hash"
                    ]
                ):
                    raise OSError(
                        "receipt_persistence_verification_failed"
                    )

                return {
                    "status": (
                        "tower_owner_release_decision_recorded"
                    ),
                    "recorded": True,
                    "receipt": receipt,
                    "receipt_chain_valid": True,
                    "separate_release_execution_gate_required": True,
                    **{
                        field: False
                        for field in SAFETY_FALSE_FIELDS
                    },
                }

            finally:

                fcntl.flock(
                    lock_file.fileno(),
                    fcntl.LOCK_UN,
                )

    except Exception as exc:

        return {
            "status": (
                "tower_owner_release_receipt_persistence_failed"
            ),
            "recorded": False,
            "errors": [
                str(exc),
            ],
            **{
                field: False
                for field in SAFETY_FALSE_FIELDS
            },
        }
