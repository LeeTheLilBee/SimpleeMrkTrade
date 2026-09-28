"""SC021 owner-local evidence desk: verified status + untrusted review pointers.

This is NOT an authenticated hosted dashboard, independent external attestation,
provider approval or release mechanism. Nothing returned here can set GO.
"""
from __future__ import annotations

from typing import Mapping

from .authority_checkpoints import (
    SignedAuthorityCheckpoint, verify_authority_checkpoint,
)
from .contracts import CloudError, IntegrityError
from .journal import SQLiteOperationalJournal
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
    pinned_public_keys: Mapping[str, bytes] | None = None,
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
    if (checkpoint is None) != (pinned_public_keys is None):
        raise CloudError("signed checkpoint and independent pinned public keys required together")

    # Fail closed on any tampered storage or replay history, including when
    # optional evidence/pointers are omitted. Never swallow verification errors.
    local = owner_safe_source_snapshot(journal)
    replay = replay_store.verify_chain()
    if replay["valid"] is not True or replay["production_authorized"] is not False:
        raise IntegrityError("unexpected replay ledger source status")

    release = source_preflight(release_references)
    provider = review_candidate(candidate, provider_references) if candidate is not None else None
    checkpoint_summary = {
        "supplied": checkpoint is not None,
        "local_storage_and_replay_prefix_verified": False,
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
        "cross_ledger_point_in_time_certified": False,
        "local_storage": {
            "attention": local["attention"],
            "local_storage_point_in_time_consistent": local["local_storage_point_in_time_consistent"],
            "journal_event_count": local["journal_event_count"],
            "pending_primary_count": local["pending_primary_count"],
            "pending_backup_count": local["pending_backup_count"],
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
