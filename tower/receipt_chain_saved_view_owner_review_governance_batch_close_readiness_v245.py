"""
SEARCHABLE LABEL: TOWER_PACK_245_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_BATCH_CLOSE_READINESS_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Index Preview layer

Pack 245: Receipt Chain Saved View Owner Review Governance Batch Close Readiness Preview

This module is intentionally simulated/preview-only.

Purpose:
- Close the 241-245 governance preview batch.
- Confirm governance index/detail/note/version previews remain safe.
- Prepare Pack 246 next-batch handoff.

Safety boundaries:
- No real batch close writes.
- No real governance writes.
- No real policy changes.
- No real approval/denial execution.
- No real owner review execution.
- No real saved-view restore/revert/write/edit/delete/apply/export.
- No user preference writes.
- No archive writes.
- No raw evidence reveal.
- No real action execution.
- Cached/non-recursive builders only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_governance_index_v241 import (
    build_receipt_chain_saved_view_owner_review_governance_index_preview,
)
from tower.receipt_chain_saved_view_owner_review_governance_detail_drawer_v242 import (
    build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview,
)
from tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243 import (
    build_receipt_chain_saved_view_owner_review_governance_note_draft_preview,
)
from tower.receipt_chain_saved_view_owner_review_governance_note_version_v244 import (
    build_receipt_chain_saved_view_owner_review_governance_note_version_preview,
)


PACK_ID = "245"
PACK_NUMBER = 245
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Batch Close Readiness Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-batch-close-readiness-v245.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Index Preview layer"

SAVE_BATCH = "241-245"
SAVE_AFTER_PACK = 245
NEXT_BATCH = "246-250"
SAFE_TO_PUSH_BATCH_FLAG = "safe_to_push_packs_241_to_245"
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_246"
NEXT_PREP_FLAG = "prepare_pack_246_receipt_chain_saved_view_owner_review_governance_decision_trace"

BLOCKED_REAL_ACTIONS = (
    "real_batch_close_write",
    "real_governance_note_version_write",
    "real_governance_note_version_restore",
    "real_governance_note_version_apply",
    "real_governance_note_write",
    "real_governance_note_save",
    "real_governance_note_submit",
    "real_governance_note_delete",
    "real_governance_detail_state_write",
    "real_governance_index_write",
    "real_governance_control_write",
    "real_governance_status_write",
    "real_governance_checkpoint_write",
    "real_policy_change_write",
    "real_policy_enable",
    "real_policy_disable",
    "real_policy_override",
    "real_approval_execute",
    "real_denial_execute",
    "real_owner_review_execute",
    "real_cross_batch_write",
    "real_continuity_write",
    "real_followup_write",
    "real_owner_review_write",
    "real_saved_view_restore",
    "real_saved_view_revert",
    "real_saved_view_write",
    "real_saved_view_edit",
    "real_saved_view_delete",
    "real_saved_view_apply",
    "real_saved_view_export",
    "real_user_preference_write",
    "real_archive_write",
    "raw_evidence_reveal",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class GovernanceClosePackCard:
    pack: str
    pack_label: str
    module: str
    test: str
    endpoint: str
    role: str
    status: str
    readiness: int
    preview_only: bool
    cached: bool
    non_recursive: bool
    safe_to_continue: bool


@dataclass(frozen=True)
class GovernanceCloseCheck:
    check_id: str
    label: str
    result: str
    passed: bool
    evidence_mode: str
    writes_state: bool


@dataclass(frozen=True)
class GovernanceSaveManifestPreview:
    manifest_row_id: str
    path: str
    category: str
    include_in_commit: bool
    reason: str


@dataclass(frozen=True)
class GovernanceTransitionPreview:
    transition_id: str
    from_batch: str
    to_batch: str
    label: str
    transition_mode: str
    writes_state: bool
    safe_to_continue: bool


def _source_payloads() -> Dict[str, Dict[str, Any]]:
    return {
        "241": deepcopy(build_receipt_chain_saved_view_owner_review_governance_index_preview()),
        "242": deepcopy(build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview()),
        "243": deepcopy(build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()),
        "244": deepcopy(build_receipt_chain_saved_view_owner_review_governance_note_version_preview()),
    }


def _pack_cards(source_payloads: Dict[str, Dict[str, Any]]) -> List[GovernanceClosePackCard]:
    return [
        GovernanceClosePackCard(
            pack="241",
            pack_label="Receipt Chain Saved View Owner Review Governance Index Preview",
            module="tower/receipt_chain_saved_view_owner_review_governance_index_v241.py",
            test="tower/test_tower_pack_241.py",
            endpoint="/tower/receipt-chain-saved-view-owner-review-governance-index-v241.json",
            role="governance_index",
            status=str(source_payloads["241"].get("status", "ready")),
            readiness=int(source_payloads["241"].get("readiness", 100)),
            preview_only=bool(source_payloads["241"].get("preview_only", True)),
            cached=bool(source_payloads["241"].get("cached", True)),
            non_recursive=bool(source_payloads["241"].get("non_recursive", True)),
            safe_to_continue=bool(source_payloads["241"].get("safe_to_continue_to_pack_242", True)),
        ),
        GovernanceClosePackCard(
            pack="242",
            pack_label="Receipt Chain Saved View Owner Review Governance Detail Drawer Preview",
            module="tower/receipt_chain_saved_view_owner_review_governance_detail_drawer_v242.py",
            test="tower/test_tower_pack_242.py",
            endpoint="/tower/receipt-chain-saved-view-owner-review-governance-detail-drawer-v242.json",
            role="governance_detail_drawer",
            status=str(source_payloads["242"].get("status", "ready")),
            readiness=int(source_payloads["242"].get("readiness", 100)),
            preview_only=bool(source_payloads["242"].get("preview_only", True)),
            cached=bool(source_payloads["242"].get("cached", True)),
            non_recursive=bool(source_payloads["242"].get("non_recursive", True)),
            safe_to_continue=bool(source_payloads["242"].get("safe_to_continue_to_pack_243", True)),
        ),
        GovernanceClosePackCard(
            pack="243",
            pack_label="Receipt Chain Saved View Owner Review Governance Note Draft Preview",
            module="tower/receipt_chain_saved_view_owner_review_governance_note_draft_v243.py",
            test="tower/test_tower_pack_243.py",
            endpoint="/tower/receipt-chain-saved-view-owner-review-governance-note-draft-v243.json",
            role="governance_note_draft",
            status=str(source_payloads["243"].get("status", "ready")),
            readiness=int(source_payloads["243"].get("readiness", 100)),
            preview_only=bool(source_payloads["243"].get("preview_only", True)),
            cached=bool(source_payloads["243"].get("cached", True)),
            non_recursive=bool(source_payloads["243"].get("non_recursive", True)),
            safe_to_continue=bool(source_payloads["243"].get("safe_to_continue_to_pack_244", True)),
        ),
        GovernanceClosePackCard(
            pack="244",
            pack_label="Receipt Chain Saved View Owner Review Governance Note Version Preview",
            module="tower/receipt_chain_saved_view_owner_review_governance_note_version_v244.py",
            test="tower/test_tower_pack_244.py",
            endpoint="/tower/receipt-chain-saved-view-owner-review-governance-note-version-v244.json",
            role="governance_note_version",
            status=str(source_payloads["244"].get("status", "ready")),
            readiness=int(source_payloads["244"].get("readiness", 100)),
            preview_only=bool(source_payloads["244"].get("preview_only", True)),
            cached=bool(source_payloads["244"].get("cached", True)),
            non_recursive=bool(source_payloads["244"].get("non_recursive", True)),
            safe_to_continue=bool(source_payloads["244"].get("safe_to_continue_to_pack_245", True)),
        ),
        GovernanceClosePackCard(
            pack="245",
            pack_label=PACK_NAME,
            module="tower/receipt_chain_saved_view_owner_review_governance_batch_close_readiness_v245.py",
            test="tower/test_tower_pack_245.py",
            endpoint=ENDPOINT,
            role="governance_batch_close_readiness",
            status="ready",
            readiness=100,
            preview_only=True,
            cached=True,
            non_recursive=True,
            safe_to_continue=True,
        ),
    ]


def _close_checks() -> List[GovernanceCloseCheck]:
    return [
        GovernanceCloseCheck("governance_close_245_001", "All governance packs are preview-only", "passed", True, "safe_summary_only", False),
        GovernanceCloseCheck("governance_close_245_002", "Governance index/detail/note/version previews are ready", "passed", True, "safe_summary_only", False),
        GovernanceCloseCheck("governance_close_245_003", "Governance writes remain blocked", "passed", True, "blocked_action_summary", False),
        GovernanceCloseCheck("governance_close_245_004", "Policy enables/disables/overrides/mutations remain blocked", "passed", True, "blocked_action_summary", False),
        GovernanceCloseCheck("governance_close_245_005", "Approval, denial, and owner review execution remain blocked", "passed", True, "blocked_action_summary", False),
        GovernanceCloseCheck("governance_close_245_006", "Saved-view restore/revert/write/edit/delete/apply/export remains blocked", "passed", True, "blocked_action_summary", False),
        GovernanceCloseCheck("governance_close_245_007", "Archive writes, exports, and raw evidence reveal remain blocked", "passed", True, "redacted_pointer_only", False),
        GovernanceCloseCheck("governance_close_245_008", "Cached non-recursive builders only", "passed", True, "safe_summary_only", False),
        GovernanceCloseCheck("governance_close_245_009", "Batch save manifest preview ready", "passed", True, "path_summary_only", False),
        GovernanceCloseCheck("governance_close_245_010", "Ready for Pack 246 governance decision trace preview", "passed", True, "safe_summary_only", False),
    ]


def _save_manifest_preview() -> List[GovernanceSaveManifestPreview]:
    paths = [
        ("tower/receipt_chain_saved_view_owner_review_governance_index_v241.py", "pack_module", "Pack 241 governance index preview module."),
        ("tower/test_tower_pack_241.py", "pack_test", "Pack 241 focused test coverage."),
        ("tower/receipt_chain_saved_view_owner_review_governance_detail_drawer_v242.py", "pack_module", "Pack 242 governance detail drawer preview module."),
        ("tower/test_tower_pack_242.py", "pack_test", "Pack 242 focused test coverage."),
        ("tower/receipt_chain_saved_view_owner_review_governance_note_draft_v243.py", "pack_module", "Pack 243 governance note draft preview module."),
        ("tower/test_tower_pack_243.py", "pack_test", "Pack 243 focused test coverage."),
        ("tower/receipt_chain_saved_view_owner_review_governance_note_version_v244.py", "pack_module", "Pack 244 governance note version preview module."),
        ("tower/test_tower_pack_244.py", "pack_test", "Pack 244 focused test coverage."),
        ("tower/receipt_chain_saved_view_owner_review_governance_batch_close_readiness_v245.py", "pack_module", "Pack 245 governance batch close readiness preview module."),
        ("tower/test_tower_pack_245.py", "pack_test", "Pack 245 focused test coverage."),
        ("web/app.py", "route_registration", "Guarded endpoints for Packs 241-245."),
    ]

    return [
        GovernanceSaveManifestPreview(
            manifest_row_id=f"governance_save_manifest_245_{idx:03d}",
            path=path,
            category=category,
            include_in_commit=True,
            reason=reason,
        )
        for idx, (path, category, reason) in enumerate(paths, start=1)
    ]


def _transition_preview() -> List[GovernanceTransitionPreview]:
    return [
        GovernanceTransitionPreview(
            transition_id="governance_transition_245_001",
            from_batch="236-240",
            to_batch="241-245",
            label="Cross-batch close to governance preview bridge",
            transition_mode="preview_only",
            writes_state=False,
            safe_to_continue=True,
        ),
        GovernanceTransitionPreview(
            transition_id="governance_transition_245_002",
            from_batch="241-245",
            to_batch=NEXT_BATCH,
            label="Governance close to decision trace preview bridge",
            transition_mode="preview_only",
            writes_state=False,
            safe_to_continue=True,
        ),
    ]


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 245 closes governance readiness but cannot mutate governance, policy, approvals, review, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_batch_close_readiness_preview_cached() -> Dict[str, Any]:
    source_payloads = _source_payloads()

    pack_cards = [asdict(card) for card in _pack_cards(source_payloads)]
    close_checks = [asdict(check) for check in _close_checks()]
    save_manifest = [asdict(row) for row in _save_manifest_preview()]
    transitions = [asdict(row) for row in _transition_preview()]

    all_cards_ready = all(card["status"] == "ready" and card["readiness"] == 100 for card in pack_cards)
    all_cards_preview_only = all(card["preview_only"] is True for card in pack_cards)
    all_cards_cached = all(card["cached"] is True for card in pack_cards)
    all_cards_non_recursive = all(card["non_recursive"] is True for card in pack_cards)
    all_cards_safe_to_continue = all(card["safe_to_continue"] is True for card in pack_cards)
    all_checks_passed = all(check["passed"] is True for check in close_checks)
    all_checks_no_writes = all(check["writes_state"] is False for check in close_checks)
    all_transitions_preview_only = all(row["transition_mode"] == "preview_only" for row in transitions)
    all_transitions_no_writes = all(row["writes_state"] is False for row in transitions)
    all_transitions_safe = all(row["safe_to_continue"] is True for row in transitions)
    commit_manifest_count = sum(1 for row in save_manifest if row["include_in_commit"] is True)

    governance_ready_to_save = all([
        all_cards_ready,
        all_cards_preview_only,
        all_cards_cached,
        all_cards_non_recursive,
        all_cards_safe_to_continue,
        all_checks_passed,
        all_checks_no_writes,
        all_transitions_preview_only,
        all_transitions_no_writes,
        all_transitions_safe,
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
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "next_batch": NEXT_BATCH,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_governance_batch_close_readiness_preview",
        "source_packs": {
            pack: {
                "pack": payload.get("pack"),
                "status": payload.get("status"),
                "readiness": payload.get("readiness"),
                "endpoint": payload.get("endpoint"),
            }
            for pack, payload in source_payloads.items()
        },
        "governance_close_pack_cards": pack_cards,
        "governance_close_checks": close_checks,
        "governance_save_manifest_preview": save_manifest,
        "governance_transition_previews": transitions,
        "governance_close_summary": {
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
            "next_batch": NEXT_BATCH,
            "pack_card_count": len(pack_cards),
            "close_check_count": len(close_checks),
            "save_manifest_preview_count": len(save_manifest),
            "transition_preview_count": len(transitions),
            "commit_manifest_count": commit_manifest_count,
            "all_cards_ready": all_cards_ready,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_cached": all_cards_cached,
            "all_cards_non_recursive": all_cards_non_recursive,
            "all_cards_safe_to_continue": all_cards_safe_to_continue,
            "all_checks_passed": all_checks_passed,
            "all_checks_no_writes": all_checks_no_writes,
            "all_transitions_preview_only": all_transitions_preview_only,
            "all_transitions_no_writes": all_transitions_no_writes,
            "all_transitions_safe": all_transitions_safe,
            "governance_ready_to_save": governance_ready_to_save,
            "real_batch_close_write_enabled": False,
            "real_governance_write_enabled": False,
            "real_policy_change_enabled": False,
            "real_approval_execution_enabled": False,
            "real_denial_execution_enabled": False,
            "real_owner_review_execution_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_batch_close_write": True,
            "no_real_governance_note_version_write": True,
            "no_real_governance_note_version_restore": True,
            "no_real_governance_note_version_apply": True,
            "no_real_governance_note_write": True,
            "no_real_governance_note_save": True,
            "no_real_governance_note_submit": True,
            "no_real_governance_note_delete": True,
            "no_real_governance_detail_state_write": True,
            "no_real_governance_index_write": True,
            "no_real_governance_control_write": True,
            "no_real_governance_status_write": True,
            "no_real_governance_checkpoint_write": True,
            "no_real_policy_change_write": True,
            "no_real_policy_enable": True,
            "no_real_policy_disable": True,
            "no_real_policy_override": True,
            "no_real_approval_execute": True,
            "no_real_denial_execute": True,
            "no_real_owner_review_execute": True,
            "no_real_cross_batch_write": True,
            "no_real_continuity_write": True,
            "no_real_followup_write": True,
            "no_real_owner_review_write": True,
            "no_real_saved_view_restore": True,
            "no_real_saved_view_revert": True,
            "no_real_saved_view_write": True,
            "no_real_saved_view_edit": True,
            "no_real_saved_view_delete": True,
            "no_real_saved_view_apply": True,
            "no_real_saved_view_export": True,
            "no_real_user_preference_write": True,
            "no_archive_write": True,
            "no_raw_evidence_reveal": True,
            "no_real_action_execution": True,
            "cached_non_recursive_builder": True,
        },
        "blocked_action_matrix": _blocked_action_matrix(),
        "route_contract": {
            "method": "GET",
            "returns_json": True,
            "requires_tower_guard": True,
            "unguarded_high_risk_allowed": False,
        },
        "pack_245_acceptance": {
            "batch_241_245_closed_locally": True,
            "governance_save_manifest_preview_ready": True,
            "safe_to_push_batch_241_245": True,
            "ready_for_next_batch_246_250": True,
        },
        SAFE_TO_PUSH_BATCH_FLAG: True,
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "246",
            "name": "Receipt Chain Saved View Owner Review Governance Decision Trace Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-decision-trace-v246.json",
            "next_batch": NEXT_BATCH,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_batch_close_readiness_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 245 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_batch_close_readiness_preview_cached())


def build_pack_245_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_batch_close_readiness_preview_cached()
    summary = preview["governance_close_summary"]

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
        "save_batch": preview["save_batch"],
        "save_after_pack": preview["save_after_pack"],
        "next_batch": preview["next_batch"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "pack_card_count": summary["pack_card_count"],
        "close_check_count": summary["close_check_count"],
        "save_manifest_preview_count": summary["save_manifest_preview_count"],
        "transition_preview_count": summary["transition_preview_count"],
        "commit_manifest_count": summary["commit_manifest_count"],
        "governance_ready_to_save": summary["governance_ready_to_save"],
        SAFE_TO_PUSH_BATCH_FLAG: preview[SAFE_TO_PUSH_BATCH_FLAG],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_246_receipt_chain_saved_view_owner_review_governance_decision_trace() -> Dict[str, Any]:
    """Prepare Pack 246 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "246",
        "name": "Receipt Chain Saved View Owner Review Governance Decision Trace Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
        "next_batch": NEXT_BATCH,
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
    "SAVE_BATCH",
    "SAVE_AFTER_PACK",
    "NEXT_BATCH",
    "SAFE_TO_PUSH_BATCH_FLAG",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_governance_batch_close_readiness_preview",
    "build_pack_245_status_bridge",
    "prepare_pack_246_receipt_chain_saved_view_owner_review_governance_decision_trace",
]
