"""SC003: provider procurement evidence checklist, never deployment authority.

A supplied reference is only a review pointer, not verified proof. All provider
statements and source-only probes are untrusted until independent checks, explicit
owner approval and a later Tower/runtime release gate.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import CloudError

_CHECKS = (
    "atomic_conditional_put_verified",
    "dedicated_private_namespace",
    "bucket_public_access_block",
    "versioning_and_object_lock",
    "retention_and_legal_hold_policy",
    "least_privilege_service_identity",
    "authenticated_transport",
    "at_rest_encryption_and_key_control",
    "audit_access_and_incident_delivery",
    "independent_backup_failure_domain",
    "key_recovery_and_restore_drill",
    "data_location_and_physical_server_owner",
    "subprocessor_and_infrastructure_disclosure",
    "supplier_security_review",
    "owner_funding_and_vendor_approval",
)
_REF = re.compile(r"[A-Za-z0-9_.:/@-]{1,180}\Z")


@dataclass(frozen=True)
class ProviderCandidate:
    provider_label: str
    software_operator: str
    physical_server_owner: str
    storage_jurisdiction: str
    external_dependencies: tuple[str, ...] = ()
    # Free-form provider reputation or ownership preference may be recorded
    # in due diligence, but no vendor is implicitly approved or selected.


@dataclass(frozen=True)
class ProviderReview:
    candidate: ProviderCandidate
    evidence_references: dict[str, str]
    missing: tuple[str, ...]
    status: str = "NO_GO"
    storage_runtime_authorized: bool = False
    provider_independently_verified: bool = False
    owner_approved: bool = False

    @property
    def documentation_complete_for_review(self) -> bool:
        return not self.missing


def review_candidate(
    candidate: ProviderCandidate, evidence_references: dict[str, str],
) -> ProviderReview:
    if not isinstance(candidate, ProviderCandidate) or not all(
        isinstance(x, str) and 1 <= len(x.strip()) <= 180
        for x in (
            candidate.provider_label, candidate.software_operator,
            candidate.physical_server_owner, candidate.storage_jurisdiction,
        )
    ) or not isinstance(candidate.external_dependencies, tuple) or not all(
        isinstance(x, str) and 0 < len(x.strip()) <= 180
        for x in candidate.external_dependencies
    ):
        raise CloudError("provider ownership/dependency disclosure required")
    if not isinstance(evidence_references, dict) or (
        set(evidence_references) - set(_CHECKS)
    ):
        raise CloudError("unexpected provider evidence declaration")
    for value in evidence_references.values():
        if not isinstance(value, str) or not _REF.fullmatch(value):
            raise CloudError("invalid non-secret evidence reference")
    missing = tuple(check for check in _CHECKS if not evidence_references.get(check))
    return ProviderReview(candidate, dict(evidence_references), missing)


def required_provider_checks() -> tuple[str, ...]:
    return _CHECKS
