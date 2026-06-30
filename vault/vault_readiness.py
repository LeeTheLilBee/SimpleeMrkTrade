"""Readiness scoring for Archive Vault."""

from __future__ import annotations

from typing import Dict, List

from .vault_contracts import VaultReadinessSignal
from .vault_registry import DOCUMENT_TYPES, PACKET_TEMPLATES, SAMPLE_DOCUMENT_RECORDS, SAMPLE_RECEIPTS
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, TOWER_GUARD_CONTRACT


def get_readiness_signals() -> List[VaultReadinessSignal]:
    return [
        VaultReadinessSignal(
            signal_id="vault_app_registered",
            label="Vault app contract exists",
            value=True,
            severity="ready",
            summary="Archive Vault has a stable app_id and importable service layer.",
        ),
        VaultReadinessSignal(
            signal_id="document_contracts_ready",
            label="Document contracts ready",
            value=len(DOCUMENT_TYPES) >= 6 and len(SAMPLE_DOCUMENT_RECORDS) >= 4,
            severity="ready",
            summary="Core document types and canonical record shapes are available.",
        ),
        VaultReadinessSignal(
            signal_id="packet_templates_ready",
            label="Packet templates ready",
            value=len(PACKET_TEMPLATES) >= 6,
            severity="ready",
            summary="ATM, apartment, trust, OB, Soulaana, and beta packet templates are present.",
        ),
        VaultReadinessSignal(
            signal_id="receipt_chain_ready",
            label="Receipt chain ready",
            value=len(SAMPLE_RECEIPTS) >= 2,
            severity="ready",
            summary="Build and security-boundary receipt examples are linked.",
        ),
        VaultReadinessSignal(
            signal_id="tower_guard_contract_ready",
            label="Tower guard contract ready",
            value=bool(TOWER_GUARD_CONTRACT.get("tower_required")) and not TOWER_GUARD_CONTRACT.get("vault_owns_permissions"),
            severity="ready",
            summary="Vault defers identity, permissions, clearance, and step-up authority to The Tower.",
        ),
        VaultReadinessSignal(
            signal_id="no_direct_upload_enforced",
            label="No direct upload enforced",
            value=NO_DIRECT_UPLOAD_POLICY.get("enabled") is True and NO_DIRECT_UPLOAD_POLICY.get("direct_upload_allowed") is False,
            severity="locked",
            summary="Raw direct uploads are blocked until storage clearance is approved.",
        ),
        VaultReadinessSignal(
            signal_id="redacted_view_ready",
            label="Redacted view policy ready",
            value=REDACTION_POLICY.get("enabled") is True,
            severity="ready",
            summary="Sensitive fields default to redacted and Clouds receives summary-only views.",
        ),
        VaultReadinessSignal(
            signal_id="clouds_source_ready",
            label="Clouds source contract ready",
            value=True,
            severity="ready",
            summary="Clouds can later read Vault readiness, packet count, blocked reasons, and owner focus items.",
        ),
    ]


def get_readiness_score() -> Dict[str, object]:
    signals = get_readiness_signals()
    passed = sum(1 for signal in signals if signal.value)
    total = len(signals)
    score = int(round((passed / total) * 100)) if total else 0
    blockers = [signal.to_dict() for signal in signals if not signal.value]
    return {
        "score": score,
        "passed": passed,
        "total": total,
        "label": "ready" if score == 100 else "needs_attention",
        "blockers": blockers,
        "signals": [signal.to_dict() for signal in signals],
    }
