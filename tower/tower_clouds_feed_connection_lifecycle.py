"""
GP067 — Feed connection lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FeedConnectionState(
    str,
    Enum,
):

    DISCONNECTED = (
        "disconnected"
    )

    CONNECTED_UNVERIFIED = (
        "connected_unverified"
    )

    CERTIFICATION_VERIFIED = (
        "certification_verified"
    )

    EXTERNAL_VERIFIED = (
        "external_verified"
    )

    DEGRADED = (
        "degraded"
    )

    REVOKED = (
        "revoked"
    )


@dataclass(frozen=True)
class FeedConnectionReceipt:

    source_id: str

    connection_state: str

    external_transport_connected: bool

    external_endpoint_verified: bool

    authenticated_message: bool

    fresh_message: bool

    replay_rejected: bool

    revoked: bool

    certification_fixture_only: bool

    live_payload_claim: bool

    counts_as_real_live_connection: bool

    owner_current_state_available: bool

    safe_to_interpret_as_current: bool

    connection_attention_required: bool

    reason_codes: tuple[
        str,
        ...
    ]

    capital_movement_performed: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = (
            self.__dict__.copy()
        )

        data[
            "reason_codes"
        ] = list(
            self.reason_codes
        )

        return data
