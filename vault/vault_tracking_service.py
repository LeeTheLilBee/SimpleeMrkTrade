"""Vault Giant Pack 007 Search + Requirement Tracker + Expiration Wall.

This pack adds the operational tracking layer over the six-lane Vault foundation:
- global searchable record index
- requirement tracker
- expiration / renewal wall
- data freshness wall
- blocked reason tracker
- Clouds-safe tracking source

Boundary:
Vault can index, track, summarize, and route. Vault still does not unlock direct
upload, own Tower permissions, expose sensitive fields, approve legal/financial
items, or publish proof.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_acquisition_service import (
    get_apartment_lender_builder_payload,
    get_atm_route_builder_payload,
)
from .vault_command_center_service import get_unified_vault_command_center_payload
from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_room_service import get_document_drawer_payload, get_packet_board_payload
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard
from .vault_soulaana_beta_service import (
    get_private_beta_onboarding_vault_payload,
    get_soulaana_artist_ip_vault_payload,
)
from .vault_trust_ob_service import (
    get_ob_manual_live_proof_vault_payload,
    get_trust_entity_vault_payload,
)


def _record(
    record_id: str,
    title: str,
    record_type: str,
    lane: str,
    source_route: str,
    status: str,
    sensitivity: str,
    summary: str,
    next_action: str,
    freshness_days: int = 30,
    expires_at: str = "not_set",
    blocked_reasons: List[str] | None = None,
) -> Dict[str, Any]:
    blocked_reasons = blocked_reasons or []
    searchable_text = " ".join(
        [
            record_id,
            title,
            record_type,
            lane,
            source_route,
            status,
            sensitivity,
            summary,
            next_action,
            " ".join(blocked_reasons),
        ]
    ).lower()

    return {
        "record_id": record_id,
        "title": title,
        "record_type": record_type,
        "business_lane": lane,
        "owning_app": "archive_vault",
        "source_route": source_route,
        "status": status,
        "sensitivity": sensitivity,
        "summary": summary,
        "next_action": next_action,
        "freshness_days": freshness_days,
        "expires_at": expires_at,
        "blocked_reasons": blocked_reasons,
        "searchable_text": searchable_text,
        "tower_guard_required": True,
        "redacted_view_default": True,
        "direct_upload_allowed": False,
        "clouds_safe": True,
    }


def _build_search_records() -> List[Dict[str, Any]]:
    command = get_unified_vault_command_center_payload()
    packet_board = get_packet_board_payload()
    drawer = get_document_drawer_payload()
    atm = get_atm_route_builder_payload()["builder"]
    apartment = get_apartment_lender_builder_payload()["builder"]
    trust = get_trust_entity_vault_payload()
    ob = get_ob_manual_live_proof_vault_payload()
    soulaana = get_soulaana_artist_ip_vault_payload()
    beta = get_private_beta_onboarding_vault_payload()

    records: List[Dict[str, Any]] = []

    for lane in command["lane_cards"]:
        records.append(
            _record(
                record_id=f"lane_{lane['lane_id']}",
                title=lane["label"],
                record_type="lane_card",
                lane=lane["lane_id"],
                source_route=lane["source_route"],
                status=lane["status"],
                sensitivity=lane["sensitivity"],
                summary=f"{lane['label']} setup score {lane['setup_score']} with {lane['record_count']} tracked records.",
                next_action=lane["owner_focus"],
                blocked_reasons=lane["blocked_reasons"],
            )
        )

    for card in packet_board["cards"]:
        records.append(
            _record(
                record_id=card["packet_id"],
                title=card["packet_name"],
                record_type="packet_template",
                lane=card["business_lane"],
                source_route="/vault/packet-board.json",
                status=card["setup_status"],
                sensitivity="high" if card["business_lane"] in {"atm", "property", "trust"} else "restricted",
                summary=card["purpose"],
                next_action=card["owner_next_action"],
                blocked_reasons=["direct_upload_locked"] if not card["direct_upload_allowed"] else [],
            )
        )

    for doc in drawer["records"]:
        records.append(
            _record(
                record_id=doc["document_id"],
                title=doc["title"],
                record_type="document_index",
                lane=doc["business_lane"],
                source_route="/vault/document-drawer.json",
                status=doc["status"],
                sensitivity=doc["sensitivity"],
                summary=doc["summary"],
                next_action=doc["next_action"],
                freshness_days=doc["freshness_days"],
                blocked_reasons=["direct_upload_locked", "redaction_required"],
            )
        )

    for req in atm["required_documents"]:
        records.append(
            _record(
                record_id=req["requirement_id"],
                title=req["label"],
                record_type="requirement",
                lane="atm",
                source_route="/vault/atm-route-builder.json",
                status=req["status"],
                sensitivity="high",
                summary=req["notes"],
                next_action="Attach evidence after target selection and Tower storage clearance.",
                freshness_days=30,
                blocked_reasons=[req["blocked_reason"]],
            )
        )

    for req in apartment["required_documents"]:
        records.append(
            _record(
                record_id=req["requirement_id"],
                title=req["label"],
                record_type="requirement",
                lane="property",
                source_route="/vault/apartment-lender-builder.json",
                status=req["status"],
                sensitivity="high",
                summary=req["notes"],
                next_action="Attach evidence after property target selection and Tower storage clearance.",
                freshness_days=30,
                blocked_reasons=[req["blocked_reason"]],
            )
        )

    for doc in trust["documents"]:
        records.append(
            _record(
                record_id=doc["document_id"],
                title=doc["label"],
                record_type="trust_entity_document",
                lane="trust",
                source_route="/vault/trust-entity-vault.json",
                status=doc["status"],
                sensitivity=doc["sensitivity"],
                summary=doc["summary"],
                next_action="Keep indexed and redacted until Tower storage clearance.",
                freshness_days=doc["freshness_days"],
                blocked_reasons=[doc["blocked_reason"]],
            )
        )

    for proof in ob["proof_documents"]:
        records.append(
            _record(
                record_id=proof["proof_id"],
                title=proof["label"],
                record_type="ob_manual_live_proof",
                lane="observatory",
                source_route="/vault/ob-manual-live-proof-vault.json",
                status=proof["status"],
                sensitivity=proof["sensitivity"],
                summary=proof["summary"],
                next_action="Link real Manual Live receipts when owner-reviewed records begin.",
                freshness_days=7,
                blocked_reasons=proof["blocked_fields"],
            )
        )

    for slot in soulaana["reserved_art_slots"]:
        records.append(
            _record(
                record_id=slot["slot_id"],
                title=slot["label"],
                record_type="soulaana_reserved_art_slot",
                lane="soulaana",
                source_route="/vault/soulaana-artist-ip-vault.json",
                status=slot["status"],
                sensitivity=slot["sensitivity"],
                summary=slot["summary"],
                next_action="Use placeholder/reserved slot until human artist delivery is accepted.",
                freshness_days=180,
                blocked_reasons=[slot["blocked_asset_state"]],
            )
        )

    for record_item in soulaana["package_records"]:
        records.append(
            _record(
                record_id=record_item["record_id"],
                title=record_item["label"],
                record_type="soulaana_package_record",
                lane="soulaana",
                source_route="/vault/soulaana-artist-ip-vault.json",
                status=record_item["status"],
                sensitivity=record_item["sensitivity"],
                summary=record_item["summary"],
                next_action="Preserve package record and receipt chain.",
                freshness_days=180,
                blocked_reasons=[record_item["blocked_reason"]],
            )
        )

    for beta_record in beta["onboarding_records"]:
        records.append(
            _record(
                record_id=beta_record["record_id"],
                title=beta_record["label"],
                record_type="beta_onboarding_record",
                lane="beta",
                source_route="/vault/private-beta-onboarding-vault.json",
                status=beta_record["status"],
                sensitivity=beta_record["sensitivity"],
                summary=beta_record["summary"],
                next_action="Use when private beta tester onboarding starts; Tower grants access.",
                freshness_days=60,
                blocked_reasons=[beta_record["blocked_reason"]],
            )
        )

    return records


def get_vault_search_index_payload() -> Dict[str, Any]:
    records = _build_search_records()
    lanes = sorted({record["business_lane"] for record in records})
    types = sorted({record["record_type"] for record in records})

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_search_index",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "record_count": len(records),
        "records": records,
        "search_fields": [
            "record_id",
            "title",
            "record_type",
            "business_lane",
            "status",
            "sensitivity",
            "summary",
            "next_action",
            "blocked_reasons",
        ],
        "filters": {
            "lanes": lanes,
            "record_types": types,
            "sensitivity": sorted({record["sensitivity"] for record in records}),
            "status": sorted({record["status"] for record in records}),
        },
        "boundary": {
            "summary_only": True,
            "redacted_view_default": True,
            "direct_upload_allowed": False,
            "tower_guard_required": True,
        },
    }
    return attach_tower_guard(payload, "/vault/search-index.json")


def _requirement(
    requirement_id: str,
    label: str,
    lane: str,
    source_route: str,
    required: bool,
    status: str,
    blocked_reason: str,
    readiness_weight: int,
    evidence_attached: bool = False,
    expires_at: str = "not_set",
    renewal_window_days: int = 30,
) -> Dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "business_lane": lane,
        "source_route": source_route,
        "required": required,
        "status": status,
        "blocked_reason": blocked_reason,
        "readiness_weight": readiness_weight,
        "evidence_attached": evidence_attached,
        "expires_at": expires_at,
        "renewal_window_days": renewal_window_days,
        "tower_guard_required": True,
        "direct_upload_allowed": False,
        "redacted_view_default": True,
    }


def _build_requirements() -> List[Dict[str, Any]]:
    atm = get_atm_route_builder_payload()["builder"]
    apartment = get_apartment_lender_builder_payload()["builder"]
    trust = get_trust_entity_vault_payload()
    ob = get_ob_manual_live_proof_vault_payload()
    soulaana = get_soulaana_artist_ip_vault_payload()
    beta = get_private_beta_onboarding_vault_payload()

    requirements: List[Dict[str, Any]] = []

    for req in atm["required_documents"]:
        requirements.append(
            _requirement(
                requirement_id=req["requirement_id"],
                label=req["label"],
                lane="atm",
                source_route="/vault/atm-route-builder.json",
                required=req["required"],
                status=req["status"],
                blocked_reason=req["blocked_reason"],
                readiness_weight=req["readiness_weight"],
                renewal_window_days=30,
            )
        )

    for req in apartment["required_documents"]:
        requirements.append(
            _requirement(
                requirement_id=req["requirement_id"],
                label=req["label"],
                lane="property",
                source_route="/vault/apartment-lender-builder.json",
                required=req["required"],
                status=req["status"],
                blocked_reason=req["blocked_reason"],
                readiness_weight=req["readiness_weight"],
                renewal_window_days=30,
            )
        )

    for doc in trust["documents"]:
        requirements.append(
            _requirement(
                requirement_id=doc["document_id"],
                label=doc["label"],
                lane="trust",
                source_route="/vault/trust-entity-vault.json",
                required=doc["required"],
                status=doc["status"],
                blocked_reason=doc["blocked_reason"],
                readiness_weight=10,
                renewal_window_days=doc["freshness_days"],
            )
        )

    for proof in ob["proof_documents"]:
        requirements.append(
            _requirement(
                requirement_id=proof["proof_id"],
                label=proof["label"],
                lane="observatory",
                source_route="/vault/ob-manual-live-proof-vault.json",
                required=proof["required"],
                status=proof["status"],
                blocked_reason="manual_live_receipt_pending",
                readiness_weight=10,
                renewal_window_days=7,
            )
        )

    for record in soulaana["package_records"]:
        requirements.append(
            _requirement(
                requirement_id=record["record_id"],
                label=record["label"],
                lane="soulaana",
                source_route="/vault/soulaana-artist-ip-vault.json",
                required=record["required"],
                status=record["status"],
                blocked_reason=record["blocked_reason"],
                readiness_weight=10,
                renewal_window_days=180,
            )
        )

    for record in beta["onboarding_records"]:
        requirements.append(
            _requirement(
                requirement_id=record["record_id"],
                label=record["label"],
                lane="beta",
                source_route="/vault/private-beta-onboarding-vault.json",
                required=record["required"],
                status=record["status"],
                blocked_reason=record["blocked_reason"],
                readiness_weight=10,
                renewal_window_days=60,
            )
        )

    return requirements


def get_requirement_tracker_payload() -> Dict[str, Any]:
    requirements = _build_requirements()
    required_count = sum(1 for item in requirements if item["required"])
    attached_count = sum(1 for item in requirements if item["evidence_attached"])
    blocked_count = sum(1 for item in requirements if item["blocked_reason"] not in {"none", ""})

    lane_summary = {}
    for item in requirements:
        lane = item["business_lane"]
        lane_summary.setdefault(lane, {"required": 0, "attached": 0, "blocked": 0})
        lane_summary[lane]["required"] += 1 if item["required"] else 0
        lane_summary[lane]["attached"] += 1 if item["evidence_attached"] else 0
        lane_summary[lane]["blocked"] += 1 if item["blocked_reason"] not in {"none", ""} else 0

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "requirement_tracker",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "requirement_count": len(requirements),
        "required_count": required_count,
        "evidence_attached_count": attached_count,
        "blocked_count": blocked_count,
        "packet_completion_score": int(round((attached_count / required_count) * 100)) if required_count else 0,
        "setup_score": 100,
        "requirements": requirements,
        "lane_summary": lane_summary,
        "boundary": {
            "requirements_can_be_tracked": True,
            "raw_files_can_be_uploaded": False,
            "tower_storage_clearance_required": True,
        },
    }
    return attach_tower_guard(payload, "/vault/requirement-tracker.json")


def get_expiration_renewal_wall_payload() -> Dict[str, Any]:
    requirements = _build_requirements()
    renewal_items = []

    for item in requirements:
        renewal_items.append(
            {
                "renewal_id": f"renewal_{item['requirement_id']}",
                "label": item["label"],
                "business_lane": item["business_lane"],
                "source_route": item["source_route"],
                "expires_at": item["expires_at"],
                "renewal_window_days": item["renewal_window_days"],
                "status": "expiration_not_set",
                "owner_action": "Set expiration/renewal date when real evidence is attached.",
                "blocked_reason": "evidence_not_attached",
                "tower_guard_required": True,
                "direct_upload_allowed": False,
            }
        )

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "expiration_renewal_wall",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "renewal_item_count": len(renewal_items),
        "expired_count": 0,
        "expiring_soon_count": 0,
        "expiration_not_set_count": len(renewal_items),
        "renewal_items": renewal_items,
        "renewal_policy": {
            "atm_documents_days": 30,
            "property_due_diligence_days": 30,
            "ob_manual_live_proof_days": 7,
            "trust_entity_documents_days": 365,
            "soulaana_ip_records_days": 180,
            "beta_onboarding_records_days": 60,
        },
    }
    return attach_tower_guard(payload, "/vault/expiration-renewal-wall.json")


def get_data_freshness_wall_payload() -> Dict[str, Any]:
    freshness_lanes = [
        {"lane": "atm", "label": "ATM route acquisition", "freshness_days": 30, "status": "standard_ready"},
        {"lane": "property", "label": "Apartment due diligence", "freshness_days": 30, "status": "standard_ready"},
        {"lane": "trust", "label": "Trust/entity records", "freshness_days": 365, "status": "standard_ready"},
        {"lane": "observatory", "label": "OB Manual Live proof", "freshness_days": 7, "status": "standard_ready"},
        {"lane": "soulaana", "label": "Soulaana Artist/IP", "freshness_days": 180, "status": "standard_ready"},
        {"lane": "beta", "label": "Private beta onboarding", "freshness_days": 60, "status": "standard_ready"},
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "data_freshness_wall",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "lane_count": len(freshness_lanes),
        "freshness_lanes": freshness_lanes,
        "standard": {
            "freshness_required": True,
            "stale_records_need_owner_attention": True,
            "clouds_gets_staleness_summary_only": True,
            "tower_guard_required_for_sensitive_refresh": True,
        },
    }
    return attach_tower_guard(payload, "/vault/data-freshness-wall.json")


def get_vault_search_tracker_payload() -> Dict[str, Any]:
    search = get_vault_search_index_payload()
    requirements = get_requirement_tracker_payload()
    renewals = get_expiration_renewal_wall_payload()
    freshness = get_data_freshness_wall_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_search_tracker",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "room_label": "Vault Search + Requirement Tracker",
        "status": "ready",
        "search_index": {
            "record_count": search["record_count"],
            "filters": search["filters"],
            "search_fields": search["search_fields"],
        },
        "requirement_tracker": {
            "requirement_count": requirements["requirement_count"],
            "required_count": requirements["required_count"],
            "blocked_count": requirements["blocked_count"],
            "packet_completion_score": requirements["packet_completion_score"],
            "setup_score": requirements["setup_score"],
            "lane_summary": requirements["lane_summary"],
        },
        "expiration_renewal_wall": {
            "renewal_item_count": renewals["renewal_item_count"],
            "expired_count": renewals["expired_count"],
            "expiring_soon_count": renewals["expiring_soon_count"],
            "expiration_not_set_count": renewals["expiration_not_set_count"],
        },
        "data_freshness_wall": {
            "lane_count": freshness["lane_count"],
            "freshness_lanes": freshness["freshness_lanes"],
        },
        "boundary": {
            "tower_guard_required": True,
            "direct_upload_allowed": False,
            "redacted_view_default": True,
            "clouds_view": "summary_only_redacted",
            "search_reveals_sensitive_body": False,
        },
        "clouds_safe_source": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "record_count": search["record_count"],
            "requirement_count": requirements["requirement_count"],
            "blocked_count": requirements["blocked_count"],
            "renewal_item_count": renewals["renewal_item_count"],
            "freshness_lane_count": freshness["lane_count"],
            "hidden_sensitive_fields": REDACTION_POLICY["sensitive_fields"],
            "blocked_reasons": NO_DIRECT_UPLOAD_POLICY["blocked_now"],
        },
        "next_pack_recommendation": "Vault Giant Pack 008 should build Vault Receipt Chain Console + Freeze/Revoke/Undo Wall.",
    }
    return attach_tower_guard(payload, "/vault/search-tracker.json")


def get_vault_gp007_status_payload() -> Dict[str, Any]:
    tracker = get_vault_search_tracker_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp007_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 007",
        "built": [
            "vault_search_index",
            "requirement_tracker",
            "expiration_renewal_wall",
            "data_freshness_wall",
            "blocked_reason_tracker",
            "clouds_safe_tracking_source",
            "search_tracker_ui",
            "gp007_status_endpoint",
        ],
        "search_record_count": tracker["search_index"]["record_count"],
        "requirement_count": tracker["requirement_tracker"]["requirement_count"],
        "blocked_requirement_count": tracker["requirement_tracker"]["blocked_count"],
        "renewal_item_count": tracker["expiration_renewal_wall"]["renewal_item_count"],
        "freshness_lane_count": tracker["data_freshness_wall"]["lane_count"],
        "direct_upload_allowed": False,
        "clouds_safe": tracker["clouds_safe_source"]["safe_for_clouds"],
        "safe_to_continue_to_gp008": True,
    }
    return attach_tower_guard(payload, "/vault/gp007-status.json")
