"""
GP065 — Six-source connection trust / source identity registry.

Uses exact contract identifiers already defined by Clouds GP041–GP043.
"""

from __future__ import annotations

from functools import lru_cache

try:

    from .tower_clouds_feed_source_trust import (
        CloudsFeedSourceTrustRegistry,
        CloudsFeedSourceTrustSpec,
    )

    from .tower_clouds_gp060_reconciliation_closeout_service import (
        get_clouds_gp064_status_payload,
    )

except ImportError:

    from tower_clouds_feed_source_trust import (
        CloudsFeedSourceTrustRegistry,
        CloudsFeedSourceTrustSpec,
    )

    from tower_clouds_gp060_reconciliation_closeout_service import (
        get_clouds_gp064_status_payload,
    )


CANONICAL_CONNECTION_SOURCE_IDS = (

    "observatory",

    "tower",

    "teller",

    "grounds",

    "archive_vault",

    "atm_operations",
)


SOURCE_DEFINITIONS = {

    "observatory": {
        "source_label":
        "The Observatory",

        "adapter_id":
        "clouds-adapter-observatory-v1",

        "source_contract_version":
        "observatory-clouds-summary-v1",
    },

    "tower": {
        "source_label":
        "The Tower",

        "adapter_id":
        "clouds-adapter-tower-v1",

        "source_contract_version":
        "tower-clouds-summary-v1",
    },

    "teller": {
        "source_label":
        "The Teller",

        "adapter_id":
        "clouds-adapter-teller-v1",

        "source_contract_version":
        "teller-clouds-summary-v1",
    },

    "grounds": {
        "source_label":
        "The Grounds",

        "adapter_id":
        "clouds-adapter-grounds-v1",

        "source_contract_version":
        "grounds-clouds-summary-v1",
    },

    "archive_vault": {
        "source_label":
        "Archive Vault",

        "adapter_id":
        "clouds-adapter-archive-vault-v1",

        "source_contract_version":
        "archive-vault-clouds-summary-v1",
    },

    "atm_operations": {
        "source_label":
        "ATM Operations",

        "adapter_id":
        "clouds-adapter-atm-operations-v1",

        "source_contract_version":
        "atm-operations-clouds-summary-v1",
    },
}


def _key_ref(
    source_id,
):

    return (
        "tower-secret-ref:"
        "clouds-summary-signing/"
        f"{source_id}/v1"
    )


@lru_cache(
    maxsize=1
)
def get_clouds_feed_source_trust_registry():

    sources = tuple(

        CloudsFeedSourceTrustSpec(

            source_id=source_id,

            source_label=(
                SOURCE_DEFINITIONS[
                    source_id
                ][
                    "source_label"
                ]
            ),

            adapter_id=(
                SOURCE_DEFINITIONS[
                    source_id
                ][
                    "adapter_id"
                ]
            ),

            source_contract_version=(
                SOURCE_DEFINITIONS[
                    source_id
                ][
                    "source_contract_version"
                ]
            ),

            clouds_feed_schema_version=(
                "clouds-operating-feed-v1"
            ),

            signature_algorithm=(
                "hmac-sha256"
            ),

            signing_key_ref=(
                _key_ref(
                    source_id
                )
            ),

            credential_reference_only=True,

            secret_material_stored=False,

            external_transport_required=True,

            external_connection_verification_required=True,

            raw_source_access_allowed=False,

            downstream_execution_allowed=False,

            cross_app_import_allowed=False,
        )

        for source_id
        in CANONICAL_CONNECTION_SOURCE_IDS
    )


    return CloudsFeedSourceTrustRegistry(

        registry_version=(
            "tower-clouds-source-trust-v1"
        ),

        sources=sources,

        source_count=len(
            sources
        ),

        credential_reference_count=sum(
            item
            .credential_reference_only
            is True

            for item
            in sources
        ),

        secret_material_count=sum(
            item
            .secret_material_stored
            is True

            for item
            in sources
        ),

        external_transport_required_count=sum(
            item
            .external_transport_required
            is True

            for item
            in sources
        ),

        external_verification_required_count=sum(
            item
            .external_connection_verification_required
            is True

            for item
            in sources
        ),

        raw_source_access_allowed_count=sum(
            item
            .raw_source_access_allowed
            is True

            for item
            in sources
        ),

        downstream_execution_allowed_count=sum(
            item
            .downstream_execution_allowed
            is True

            for item
            in sources
        ),

        cross_app_import_allowed_count=sum(
            item
            .cross_app_import_allowed
            is True

            for item
            in sources
        ),
    )


def get_clouds_feed_source_trust_spec(
    source_id,
):

    for item in (
        get_clouds_feed_source_trust_registry()
        .sources
    ):

        if (
            item.source_id
            == source_id
        ):

            return item


    raise KeyError(
        "Unknown Clouds feed source: "
        f"{source_id}"
    )


def get_clouds_gp065_status_payload():

    gp064 = (
        get_clouds_gp064_status_payload()
    )

    registry = (
        get_clouds_feed_source_trust_registry()
    )


    source_ids = tuple(
        item.source_id
        for item
        in registry.sources
    )


    unique_contracts = {
        item.source_contract_version
        for item
        in registry.sources
    }


    unique_key_refs = {
        item.signing_key_ref
        for item
        in registry.sources
    }


    safe = (
        gp064["status"]
        == "ready"

        and gp064[
            "safe_to_continue"
        ]
        is True

        and registry.source_count
        == 6

        and source_ids
        == CANONICAL_CONNECTION_SOURCE_IDS

        and len(
            unique_contracts
        )
        == 6

        and len(
            unique_key_refs
        )
        == 6

        and registry
        .credential_reference_count
        == 6

        and registry
        .secret_material_count
        == 0

        and registry
        .external_transport_required_count
        == 6

        and registry
        .external_verification_required_count
        == 6

        and registry
        .raw_source_access_allowed_count
        == 0

        and registry
        .downstream_execution_allowed_count
        == 0

        and registry
        .cross_app_import_allowed_count
        == 0
    )


    return {

        "pack":
        "GP065",

        "section":
        (
            "SIX-SOURCE CONNECTION TRUST / "
            "SOURCE IDENTITY REGISTRY"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "registry_version":
        registry.registry_version,

        "canonical_source_count":
        6,

        "source_ids":
        list(
            source_ids
        ),

        "unique_source_contract_count":
        len(
            unique_contracts
        ),

        "unique_signing_key_ref_count":
        len(
            unique_key_refs
        ),

        "credential_reference_count":
        6,

        "secret_material_count":
        0,

        "signature_algorithm":
        "hmac-sha256",

        "external_transport_required_count":
        6,

        "external_verification_required_count":
        6,

        "raw_source_access_allowed_count":
        0,

        "cross_app_import_allowed_count":
        0,

        "downstream_execution_allowed_count":
        0,

        "real_live_connection_count":
        0,

        "real_live_feeds_connected":
        False,

        "external_transport_attempted":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP066 — SIGNED SUMMARY TRANSPORT / "
            "AUTHENTICITY + REPLAY GATE"
        ),
    }
