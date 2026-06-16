"""
SEARCHABLE LABEL: TOWER_PACK_289_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_NOTE_VERSION_PREVIEW_MODULE

Pack 289: Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Note Version Preview

Simulated/preview-only. Cached/non-recursive. No note version writes/restores/applies/deletes,
no note writes, no evidence writes, and no raw evidence reveal.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_draft_v288 import (
    build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_draft_preview,
)


PACK_ID = "289"
PACK_NUMBER = 289
PACK_NAME = "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-note-version-v289.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Handoff Policy Route Enforcement Audit Evidence layer"

SOURCE_PACK = "288"
SOURCE_CLOSED_BATCH = "281-285"
SAVE_BATCH = "286-290"
SAVE_AFTER_PACK = 290
NEXT_BATCH = "286-290"
NEXT_PACK = "290"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_290"
NEXT_PREP_FLAG = "prepare_pack_290_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_note_version_write",
    "real_note_version_save",
    "real_note_version_restore",
    "real_note_version_apply",
    "real_note_version_delete",
    "real_note_write",
    "real_note_save",
    "real_note_submit",
    "real_note_delete",
    "real_evidence_write",
    "real_evidence_export",
    "real_evidence_reveal",
    "raw_evidence_reveal",
    "real_evidence_restore",
    "real_evidence_apply",
    "real_evidence_delete",
    "real_audit_write",
    "real_audit_result_apply",
    "real_audit_override",
    "real_policy_write",
    "real_policy_apply",
    "real_policy_override",
    "real_route_enforcement_write",
    "real_route_enforcement_apply",
    "real_route_change",
    "real_route_activation",
    "real_handoff_execute",
    "real_handoff_write",
    "real_registry_write",
    "real_clearance_write",
    "real_permission_write",
    "real_billing_write",
    "real_subscription_write",
    "real_account_security_write",
    "real_receipt_write",
    "real_archive_write",
    "real_action_execution",
)


@dataclass(frozen=True)
class AuditEvidenceNoteVersionCard:
    version_id: str
    draft_id: str
    evidence_id: str
    evidence_family: str
    source_audit_family: str
    label: str
    version_label: str
    version_status: str
    protected_surface: str
    boundary_proved: str
    severity: str
    version_mode: str
    pointer_only: bool
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class AuditEvidenceNoteVersionField:
    field_id: str
    version_id: str
    evidence_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class AuditEvidenceNoteVersionAction:
    action_id: str
    version_id: str
    evidence_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class AuditEvidenceNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drafts = source_payload.get("handoff_policy_route_audit_evidence_note_draft_cards", [])
    if isinstance(drafts, list) and drafts:
        return deepcopy(drafts)
    return []


def _build_cards(drafts: List[Dict[str, Any]]) -> List[AuditEvidenceNoteVersionCard]:
    cards: List[AuditEvidenceNoteVersionCard] = []
    for idx, draft in enumerate(drafts, start=1):
        evidence_family = str(draft.get("evidence_family", "UNKNOWN_EVIDENCE"))
        cards.append(
            AuditEvidenceNoteVersionCard(
                version_id=f"handoff_policy_route_audit_evidence_note_version_289_{idx:03d}",
                draft_id=str(draft.get("draft_id", f"draft_{idx:03d}")),
                evidence_id=str(draft.get("evidence_id", f"evidence_{idx:03d}")),
                evidence_family=evidence_family,
                source_audit_family=str(draft.get("source_audit_family", "UNKNOWN_AUDIT")),
                label=f"Evidence note version for {evidence_family}",
                version_label="v1 preview only",
                version_status="evidence_note_version_preview_ready",
                protected_surface=str(draft.get("protected_surface", "Unknown surface")),
                boundary_proved=str(draft.get("boundary_proved", "Unknown boundary")),
                severity=str(draft.get("severity", "high")),
                version_mode="preview_only",
                pointer_only=True,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )
    return cards


def _build_fields(cards: List[AuditEvidenceNoteVersionCard]) -> List[AuditEvidenceNoteVersionField]:
    fields: List[AuditEvidenceNoteVersionField] = []
    for card in cards:
        specs = [
            ("version_label", "Version label", card.version_label, "locked_summary", "safe_preview", False),
            ("version_status", "Version status", card.version_status, "locked_summary", "safe_preview", False),
            ("evidence_family", "Evidence family", card.evidence_family, "locked_summary", "safe_preview", False),
            ("source_audit_family", "Source audit family", card.source_audit_family, "locked_summary", "safe_preview", False),
            ("protected_surface", "Protected surface", card.protected_surface, "locked_summary", "safe_preview", False),
            ("boundary_proved", "Boundary proved", card.boundary_proved, "textarea_preview", "safe_preview", True),
            ("severity", "Severity", f"{card.severity}; preview label only.", "textarea_preview", "safe_preview", True),
            ("pointer_summary", "Pointer summary", "Version preserves pointer-only evidence; raw evidence is hidden.", "locked_summary", "redacted_pointer_only", False),
            ("raw_evidence_statement", "Raw evidence statement", "Raw evidence is not visible, exported, restored, applied, written, or versioned.", "redacted_pointer", "redacted_pointer_only", False),
            ("version_mutation_block", "Version mutation block", "Note version writes/restores/applies/deletes are blocked.", "locked_summary", "safe_preview", False),
            ("note_mutation_block", "Note mutation block", "Note writes/saves/submits/deletes are blocked.", "locked_summary", "safe_preview", False),
            ("evidence_mutation_block", "Evidence mutation block", "Evidence/audit/policy/route/handoff/registry/security/billing/receipt mutations are blocked.", "locked_summary", "safe_preview", False),
            ("owner_version_preview", "Owner version preview", f"Owner can inspect {card.evidence_family} note version safely as pointer-only preview.", "textarea_preview", "safe_preview", True),
            ("next_step", "Next step", "Prepare Pack 290 evidence batch close readiness preview without writing state.", "textarea_preview", "safe_preview", True),
        ]
        for key, label, value, field_type, redaction, editable in specs:
            fields.append(
                AuditEvidenceNoteVersionField(
                    field_id=f"{card.version_id}_field_{key}",
                    version_id=card.version_id,
                    evidence_id=card.evidence_id,
                    label=label,
                    field_type=field_type,
                    preview_value=value,
                    redaction_state=redaction,
                    editable_preview=editable,
                    writes_state=False,
                    raw_evidence_visible=False,
                )
            )
    return fields


def _build_actions(cards: List[AuditEvidenceNoteVersionCard]) -> List[AuditEvidenceNoteVersionAction]:
    actions: List[AuditEvidenceNoteVersionAction] = []
    blocked_specs = [
        ("save_version", "Save note version", "Real note version saves are blocked."),
        ("restore_version", "Restore note version", "Real note version restores are blocked."),
        ("apply_version", "Apply note version", "Real note version applies are blocked."),
        ("delete_version", "Delete note version", "Real note version deletes are blocked."),
        ("save_note", "Save evidence note", "Real note saves are blocked."),
        ("submit_note", "Submit evidence note", "Real note submits are blocked."),
        ("delete_note", "Delete evidence note", "Real note deletes are blocked."),
        ("open_raw", "Open raw evidence", "Raw evidence reveal is blocked."),
        ("write_evidence", "Write evidence", "Real evidence writes are blocked."),
        ("export_evidence", "Export evidence", "Real evidence exports are blocked."),
        ("apply_evidence", "Apply evidence", "Real evidence applies are blocked."),
        ("restore_evidence", "Restore evidence", "Real evidence restores are blocked."),
        ("write_audit", "Write audit result", "Real audit writes are blocked."),
        ("write_policy", "Write policy", "Real policy writes are blocked."),
        ("change_route", "Change route", "Real route changes are blocked."),
        ("execute_handoff", "Execute handoff", "Real handoff execution is blocked."),
        ("write_registry", "Write registry", "Registry writes are blocked."),
        ("change_clearance", "Change clearance", "Clearance and permission writes are blocked."),
        ("write_billing", "Write billing/security", "Billing and account security writes are blocked."),
        ("write_receipt", "Write receipt/archive", "Receipt/archive writes are blocked."),
    ]

    for card in cards:
        actions.append(
            AuditEvidenceNoteVersionAction(
                action_id=f"{card.version_id}_action_preview",
                version_id=card.version_id,
                evidence_id=card.evidence_id,
                label="Preview evidence note version",
                visible=True,
                enabled=True,
                result="preview_allowed",
                reason="Previewing the evidence note version does not write state or reveal raw evidence.",
            )
        )
        for key, label, reason in blocked_specs:
            actions.append(
                AuditEvidenceNoteVersionAction(
                    action_id=f"{card.version_id}_action_{key}",
                    version_id=card.version_id,
                    evidence_id=card.evidence_id,
                    label=label,
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason=reason,
                )
            )
    return actions


def _build_checkpoints() -> List[AuditEvidenceNoteVersionCheckpoint]:
    rows = [
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_001", "Pack 288 source evidence note draft is ready", "safe_summary_only"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_002", "Evidence note version cards are preview-only and pointer-only", "safe_summary_only"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_003", "Version fields do not write state or reveal raw evidence", "redacted_pointer_only"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_004", "Note version restore/apply/delete paths remain blocked", "blocked_action_summary"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_005", "Note save/submit/delete paths remain blocked", "blocked_action_summary"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_006", "Evidence/audit/policy/route/handoff/registry/security/billing/receipt mutations remain blocked", "blocked_action_summary"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_007", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("handoff_policy_route_audit_evidence_note_version_checkpoint_289_008", "Ready for Pack 290 audit evidence batch close readiness preview", "safe_summary_only"),
    ]
    return [
        AuditEvidenceNoteVersionCheckpoint(
            checkpoint_id=checkpoint_id,
            label=label,
            passed=True,
            result="passed",
            evidence_mode=evidence_mode,
            writes_state=False,
        )
        for checkpoint_id, label, evidence_mode in rows
    ]


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 289 previews pointer-only evidence note versions and cannot write/restore/apply/delete versions, write notes, reveal raw evidence, or mutate Tower state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    source_drafts = _source_drafts(source_payload)

    cards_raw = _build_cards(source_drafts)
    fields_raw = _build_fields(cards_raw)
    actions_raw = _build_actions(cards_raw)
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(row) for row in cards_raw]
    fields = [asdict(row) for row in fields_raw]
    actions = [asdict(row) for row in actions_raw]
    checkpoints = [asdict(row) for row in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    redacted_field_count = sum(1 for field in fields if field["redaction_state"] == "redacted_pointer_only")
    editable_field_count = sum(1 for field in fields if field["editable_preview"] is True)

    all_cards_preview_only = all(card["version_mode"] == "preview_only" for card in cards)
    all_cards_pointer_only = all(card["pointer_only"] is True for card in cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in cards)
    all_cards_non_executable = all(card["executable"] is False for card in cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in cards)
    all_fields_no_writes = all(field["writes_state"] is False for field in fields)
    all_fields_no_raw_evidence = all(field["raw_evidence_visible"] is False for field in fields)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    evidence_note_version_ready = all([
        all_cards_preview_only,
        all_cards_pointer_only,
        all_cards_no_writes,
        all_cards_non_executable,
        all_cards_no_raw_evidence,
        all_fields_no_writes,
        all_fields_no_raw_evidence,
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
        "receipt_chain_layer": "saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview",
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_289"),
        "handoff_policy_route_audit_evidence_note_version_cards": cards,
        "handoff_policy_route_audit_evidence_note_version_fields": fields,
        "handoff_policy_route_audit_evidence_note_version_actions": actions,
        "handoff_policy_route_audit_evidence_note_version_checkpoints": checkpoints,
        "handoff_policy_route_audit_evidence_note_version_summary": {
            "source_note_draft_count": len(source_drafts),
            "version_card_count": len(cards),
            "version_field_count": len(fields),
            "version_action_count": len(actions),
            "version_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "redacted_field_count": redacted_field_count,
            "editable_field_count": editable_field_count,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_pointer_only": all_cards_pointer_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_non_executable": all_cards_non_executable,
            "all_cards_no_raw_evidence": all_cards_no_raw_evidence,
            "all_fields_no_writes": all_fields_no_writes,
            "all_fields_no_raw_evidence": all_fields_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "evidence_note_version_ready": evidence_note_version_ready,
            "real_note_version_write_enabled": False,
            "real_note_version_save_enabled": False,
            "real_note_version_restore_enabled": False,
            "real_note_version_apply_enabled": False,
            "real_note_version_delete_enabled": False,
            "real_note_write_enabled": False,
            "real_note_save_enabled": False,
            "real_note_submit_enabled": False,
            "real_note_delete_enabled": False,
            "real_evidence_write_enabled": False,
            "real_evidence_export_enabled": False,
            "real_evidence_reveal_enabled": False,
            "raw_evidence_visible": False,
            "real_audit_write_enabled": False,
            "real_policy_write_enabled": False,
            "real_route_change_enabled": False,
            "real_handoff_execute_enabled": False,
            "real_registry_write_enabled": False,
            "real_clearance_write_enabled": False,
            "real_billing_write_enabled": False,
            "real_receipt_write_enabled": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_note_version_write": True,
            "no_real_note_version_save": True,
            "no_real_note_version_restore": True,
            "no_real_note_version_apply": True,
            "no_real_note_version_delete": True,
            "no_real_note_write": True,
            "no_real_note_save": True,
            "no_real_note_submit": True,
            "no_real_note_delete": True,
            "no_real_evidence_write": True,
            "no_real_evidence_export": True,
            "no_real_evidence_reveal": True,
            "no_raw_evidence_reveal": True,
            "no_real_audit_write": True,
            "no_real_policy_write": True,
            "no_real_route_change": True,
            "no_real_handoff_execute": True,
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
        "pack_289_acceptance": {
            "source_pack_288_verified": True,
            "evidence_note_versions_built": True,
            "pointer_only_evidence_preserved": True,
            "raw_evidence_hidden": True,
            "note_version_mutation_paths_blocked": True,
            "note_mutation_paths_blocked": True,
            "evidence_mutation_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_policy_route_enforcement_audit_evidence_batch_close_readiness": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-batch-close-readiness-v290.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview() -> Dict[str, Any]:
    return deepcopy(_build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview_cached())


def build_pack_289_status_bridge() -> Dict[str, Any]:
    preview = _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview_cached()
    summary = preview["handoff_policy_route_audit_evidence_note_version_summary"]
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
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "version_card_count": summary["version_card_count"],
        "version_field_count": summary["version_field_count"],
        "version_action_count": summary["version_action_count"],
        "evidence_note_version_ready": summary["evidence_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_290_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_batch_close_readiness() -> Dict[str, Any]:
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Batch Close Readiness Preview",
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
    "build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview",
    "build_pack_289_status_bridge",
    "prepare_pack_290_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_batch_close_readiness",
]
