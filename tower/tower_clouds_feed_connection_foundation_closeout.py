"""
GP068 — Tower↔Clouds real-feed connection foundation closeout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TowerCloudsFeedConnectionFoundationCloseout:

    checkpoint_id: str

    source_trust_registry_ready: bool

    six_source_identity_ready: bool

    secret_reference_boundary_ready: bool

    signed_transport_ready: bool

    body_integrity_ready: bool

    signature_verification_ready: bool

    replay_rejection_ready: bool

    freshness_gate_ready: bool

    disconnected_state_ready: bool

    connected_unverified_state_ready: bool

    certification_verified_state_ready: bool

    external_verified_state_contract_ready: bool

    degraded_state_ready: bool

    revoked_state_ready: bool

    certification_fixture_live_claim_blocked: bool

    ready_for_source_connection_wave_1: bool

    wave_1_source_ids: tuple[
        str,
        ...
    ]

    real_live_connection_count: int

    real_live_feeds_connected: bool

    source_endpoints_contacted: bool

    external_transport_attempted: bool

    hosted_tower_integration_verified: bool

    hosted_staging_verified: bool

    external_beta_acceptance_recorded: bool

    externally_beta_ready: bool

    secret_material_persisted: bool

    capital_movement_performed: bool

    downstream_execution_performed: bool

    conclusion: str


    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = (
            self.__dict__.copy()
        )

        data[
            "wave_1_source_ids"
        ] = list(
            self.wave_1_source_ids
        )

        return data
