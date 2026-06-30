"""Contracts for Archive Vault records, receipt chains, and packets.

This file is intentionally dependency-light so The Clouds, The Tower, OB, Teller,
ATM, Property, and future Simplee apps can safely import the same shapes without
creating circular app dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


VAULT_VERSION = "vault_giant_pack_001"


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp for generated snapshots."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class VaultUniversalId:
    """Universal identity links used across Simplee ecosystem apps."""

    app_id: str
    entity_id: str
    lane_id: str
    account_id: str
    asset_id: str = ""
    document_id: str = ""
    receipt_id: str = ""
    decision_id: str = ""
    task_id: str = ""
    contact_id: str = ""
    event_id: str = ""
    packet_id: str = ""

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class VaultDocumentRecord:
    """Canonical Vault document record.

    Vault stores the record, ownership, permissions, status, packet links, and
    proof chain. Physical storage can be attached later only after Tower grants
    the approved upload/storage provider.
    """

    document_id: str
    title: str
    document_type: str
    business_lane: str
    owning_app: str
    sensitivity: str
    status: str
    required_for: List[str]
    universal_id: VaultUniversalId
    allowed_viewers: List[str] = field(default_factory=list)
    linked_asset: str = ""
    linked_contact: str = ""
    linked_decision: str = ""
    linked_receipt_ids: List[str] = field(default_factory=list)
    freshness_days: int = 30
    expires_at: str = ""
    redaction_required: bool = True
    direct_upload_allowed: bool = False
    storage_provider: str = "not_connected"
    created_at: str = field(default_factory=utc_now_iso)
    summary: str = ""
    next_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["universal_id"] = self.universal_id.to_dict()
        return data


@dataclass(frozen=True)
class VaultReceiptRecord:
    """Proof/receipt record attached to documents, packets, decisions, or events."""

    receipt_id: str
    receipt_type: str
    business_lane: str
    owning_app: str
    linked_document_ids: List[str]
    linked_packet_id: str
    linked_decision_id: str
    status: str
    actor: str
    tower_required: bool = True
    owner_approval_required: bool = True
    revocation_status: str = "active"
    created_at: str = field(default_factory=utc_now_iso)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VaultPacketTemplate:
    """Reusable due-diligence and proof packet template."""

    packet_id: str
    packet_name: str
    business_lane: str
    owning_app: str
    purpose: str
    required_document_types: List[str]
    required_receipt_types: List[str]
    approval_chain: List[str]
    readiness_weight: int
    redaction_profile: str
    status: str = "template_ready"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VaultReadinessSignal:
    """Individual readiness signal for owner dashboard and Clouds handoff."""

    signal_id: str
    label: str
    value: bool
    severity: str
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
