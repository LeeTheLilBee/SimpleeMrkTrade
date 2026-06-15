"""
SEARCHABLE LABEL: TOWER_PACK_278_HANDOFF_POLICY_ROUTE_ENFORCEMENT_NOTE_DRAFT_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Handoff Policy Route Enforcement layer

Pack 278: Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Draft Preview

This module is intentionally simulated/preview-only.

Purpose:
- Build safe owner/admin note draft previews from Pack 277 policy route enforcement detail drawers.
- Explain policy ID, route path, gate, enforcement mode, denial behavior, data boundary, and mutation blockers per lane.
- Keep OB rooms, OB mission accounts, Teller surfaces, Tower-owned access/billing/security routes, and receipt/proof lanes protected.
- Prepare Pack 279 handoff policy route enforcement note version preview.

Safety boundaries:
- No real note writes, saves, submits, or deletes.
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

from tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277 import (
    build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview,
)


PACK_ID = "278"
PACK_NUMBER = 278
PACK_NAME = "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Draft Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-note-draft-v278.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Handoff Policy Route Enforcement layer"

SOURCE_PACK = "277"
SOURCE_CLOSED_BATCH = "271-275"
SAVE_BATCH = "276-280"
SAVE_AFTER_PACK = 280
NEXT_BATCH = "276-280"
NEXT_PACK = "279"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_279"
NEXT_PREP_FLAG = "prepare_pack_279_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version"

BLOCKED_REAL_ACTIONS = (
    "real_note_write",
    "real_note_save",
    "real_note_submit",
    "real_note_delete",
    "real_note_version_write",
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
class HandoffPolicyRouteEnforcementNoteDraftCard:
    draft_id: str
    drawer_id: str
    enforcement_id: str
    policy_id: str
    enforcement_family: str
    source_surface: str
    destination_surface: str
    label: str
    draft_status: str
    draft_mode: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteDraftField:
    field_id: str
    draft_id: str
    enforcement_id: str
    policy_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteDraftAction:
    action_id: str
    draft_id: str
    enforcement_id: str
    policy_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementNoteDraftCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview())


def _source_drawers(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drawers = source_payload.get("handoff_policy_route_enforcement_detail_drawers", [])
    if isinstance(drawers, list) and drawers:
        return deepcopy(drawers)

    return [
        {
            "drawer_id": "fallback_handoff_policy_route_enforcement_detail_drawer",
            "enforcement_id": "fallback_policy_enforcement",
            "policy_id": "tower.default_deny",
            "policy_label": "Default deny before explicit approval",
            "enforcement_family": "TOWER_DEFAULT_DENY_ROUTE_ENFORCEMENT",
            "source_surface": "Any.Source",
            "destination_surface": "Any.Destination",
            "enforcement_mode": "deny_by_default_preview",
            "denial_behavior": "deny_until_tower_clear",
            "gate_type": "default_deny_gate",
        }
    ]


def _build_cards(drawers: List[Dict[str, Any]]) -> List[HandoffPolicyRouteEnforcementNoteDraftCard]:
    cards: List[HandoffPolicyRouteEnforcementNoteDraftCard] = []

    for idx, drawer in enumerate(drawers, start=1):
        source_surface = str(drawer.get("source_surface", "Unknown.Source"))
        destination_surface = str(drawer.get("destination_surface", "Unknown.Destination"))
        policy_id = str(drawer.get("policy_id", "tower.unknown_policy"))

        cards.append(
            HandoffPolicyRouteEnforcementNoteDraftCard(
                draft_id=f"handoff_policy_route_enforcement_note_draft_278_{idx:03d}",
                drawer_id=str(drawer.get("drawer_id", f"drawer_{idx:03d}")),
                enforcement_id=str(drawer.get("enforcement_id", f"enforcement_{idx:03d}")),
                policy_id=policy_id,
                enforcement_family=str(drawer.get("enforcement_family", "UNKNOWN_ENFORCEMENT_FAMILY")),
                source_surface=source_surface,
                destination_surface=destination_surface,
                label=f"Policy route enforcement note draft for {policy_id}: {source_surface} → {destination_surface}",
                draft_status="policy_route_enforcement_note_draft_preview_ready",
                draft_mode="preview_only",
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )

    return cards


def _drawer_by_enforcement(drawers: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(drawer.get("enforcement_id")): drawer for drawer in drawers}


def _build_fields(
    cards: List[HandoffPolicyRouteEnforcementNoteDraftCard],
    drawers: List[Dict[str, Any]],
) -> List[HandoffPolicyRouteEnforcementNoteDraftField]:
    fields: List[HandoffPolicyRouteEnforcementNoteDraftField] = []
    drawer_lookup = _drawer_by_enforcement(drawers)

    for card in cards:
        drawer = drawer_lookup.get(card.enforcement_id, {})
        policy_label = str(drawer.get("policy_label", "Unknown policy"))
        enforcement_mode = str(drawer.get("enforcement_mode", "preview_only"))
        denial_behavior = str(drawer.get("denial_behavior", "deny_when_unknown"))
        gate_type = str(drawer.get("gate_type", "tower_gate"))

        fields.extend(
            [
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_title",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Draft title",
                    field_type="textarea_preview",
                    preview_value=f"Tower policy route enforcement review: {card.policy_id}",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_route_path",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Route path note",
                    field_type="locked_summary",
                    preview_value=f"{card.source_surface} → {card.destination_surface}",
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_policy_id",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Policy ID note",
                    field_type="locked_summary",
                    preview_value=card.policy_id,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_policy_label",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Policy label note",
                    field_type="textarea_preview",
                    preview_value=f"{card.policy_id} means: {policy_label}. This preview does not write or apply policy.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_gate_type",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Gate note",
                    field_type="textarea_preview",
                    preview_value=f"Gate type remains {gate_type}. Access stays denied unless Tower allows preview access.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_enforcement_mode",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Enforcement mode note",
                    field_type="textarea_preview",
                    preview_value=f"Enforcement mode is {enforcement_mode}. No route enforcement write/apply occurs.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_denial_behavior",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Denial behavior note",
                    field_type="textarea_preview",
                    preview_value=f"Denial behavior is {denial_behavior}. Unsafe actions remain blocked.",
                    redaction_state="redacted_pointer_only",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_data_boundary",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Data boundary note",
                    field_type="locked_summary",
                    preview_value="Raw evidence, private documents, payment details, OB trade intelligence, and internal registry details remain hidden or pointer-only.",
                    redaction_state="redacted_pointer_only",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_ob_teller_boundary",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="OB/Teller boundary note",
                    field_type="locked_summary",
                    preview_value="OB and Teller UI are not built here. Tower only previews policy route enforcement boundaries.",
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_mutation_block",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Mutation block note",
                    field_type="locked_summary",
                    preview_value="Note saves, policy writes/applies/overrides/deletes, route enforcement writes/applies, route changes, evidence writes, raw evidence reveal, handoff execution, registry writes, clearance writes, billing/security writes, receipt/archive writes, and real actions remain blocked.",
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementNoteDraftField(
                    field_id=f"{card.draft_id}_field_next_step",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Next step note",
                    field_type="textarea_preview",
                    preview_value="Prepare Pack 279 handoff policy route enforcement note version preview without writing note versions.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return fields


def _build_actions(cards: List[HandoffPolicyRouteEnforcementNoteDraftCard]) -> List[HandoffPolicyRouteEnforcementNoteDraftAction]:
    actions: List[HandoffPolicyRouteEnforcementNoteDraftAction] = []

    for card in cards:
        actions.extend(
            [
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_preview",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Preview note draft",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing the policy route enforcement note draft does not write state.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_save",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Save note draft",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note saves are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_submit",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Submit note draft",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note submits are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_delete",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Delete note draft",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real note deletes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_policy",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_apply_policy",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Apply policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy applies are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_override_policy",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Override policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy overrides are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_route_enforcement",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write route enforcement",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route enforcement writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_apply_route_enforcement",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Apply route enforcement",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route enforcement applies are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_change_route",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Change route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route changes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_evidence",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real evidence writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_reveal_raw_evidence",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_execute_handoff",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Execute handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff execution is blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_registry",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write registry",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="App, room, mission account, and handoff registry writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_change_clearance",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Change clearance",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Clearance and permission changes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_billing",
                    draft_id=card.draft_id,
                    enforcement_id=card.enforcement_id,
                    policy_id=card.policy_id,
                    label="Write billing/security",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Billing, subscription, checkout, customer portal, and account security writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_receipt",
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


def _build_checkpoints() -> List[HandoffPolicyRouteEnforcementNoteDraftCheckpoint]:
    rows = [
        ("handoff_policy_route_note_draft_checkpoint_278_001", "Pack 277 source policy route enforcement detail drawer is ready", "safe_summary_only"),
        ("handoff_policy_route_note_draft_checkpoint_278_002", "Policy route enforcement note draft cards are preview-only", "safe_summary_only"),
        ("handoff_policy_route_note_draft_checkpoint_278_003", "Draft fields do not write state or reveal raw evidence", "redacted_pointer_only"),
        ("handoff_policy_route_note_draft_checkpoint_278_004", "Policy ID, route path, gate, enforcement mode, denial behavior, data boundary, and mutation blocker notes are represented safely", "safe_summary_only"),
        ("handoff_policy_route_note_draft_checkpoint_278_005", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("handoff_policy_route_note_draft_checkpoint_278_006", "Tower ownership of policy, access, clearance, billing, security, and routes is preserved", "safe_summary_only"),
        ("handoff_policy_route_note_draft_checkpoint_278_007", "Note saves/submits/deletes, policy writes/applies/overrides, route enforcement writes/applies, route changes, handoff execution, evidence writes, registry writes, clearance writes, billing writes, receipt writes, and real actions remain blocked", "blocked_action_summary"),
        ("handoff_policy_route_note_draft_checkpoint_278_008", "Ready for Pack 279 policy route enforcement note version preview", "safe_summary_only"),
    ]

    return [
        HandoffPolicyRouteEnforcementNoteDraftCheckpoint(
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
            "reason": "Pack 278 previews policy route enforcement note drafts only and cannot mutate notes, policies, route enforcement, routes, evidence, handoffs, registries, clearance, billing, security, receipts, archives, or real actions.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    source_drawers = _source_drawers(source_payload)

    cards_raw = _build_cards(source_drawers)
    fields_raw = _build_fields(cards_raw, source_drawers)
    actions_raw = _build_actions(cards_raw)
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(card) for card in cards_raw]
    fields = [asdict(field) for field in fields_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    editable_field_count = sum(1 for field in fields if field["editable_preview"] is True)
    locked_field_count = sum(1 for field in fields if field["editable_preview"] is False)
    redacted_field_count = sum(1 for field in fields if field["redaction_state"] == "redacted_pointer_only")

    all_cards_preview_only = all(card["draft_mode"] == "preview_only" for card in cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in cards)
    all_cards_non_executable = all(card["executable"] is False for card in cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in cards)

    all_fields_no_writes = all(field["writes_state"] is False for field in fields)
    all_fields_no_raw_evidence = all(field["raw_evidence_visible"] is False for field in fields)

    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    handoff_policy_route_enforcement_note_draft_ready = all([
        all_cards_preview_only,
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
        "receipt_chain_layer": "saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview",
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_278"),
        "handoff_policy_route_enforcement_note_draft_cards": cards,
        "handoff_policy_route_enforcement_note_draft_fields": fields,
        "handoff_policy_route_enforcement_note_draft_actions": actions,
        "handoff_policy_route_enforcement_note_draft_checkpoints": checkpoints,
        "handoff_policy_route_enforcement_note_draft_summary": {
            "source_detail_drawer_count": len(source_drawers),
            "draft_card_count": len(cards),
            "draft_field_count": len(fields),
            "draft_action_count": len(actions),
            "draft_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "editable_field_count": editable_field_count,
            "locked_field_count": locked_field_count,
            "redacted_field_count": redacted_field_count,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_non_executable": all_cards_non_executable,
            "all_cards_no_raw_evidence": all_cards_no_raw_evidence,
            "all_fields_no_writes": all_fields_no_writes,
            "all_fields_no_raw_evidence": all_fields_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "handoff_policy_route_enforcement_note_draft_ready": handoff_policy_route_enforcement_note_draft_ready,
            "real_note_write_enabled": False,
            "real_note_save_enabled": False,
            "real_note_submit_enabled": False,
            "real_note_delete_enabled": False,
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
        "pack_278_acceptance": {
            "source_pack_277_verified": True,
            "policy_route_enforcement_note_draft_cards_built": True,
            "policy_note_fields_built": True,
            "route_path_note_fields_built": True,
            "gate_and_denial_note_fields_built": True,
            "data_boundary_note_fields_built": True,
            "note_save_submit_delete_blocked": True,
            "mutation_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_policy_route_enforcement_note_version": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Version Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-note-version-v279.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 278 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview_cached())


def build_pack_278_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview_cached()
    summary = preview["handoff_policy_route_enforcement_note_draft_summary"]

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
        "draft_card_count": summary["draft_card_count"],
        "draft_field_count": summary["draft_field_count"],
        "draft_action_count": summary["draft_action_count"],
        "handoff_policy_route_enforcement_note_draft_ready": summary["handoff_policy_route_enforcement_note_draft_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_279_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version() -> Dict[str, Any]:
    """Prepare Pack 279 direction without writing state."""
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Version Preview",
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
    "build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft_preview",
    "build_pack_278_status_bridge",
    "prepare_pack_279_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_version",
]
