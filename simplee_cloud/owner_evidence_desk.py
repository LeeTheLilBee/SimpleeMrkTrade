"""SC021 owner-local evidence desk: verified status + untrusted review pointers.

This is NOT an authenticated hosted dashboard, independent external attestation,
provider approval or release mechanism. Nothing returned here can set GO.
"""
from __future__ import annotations

from typing import Mapping

from .authority_checkpoints import (
    SignedAuthorityCheckpoint, verify_authority_checkpoint,
)
from .control_checkpoints import (
    SignedControlCheckpoint, verify_control_checkpoint,
)
from .contracts import CloudError, IntegrityError
from .journal import SQLiteOperationalJournal
from .journaled_backup import JournaledBackupOperations
from .namespace_bindings import SQLiteNamespaceBindingLedger
from .namespace_coverage import source_namespace_binding_coverage
from .key_readiness import source_backup_key_readiness
from .provider_review import ProviderCandidate, review_candidate, required_provider_checks
from .readiness import source_preflight
from .source_status import owner_safe_source_snapshot
from .tower_grants import SQLiteNonceReplayStore


def owner_local_evidence_desk(
    *, journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    candidate: ProviderCandidate | None = None,
    provider_references: dict[str, str] | None = None,
    release_references: Mapping[str, str] | None = None,
    checkpoint: SignedAuthorityCheckpoint | None = None,
    control_checkpoint: SignedControlCheckpoint | None = None,
    namespace_bindings: SQLiteNamespaceBindingLedger | None = None,
    pinned_public_keys: Mapping[str, bytes] | None = None,
    backup_operations: JournaledBackupOperations | None = None,
) -> dict:
    """Combine verified local-source facts without accepting self-asserted GO.

    A supplied signed checkpoint is only verified against *both* local ledgers.
    It cannot attest to immutable external custody or the true latest tip.
    """
    if not isinstance(journal, SQLiteOperationalJournal) or not isinstance(
        replay_store, SQLiteNonceReplayStore
    ):
        raise CloudError("separate verified Cloud and replay source ledgers required")
    if (candidate is None) != (provider_references is None):
        raise CloudError("provider identity and evidence pointers must be supplied together")
    if checkpoint is not None and control_checkpoint is not None:
        raise CloudError("supply one checkpoint generation, never both")
    supplied_checkpoint = (
        checkpoint if checkpoint is not None else control_checkpoint
    )
    if (supplied_checkpoint is None) != (pinned_public_keys is None):
        raise CloudError("signed checkpoint and independent pinned public keys required together")
    if namespace_bindings is not None and not isinstance(
        namespace_bindings, SQLiteNamespaceBindingLedger
    ):
        raise CloudError("verified namespace binding ledger required")
    if control_checkpoint is not None and namespace_bindings is None:
        raise CloudError("control checkpoint requires verified namespace binding ledger")
    if backup_operations is not None and (
        not isinstance(backup_operations, JournaledBackupOperations) or
        backup_operations.journal.path != journal.path
    ):
        raise CloudError("backup key preflight must use this verified Cloud journal")

    # Fail closed on any tampered storage or replay history, including when
    # optional evidence/pointers are omitted. Never swallow verification errors.
    local = owner_safe_source_snapshot(journal)
    replay = replay_store.verify_chain()
    if replay["valid"] is not True or replay["production_authorized"] is not False:
        raise IntegrityError("unexpected replay ledger source status")

    namespace_summary = {
        "supplied": namespace_bindings is not None,
        "status": "NOT_EVALUATED",
        "binding_count": None,
        "event_count": None,
        "resolver_namespace_count": None,
        "matched_namespace_count": None,
        "missing_resolver_namespace_count": None,
        "unused_enrolled_namespace_count": None,
        "raw_entity_ids_persisted": False,
        "external_registry_certified": False,
        "binding_key_matches_registered_commitment": None,
        "binding_key_commitment_external_anchor_certified": False,
        "binding_key_custody_certified": False,
        "production_authorized": False,
    }
    if namespace_bindings is not None:
        verified_namespace = namespace_bindings.verify_chain()
        coverage = source_namespace_binding_coverage(journal, namespace_bindings)
        namespace_summary.update({
            "status": coverage["status"],
            "binding_count": verified_namespace["binding_count"],
            "event_count": verified_namespace["event_count"],
            "resolver_namespace_count": coverage["resolver_namespace_count"],
            "matched_namespace_count": coverage["matched_namespace_count"],
            "missing_resolver_namespace_count": coverage["missing_resolver_namespace_count"],
            "unused_enrolled_namespace_count": coverage["unused_enrolled_namespace_count"],
            "raw_entity_ids_persisted": False,
            "binding_key_matches_registered_commitment": verified_namespace["binding_key_matches_registered_commitment"],
            "binding_key_commitment_external_anchor_certified": False,
            "external_registry_certified": False,
            "binding_key_custody_certified": False,
            "production_authorized": False,
        })

    release = source_preflight(release_references)
    provider = review_candidate(candidate, provider_references) if candidate is not None else None
    checkpoint_summary = {
        "supplied": supplied_checkpoint is not None,
        "kind": (
            "SC020_STORAGE_REPLAY"
            if checkpoint is not None else
            "SC039_STORAGE_REPLAY_NAMESPACE"
            if control_checkpoint is not None else
            "NONE"
        ),
        "local_storage_and_replay_prefix_verified": False,
        "local_namespace_prefix_verified": False,
        "local_cross_ledger_checkpoint_verified": False,
        "local_namespace_binding_key_commitment_signed": False,
        "actual_external_latest_attested": False,
        "external_immutability_certified": False,
    }
    if checkpoint is not None:
        doc = verify_authority_checkpoint(
            checkpoint, pinned_public_keys=pinned_public_keys,
            journal=journal, replay_store=replay_store,
        )
        checkpoint_summary["local_storage_and_replay_prefix_verified"] = True
        checkpoint_summary["storage_event_count"] = doc["storage_event_count"]
        checkpoint_summary["replay_event_count"] = doc["replay_event_count"]
    elif control_checkpoint is not None:
        doc = verify_control_checkpoint(
            control_checkpoint, pinned_public_keys=pinned_public_keys,
            journal=journal, replay_store=replay_store,
            namespace_bindings=namespace_bindings,
        )
        checkpoint_summary["kind"] = (
            "SC043_STORAGE_REPLAY_NAMESPACE_KEY"
            if doc["schema"] == "simplee.cloud.control-checkpoint.v2"
            else "SC039_STORAGE_REPLAY_NAMESPACE"
        )
        checkpoint_summary["local_storage_and_replay_prefix_verified"] = True
        checkpoint_summary["local_namespace_prefix_verified"] = True
        checkpoint_summary["local_cross_ledger_checkpoint_verified"] = True
        checkpoint_summary["local_namespace_binding_key_commitment_signed"] = (
            doc["schema"] == "simplee.cloud.control-checkpoint.v2"
        )
        checkpoint_summary["storage_event_count"] = doc["storage_event_count"]
        checkpoint_summary["replay_event_count"] = doc["replay_event_count"]
        checkpoint_summary["namespace_event_count"] = doc["namespace_event_count"]

    key_summary = {
        "supplied": backup_operations is not None,
        "status": "NOT_EVALUATED",
        "acknowledged_backup_count": None,
        "distinct_key_reference_count": None,
        "resolvable_key_reference_count": None,
        "unavailable_key_reference_count": None,
        "acknowledged_backups_depending_on_unavailable_key_count": None,
        "pending_backup_count": None,
        "integrity_hold_backup_count": None,
        "provider_bytes_read": False,
        "backup_ciphertext_authenticated_in_this_check": False,
        "external_kms_hsm_custody_certified": False,
        "old_key_recovery_drill_certified": False,
        "production_authorized": False,
    }
    if backup_operations is not None:
        verified_keys = source_backup_key_readiness(backup_operations)
        for key in tuple(key_summary):
            if key == "supplied":
                continue
            if key in verified_keys:
                key_summary[key] = verified_keys[key]

    provider_count = len(required_provider_checks())
    return {
        "schema": "simplee.cloud.owner-local-evidence-desk.v1",
        "status": "SOURCE_ONLY_NO_GO",
        "production_authorized": False,
        "hosted_receiver_enabled": False,
        "actual_provider_contacted": False,
        "real_tower_issuer_verified": False,
        "real_vault_registry_verified": False,
        "owner_release_recorded": False,
        "retention_deletion_protocol_connected": False,
        "cloud_delete_capability_exposed": False,
        "provider_delete_authorized": False,
        "cross_ledger_point_in_time_certified": False,
        "local_storage": {
            "attention": local["attention"],
            "local_storage_point_in_time_consistent": local["local_storage_point_in_time_consistent"],
            "journal_event_count": local["journal_event_count"],
            "pending_primary_count": local["pending_primary_count"],
            "pending_backup_count": local["pending_backup_count"],
            "restore_request_count": local["restore_request_count"],
            "restore_completed_count": local["restore_completed_count"],
            "restore_integrity_hold_count": local["restore_integrity_hold_count"],
            "restore_pending_count": local["restore_pending_count"],
            "restore_retryable_outage_count": local["restore_retryable_outage_count"],
            "restore_physical_recovery_certified": False,
            "restore_vault_original_authenticated": False,
            "acknowledged_primary_object_count": local["acknowledged_primary_object_count"],
            "matched_backup_ack_count": local["matched_backup_ack_count"],
            "uncovered_primary_object_count": local["uncovered_primary_object_count"],
            "uncovered_with_pending_backup_count": local["uncovered_with_pending_backup_count"],
            "actual_backup_bytes_reverified": False,
            "independent_failure_domain_certified": False,
            "primary_integrity_hold_count": local["primary_integrity_hold_count"],
            "backup_integrity_hold_count": local["backup_integrity_hold_count"],
            "backend_error_event_count": local["backend_error_event_count"],
            "total_incident_records": local["total_incident_records"],
            "work_queue": local["work_queue"],
        },
        "local_replay": {
            "verified": True,
            "event_count": replay["event_count"],
            "consumed_count": replay["consumed_count"],
            "external_checkpoint_certified": False,
        },
        "joint_checkpoint": checkpoint_summary,
        "namespace_binding_readiness": namespace_summary,
        "backup_key_readiness": key_summary,
        "provider_review": {
            "supplied": provider is not None,
            "required_check_count": provider_count,
            "review_references_present": provider_count - len(provider.missing) if provider else 0,
            "missing_check_ids": list(provider.missing) if provider else list(required_provider_checks()),
            "independently_verified": False,
            "owner_approved": False,
            "storage_runtime_authorized": False,
        },
        "release_gates": {
            "required_count": release["gate_count"],
            "review_references_present": release["review_references_present"],
            "independent_certifications": 0,
            "production_authorized": False,
        },
        "next_action": (
            "Resolve local source holds first; Tower/Vault authority, provider and "
            "offsite proofs remain independently gated. Never interpret evidence "
            "references, source-checkpoint signatures or empty local metrics as GO."
        ),
    }
