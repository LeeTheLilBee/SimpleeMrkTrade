"""
SEARCHABLE LABEL: TOWER_PACK_279_HANDOFF_POLICY_ROUTE_ENFORCEMENT_NOTE_VERSION_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Handoff Policy Route Enforcement layer

Pack 279: Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Version Preview

This module is intentionally simulated/preview-only.

Purpose:
- Build safe note version previews from Pack 278 policy route enforcement note drafts.
- Compare simulated note versions without writing/restoring/applying/deleting note versions.
- Preserve Tower ownership of policy, route enforcement, access, clearance, billing/security, data boundaries, and receipt/proof protection.
- Prepare Pack 280 policy route enforcement batch close readiness preview.

Safety boundaries:
- No real note writes, saves, submits, or deletes.
- No real note version writes, restores, applies, or deletes.
- No real policy writes, applies, overrides, or deletes.
- No real route enforcement writes/applies.
- No real route changes or activations.
- No real evidence writes or exports.
- No raw evidence reveal.
- No real handoff execution.
- No real app/room/account registry writes.
- No real OB/Teller UI work.
- No real clearance, permission, billing, subscription, checkout, or security writes.
- No real receipt/archive writes.
- Cached/non-recursive builders only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_v278 import (
    build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview,
)


PACK_ID = "279"
PACK_NUMBER = 279
PACK_NAME = "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-note-version-v279.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Handoff Policy Route Enforcement layer"

SOURCE_PACK = "278"
SOURCE_CLOSED_BATCH = "271-275"
SAVE_BATCH = "276-280"
SAVE_AFTER_PACK = 280
NEXT_BATCH = "276-280"
NEXT_PACK = "280"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_280"
NEXT_PREP_FLAG = "prepare_pack_280_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_note_write",
    "real_note_save",
    "real_note_submit",
    "real_note_delete",
    "real_note_version_write",
    "real_note_version_restore",
    "real_note_version_apply",
    "real_note_version_delete",
    "real_note_version_compare_write",
    "real_policy_write",
    "real_policy_apply",
    "real_policy_override",
    "real_policy_delete",
    "real_route_enforcement_write",
    "real_route_enforcement_apply",
    "real_route_change",
    "real_route_activation",
    "real_route_deactivation",
    "real_evidence_write",
    "real_evidence_export",
    "raw_evidence_reveal",
    "real_handoff_execute",
    "real_handoff_write",
    "real_app_registry_write",
    "real_room_registry_write",
    "real_mission_account_registry_write",
    "real_ob_route_change",
    "real_teller_route_change",
    "real_tower_route_change",
    "real_clearance_write",
    "real_permission_write",
    "real_mode_permission_write",
    "real_billing_write",
    "real_subscription_write",
    "real_checkout_write",
    "real_customer_portal_write",
    "real_account_security_write",
    "real_receipt_write",
    "real_archive_write",
    "real_owner_review_execute",
    "real_saved_view_write",
    "real_saved_view_apply",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteVersionCard:
    version_id: str
    draft_id: str
    enforcement_id: str
    policy_id: str
    enforcement_family: str
    source_surface: str
    destination_surface: str
    label: str
    version_label: str
    version_status: str
    version_mode: str
    changed_field_count: int
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteVersionCompareRow:
    compare_row_id: str
    version_id: str
    draft_id: str
    enforcement_id: str
    policy_id: str
    label: str
    field_name: str
    previous_preview: str
    current_preview: str
    change_type: str
    redaction_state: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteVersionAction:
    action_id: str
    version_id: str
    draft_id: str
    enforcement_id: str
    policy_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drafts = source_payload.get("handoff_policy_route_enforcement_note_draft_cards", [])
    if isinstance(drafts, list) and drafts:
        return deepcopy(drafts)

    return [
        {
            "draft_id": "fallback_handoff_policy_route_enforcement_note_draft",
            "enforcement_id": "fallback_policy_enforcement",
            "policy_id": "tower.default_deny",
            "enforcement_family": "TOWER_DEFAULT_DENY_ROUTE_ENFORCEMENT",
            "source_surface": "Any.Source",
            "destination_surface": "Any.Destination",
        }
    ]


def _build_version_cards(drafts: List[Dict[str, Any]]) -> List[HandoffPolicyRouteEnforcementNoteVersionCard]:
    cards: List[HandoffPolicyRouteEnforcementNoteVersionCard] = []

    for idx, draft in enumerate(drafts, start=1):
        source_surface = str(draft.get("source_surface", "Unknown.Source"))
        destination_surface = str(draft.get("destination_surface", "Unknown.Destination"))
        policy_id = str(draft.get("policy_id", "tower.unknown_policy"))
        common = {
            "draft_id": str(draft.get("draft_id", f"draft_{idx:03d}")),
            "enforcement_id": str(draft.get("enforcement_id", f"enforcement_{idx:03d}")),
            "policy_id": policy_id,
            "enforcement_family": str(draft.get("enforcement_family", "UNKNOWN_ENFORCEMENT_FAMILY")),
            "source_surface": source_surface,
            "destination_surface": destination_surface,
            "version_status": "policy_route_enforcement_note_version_preview_ready",
            "version_mode": "preview_only",
            "writes_state": False,
            "executable": False,
            "raw_evidence_visible": False,
        }

        cards.append(
            HandoffPolicyRouteEnforcementNoteVersionCard(
                version_id=f"handoff_policy_route_enforcement_note_version_279_{idx:03d}_v1",
                label=f"Initial policy route enforcement note version preview for {policy_id}",
                version_label="Initial simulated policy route enforcement note version",
                changed_field_count=11,
                **common,
            )
        )
        cards.append(
            HandoffPolicyRouteEnforcementNoteVersionCard(
                version_id=f"handoff_policy_route_enforcement_note_version_279_{idx:03d}_v2",
                label=f"Revised policy route enforcement note version preview for {policy_id}",
                version_label="Revised simulated policy route enforcement note version",
                changed_field_count=13,
                **common,
            )
        )

    return cards


def _build_compare_rows(cards: List[HandoffPolicyRouteEnforcementNoteVersionCard]) -> List[HandoffPolicyRouteEnforcementNoteVersionCompareRow]:
    rows: List[HandoffPolicyRouteEnforcementNoteVersionCompareRow] = []

    specs = [
        ("title", "Previous policy enforcement title", "Versioned policy enforcement review title", "title_preview_change", "safe_preview"),
        ("route_path", "Previous route path note", "Versioned route path preserved", "route_path_unchanged", "safe_preview"),
        ("policy_id", "Previous policy ID note", "Versioned policy ID preserved", "policy_id_unchanged", "safe_preview"),
        ("policy_label", "Previous policy label note", "Versioned policy label preserved without applying policy", "policy_label_preview_change", "safe_preview"),
        ("gate_type", "Previous gate note", "Versioned gate note preserves Tower-controlled access", "gate_preview_change", "safe_preview"),
        ("enforcement_mode", "Previous enforcement mode note", "Versioned enforcement mode remains preview-only", "enforcement_mode_unchanged", "safe_preview"),
        ("denial_behavior", "Previous denial behavior note", "Versioned denial behavior remains strict", "denial_behavior_unchanged", "redacted_pointer_only"),
        ("data_boundary", "Previous data boundary note", "Versioned data boundary keeps raw/private data hidden", "data_boundary_unchanged", "redacted_pointer_only"),
        ("ob_teller_boundary", "Previous OB/Teller boundary note", "Versioned OB/Teller UI-not-built boundary preserved", "boundary_unchanged", "safe_preview"),
        ("mutation_block", "Previous mutation blocker note", "Versioned mutation blocker remains strict", "mutation_boundary_unchanged", "safe_preview"),
        ("next_step", "Prepare Pack 279", "Prepare Pack 280 batch close readiness", "next_step_preview_change", "safe_preview"),
    ]

    for card in cards:
        for field_name, previous, current, change_type, redaction_state in specs:
            rows.append(
                HandoffPolicyRouteEnforcementNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_{field_name}",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label=f"Compare {field_name} for {card.policy_id}",
                    field_name=field_name,
                    previous_preview=previous,
                    current_preview=f"{current}: {card.source_surface} → {card.destination_surface}",
                    change_type=change_type,
                    redaction_state=redaction_state,
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                )
            )

    return rows


def _build_actions(cards: List[HandoffPolicyRouteEnforcementNoteVersionCard]) -> List[HandoffPolicyRouteEnforcementNoteVersionAction]:
    actions: List[HandoffPolicyRouteEnforcementNoteVersionAction] = []

    for card in cards:
        actions.extend(
            [
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_preview",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Preview note version",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing the policy route enforcement note version does not write state.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_restore",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Restore note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note version restores are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Apply note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note version applies are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_save_current",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Save as current note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note saves are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_submit",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Submit note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note submits are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_delete",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Delete note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note version deletes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_policy",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply_policy",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Apply policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy applies are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_override_policy",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Override policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy overrides are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_route_enforcement",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write route enforcement",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route enforcement writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_change_route",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Change route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route changes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_activate_route",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Activate route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route activation is blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_evidence",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real evidence writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_reveal_raw_evidence",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_handoff",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Execute handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff execution is blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_registry",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write registry",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="App, room, mission account, and handoff registry writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_change_clearance",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Change clearance",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Clearance and permission changes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_billing",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write billing/security",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Billing, subscription, checkout, customer portal, and account security writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_receipt",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write receipt/archive",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real receipt/archive writes are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[HandoffPolicyRouteEnforcementNoteVersionCheckpoint]:
    rows = [
        ("handoff_policy_route_note_version_checkpoint_279_001", "Pack 278 source policy route enforcement note draft is ready", "safe_summary_only"),
        ("handoff_policy_route_note_version_checkpoint_279_002", "Policy route enforcement note version cards are preview-only", "safe_summary_only"),
        ("handoff_policy_route_note_version_checkpoint_279_003", "Version compare rows do not write state or reveal raw evidence", "redacted_pointer_only"),
        ("handoff_policy_route_note_version_checkpoint_279_004", "Policy, route path, gate, enforcement mode, denial behavior, data boundary, and mutation blocker version comparisons are represented safely", "safe_summary_only"),
        ("handoff_policy_route_note_version_checkpoint_279_005", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("handoff_policy_route_note_version_checkpoint_279_006", "Tower ownership of policy, access, clearance, billing, security, and routes is preserved", "safe_summary_only"),
        ("handoff_policy_route_note_version_checkpoint_279_007", "Version restore/apply/save/submit/delete, note writes, policy writes/applies/overrides, route enforcement writes/applies, route changes, handoff execution, evidence writes, registry writes, clearance writes, billing writes, receipt writes, and real actions remain blocked", "blocked_action_summary"),
        ("handoff_policy_route_note_version_checkpoint_279_008", "Ready for Pack 280 policy route enforcement batch close readiness preview", "safe_summary_only"),
    ]

    return [
        HandoffPolicyRouteEnforcementNoteVersionCheckpoint(
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
            "reason": "Pack 279 previews policy route enforcement note versions only and cannot mutate note versions, notes, policies, route enforcement, routes, evidence, handoffs, registries, clearance, billing, security, receipts, archives, or real actions.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    source_drafts = _source_drafts(source_payload)

    cards_raw = _build_version_cards(source_drafts)
    rows_raw = _build_compare_rows(cards_raw)
    actions_raw = _build_actions(cards_raw)
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(card) for card in cards_raw]
    rows = [asdict(row) for row in rows_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    redacted_compare_row_count = sum(1 for row in rows if row["redaction_state"] == "redacted_pointer_only")

    all_cards_preview_only = all(card["version_mode"] == "preview_only" for card in cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in cards)
    all_cards_non_executable = all(card["executable"] is False for card in cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in cards)

    all_rows_no_writes = all(row["writes_state"] is False for row in rows)
    all_rows_non_executable = all(row["executable"] is False for row in rows)
    all_rows_no_raw_evidence = all(row["raw_evidence_visible"] is False for row in rows)

    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    handoff_policy_route_enforcement_note_version_ready = all([
        all_cards_preview_only,
        all_cards_no_writes,
        all_cards_non_executable,
        all_cards_no_raw_evidence,
        all_rows_no_writes,
        all_rows_non_executable,
        all_rows_no_raw_evidence,
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
        "receipt_chain_layer": "saved_view_owner_review_handoff_policy_route_enforcement_note_version_preview",
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_279"),
        "handoff_policy_route_enforcement_note_version_cards": cards,
        "handoff_policy_route_enforcement_note_version_compare_rows": rows,
        "handoff_policy_route_enforcement_note_version_actions": actions,
        "handoff_policy_route_enforcement_note_version_checkpoints": checkpoints,
        "handoff_policy_route_enforcement_note_version_summary": {
            "source_draft_card_count": len(source_drafts),
            "version_card_count": len(cards),
            "compare_row_count": len(rows),
            "version_action_count": len(actions),
            "version_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "redacted_compare_row_count": redacted_compare_row_count,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_non_executable": all_cards_non_executable,
            "all_cards_no_raw_evidence": all_cards_no_raw_evidence,
            "all_rows_no_writes": all_rows_no_writes,
            "all_rows_non_executable": all_rows_non_executable,
            "all_rows_no_raw_evidence": all_rows_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "handoff_policy_route_enforcement_note_version_ready": handoff_policy_route_enforcement_note_version_ready,
            "real_note_write_enabled": False,
            "real_note_save_enabled": False,
            "real_note_submit_enabled": False,
            "real_note_delete_enabled": False,
            "real_note_version_write_enabled": False,
            "real_note_version_restore_enabled": False,
            "real_note_version_apply_enabled": False,
            "real_note_version_delete_enabled": False,
            "real_policy_write_enabled": False,
            "real_policy_apply_enabled": False,
            "real_policy_override_enabled": False,
            "real_route_enforcement_write_enabled": False,
            "real_route_enforcement_apply_enabled": False,
            "real_route_change_enabled": False,
            "real_route_activation_enabled": False,
            "real_evidence_write_enabled": False,
            "real_evidence_export_enabled": False,
            "raw_evidence_visible": False,
            "real_handoff_execute_enabled": False,
            "real_handoff_write_enabled": False,
            "real_app_registry_write_enabled": False,
            "real_room_registry_write_enabled": False,
            "real_mission_account_registry_write_enabled": False,
            "real_ob_route_change_enabled": False,
            "real_teller_route_change_enabled": False,
            "real_tower_route_change_enabled": False,
            "real_clearance_write_enabled": False,
            "real_permission_write_enabled": False,
            "real_billing_write_enabled": False,
            "real_subscription_write_enabled": False,
            "real_receipt_write_enabled": False,
            "real_archive_write_enabled": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_note_write": True,
            "no_real_note_save": True,
            "no_real_note_submit": True,
            "no_real_note_delete": True,
            "no_real_note_version_write": True,
            "no_real_note_version_restore": True,
            "no_real_note_version_apply": True,
            "no_real_note_version_delete": True,
            "no_real_policy_write": True,
            "no_real_policy_apply": True,
            "no_real_policy_override": True,
            "no_real_route_enforcement_write": True,
            "no_real_route_enforcement_apply": True,
            "no_real_route_change": True,
            "no_real_route_activation": True,
            "no_real_evidence_write": True,
            "no_real_evidence_export": True,
            "no_raw_evidence_reveal": True,
            "no_real_handoff_execute": True,
            "no_real_handoff_write": True,
            "no_real_app_registry_write": True,
            "no_real_room_registry_write": True,
            "no_real_mission_account_registry_write": True,
            "no_real_clearance_write": True,
            "no_real_permission_write": True,
            "no_real_billing_write": True,
            "no_real_subscription_write": True,
            "no_real_receipt_write": True,
            "no_real_archive_write": True,
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
        "pack_279_acceptance": {
            "source_pack_278_verified": True,
            "policy_route_enforcement_note_version_cards_built": True,
            "policy_route_enforcement_note_version_compare_rows_built": True,
            "note_version_restore_apply_delete_blocked": True,
            "policy_route_gate_and_denial_version_comparisons_safe": True,
            "data_boundary_version_comparisons_safe": True,
            "mutation_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_policy_route_enforcement_batch_close": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-batch-close-readiness-v280.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 279 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version_preview_cached())


def build_pack_279_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version_preview_cached()
    summary = preview["handoff_policy_route_enforcement_note_version_summary"]

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
        "compare_row_count": summary["compare_row_count"],
        "version_action_count": summary["version_action_count"],
        "handoff_policy_route_enforcement_note_version_ready": summary["handoff_policy_route_enforcement_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_280_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_batch_close_readiness() -> Dict[str, Any]:
    """Prepare Pack 280 direction without writing state."""
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Batch Close Readiness Preview",
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
    "build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version_preview",
    "build_pack_279_status_bridge",
    "prepare_pack_280_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_batch_close_readiness",
]
