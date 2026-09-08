
"""Hosted owner verification and release-prerequisite certificate / TWR116-TWR120."""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping
from typing import Any

from tower.hosted_owner_release_candidate_state import (
    OWNER_APPROVED,
    project_owner_release_candidate_state,
)
from tower.hosted_owner_release_readiness import (
    HOSTED_OWNER_APPROVED_CERTIFIED,
    certify_hosted_owner_release_walkthrough,
)
from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    SAFETY_FALSE_FIELDS,
    owner_release_session_context,
    read_owner_release_decision_receipts,
    validate_owner_release_context,
    verify_owner_release_decision_receipt,
)


OWNER_VERIFICATION_REQUIRED = "OWNER_VERIFICATION_REQUIRED"
RELEASE_PREREQUISITES_NOT_CERTIFIED = "RELEASE_PREREQUISITES_NOT_CERTIFIED"
RELEASE_PREREQUISITES_CERTIFIED_EXECUTION_LOCKED = (
    "RELEASE_PREREQUISITES_CERTIFIED_EXECUTION_LOCKED"
)

PREREQUISITE_CERTIFICATE_SCHEMA = (
    "tower.hosted-release-prerequisite-certificate.twr116-120.v1"
)


def _safety() -> dict[str, bool]:
    return {field: False for field in SAFETY_FALSE_FIELDS}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _not_verified(*, state: str, reason: str) -> dict[str, Any]:
    return {
        "status": "tower_hosted_owner_verification_not_complete",
        "verification_state": state,
        "owner_verified_for_release": False,
        "release_prerequisites_certified": False,
        "reason": reason,
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        "release_execution_authorized": False,
        "staging_ready": False,
        **_safety(),
    }


def _matching_approval_receipt(
    *,
    owner_context: Mapping[str, Any],
    receipt_id: str,
    expected_revision: str,
    packet_integrity_hash: str,
) -> dict[str, Any] | None:

    ledger = read_owner_release_decision_receipts(
        owner_context=owner_context
    )

    if (
        ledger.get("status") != "tower_owner_release_receipts_ready"
        or ledger.get("chain_valid") is not True
    ):
        return None

    for receipt in reversed(ledger.get("receipts", [])):
        if receipt.get("receipt_id") != receipt_id:
            continue

        if receipt.get("decision") != APPROVE_RELEASE:
            return None

        if receipt.get("expected_revision") != expected_revision:
            return None

        if receipt.get("actual_revision") != expected_revision:
            return None

        if receipt.get("packet_integrity_hash") != packet_integrity_hash:
            return None

        verification = verify_owner_release_decision_receipt(receipt)

        if not verification.get("valid"):
            return None

        return dict(receipt)

    return None


