"""SC006 owner-facing source preflight: evidence inventory, never a release switch.

A document URL, tracking issue, locally populated field, successful synthetic
test or operator assertion is NOT independently authenticated infrastructure
proof. This module cannot return GO and cannot enable a runtime/provider.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

from .contracts import CloudError

_ID = re.compile(r"[A-Za-z0-9_.:/@#-]{1,180}\Z")


@dataclass(frozen=True)
class ReadinessGate:
    gate_id: str
    owner: str
    title: str
    required_proof: str


_GATES = (
    ReadinessGate(
        "tower_real_issuer", "Tower", "Current signed grant issuer",
        "Independent Tower signing key custody, rotation, approval/step-up and revocation proof",
    ),
    ReadinessGate(
        "private_vault_peer", "Tower + Cloud", "Authenticated Vault service peer",
        "Real private transport/mTLS identity verification; reject caller-provided peer booleans",
    ),
    ReadinessGate(
        "vault_canonical_registry", "Archive Vault", "Canonical evidence and receipts",
        "Vault original hash and malware scan proof, versions, retention, legal hold and canonical receipt transaction",
    ),
    ReadinessGate(
        "durable_replay_and_authority", "Tower + Cloud", "Durable replay and policy checks",
        "Independent nonce/revocation failover and adversarial end-to-end expired/revoked grant tests",
    ),
    ReadinessGate(
        "approved_private_provider", "Owner + Cloud", "Private locked provider",
        "Owner-selected real operator, actual physical-server owner, jurisdiction/subprocessors, conditional create and object-lock evidence",
    ),
    ReadinessGate(
        "independent_backup_keys", "Owner + Cloud", "Independent backup domain and keys",
        "Separate failure domain, IAM, key custody, rotation, recovery and retention policy",
    ),
    ReadinessGate(
        "external_audit_checkpoint", "Cloud + independent custodian", "Immutable offsite journal anchor",
        "Independent signer, create-only offsite sink, rollback detection and tested custody",
    ),
    ReadinessGate(
        "site_loss_restore", "Cloud + Archive Vault", "Measured full recovery drill",
        "Real primary outage, independently retrieved ciphertext and keys, Vault original authentication and recovery decision/receipt",
    ),
    ReadinessGate(
        "incident_monitoring", "Cloud + Tower", "Alert delivery and incident response",
        "Demonstrated owner alert delivery, scoped metrics, escalation and outage runbook",
    ),
    ReadinessGate(
        "owner_release", "Owner", "Funding, vendor and production acceptance",
        "Explicit owner approval for provider/hardware, costs, RPO/RTO and separately documented production decision",
    ),
)

GATE_IDS = frozenset(gate.gate_id for gate in _GATES)


def source_preflight(
    evidence_references: Mapping[str, str] | None = None,
) -> dict:
    """Produce a compact owner-ready HOLD report, not approval verification.

    References are unverified review pointers. There is deliberately no boolean
    or certificate constructor that can set production_authorized from inputs.
    """
    references = {} if evidence_references is None else evidence_references
    if not isinstance(references, Mapping) or set(references) - GATE_IDS:
        raise CloudError("unexpected release-gate evidence reference")
    if any(
        not isinstance(ref, str) or not _ID.fullmatch(ref)
        for ref in references.values()
    ):
        raise CloudError("only short non-secret review references are accepted")
    gates = [
        {
            "gate_id": item.gate_id,
            "owner": item.owner,
            "title": item.title,
            "required_proof": item.required_proof,
            "review_reference_present": bool(references.get(item.gate_id)),
            "independently_certified": False,
            "status": "EVIDENCE_REVIEW_PENDING",
        }
        for item in _GATES
    ]
    return {
        "service": "simplee_sovereign_cloud",
        "status": "SOURCE_ONLY_NO_GO",
        "production_authorized": False,
        "hosted_receiver_enabled": False,
        "release_decision_recorded": False,
        "source_tests_are_not_live_proof": True,
        "gate_count": len(gates),
        "review_references_present": sum(x["review_reference_present"] for x in gates),
        "independent_certifications": 0,
        "gates": gates,
    }
