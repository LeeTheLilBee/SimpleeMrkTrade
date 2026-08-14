"""
GP039 — External Receipt / Acceptance Validation Contract.

Defines how a future real Tower/external receipt must prove
delivery and acceptance.

Certification fixtures never count as real external receipts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExternalReceiptAcceptanceState(str, Enum):
    ACCEPTED = "accepted"
    DECLINED = "declined"
    UNKNOWN = "unknown"


class ExternalReceiptValidationState(str, Enum):
    VALID = "valid"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ExternalHandoffReceiptClaim:
    receipt_id: str

    delivery_attempt_record_id: str

    delivery_envelope_id: str
    delivery_envelope_integrity_hash: str

    delivery_target_kind: str
    delivery_target_id: str

    acceptance_state: str

    source_claims_external_delivery: bool

    external_delivery_attempted: bool
    external_receipt_present: bool
    handoff_delivered: bool

    fixture_only: bool

    receipt_integrity_hash: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ExternalHandoffReceiptValidation:
    validation_id: str
    receipt_id: str

    validation_state: str

    attempt_binding_verified: bool
    envelope_binding_verified: bool
    target_binding_verified: bool
    receipt_integrity_verified: bool

    acceptance_verified: bool

    fixture_only: bool

    counts_as_real_external_receipt: bool

    handoff_delivered_verified: bool

    soulaana_summary: str
    soulaana_why_it_matters: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
