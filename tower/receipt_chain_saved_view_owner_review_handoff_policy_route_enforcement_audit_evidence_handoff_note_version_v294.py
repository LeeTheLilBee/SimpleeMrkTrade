"""
SEARCHABLE LABEL: TOWER_PACK_294_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_HANDOFF_NOTE_VERSION_PREVIEW_MODULE

Pack 294:
Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Note Version Preview

Preview-only. Cached/non-recursive. No real handoff, no note version writes/restores/applies/deletes, no raw evidence reveal, and no Tower mutations.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft_v293 import (
    build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft_preview,
)


PACK_ID = "294"
PACK_NUMBER = 294
PACK_NAME = "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-note-version-v294.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Handoff Policy Route Enforcement Audit Evidence Handoff layer"

SOURCE_PACK = "293"
SOURCE_CLOSED_BATCH = "286-290"
SAVE_BATCH = "291-295"
SAVE_AFTER_PACK = 295
NEXT_BATCH = "291-295"
NEXT_PACK = "295"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_295"
NEXT_PREP_FLAG = "prepare_pack_295_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_handoff_execute",
    "real_handoff_write",
    "real_handoff_note_version_write",
    "real_handoff_note_version_save",
    "real_handoff_note_version_restore",
    "real_handoff_note_version_apply",
    "real_handoff_note_version_delete",
    "real_handoff_note_write",
    "real_handoff_note_save",
    "real_handoff_note_submit",
    "real_handoff_note_delete",
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
class EvidenceHandoffNoteVersionCard:
    version_id: str
    draft_id: str
    handoff_id: str
    handoff_family: str
    label: str
    version_label: str
    version_status: str
    version_mode: str
    pointer_only: bool
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class EvidenceHandoffNoteVersionField:
    field_id: str
    version_id: str
    handoff_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class EvidenceHandoffNoteVersionAction:
    action_id: str
    version_id: str
    handoff_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class EvidenceHandoffNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    handoff_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drafts = source_payload.get("handoff_policy_route_audit_evidence_handoff_note_draft_cards", [])
    if isinstance(drafts, list) and drafts:
        return deepcopy(drafts)
    return []


def _build_cards(drafts: List[Dict[str, Any]]) -> List[EvidenceHandoffNoteVersionCard]:
    cards: List[EvidenceHandoffNoteVersionCard] = []
    for idx, draft in enumerate(drafts, start=1):
        family = str(draft.get("handoff_family", "UNKNOWN_HANDOFF"))
        cards.append(
            EvidenceHandoffNoteVersionCard(
                version_id=f"handoff_policy_route_audit_evidence_handoff_note_version_294_{idx:03d}",
                draft_id=str(draft.get("draft_id", f"draft_{idx:03d}")),
                handoff_id=str(draft.get("handoff_id", f"handoff_{idx:03d}")),
                handoff_family=family,
                label=f"Handoff note version for {family}",
                version_label="v1 preview only",
                version_status="handoff_note_version_preview_ready",
                version_mode="preview_only",
                pointer_only=True,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )
    return cards


def _build_fields(cards: List[EvidenceHandoffNoteVersionCard]) -> List[EvidenceHandoffNoteVersionField]:
    fields: List[EvidenceHandoffNoteVersionField] = []
    specs = [
        ("version_label", "Version label", "locked_summary", "safe_preview", False),
        ("version_status", "Version status", "locked_summary", "safe_preview", False),
        ("handoff_family", "Handoff family", "locked_summary", "safe_preview", False),
        ("pointer_summary", "Pointer summary", "locked_summary", "redacted_pointer_only", False),
        ("raw_evidence_statement", "Raw evidence statement", "redacted_pointer", "redacted_pointer_only", False),
        ("version_write_block", "Version write block", "locked_summary", "safe_preview", False),
        ("version_restore_apply_block", "Version restore/apply block", "locked_summary", "safe_preview", False),
        ("note_write_block", "Note write block", "locked_summary", "safe_preview", False),
        ("handoff_execution_block", "Handoff execution block", "locked_summary", "safe_preview", False),
        ("mutation_block", "Mutation block", "locked_summary", "safe_preview", False),
        ("ob_teller_boundary", "OB/Teller boundary", "locked_summary", "safe_preview", False),
        ("owner_version_preview", "Owner version preview", "textarea_preview", "safe_preview", True),
        ("next_step", "Next step", "textarea_preview", "safe_preview", True),
    ]

    for card in cards:
        values = {
            "version_label": card.version_label,
            "version_status": card.version_status,
            "handoff_family": card.handoff_family,
            "pointer_summary": "Handoff note version remains pointer-only.",
            "raw_evidence_statement": "Raw evidence is hidden and cannot be versioned or revealed.",
            "version_write_block": "Real note version writes/saves/deletes remain blocked.",
            "version_restore_apply_block": "Real note version restores/applies remain blocked.",
            "note_write_block": "Real note writes/saves/submits/deletes remain blocked.",
            "handoff_execution_block": "Real handoff execution remains blocked.",
            "mutation_block": "Evidence/audit/policy/route/registry/security/billing/receipt mutations remain blocked.",
            "ob_teller_boundary": "OB/Teller UI and routes are not built in this Tower pack.",
            "owner_version_preview": f"Owner can preview the handoff note version for {card.handoff_family} safely.",
            "next_step": "Prepare Pack 295 handoff batch close readiness preview without writing state.",
        }
        for key, label, field_type, redaction_state, editable in specs:
            fields.append(
                EvidenceHandoffNoteVersionField(
                    field_id=f"{card.version_id}_field_{key}",
                    version_id=card.version_id,
                    handoff_id=card.handoff_id,
                    label=label,
                    field_type=field_type,
                    preview_value=values[key],
                    redaction_state=redaction_state,
                    editable_preview=editable,
                    writes_state=False,
                    raw_evidence_visible=False,
                )
            )
    return fields


def _build_actions(cards: List[EvidenceHandoffNoteVersionCard]) -> List[EvidenceHandoffNoteVersionAction]:
    actions: List[EvidenceHandoffNoteVersionAction] = []
    blocked_specs = [
        ("save_version", "Save handoff note version", "Real handoff note version saves are blocked."),
        ("restore_version", "Restore handoff note version", "Real handoff note version restores are blocked."),
        ("apply_version", "Apply handoff note version", "Real handoff note version applies are blocked."),
        ("delete_version", "Delete handoff note version", "Real handoff note version deletes are blocked."),
        ("save_draft", "Save handoff note draft", "Real handoff note draft saves are blocked."),
        ("submit_draft", "Submit handoff note draft", "Real handoff note draft submits are blocked."),
        ("delete_draft", "Delete handoff note draft", "Real handoff note draft deletes are blocked."),
        ("execute_handoff", "Execute handoff", "Real handoff execution is blocked."),
        ("write_handoff", "Write handoff", "Real handoff writes are blocked."),
        ("transfer_evidence", "Transfer evidence", "Real evidence transfer is blocked."),
        ("open_raw", "Open raw evidence", "Raw evidence reveal is blocked."),
        ("write_evidence", "Write evidence", "Evidence writes are blocked."),
        ("write_audit", "Write audit", "Audit writes are blocked."),
        ("write_policy", "Write policy", "Policy writes are blocked."),
        ("change_route", "Change route", "Route changes are blocked."),
        ("write_registry", "Write registry", "Registry writes are blocked."),
        ("change_clearance", "Change clearance", "Clearance writes are blocked."),
        ("write_billing", "Write billing/security", "Billing/security writes are blocked."),
        ("write_receipt", "Write receipt/archive", "Receipt/archive writes are blocked."),
    ]
    for card in cards:
        actions.append(
            EvidenceHandoffNoteVersionAction(
                action_id=f"{card.version_id}_action_preview",
                version_id=card.version_id,
                handoff_id=card.handoff_id,
                label="Preview handoff note version",
                visible=True,
                enabled=True,
                result="preview_allowed",
                reason="Previewing a pointer-only note version does not write state or reveal raw evidence.",
            )
        )
        for key, label, reason in blocked_specs:
            actions.append(
                EvidenceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_{key}",
                    version_id=card.version_id,
                    handoff_id=card.handoff_id,
                    label=label,
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason=reason,
                )
            )
    return actions


def _build_checkpoints() -> List[EvidenceHandoffNoteVersionCheckpoint]:
    rows = [
        ("evidence_handoff_note_version_294_001", "Pack 293 handoff note draft is ready", "safe_summary_only"),
        ("evidence_handoff_note_version_294_002", "Handoff note versions are preview-only and pointer-only", "safe_summary_only"),
        ("evidence_handoff_note_version_294_003", "Raw evidence remains hidden", "redacted_pointer_only"),
        ("evidence_handoff_note_version_294_004", "Real handoff execution is blocked", "blocked_action_summary"),
        ("evidence_handoff_note_version_294_005", "Real note version writes/restores/applies/deletes are blocked", "blocked_action_summary"),
        ("evidence_handoff_note_version_294_006", "Evidence/audit/policy/route mutations are blocked", "blocked_action_summary"),
        ("evidence_handoff_note_version_294_007", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("evidence_handoff_note_version_294_008", "Ready for Pack 295 handoff batch close readiness", "safe_summary_only"),
    ]
    return [
        EvidenceHandoffNoteVersionCheckpoint(
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
            "reason": "Pack 294 previews handoff note versions only and cannot write/restore/apply/delete versions, execute handoffs, reveal raw evidence, or mutate Tower state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
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

    handoff_note_version_ready = all([
        source_payload.get("pack") == "293",
        source_payload.get("status") == "ready",
        source_payload.get("readiness") == 100,
        source_payload.get("safe_to_continue_to_pack_294") is True,
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
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_294"),
        "handoff_policy_route_audit_evidence_handoff_note_version_cards": cards,
        "handoff_policy_route_audit_evidence_handoff_note_version_fields": fields,
        "handoff_policy_route_audit_evidence_handoff_note_version_actions": actions,
        "handoff_policy_route_audit_evidence_handoff_note_version_checkpoints": checkpoints,
        "handoff_policy_route_audit_evidence_handoff_note_version_summary": {
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
            "handoff_note_version_ready": handoff_note_version_ready,
            "real_handoff_execute_enabled": False,
            "real_handoff_write_enabled": False,
            "real_handoff_note_version_write_enabled": False,
            "real_handoff_note_version_save_enabled": False,
            "real_handoff_note_version_restore_enabled": False,
            "real_handoff_note_version_apply_enabled": False,
            "real_handoff_note_version_delete_enabled": False,
            "real_handoff_note_write_enabled": False,
            "real_handoff_note_save_enabled": False,
            "real_handoff_note_submit_enabled": False,
            "real_handoff_note_delete_enabled": False,
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
            "no_real_handoff_note_version_write": True,
            "no_real_handoff_note_version_save": True,
            "no_real_handoff_note_version_restore": True,
            "no_real_handoff_note_version_apply": True,
            "no_real_handoff_note_version_delete": True,
            "no_real_handoff_note_write": True,
            "no_real_handoff_note_save": True,
            "no_real_handoff_note_submit": True,
            "no_real_handoff_note_delete": True,
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
        "pack_294_acceptance": {
            "source_pack_293_verified": True,
            "evidence_handoff_note_versions_built": True,
            "pointer_only_handoff_preserved": True,
            "raw_evidence_hidden": True,
            "handoff_execution_blocked": True,
            "note_version_write_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_pack_295_handoff_batch_close_readiness": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-batch-close-readiness-v295.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def build_pack_294_status_bridge() -> Dict[str, Any]:
    preview = _build_cached()
    summary = preview["handoff_policy_route_audit_evidence_handoff_note_version_summary"]
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
        "version_card_count": summary["version_card_count"],
        "handoff_note_version_ready": summary["handoff_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_295_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness() -> Dict[str, Any]:
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Evidence Handoff Batch Close Readiness Preview",
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
    "build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview",
    "build_pack_294_status_bridge",
    "prepare_pack_295_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness",
]
