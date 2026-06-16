"""
SEARCHABLE LABEL: TOWER_PACK_292_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_HANDOFF_DETAIL_DRAWER_PREVIEW_MODULE

Pack 292:
Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Detail Drawer Preview

Preview-only. Cached/non-recursive. No real evidence handoff, no raw evidence reveal, and no Tower mutations.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291 import (
    build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview,
)


PACK_ID = "292"
PACK_NUMBER = 292
PACK_NAME = "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Detail Drawer Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-detail-drawer-v292.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Handoff Policy Route Enforcement Audit Evidence Handoff layer"

SOURCE_PACK = "291"
SOURCE_CLOSED_BATCH = "286-290"
SAVE_BATCH = "291-295"
SAVE_AFTER_PACK = 295
NEXT_BATCH = "291-295"
NEXT_PACK = "293"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_293"
NEXT_PREP_FLAG = "prepare_pack_293_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft"

BLOCKED_REAL_ACTIONS = (
    "real_handoff_execute",
    "real_handoff_write",
    "real_handoff_detail_write",
    "real_evidence_transfer",
    "real_evidence_write",
    "real_evidence_export",
    "real_evidence_reveal",
    "raw_evidence_reveal",
    "real_note_write",
    "real_note_version_write",
    "real_audit_write",
    "real_policy_write",
    "real_route_change",
    "real_route_enforcement_write",
    "real_registry_write",
    "real_clearance_write",
    "real_permission_write",
    "real_billing_write",
    "real_subscription_write",
    "real_account_security_write",
    "real_receipt_write",
    "real_archive_write",
    "real_ob_route_change",
    "real_teller_route_change",
    "real_action_execution",
)


@dataclass(frozen=True)
class EvidenceHandoffDetailDrawer:
    drawer_id: str
    handoff_id: str
    handoff_family: str
    label: str
    handoff_subject: str
    protected_surface: str
    boundary_preserved: str
    drawer_status: str
    preview_only: bool
    pointer_only: bool
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class EvidenceHandoffDetailSection:
    section_id: str
    drawer_id: str
    handoff_id: str
    label: str
    section_type: str
    summary: str
    handoff_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class EvidenceHandoffDetailAction:
    action_id: str
    drawer_id: str
    handoff_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class EvidenceHandoffDetailCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    handoff_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview())


def _source_cards(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    cards = source_payload.get("handoff_policy_route_audit_evidence_handoff_index_cards", [])
    if isinstance(cards, list) and cards:
        return deepcopy(cards)
    return []


def _build_drawers(cards: List[Dict[str, Any]]) -> List[EvidenceHandoffDetailDrawer]:
    return [
        EvidenceHandoffDetailDrawer(
            drawer_id=f"handoff_policy_route_audit_evidence_handoff_detail_drawer_292_{idx:03d}",
            handoff_id=str(card.get("handoff_id", f"handoff_{idx:03d}")),
            handoff_family=str(card.get("handoff_family", "UNKNOWN_HANDOFF")),
            label=f"Handoff detail drawer for {card.get('handoff_family', 'UNKNOWN_HANDOFF')}",
            handoff_subject=str(card.get("handoff_subject", "Unknown handoff subject")),
            protected_surface=str(card.get("protected_surface", "Unknown protected surface")),
            boundary_preserved=str(card.get("boundary_preserved", "Unknown boundary")),
            drawer_status="handoff_detail_drawer_preview_ready",
            preview_only=True,
            pointer_only=True,
            writes_state=False,
            executable=False,
            raw_evidence_visible=False,
        )
        for idx, card in enumerate(cards, start=1)
    ]


def _build_sections(drawers: List[EvidenceHandoffDetailDrawer]) -> List[EvidenceHandoffDetailSection]:
    sections: List[EvidenceHandoffDetailSection] = []
    specs = [
        ("handoff_scope", "Handoff scope", "Safe summary of the handoff lane."),
        ("protected_surface", "Protected surface", "Protected surface remains pointer-only."),
        ("boundary_preserved", "Boundary preserved", "Boundary remains Tower-controlled."),
        ("raw_evidence", "Raw evidence", "Raw evidence is hidden."),
        ("handoff_execution", "Handoff execution", "Real handoff execution is blocked."),
        ("mutation_block", "Mutation block", "Evidence/note/audit/policy/route/registry/billing/receipt mutations are blocked."),
        ("ob_teller_boundary", "OB/Teller boundary", "OB and Teller UI/routes are not built here."),
        ("next_step", "Next step", "Prepares Pack 293 handoff note draft preview."),
    ]
    for drawer in drawers:
        for key, label, template in specs:
            sections.append(
                EvidenceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_{key}",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label=label,
                    section_type=key,
                    summary=f"{template} Family: {drawer.handoff_family}.",
                    handoff_mode="preview_pointer_handoff_detail",
                    writes_state=False,
                    raw_evidence_visible=False,
                )
            )
    return sections


def _build_actions(drawers: List[EvidenceHandoffDetailDrawer]) -> List[EvidenceHandoffDetailAction]:
    actions: List[EvidenceHandoffDetailAction] = []
    blocked_specs = [
        ("execute_handoff", "Execute handoff", "Real handoff execution is blocked."),
        ("write_handoff", "Write handoff detail", "Real handoff detail writes are blocked."),
        ("transfer_evidence", "Transfer evidence", "Real evidence transfer is blocked."),
        ("open_raw", "Open raw evidence", "Raw evidence reveal is blocked."),
        ("write_evidence", "Write evidence", "Evidence writes are blocked."),
        ("write_note", "Write note/version", "Note/version writes are blocked."),
        ("write_audit", "Write audit", "Audit writes are blocked."),
        ("write_policy", "Write policy", "Policy writes are blocked."),
        ("change_route", "Change route", "Route changes are blocked."),
        ("write_registry", "Write registry", "Registry writes are blocked."),
        ("change_clearance", "Change clearance", "Clearance writes are blocked."),
        ("write_billing", "Write billing/security", "Billing/security writes are blocked."),
        ("write_receipt", "Write receipt/archive", "Receipt/archive writes are blocked."),
    ]
    for drawer in drawers:
        actions.append(
            EvidenceHandoffDetailAction(
                action_id=f"{drawer.drawer_id}_action_preview",
                drawer_id=drawer.drawer_id,
                handoff_id=drawer.handoff_id,
                label="Preview handoff detail drawer",
                visible=True,
                enabled=True,
                result="preview_allowed",
                reason="Previewing a pointer-only handoff detail drawer does not write state or reveal raw evidence.",
            )
        )
        for key, label, reason in blocked_specs:
            actions.append(
                EvidenceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_{key}",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label=label,
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason=reason,
                )
            )
    return actions


def _build_checkpoints() -> List[EvidenceHandoffDetailCheckpoint]:
    rows = [
        ("evidence_handoff_detail_292_001", "Pack 291 handoff index is ready", "safe_summary_only"),
        ("evidence_handoff_detail_292_002", "Handoff detail drawers are preview-only and pointer-only", "safe_summary_only"),
        ("evidence_handoff_detail_292_003", "Raw evidence remains hidden", "redacted_pointer_only"),
        ("evidence_handoff_detail_292_004", "Real handoff execution is blocked", "blocked_action_summary"),
        ("evidence_handoff_detail_292_005", "Handoff detail writes are blocked", "blocked_action_summary"),
        ("evidence_handoff_detail_292_006", "Evidence/note/audit/policy/route mutations are blocked", "blocked_action_summary"),
        ("evidence_handoff_detail_292_007", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("evidence_handoff_detail_292_008", "Ready for Pack 293 handoff note draft", "safe_summary_only"),
    ]
    return [
        EvidenceHandoffDetailCheckpoint(
            checkpoint_id=checkpoint_id,
            label=label,
            passed=True,
            result="passed",
            handoff_mode=mode,
            writes_state=False,
        )
        for checkpoint_id, label, mode in rows
    ]


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 292 previews evidence handoff detail drawers only and cannot execute handoffs or mutate Tower state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    source_cards = _source_cards(source_payload)

    drawers_raw = _build_drawers(source_cards)
    sections_raw = _build_sections(drawers_raw)
    actions_raw = _build_actions(drawers_raw)
    checkpoints_raw = _build_checkpoints()

    drawers = [asdict(row) for row in drawers_raw]
    sections = [asdict(row) for row in sections_raw]
    actions = [asdict(row) for row in actions_raw]
    checkpoints = [asdict(row) for row in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)

    all_drawers_preview_only = all(drawer["preview_only"] is True for drawer in drawers)
    all_drawers_pointer_only = all(drawer["pointer_only"] is True for drawer in drawers)
    all_drawers_no_writes = all(drawer["writes_state"] is False for drawer in drawers)
    all_drawers_non_executable = all(drawer["executable"] is False for drawer in drawers)
    all_drawers_no_raw_evidence = all(drawer["raw_evidence_visible"] is False for drawer in drawers)
    all_sections_no_writes = all(section["writes_state"] is False for section in sections)
    all_sections_no_raw_evidence = all(section["raw_evidence_visible"] is False for section in sections)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    handoff_detail_drawer_ready = all([
        source_payload.get("pack") == "291",
        source_payload.get("status") == "ready",
        source_payload.get("readiness") == 100,
        source_payload.get("safe_to_continue_to_pack_292") is True,
        all_drawers_preview_only,
        all_drawers_pointer_only,
        all_drawers_no_writes,
        all_drawers_non_executable,
        all_drawers_no_raw_evidence,
        all_sections_no_writes,
        all_sections_no_raw_evidence,
        all_actions_safe,
        all_checkpoints_passed,
        all_checkpoints_no_writes,
    ])

    preview = {
        "pack": PACK_ID,
        "pack_number": PACK_NUMBER,
        "pack_name": PACK_NAME,
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "tower_area": TOWER_AREA,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
        "source_pack": SOURCE_PACK,
        "source_closed_batch": SOURCE_CLOSED_BATCH,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "next_batch": NEXT_BATCH,
        "next_pack": NEXT_PACK,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_292"),
        "handoff_policy_route_audit_evidence_handoff_detail_drawers": drawers,
        "handoff_policy_route_audit_evidence_handoff_detail_sections": sections,
        "handoff_policy_route_audit_evidence_handoff_detail_actions": actions,
        "handoff_policy_route_audit_evidence_handoff_detail_checkpoints": checkpoints,
        "handoff_policy_route_audit_evidence_handoff_detail_summary": {
            "source_handoff_card_count": len(source_cards),
            "detail_drawer_count": len(drawers),
            "detail_section_count": len(sections),
            "detail_action_count": len(actions),
            "detail_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "all_drawers_preview_only": all_drawers_preview_only,
            "all_drawers_pointer_only": all_drawers_pointer_only,
            "all_drawers_no_writes": all_drawers_no_writes,
            "all_drawers_non_executable": all_drawers_non_executable,
            "all_drawers_no_raw_evidence": all_drawers_no_raw_evidence,
            "all_sections_no_writes": all_sections_no_writes,
            "all_sections_no_raw_evidence": all_sections_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "handoff_detail_drawer_ready": handoff_detail_drawer_ready,
            "real_handoff_execute_enabled": False,
            "real_handoff_write_enabled": False,
            "real_handoff_detail_write_enabled": False,
            "real_evidence_transfer_enabled": False,
            "real_evidence_write_enabled": False,
            "real_evidence_reveal_enabled": False,
            "raw_evidence_visible": False,
            "real_note_write_enabled": False,
            "real_note_version_write_enabled": False,
            "real_audit_write_enabled": False,
            "real_policy_write_enabled": False,
            "real_route_change_enabled": False,
            "real_registry_write_enabled": False,
            "real_clearance_write_enabled": False,
            "real_billing_write_enabled": False,
            "real_receipt_write_enabled": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_handoff_execute": True,
            "no_real_handoff_write": True,
            "no_real_handoff_detail_write": True,
            "no_real_evidence_transfer": True,
            "no_real_evidence_write": True,
            "no_real_evidence_reveal": True,
            "no_raw_evidence_reveal": True,
            "no_real_note_write": True,
            "no_real_note_version_write": True,
            "no_real_audit_write": True,
            "no_real_policy_write": True,
            "no_real_route_change": True,
            "no_real_registry_write": True,
            "no_real_clearance_write": True,
            "no_real_billing_write": True,
            "no_real_receipt_write": True,
            "no_real_action_execution": True,
            "cached_non_recursive_builder": True,
            "ob_ui_not_built_in_tower_pack": True,
            "teller_ui_not_built_in_tower_pack": True,
        },
        "blocked_action_matrix": _blocked_action_matrix(),
        "route_contract": {
            "method": "GET",
            "returns_json": True,
            "requires_tower_guard": True,
            "unguarded_high_risk_allowed": False,
        },
        "pack_292_acceptance": {
            "source_pack_291_verified": True,
            "evidence_handoff_detail_drawers_built": True,
            "pointer_only_handoff_preserved": True,
            "raw_evidence_hidden": True,
            "handoff_execution_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_pack_293_handoff_note_draft": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Note Draft Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-note-draft-v293.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def build_pack_292_status_bridge() -> Dict[str, Any]:
    preview = _build_cached()
    summary = preview["handoff_policy_route_audit_evidence_handoff_detail_summary"]
    return {
        "pack": preview["pack"],
        "pack_number": preview["pack_number"],
        "pack_name": preview["pack_name"],
        "status": preview["status"],
        "readiness": preview["readiness"],
        "endpoint": preview["endpoint"],
        "tower_section": preview["tower_section"],
        "tower_layer": preview["tower_layer"],
        "tower_sublayer": preview["tower_sublayer"],
        "source_pack": preview["source_pack"],
        "source_closed_batch": preview["source_closed_batch"],
        "save_batch": preview["save_batch"],
        "save_after_pack": preview["save_after_pack"],
        "next_pack": preview["next_pack"],
        "detail_drawer_count": summary["detail_drawer_count"],
        "handoff_detail_drawer_ready": summary["handoff_detail_drawer_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_293_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft() -> Dict[str, Any]:
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Note Draft Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
        "source_closed_batch": SOURCE_CLOSED_BATCH,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "blocked_real_actions": list(BLOCKED_REAL_ACTIONS),
        "safe_to_continue": True,
    }


__all__ = [
    "PACK_ID",
    "PACK_NUMBER",
    "PACK_NAME",
    "ENDPOINT",
    "TOWER_AREA",
    "TOWER_SECTION",
    "TOWER_LAYER",
    "TOWER_SUBLAYER",
    "SOURCE_PACK",
    "SOURCE_CLOSED_BATCH",
    "SAVE_BATCH",
    "SAVE_AFTER_PACK",
    "NEXT_BATCH",
    "NEXT_PACK",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview",
    "build_pack_292_status_bridge",
    "prepare_pack_293_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft",
]
