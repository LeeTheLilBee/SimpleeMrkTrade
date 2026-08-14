"""
GP039 — External Receipt / Acceptance Validation Contract.

Builds a strict validator for future real external receipts.

The built-in fixture proves the validator only.
It does not count as real Tower delivery.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .external_handoff_receipt import (
        ExternalHandoffReceiptClaim,
        ExternalHandoffReceiptValidation,
        ExternalReceiptAcceptanceState,
        ExternalReceiptValidationState,
    )

    from .protected_handoff_delivery_attempt_service import (
        get_clouds_gp038_status_payload,
        get_gp038_delivery_attempt_record,
    )

except ImportError:
    from external_handoff_receipt import (
        ExternalHandoffReceiptClaim,
        ExternalHandoffReceiptValidation,
        ExternalReceiptAcceptanceState,
        ExternalReceiptValidationState,
    )

    from protected_handoff_delivery_attempt_service import (
        get_clouds_gp038_status_payload,
        get_gp038_delivery_attempt_record,
    )


def _receipt_hash_payload(
    *,
    receipt_id,
    attempt,
    acceptance_state,
    fixture_only,
):
    return {
        "receipt_id": receipt_id,

        "delivery_attempt_record_id": (
            attempt.delivery_attempt_record_id
        ),

        "delivery_envelope_id": (
            attempt.delivery_envelope_id
        ),

        "delivery_envelope_integrity_hash": (
            attempt
            .delivery_envelope_integrity_hash
        ),

        "delivery_target_kind": (
            attempt.delivery_target_kind
        ),

        "delivery_target_id": (
            attempt.delivery_target_id
        ),

        "acceptance_state": (
            acceptance_state
        ),

        "source_claims_external_delivery": True,

        "external_delivery_attempted": True,

        "external_receipt_present": True,

        "handoff_delivered": (
            acceptance_state
            == "accepted"
        ),

        "fixture_only": (
            fixture_only
        ),
    }


def _sha256(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return hashlib.sha256(
        canonical
    ).hexdigest()


def build_gp039_certification_fixture():
    """
    Validator certification fixture only.

    Never counts as real external delivery.
    """

    attempt = (
        get_gp038_delivery_attempt_record()
    )

    receipt_id = (
        "gp039-certification-fixture-receipt"
    )

    acceptance_state = (
        ExternalReceiptAcceptanceState
        .ACCEPTED.value
    )

    payload = _receipt_hash_payload(
        receipt_id=receipt_id,
        attempt=attempt,
        acceptance_state=acceptance_state,
        fixture_only=True,
    )

    return ExternalHandoffReceiptClaim(
        receipt_id=receipt_id,

        delivery_attempt_record_id=(
            attempt.delivery_attempt_record_id
        ),

        delivery_envelope_id=(
            attempt.delivery_envelope_id
        ),

        delivery_envelope_integrity_hash=(
            attempt
            .delivery_envelope_integrity_hash
        ),

        delivery_target_kind=(
            attempt.delivery_target_kind
        ),

        delivery_target_id=(
            attempt.delivery_target_id
        ),

        acceptance_state=(
            acceptance_state
        ),

        source_claims_external_delivery=True,

        external_delivery_attempted=True,

        external_receipt_present=True,

        handoff_delivered=True,

        fixture_only=True,

        receipt_integrity_hash=(
            _sha256(payload)
        ),
    )


def validate_external_handoff_receipt(
    receipt,
):
    attempt = (
        get_gp038_delivery_attempt_record()
    )

    expected_payload = {
        "receipt_id": (
            receipt.receipt_id
        ),

        "delivery_attempt_record_id": (
            receipt.delivery_attempt_record_id
        ),

        "delivery_envelope_id": (
            receipt.delivery_envelope_id
        ),

        "delivery_envelope_integrity_hash": (
            receipt
            .delivery_envelope_integrity_hash
        ),

        "delivery_target_kind": (
            receipt.delivery_target_kind
        ),

        "delivery_target_id": (
            receipt.delivery_target_id
        ),

        "acceptance_state": (
            receipt.acceptance_state
        ),

        "source_claims_external_delivery": (
            receipt
            .source_claims_external_delivery
        ),

        "external_delivery_attempted": (
            receipt.external_delivery_attempted
        ),

        "external_receipt_present": (
            receipt.external_receipt_present
        ),

        "handoff_delivered": (
            receipt.handoff_delivered
        ),

        "fixture_only": (
            receipt.fixture_only
        ),
    }

    integrity_verified = (
        _sha256(expected_payload)
        == receipt.receipt_integrity_hash
    )

    attempt_binding_verified = (
        receipt.delivery_attempt_record_id
        == attempt.delivery_attempt_record_id
    )

    envelope_binding_verified = (
        receipt.delivery_envelope_id
        == attempt.delivery_envelope_id

        and receipt
        .delivery_envelope_integrity_hash
        == attempt
        .delivery_envelope_integrity_hash
    )

    target_binding_verified = (
        receipt.delivery_target_kind
        == attempt.delivery_target_kind

        and receipt.delivery_target_id
        == attempt.delivery_target_id
    )

    acceptance_verified = (
        receipt.acceptance_state
        == "accepted"

        and receipt
        .source_claims_external_delivery
        is True

        and receipt
        .external_delivery_attempted
        is True

        and receipt
        .external_receipt_present
        is True

        and receipt.handoff_delivered
        is True
    )

    valid = (
        integrity_verified
        and attempt_binding_verified
        and envelope_binding_verified
        and target_binding_verified
        and acceptance_verified
    )

    real_external = (
        valid
        and receipt.fixture_only
        is False
    )

    return ExternalHandoffReceiptValidation(
        validation_id=(
            "external-receipt-validation-"
            f"{receipt.receipt_id}"
        ),

        receipt_id=receipt.receipt_id,

        validation_state=(
            ExternalReceiptValidationState
            .VALID.value
            if valid
            else ExternalReceiptValidationState
            .REJECTED.value
        ),

        attempt_binding_verified=(
            attempt_binding_verified
        ),

        envelope_binding_verified=(
            envelope_binding_verified
        ),

        target_binding_verified=(
            target_binding_verified
        ),

        receipt_integrity_verified=(
            integrity_verified
        ),

        acceptance_verified=(
            acceptance_verified
        ),

        fixture_only=(
            receipt.fixture_only
        ),

        counts_as_real_external_receipt=(
            real_external
        ),

        handoff_delivered_verified=(
            real_external
        ),

        soulaana_summary=(
            (
                "The receipt structure is valid, but this "
                "is only the GP039 certification fixture."
            )
            if receipt.fixture_only
            else
            (
                "The external delivery receipt has been "
                "validated against the protected attempt."
            )
        ),

        soulaana_why_it_matters=(
            "Clouds must never mark a handoff delivered "
            "without a receipt that binds to the exact "
            "attempt, envelope, target, and integrity hash."
        ),

        soulaana_next_step=(
            (
                "Wait for a real Tower or external adapter "
                "receipt before marking delivery verified."
            )
            if receipt.fixture_only
            else
            (
                "Use the verified receipt in the handoff "
                "corridor closeout record."
            )
        ),
    )


def get_gp039_fixture_validation():
    return validate_external_handoff_receipt(
        build_gp039_certification_fixture()
    )


def get_clouds_gp039_status_payload():
    gp038 = (
        get_clouds_gp038_status_payload()
    )

    validation = (
        get_gp039_fixture_validation()
    )

    safe = (
        gp038["status"] == "ready"
        and gp038["safe_to_continue"] is True

        and gp038["external_transport_invoked"]
        is False

        and gp038["external_receipt_present"]
        is False

        and validation.validation_state
        == "valid"

        and validation
        .attempt_binding_verified
        is True

        and validation
        .envelope_binding_verified
        is True

        and validation
        .target_binding_verified
        is True

        and validation
        .receipt_integrity_verified
        is True

        and validation
        .acceptance_verified
        is True

        and validation.fixture_only
        is True

        and validation
        .counts_as_real_external_receipt
        is False

        and validation
        .handoff_delivered_verified
        is False
    )

    return {
        "pack": "GP039",
        "phase": "CLOUDS_PHASE_II",

        "section": (
            "EXTERNAL RECEIPT / "
            "ACCEPTANCE VALIDATION CONTRACT"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "receipt_validator_ready": True,

        "fixture_validation_state": (
            validation.validation_state
        ),

        "fixture_attempt_binding_verified": True,

        "fixture_envelope_binding_verified": True,

        "fixture_target_binding_verified": True,

        "fixture_integrity_verified": True,

        "fixture_acceptance_verified": True,

        "fixture_only": True,

        "external_receipt_connected": False,

        "external_receipt_verified": False,

        "external_acceptance_verified": False,

        "tower_receipt_verified": False,

        "handoff_delivered": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP040 — PROTECTED HANDOFF CORRIDOR "
            "CLOSEOUT / EXTERNAL BOUNDARY SEAL"
        ),
    }
