"""
GP066 — Signed summary transport contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SignedSummaryTransportEnvelope:

    transport_version: str

    source_id: str
    source_contract_version: str

    message_id: str
    nonce: str

    sent_at: str

    key_ref: str

    signature_algorithm: str

    body_sha256: str
    signature_hex: str

    certification_fixture_only: bool

    payload: dict[str, Any]


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "transport_version":
            self.transport_version,

            "source_id":
            self.source_id,

            "source_contract_version":
            self.source_contract_version,

            "message_id":
            self.message_id,

            "nonce":
            self.nonce,

            "sent_at":
            self.sent_at,

            "key_ref":
            self.key_ref,

            "signature_algorithm":
            self.signature_algorithm,

            "body_sha256":
            self.body_sha256,

            "signature_hex":
            self.signature_hex,

            "certification_fixture_only":
            self.certification_fixture_only,

            "payload":
            dict(
                self.payload
            ),
        }


@dataclass(frozen=True)
class SignedSummaryTransportValidation:

    source_id: str

    message_id: str
    nonce: str

    source_known: bool

    source_contract_matches: bool

    key_ref_matches: bool

    body_integrity_verified: bool

    signature_algorithm_verified: bool

    signature_verified: bool

    message_id_replay_detected: bool

    nonce_replay_detected: bool

    replay_rejected: bool

    certification_fixture_only: bool

    accepted_for_connection_evaluation: bool

    counts_as_real_live_connection: bool

    secret_material_persisted: bool

    downstream_execution_performed: bool

    rejection_reasons: tuple[
        str,
        ...
    ]


    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = (
            self.__dict__.copy()
        )

        data[
            "rejection_reasons"
        ] = list(
            self.rejection_reasons
        )

        return data
