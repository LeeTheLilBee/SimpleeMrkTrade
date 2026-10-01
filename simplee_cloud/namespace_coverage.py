"""SC041 redacted namespace-binding coverage reconciliation.

Compares only opaque, fully verified local source inventories. No raw entity,
namespace value, provider object or external-registry claim is returned.
"""
from __future__ import annotations

from .contracts import CloudError
from .journal import SQLiteOperationalJournal
from .namespace_bindings import SQLiteNamespaceBindingLedger


def source_namespace_binding_coverage(
    journal: SQLiteOperationalJournal,
    namespace_bindings: SQLiteNamespaceBindingLedger,
) -> dict:
    if not isinstance(journal, SQLiteOperationalJournal):
        raise CloudError("verified Cloud operational journal required")
    if not isinstance(namespace_bindings, SQLiteNamespaceBindingLedger):
        raise CloudError("verified namespace binding ledger required")

    required_doc = journal.source_resolver_namespace_inventory()
    enrolled_doc = namespace_bindings.source_namespace_inventory()
    required = required_doc["namespace_digests"]
    enrolled = enrolled_doc["namespace_digests"]
    if not isinstance(required, frozenset) or not isinstance(enrolled, frozenset):
        raise CloudError("verified opaque namespace inventories required")

    missing = required - enrolled
    unused = enrolled - required
    matched = required & enrolled
    return {
        "schema": "simplee.cloud.namespace-binding-coverage.v1",
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
        "raw_entity_ids_returned": False,
        "namespace_values_returned": False,
        "cross_ledger_point_in_time_certified": False,
        "external_registry_certified": False,
        "binding_key_custody_certified": False,
        "production_authorized": False,
    }
