"""
SEARCHABLE LABEL: TOWER_PACK_219B_RECEIPT_CHAIN_SAVED_VIEW_VERSION_COMPARE_PREVIEW_MODULE

Pack 219B: Receipt Chain Saved View Version Compare Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
- No real saved-view restore/revert/write/edit/delete/apply/export.
- No real user preference writes.
- No archive writes.
- No raw evidence reveal.
- No real action execution.
- Cached/non-recursive builders only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List, Tuple

from tower.receipt_chain_saved_view_history_v219a import (
    build_receipt_chain_saved_view_history_preview,
)


PACK_ID = "219B"
PACK_NAME = "Receipt Chain Saved View Version Compare Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-version-compare-v219b.json"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_219C"
NEXT_PREP_FLAG = "prepare_pack_219C_saved_view_compare_filter_navigation"

BLOCKED_REAL_ACTIONS = (
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
class VersionComparePair:
    compare_pair_id: str
    left_version_id: str
    right_version_id: str
    label: str
    compare_mode: str
    changed_field_count: int
    redacted_field_count: int
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class VersionCompareRow:
    row_id: str
    compare_pair_id: str
    field_name: str
    left_preview: str
    right_preview: str
    change_type: str
    severity: str
    redaction_state: str
    owner_review_hint: str
    executable: bool


@dataclass(frozen=True)
class CompareSummaryCard:
    card_id: str
    compare_pair_id: str
    label: str
    total_rows: int
    changed_rows: int
    redacted_rows: int
    blocked_action_count: int
    status: str


def _safe_history_payload() -> Dict[str, Any]:
    payload = build_receipt_chain_saved_view_history_preview()
    return deepcopy(payload)


def _build_compare_pairs() -> List[VersionComparePair]:
    return [
        VersionComparePair(
            compare_pair_id="vcmp_219b_001",
            left_version_id="sv_v218_001",
            right_version_id="sv_v218_002",
            label="Baseline vs Severity Filter",
            compare_mode="side_by_side_preview",
            changed_field_count=3,
            redacted_field_count=0,
            executable=False,
            raw_evidence_visible=False,
        ),
        VersionComparePair(
            compare_pair_id="vcmp_219b_002",
            left_version_id="sv_v218_002",
            right_version_id="sv_v218_003",
            label="Severity Filter vs Sort Preview",
            compare_mode="side_by_side_preview",
            changed_field_count=2,
            redacted_field_count=0,
            executable=False,
            raw_evidence_visible=False,
        ),
        VersionComparePair(
            compare_pair_id="vcmp_219b_003",
            left_version_id="sv_v218_003",
            right_version_id="sv_v218_004",
            label="Sort Preview vs Drawer Layout",
            compare_mode="side_by_side_preview",
            changed_field_count=5,
            redacted_field_count=1,
            executable=False,
            raw_evidence_visible=False,
        ),
        VersionComparePair(
            compare_pair_id="vcmp_219b_004",
            left_version_id="sv_v218_004",
            right_version_id="sv_v218_005",
            label="Drawer Layout vs Owner Note Link",
            compare_mode="side_by_side_preview",
            changed_field_count=4,
            redacted_field_count=2,
            executable=False,
            raw_evidence_visible=False,
        ),
        VersionComparePair(
            compare_pair_id="vcmp_219b_005",
            left_version_id="sv_v218_005",
            right_version_id="sv_v218_006",
            label="Owner Note Link vs History Checkpoint",
            compare_mode="side_by_side_preview",
            changed_field_count=6,
            redacted_field_count=2,
            executable=False,
            raw_evidence_visible=False,
        ),
        VersionComparePair(
            compare_pair_id="vcmp_219b_006",
            left_version_id="sv_v218_001",
            right_version_id="sv_v218_006",
            label="Baseline vs Current Preview",
            compare_mode="side_by_side_preview",
            changed_field_count=14,
            redacted_field_count=3,
            executable=False,
            raw_evidence_visible=False,
        ),
    ]


def _build_compare_rows() -> List[VersionCompareRow]:
    rows = [
        VersionCompareRow(
            row_id="vcrow_219b_001",
            compare_pair_id="vcmp_219b_001",
            field_name="severity_filter",
            left_preview="all",
            right_preview="high, critical",
            change_type="filter_change",
            severity="medium",
            redaction_state="safe_preview",
            owner_review_hint="Confirm high/critical receipt-chain lane is easier to review.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_002",
            compare_pair_id="vcmp_219b_001",
            field_name="containment_state_filter",
            left_preview="all",
            right_preview="quarantine, fail_closed, step_up_required",
            change_type="filter_change",
            severity="medium",
            redaction_state="safe_preview",
            owner_review_hint="Confirm containment states are focused without hiding safety context.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_003",
            compare_pair_id="vcmp_219b_002",
            field_name="sort_order",
            left_preview="manual preset order",
            right_preview="newest receipt-chain event first",
            change_type="sort_change",
            severity="low",
            redaction_state="safe_preview",
            owner_review_hint="Confirm newest-first ordering improves review speed.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_004",
            compare_pair_id="vcmp_219b_003",
            field_name="drawer_primary_section",
            left_preview="receipt summary",
            right_preview="containment status",
            change_type="layout_change",
            severity="medium",
            redaction_state="safe_preview",
            owner_review_hint="Confirm containment status belongs above deeper evidence pointers.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_005",
            compare_pair_id="vcmp_219b_003",
            field_name="raw_evidence_panel",
            left_preview="not available",
            right_preview="redacted pointer only",
            change_type="evidence_boundary_change",
            severity="high",
            redaction_state="redacted_pointer_only",
            owner_review_hint="Raw evidence remains hidden; only safe receipt pointers appear.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_006",
            compare_pair_id="vcmp_219b_004",
            field_name="owner_note_visibility",
            left_preview="hidden",
            right_preview="preview summary only",
            change_type="owner_note_change",
            severity="medium",
            redaction_state="redacted_summary_only",
            owner_review_hint="Owner notes are summarized without writing or exposing raw note history.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_007",
            compare_pair_id="vcmp_219b_004",
            field_name="owner_note_count",
            left_preview="0",
            right_preview="2 preview summaries",
            change_type="owner_note_change",
            severity="low",
            redaction_state="redacted_summary_only",
            owner_review_hint="Count is visible, raw note body is not.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_008",
            compare_pair_id="vcmp_219b_005",
            field_name="history_navigation",
            left_preview="single edit card",
            right_preview="timeline plus compare-ready rows",
            change_type="navigation_change",
            severity="medium",
            redaction_state="safe_preview",
            owner_review_hint="This creates the bridge into compare/filter navigation.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_009",
            compare_pair_id="vcmp_219b_005",
            field_name="restore_control",
            left_preview="disabled",
            right_preview="disabled with visible reason",
            change_type="safety_control_change",
            severity="high",
            redaction_state="safe_preview",
            owner_review_hint="Restore remains blocked; the UI can explain why.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_010",
            compare_pair_id="vcmp_219b_006",
            field_name="overall_review_shape",
            left_preview="baseline saved-view edit preview",
            right_preview="history checkpoint with compare-ready rows",
            change_type="summary_change",
            severity="medium",
            redaction_state="safe_preview",
            owner_review_hint="Shows full evolution from baseline to current version without applying it.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_011",
            compare_pair_id="vcmp_219b_006",
            field_name="evidence_mode",
            left_preview="receipt pointer only",
            right_preview="receipt pointer only",
            change_type="unchanged_safety_boundary",
            severity="high",
            redaction_state="redacted_pointer_only",
            owner_review_hint="Evidence boundary stayed locked across versions.",
            executable=False,
        ),
        VersionCompareRow(
            row_id="vcrow_219b_012",
            compare_pair_id="vcmp_219b_006",
            field_name="action_execution",
            left_preview="blocked",
            right_preview="blocked",
            change_type="unchanged_safety_boundary",
            severity="high",
            redaction_state="safe_preview",
            owner_review_hint="No compare row may execute action.",
            executable=False,
        ),
    ]
    return rows


def _rows_by_pair(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        index.setdefault(row["compare_pair_id"], []).append(row)
    return index


def _build_summary_cards(
    pairs: List[Dict[str, Any]],
    rows_by_pair: Dict[str, List[Dict[str, Any]]],
) -> List[CompareSummaryCard]:
    cards: List[CompareSummaryCard] = []

    for pair in pairs:
        pair_rows = rows_by_pair.get(pair["compare_pair_id"], [])
        redacted_count = sum(
            1
            for row in pair_rows
            if row["redaction_state"] in {"redacted_pointer_only", "redacted_summary_only"}
        )
        changed_count = sum(
            1
            for row in pair_rows
            if row["change_type"] != "unchanged_safety_boundary"
        )

        cards.append(
            CompareSummaryCard(
                card_id=f"summary_{pair['compare_pair_id']}",
                compare_pair_id=pair["compare_pair_id"],
                label=pair["label"],
                total_rows=len(pair_rows),
                changed_rows=changed_count,
                redacted_rows=redacted_count,
                blocked_action_count=len(BLOCKED_REAL_ACTIONS),
                status="compare_preview_ready",
            )
        )

    return cards


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 219B previews version differences only and cannot mutate state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


def _navigation_cards() -> List[Dict[str, Any]]:
    return [
        {
            "nav_id": "nav_219b_compare_pairs",
            "label": "Compare Pairs",
            "target_endpoint": ENDPOINT,
            "enabled": True,
            "mode": "preview_only",
        },
        {
            "nav_id": "nav_219b_compare_rows",
            "label": "Compare Rows",
            "target_endpoint": ENDPOINT,
            "enabled": True,
            "mode": "preview_only",
        },
        {
            "nav_id": "nav_219b_redaction_review",
            "label": "Redaction Review",
            "target_endpoint": ENDPOINT,
            "enabled": True,
            "mode": "preview_only",
        },
        {
            "nav_id": "nav_219b_restore_disabled",
            "label": "Restore/Revert Disabled",
            "target_endpoint": ENDPOINT,
            "enabled": False,
            "mode": "blocked_preview_only",
        },
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_version_compare_preview_cached() -> Dict[str, Any]:
    source_payload = _safe_history_payload()

    compare_pairs = [asdict(pair) for pair in _build_compare_pairs()]
    compare_rows = [asdict(row) for row in _build_compare_rows()]
    rows_by_pair = _rows_by_pair(compare_rows)
    summary_cards = [asdict(card) for card in _build_summary_cards(compare_pairs, rows_by_pair)]

    compare_row_count = len(compare_rows)
    compare_pair_count = len(compare_pairs)
    redacted_row_count = sum(
        1
        for row in compare_rows
        if row["redaction_state"] in {"redacted_pointer_only", "redacted_summary_only"}
    )
    high_severity_count = sum(1 for row in compare_rows if row["severity"] == "high")

    preview = {
        "pack": PACK_ID,
        "pack_name": PACK_NAME,
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_version_compare_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_219B"),
        "source_boundary": {
            "inherits_from_pack_219A": "saved_view_history_preview",
            "writes_any_saved_view": False,
            "restores_any_saved_view": False,
            "reverts_any_saved_view": False,
            "writes_any_user_preference": False,
            "writes_any_archive": False,
            "reveals_raw_evidence": False,
            "executes_any_real_action": False,
        },
        "version_compare_summary": {
            "compare_pair_count": compare_pair_count,
            "compare_row_count": compare_row_count,
            "summary_card_count": len(summary_cards),
            "redacted_row_count": redacted_row_count,
            "high_severity_row_count": high_severity_count,
            "restore_enabled": False,
            "revert_enabled": False,
            "export_enabled": False,
            "apply_enabled": False,
            "delete_enabled": False,
            "raw_evidence_visible": False,
        },
        "compare_pairs": compare_pairs,
        "compare_rows": compare_rows,
        "compare_rows_by_pair": rows_by_pair,
        "compare_summary_cards": summary_cards,
        "navigation_cards": _navigation_cards(),
        "compare_controls": {
            "left_version_selector_enabled": True,
            "right_version_selector_enabled": True,
            "compare_button_enabled": True,
            "restore_left_button_visible": True,
            "restore_left_button_enabled": False,
            "restore_right_button_visible": True,
            "restore_right_button_enabled": False,
            "revert_button_visible": True,
            "revert_button_enabled": False,
            "export_compare_button_visible": True,
            "export_compare_button_enabled": False,
            "control_mode": "preview_only",
        },
        "safety_invariants": {
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
            "all_compare_rows_non_executable": all(row["executable"] is False for row in compare_rows),
            "all_compare_pairs_non_executable": all(pair["executable"] is False for pair in compare_pairs),
            "cached_non_recursive_builder": True,
        },
        "blocked_action_matrix": _blocked_action_matrix(),
        "route_contract": {
            "method": "GET",
            "returns_json": True,
            "requires_tower_guard": True,
            "unguarded_high_risk_allowed": False,
        },
        "pack_219b_acceptance": {
            "compare_pairs_built": True,
            "compare_rows_built": True,
            "summary_cards_built": True,
            "redaction_boundary_verified": True,
            "restore_revert_export_blocked": True,
            "ready_for_compare_filter_navigation": True,
        },
        NEXT_PREP_FLAG: {
            "pack": "219C",
            "name": "Receipt Chain Saved View Compare Filter Navigation Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-compare-filter-navigation-v219c.json",
        },
        SAFE_TO_CONTINUE_FLAG: True,
    }

    return preview


def build_receipt_chain_saved_view_version_compare_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 219B preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_version_compare_preview_cached())


def build_pack_219b_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_version_compare_preview_cached()
    summary = preview["version_compare_summary"]

    return {
        "pack": preview["pack"],
        "pack_name": preview["pack_name"],
        "status": preview["status"],
        "readiness": preview["readiness"],
        "endpoint": preview["endpoint"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "source_pack": preview["source_pack"],
        "source_status": preview["source_status"],
        "compare_pair_count": summary["compare_pair_count"],
        "compare_row_count": summary["compare_row_count"],
        "summary_card_count": summary["summary_card_count"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_219C_saved_view_compare_filter_navigation() -> Dict[str, Any]:
    """Prepare the next preview-only pack direction without writing state."""
    return {
        "ready": True,
        "next_pack": "219C",
        "name": "Receipt Chain Saved View Compare Filter Navigation Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "blocked_real_actions": list(BLOCKED_REAL_ACTIONS),
        "safe_to_continue": True,
    }


__all__ = [
    "PACK_ID",
    "PACK_NAME",
    "ENDPOINT",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_version_compare_preview",
    "build_pack_219b_status_bridge",
    "prepare_pack_219C_saved_view_compare_filter_navigation",
]
