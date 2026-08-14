"""
GP044 — Six-Source Real Feed Adapter Registry /
Live Connection Readiness Gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EcosystemFeedAdapterRegistrySurface:
    title: str

    source_ids: tuple[
        str,
        ...
    ]

    specs: tuple[
        Any,
        ...
    ]

    certification_results: tuple[
        Any,
        ...
    ]

    source_count: int

    adapter_contract_ready_count: int

    accepted_certification_count: int

    external_source_connected_count: int

    verified_external_connection_count: int

    real_live_connection_count: int

    ready_for_external_feed_connection: bool

    real_live_feed_connected: bool

    live_feed_claimed: bool

    raw_source_access_performed: bool

    downstream_execution_performed: bool

    cross_app_imports_used: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,

            "source_ids": list(
                self.source_ids
            ),

            "specs": [
                item.to_dict()
                for item in self.specs
            ],

            "certification_results": [
                item.to_dict()
                for item
                in self.certification_results
            ],

            "source_count": (
                self.source_count
            ),

            "adapter_contract_ready_count": (
                self
                .adapter_contract_ready_count
            ),

            "accepted_certification_count": (
                self
                .accepted_certification_count
            ),

            "external_source_connected_count": (
                self
                .external_source_connected_count
            ),

            "verified_external_connection_count": (
                self
                .verified_external_connection_count
            ),

            "real_live_connection_count": (
                self.real_live_connection_count
            ),

            "ready_for_external_feed_connection": (
                self
                .ready_for_external_feed_connection
            ),

            "real_live_feed_connected": (
                self.real_live_feed_connected
            ),

            "live_feed_claimed": (
                self.live_feed_claimed
            ),

            "raw_source_access_performed": (
                self.raw_source_access_performed
            ),

            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),

            "cross_app_imports_used": (
                self.cross_app_imports_used
            ),

            "boundary_notice": (
                self.boundary_notice
            ),
        }
