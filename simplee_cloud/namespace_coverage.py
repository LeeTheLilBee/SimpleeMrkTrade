"""SC041/SC044 redacted namespace-binding coverage reconciliation.

Compares only opaque, fully verified local source inventories. SC044 can bind
that comparison to the exact historical prefixes carried by a signed control
checkpoint without claiming cross-database atomicity or external custody.
"""
from __future__ import annotations

from typing import Mapping

from .contracts import CloudError
from .control_checkpoints import (
    SignedControlCheckpoint, verify_control_checkpoint,
)
from .journal import SQLiteOperationalJournal
from .namespace_bindings import SQLiteNamespaceBindingLedger
from .tower_grants import SQLiteNonceReplayStore


def source_namespace_binding_coverage(
    journal: SQLiteOperationalJournal,
    namespace_bindings: SQLiteNamespaceBindingLedger,
    *,
    storage_event_count: int | None = None,
    namespace_event_count: int | None = None,
) -> dict:
    if not isinstance(journal, SQLiteOperationalJournal):
        raise CloudError("verified Cloud operational journal required")
    if not isinstance(namespace_bindings, SQLiteNamespaceBindingLedger):
        raise CloudError("verified namespace binding ledger required")
    if (storage_event_count is None) != (namespace_event_count is None):
        raise CloudError(
            "historical namespace coverage requires both signed ledger prefixes"
        )

    historical = storage_event_count is not None
    required_doc = journal.source_resolver_namespace_inventory(
        storage_event_count,
    )
    enrolled_doc = namespace_bindings.source_namespace_inventory(
        namespace_event_count,
    )
    required = required_doc["namespace_digests"]
    enrolled = enrolled_doc["namespace_digests"]
    if not isinstance(required, frozenset) or not isinstance(enrolled, frozenset):
        raise CloudError("verified opaque namespace inventories required")

    missing = required - enrolled
    unused = enrolled - required
    matched = required & enrolled
    return {
        "schema": "simplee.cloud.namespace-binding-coverage.v2",
        "status": (
            "SOURCE_ONLY_NAMESPACE_BINDING_HOLD"
            if missing else
            "SOURCE_ONLY_NAMESPACE_BINDING_COVERAGE_VERIFIED"
        ),
        "resolver_namespace_count": len(required),
        "enrolled_namespace_count": len(enrolled),
        "matched_namespace_count": len(matched),
        "missing_resolver_namespace_count": len(missing),
        "unused_enrolled_namespace_count": len(unused),
        "storage_inventory_event_count": required_doc["inventory_event_count"],
        "namespace_inventory_event_count": enrolled_doc["inventory_event_count"],
        "historical_prefix_comparison": historical,
        "storage_state_advanced_after_prefix": required_doc["historical_prefix"],
        "namespace_state_advanced_after_prefix": enrolled_doc["historical_prefix"],
        "raw_entity_ids_returned": False,
        "namespace_values_returned": False,
        "cross_ledger_point_in_time_certified": False,
        "external_registry_certified": False,
        "binding_key_custody_certified": False,
        "production_authorized": False,
    }


def source_control_checkpoint_namespace_coverage(
    *,
    checkpoint: SignedControlCheckpoint,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    namespace_bindings: SQLiteNamespaceBindingLedger,
) -> dict:
    """Verify namespace coverage at the exact signed three-ledger vector.

    The signed vector is a sequence of independently verified ledger prefixes,
    NOT a claim that three SQLite files committed one atomic transaction.
    """
    if not isinstance(replay_store, SQLiteNonceReplayStore):
        raise CloudError("verified grant replay ledger required")
    doc = verify_control_checkpoint(
        checkpoint,
        pinned_public_keys=pinned_public_keys,
        journal=journal,
        replay_store=replay_store,
        namespace_bindings=namespace_bindings,
    )
    coverage = source_namespace_binding_coverage(
        journal,
        namespace_bindings,
        storage_event_count=doc["storage_event_count"],
        namespace_event_count=doc["namespace_event_count"],
    )
    return {
        **coverage,
        "schema": "simplee.cloud.signed-vector-namespace-coverage.v1",
        "signed_control_vector_verified": True,
        "control_checkpoint_schema": doc["schema"],
        "namespace_binding_key_commitment_signed": (
            "namespace_binding_key_commitment_sha256" in doc
        ),
        "exact_signed_prefix_coverage_verified": (
            coverage["missing_resolver_namespace_count"] == 0
        ),
        "actual_external_latest_attested": False,
        "cross_ledger_point_in_time_certified": False,
        "independent_offsite_immutability_certified": False,
        "production_authorized": False,
    }
