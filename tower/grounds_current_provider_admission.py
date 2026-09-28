"""Tower-side current Grounds grant reconciliation, not a production receiver.

This source-only composition deliberately has NO Flask route, public signing
key, issuer, receiver factory, operational release factory or persistent grant.
It accepts only two server-injected independently certified future providers
and derives a bounded candidate from newly queried records on each invocation.
It never promotes their returned fields into a live Tower/Grounds handoff.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
import re
from time import time

from tower.grounds_handoff_requirements_v1 import ROOM_ROLES

SCHEMA = "tower.grounds.current-grant-reconciliation.v1"
REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
JOB_ROLES = frozenset({
    "maintenance_technician", "vendor", "inspector",
    "turnover_crew", "grounds_janitorial",
})
MAX_REFS = 500
MAX_PROPOSAL_SECONDS = 60
TOWER_KEYS = frozenset({
    "verification_state", "evidence_id", "subject_ref", "session_ref",
    "role", "revoked", "expires_at_epoch",
})
GROUNDS_KEYS = frozenset({
    "verification_state", "evidence_id", "subject_ref", "role",
    "revoked", "expires_at_epoch", "property_refs", "unit_property_pairs",
    "assigned_work_refs", "lease_state",
})


class GroundsCurrentProviderUnavailable(PermissionError):
    """Redacted mismatch/unknown error. Never include identities or grants."""


def _ref(value):
    return isinstance(value, str) and REF.fullmatch(value) is not None


def _refs(value):
    if (
        not isinstance(value, list) or len(value) > MAX_REFS
        or any(not _ref(ref) for ref in value)
        or len(value) != len(set(value))
    ):
        raise GroundsCurrentProviderUnavailable("invalid_current_grant_set")
    return frozenset(value)


def _verified(value, required):
    if (
        not isinstance(value, Mapping) or set(value) != required
        or value.get("verification_state") != "VERIFIED"
        or not _ref(value.get("evidence_id"))
        or value.get("revoked") is not False
    ):
        raise GroundsCurrentProviderUnavailable("current_authority_unverified")
    return value


def inspect_current_ground_grants(
    trusted_session_ref: str,
    *,
    current_tower_session: Callable | None = None,
    current_grounds_membership: Callable | None = None,
    now_epoch: int | None = None,
) -> dict:
    """Re-query each source with a *server-selected* session reference.

    The caller must establish that the injected functions represent actual
    independent authenticated providers; this review cannot certify them.
    No browser headers, role, household, unit or supplied grant arrays are
    read here. The current Grounds membership query receives only the subject
    and role derived from current Tower session truth. The resulting candidate
    is not an access token or a TowerScope.
    """
    if not _ref(trusted_session_ref) or not all(callable(p) for p in (
        current_tower_session, current_grounds_membership,
    )):
        raise GroundsCurrentProviderUnavailable("independent_providers_required")
    now = int(time()) if now_epoch is None else now_epoch
    if type(now) is not int or now <= 0:
        raise GroundsCurrentProviderUnavailable("verification_clock_invalid")
    try:
        tower = _verified(current_tower_session(trusted_session_ref), TOWER_KEYS)
        if (
            tower["session_ref"] != trusted_session_ref
            or not _ref(tower["subject_ref"])
            or not isinstance(tower["role"], str)
            or tower["role"] not in ROOM_ROLES
            or type(tower["expires_at_epoch"]) is not int
            or tower["expires_at_epoch"] <= now
        ):
            raise GroundsCurrentProviderUnavailable("tower_current_session_rejected")
        grounds = _verified(
            current_grounds_membership(tower["subject_ref"], tower["role"]),
            GROUNDS_KEYS,
        )
        if (
            grounds["subject_ref"] != tower["subject_ref"]
            or grounds["role"] != tower["role"]
            or type(grounds["expires_at_epoch"]) is not int
            or grounds["expires_at_epoch"] <= now
        ):
            raise GroundsCurrentProviderUnavailable("grounds_current_membership_rejected")
        properties = _refs(grounds["property_refs"])
        works = _refs(grounds["assigned_work_refs"])
        pair_source = grounds["unit_property_pairs"]
        if not isinstance(pair_source, list) or len(pair_source) > MAX_REFS:
            raise GroundsCurrentProviderUnavailable("current_unit_membership_invalid")
        pairs = set()
        for pair in pair_source:
            if (
                not isinstance(pair, (list, tuple)) or len(pair) != 2
                or not _ref(pair[0]) or not _ref(pair[1])
                or pair[0] not in properties or tuple(pair) in pairs
            ):
                raise GroundsCurrentProviderUnavailable("current_unit_membership_invalid")
            pairs.add(tuple(pair))
        if not properties:
            raise GroundsCurrentProviderUnavailable("current_property_grant_missing")
        if tower["role"] == "resident":
            if grounds["lease_state"] != "ACTIVE" or not pairs:
                raise GroundsCurrentProviderUnavailable("current_resident_lease_required")
        elif grounds["lease_state"] not in (None, "NOT_APPLICABLE"):
            raise GroundsCurrentProviderUnavailable("resident_lease_not_a_staff_grant")
        if tower["role"] in JOB_ROLES and not works:
            raise GroundsCurrentProviderUnavailable("current_job_assignment_required")
    except GroundsCurrentProviderUnavailable:
        raise
    except Exception:
        raise GroundsCurrentProviderUnavailable("independent_provider_unavailable") from None

    expires = min(
        now + MAX_PROPOSAL_SECONDS,
        tower["expires_at_epoch"],
        grounds["expires_at_epoch"],
    )
    return {
        "schema_version": SCHEMA,
        "state": "SOURCE_RECONCILED_EXTERNAL_CERTIFICATION_REQUIRED",
        "session_ref": tower["session_ref"],
        "subject_ref": tower["subject_ref"],
        "role": tower["role"],
        "property_refs": sorted(properties),
        # Property/unit pairs preserve the exact current relation; an
        # unrelated unit cannot be paired with an otherwise allowed property.
        "unit_property_pairs": [list(p) for p in sorted(pairs)],
        "assigned_work_refs": sorted(works),
        "tower_evidence_id": tower["evidence_id"],
        "grounds_evidence_id": grounds["evidence_id"],
        "evaluated_at_epoch": now,
        "candidate_until_epoch": expires,
        "current_sources_requeried": True,
        "certified_issuer": False,
        "certified_receiver": False,
        "operational_release_verified": False,
        "signed_handoff_issued": False,
        "tenant_or_staff_session_created": False,
        "can_issue_live_handoff": False,
        "money_authorized": False,
        "physical_entry_authorized": False,
    }