def project_hosted_owner_verification(
    *,
    owner_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:

    context = (
        owner_context
        if owner_context is not None
        else owner_release_session_context()
    )

    validation = validate_owner_release_context(context)

    if not validation.get("valid"):
        return _not_verified(
            state=OWNER_VERIFICATION_REQUIRED,
            reason="fresh_verified_owner_session_and_step_up_required",
        )

    walkthrough = certify_hosted_owner_release_walkthrough(
        owner_context=context
    )

    candidate = project_owner_release_candidate_state(
        owner_context=context
    )

    expected_revision = str(
        candidate.get("expected_revision") or ""
    ).strip().lower()

    packet_hash = str(
        candidate.get("packet_integrity_hash") or ""
    ).strip().lower()

    receipt_id = str(
        candidate.get("receipt_id") or ""
    ).strip()

    checks = {
        "owner_context_verified": True,

        "hosted_walkthrough_certified": bool(
            walkthrough.get("certified") is True
            and walkthrough.get("readiness_state")
            == HOSTED_OWNER_APPROVED_CERTIFIED
        ),

        "candidate_owner_approved": (
            candidate.get("candidate_state")
            == OWNER_APPROVED
        ),

        "candidate_receipt_integrity_verified": (
            candidate.get("receipt_integrity_verified") is True
        ),

        "exact_revision_present": bool(expected_revision),

        "exact_packet_integrity_hash_present": bool(packet_hash),

        "exact_receipt_id_present": bool(receipt_id),

        "walkthrough_receipt_matches_candidate": (
            bool(receipt_id)
            and walkthrough.get("receipt_id") == receipt_id
        ),

        "execution_boundaries_closed": bool(
            walkthrough.get("staging_ready") is False
            and all(
                walkthrough.get(field) is False
                for field in SAFETY_FALSE_FIELDS
            )
        ),
    }

    receipt = None

    if all(checks.values()):
        receipt = _matching_approval_receipt(
            owner_context=context,
            receipt_id=receipt_id,
            expected_revision=expected_revision,
            packet_integrity_hash=packet_hash,
        )

    checks["exact_approval_receipt_verified"] = receipt is not None

    verified = all(checks.values())

    if not verified:
        return {
            **_not_verified(
                state=RELEASE_PREREQUISITES_NOT_CERTIFIED,
                reason="hosted_owner_prerequisite_chain_not_fully_verified",
            ),
            "checks": checks,
            "expected_revision": expected_revision or None,
            "receipt_id": receipt_id or None,
        }

    return {
        "status": "tower_hosted_owner_verification_complete",
        "verification_state": (
            RELEASE_PREREQUISITES_CERTIFIED_EXECUTION_LOCKED
        ),
        "owner_verified_for_release": True,
        "release_prerequisites_certified": True,
        "checks": checks,
        "expected_revision": expected_revision,
        "packet_integrity_hash": packet_hash,
        "receipt_id": receipt_id,
        "decision": APPROVE_RELEASE,
        "receipt_integrity_verified": True,
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        "release_execution_authorized": False,
        "staging_ready": False,
        **_safety(),
    }


def build_release_prerequisite_certificate(
    *,
    owner_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:

    verification = project_hosted_owner_verification(
        owner_context=owner_context
    )

    if verification.get("release_prerequisites_certified") is not True:
        return {
            "status": "tower_release_prerequisite_certificate_not_issued",
            "certificate_issued": False,
            "verification_state": verification.get(
                "verification_state"
            ),
            "reason": verification.get("reason"),
            "owner_review_required": True,
            "separate_release_execution_gate_required": True,
            "release_execution_authorized": False,
            "staging_ready": False,
            **_safety(),
        }

    certificate = {
        "schema_version": PREREQUISITE_CERTIFICATE_SCHEMA,
        "certificate_type": "TOWER_HOSTED_RELEASE_PREREQUISITES",
        "certificate_status": "CERTIFIED_PREREQUISITES_ONLY",
        "verification_state": verification["verification_state"],
        "owner_verified_for_release": True,
        "release_prerequisites_certified": True,
        "expected_revision": verification["expected_revision"],
        "packet_integrity_hash": verification[
            "packet_integrity_hash"
        ],
        "owner_decision_receipt_id": verification["receipt_id"],
        "owner_decision": APPROVE_RELEASE,
        "owner_decision_receipt_integrity_verified": True,
        "hosted_runtime_prerequisites_verified": True,
        "owner_review_required": True,
        "separate_release_execution_gate_required": True,
        "release_execution_authorized": False,
        "staging_ready": False,
        **_safety(),
    }

    certificate_hash = _sha256(certificate)

    certificate["certificate_id"] = (
        "tower-release-prerequisite-"
        + certificate_hash[:24]
    )

    certificate["certificate_integrity_hash"] = _sha256(
        certificate
    )

    return {
        "status": "tower_release_prerequisite_certificate_ready",
        "certificate_issued": True,
        "certificate": certificate,
        "separate_release_execution_gate_required": True,
        "release_execution_authorized": False,
        "staging_ready": False,
        **_safety(),
    }


def verify_release_prerequisite_certificate(
    certificate: Mapping[str, Any],
    *,
    owner_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:

    if not isinstance(certificate, Mapping):
        return {
            "status": "tower_release_prerequisite_certificate_invalid",
            "valid": False,
            "errors": ["certificate_not_mapping"],
        }

    supplied = dict(certificate)

    supplied_hash = str(
        supplied.pop(
            "certificate_integrity_hash",
            ""
        )
        or ""
    )

    computed_hash = _sha256(supplied)

    errors = []

    if (
        certificate.get("schema_version")
        != PREREQUISITE_CERTIFICATE_SCHEMA
    ):
        errors.append("certificate_schema_mismatch")

    if (
        not supplied_hash
        or not hmac.compare_digest(
            supplied_hash,
            computed_hash,
        )
    ):
        errors.append(
            "certificate_integrity_hash_mismatch"
        )

    if (
        certificate.get("certificate_status")
        != "CERTIFIED_PREREQUISITES_ONLY"
    ):
        errors.append("certificate_status_invalid")

    if (
        certificate.get("release_prerequisites_certified")
        is not True
    ):
        errors.append(
            "certificate_prerequisites_not_certified"
        )

    if (
        certificate.get(
            "separate_release_execution_gate_required"
        )
        is not True
    ):
        errors.append(
            "certificate_separate_execution_gate_missing"
        )

    if (
        certificate.get("release_execution_authorized")
        is not False
    ):
        errors.append(
            "certificate_execution_authority_open"
        )

    if certificate.get("staging_ready") is not False:
        errors.append(
            "certificate_staging_ready_open"
        )

    for field in SAFETY_FALSE_FIELDS:
        if certificate.get(field) is not False:
            errors.append(
                f"certificate_safety_boundary_open:{field}"
            )

    expected_result = build_release_prerequisite_certificate(
        owner_context=owner_context
    )

    expected = (
        expected_result.get("certificate")
        if expected_result.get("certificate_issued")
        else None
    )

    if expected is None:
        errors.append(
            "current_verified_prerequisite_chain_unavailable"
        )
    else:
        for field in (
            "certificate_id",
            "expected_revision",
            "packet_integrity_hash",
            "owner_decision_receipt_id",
            "owner_decision",
        ):
            if certificate.get(field) != expected.get(field):
                errors.append(
                    f"certificate_current_chain_mismatch:{field}"
                )

    return {
        "status": (
            "tower_release_prerequisite_certificate_valid"
            if not errors
            else "tower_release_prerequisite_certificate_invalid"
        ),
        "valid": not errors,
        "integrity_valid": bool(
            supplied_hash
            and hmac.compare_digest(
                supplied_hash,
                computed_hash,
            )
        ),
        "errors": errors,
    }


def owner_prerequisite_certificate_dashboard_snapshot() -> dict[str, str]:

    verification = project_hosted_owner_verification()

    state = str(
        verification.get("verification_state")
        or RELEASE_PREREQUISITES_NOT_CERTIFIED
    )

    labels = {
        OWNER_VERIFICATION_REQUIRED: (
            "Owner verification needed",
            "Verify your Tower owner session before prerequisite certification.",
        ),

        RELEASE_PREREQUISITES_NOT_CERTIFIED: (
            "Prerequisites not certified",
            "Complete the hosted owner walkthrough and verified approval first.",
        ),

        RELEASE_PREREQUISITES_CERTIFIED_EXECUTION_LOCKED: (
            "Prerequisites certified · execution locked",
            "The exact hosted owner approval chain is verified; release execution still requires a separate gate.",
        ),
    }

    label, detail = labels.get(
        state,
        (
            "Prerequisite certificate unavailable",
            "Tower could not verify the prerequisite chain.",
        ),
    )

    return {
        "state": state,
        "label": label,
        "detail": detail,
    }
