"""
GP065 — Tower↔Clouds six-source connection trust registry.

Stores identity + contract expectations only.

No secret material is stored here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CloudsFeedSourceTrustSpec:

    source_id: str
    source_label: str

    adapter_id: str
    source_contract_version: str

    clouds_feed_schema_version: str

    signature_algorithm: str

    signing_key_ref: str

    credential_reference_only: bool
    secret_material_stored: bool

    external_transport_required: bool
    external_connection_verification_required: bool

    raw_source_access_allowed: bool
    downstream_execution_allowed: bool
    cross_app_import_allowed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class CloudsFeedSourceTrustRegistry:

    registry_version: str

    sources: tuple[
        CloudsFeedSourceTrustSpec,
        ...
    ]

    source_count: int

    credential_reference_count: int

    secret_material_count: int

    external_transport_required_count: int

    external_verification_required_count: int

    raw_source_access_allowed_count: int

    downstream_execution_allowed_count: int

    cross_app_import_allowed_count: int


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "registry_version":
            self.registry_version,

            "sources": [
                item.to_dict()
                for item
                in self.sources
            ],

            "source_count":
            self.source_count,

            "credential_reference_count":
            self.credential_reference_count,

            "secret_material_count":
            self.secret_material_count,

            "external_transport_required_count":
            self.external_transport_required_count,

            "external_verification_required_count":
            self.external_verification_required_count,

            "raw_source_access_allowed_count":
            self.raw_source_access_allowed_count,

            "downstream_execution_allowed_count":
            self.downstream_execution_allowed_count,

            "cross_app_import_allowed_count":
            self.cross_app_import_allowed_count,
        }
