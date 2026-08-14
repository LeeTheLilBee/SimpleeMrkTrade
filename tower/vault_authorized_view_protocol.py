"""
THE TOWER
GP471–GP480
TOWER AUTHORIZED VIEW PROTOCOL

Locked doctrine:
    Tower is the face.
    Teller is the workflow.
    Vault is the sealed memory.

Key rule:
    Teller can ask.
    Tower must decide.
    Vault only answers Tower.

This module prepares Tower-controlled view-only protocol requests for Vault.

It does not:
    - expose raw Vault links
    - expose raw Vault files
    - create public links
    - create shared folders
    - create download access
    - allow Teller to call Vault
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Mapping, Optional


PACK_ID = "GP471-GP480"
PACK_TITLE = "TOWER AUTHORIZED VIEW PROTOCOL"
DOCTRINE = "Teller can ask. Tower must decide. Vault only answers Tower."


FORBIDDEN_RAW_VAULT_FIELDS = {
    "vault_url",
    "vault_link",
    "raw_vault_url",
    "raw_file_url",
    "download_url",
    "preview_url",
    "shared_folder_url",
    "external_collaborator_link",
    "vault_file_path",
    "vault_object_key",
    "vault_storage_bucket",
    "vault_raw_payload",
    "vault_secret",
    "vault_token",
    "public_link",
    "signed_url",
    "temporary_url",
}


VIEW_ALLOWED_PROTOCOL_ACTIONS = {
    "request_authorized_view_prep",
    "request_status",
    "request_proof",
    "request_receipt",
}


class TowerAuthorizedViewDecision(str, Enum):
    VIEW_PREPARED = "view_prepared"
    VIEW_PREPARED_REDACTED = "view_prepared_redacted"
    BLOCKED = "blocked"
    NOT_VIEW_PROTOCOL = "not_view_protocol"
    INVALID_PROTOCOL_REQUEST = "invalid_protocol_request"
    DOWNLOAD_NOT_ALLOWED_IN_VIEW_PROTOCOL = "download_not_allowed_in_view_protocol"
    RAW_VAULT_EXPOSURE_BLOCKED = "raw_vault_exposure_blocked"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def receipt_hash(prefix: str, payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def nested_forbidden_hits(value: Any, path: str = "") -> List[str]:
    hits: List[str] = []

    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            lowered_key = str(key).lower()

            if lowered_key in FORBIDDEN_RAW_VAULT_FIELDS:
                hits.append(child_path)

            hits.extend(nested_forbidden_hits(child, child_path))

    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(nested_forbidden_hits(child, f"{path}[{index}]"))

    elif isinstance(value, str):
        lowered = value.lower()
        if (
            "vault://" in lowered
            or "raw_file_url" in lowered
            or "download_url" in lowered
            or "preview_url" in lowered
            or "signed_url" in lowered
            or "temporary_url" in lowered
            or "shared_folder" in lowered
            or "public-link" in lowered
        ):
            hits.append(path or "value")

    return sorted(set(hits))


def assert_no_raw_vault_exposure(value: Any, label: str = "payload") -> bool:
    hits = nested_forbidden_hits(value)
    if hits:
        raise ValueError(f"{label} contains forbidden raw Vault exposure: {', '.join(hits)}")
    return True


@dataclass(frozen=True)
class TowerAuthorizedViewScope:
    view_scope_id: str
    originating_teller_request_id: str
    tower_protocol_request_id: str
    tower_decision_receipt_id: str
    requested_output_type: str
    protocol_action: str
    workflow_type: str
    document_or_proof_type: str
    subject_person_or_vendor: str
    business_context: str
    sensitivity_level: str
    redaction_required: bool
    view_mode: str
    max_view_seconds: int
    copy_allowed: bool
    print_allowed: bool
    download_allowed: bool
    raw_links_allowed: bool
    raw_files_allowed_for_teller: bool
    teller_direct_vault_access_allowed: bool
    vault_answers_tower_only: bool
    created_at: str


@dataclass(frozen=True)
class TowerVaultAuthorizedViewRequest:
    authorized_view_request_id: str
    source_app: str
    target_app: str
    request_kind: str
    originating_teller_request_id: str
    tower_protocol_request_id: str
    tower_decision_receipt_id: str
    vault_view_scope_id: str
    requested_vault_output: str
    document_or_proof_type: str
    subject_person_or_vendor: str
    business_context: str
    redaction_required: bool
    view_only: bool
    download_allowed: bool
    raw_links_allowed: bool
    public_links_allowed: bool
    shared_folder_allowed: bool
    vault_answers_tower_only: bool
    teller_direct_vault_access_allowed: bool
    created_at: str


@dataclass(frozen=True)
class TowerAuthorizedViewSafeReturnForTeller:
    request_id: str
    status: str
    display_status: str
    workflow_safe_summary: str
    workflow_safe_receipt_id: str
    tower_decision_receipt_id: str
    authorized_view_receipt_id: str
    vault_proof_reference_safe_label: str
    redaction_applied: bool
    next_teller_action: str
    final_for_teller: bool
    safe_to_display_to_requester: bool
    vault_direct_access_allowed: bool = False
    raw_files_included: bool = False
    raw_links_included: bool = False
    download_available: bool = False
    returned_at: str = field(default_factory=utc_now)


def validate_protocol_request(protocol_request: Mapping[str, Any]) -> List[str]:
    problems: List[str] = []

    required = [
        "protocol_request_id",
        "source_app",
        "target_app",
        "originating_teller_request_id",
        "protocol_action",
        "workflow_type",
        "document_or_proof_type",
        "subject_person_or_vendor",
        "business_context",
        "requested_output_type",
        "sensitivity_level",
        "tower_decision_receipt_id",
        "redaction_required",
        "vault_answers_tower_only",
        "teller_direct_vault_access_allowed",
        "raw_links_allowed",
        "raw_files_allowed_for_teller",
    ]

    missing = [
        field_name
        for field_name in required
        if field_name not in protocol_request or protocol_request.get(field_name) in (None, "")
    ]

    if missing:
        problems.append(f"missing required fields: {', '.join(missing)}")

    if protocol_request.get("source_app") != "tower":
        problems.append("source_app must be tower")

    if protocol_request.get("target_app") != "vault":
        problems.append("target_app must be vault")

    if protocol_request.get("vault_answers_tower_only") is not True:
        problems.append("vault_answers_tower_only must be true")

    if protocol_request.get("teller_direct_vault_access_allowed") is not False:
        problems.append("teller_direct_vault_access_allowed must be false")

    if protocol_request.get("raw_links_allowed") is not False:
        problems.append("raw_links_allowed must be false")

    if protocol_request.get("raw_files_allowed_for_teller") is not False:
        problems.append("raw_files_allowed_for_teller must be false")

    protocol_action = str(protocol_request.get("protocol_action", ""))

    if protocol_action == "request_authorized_download_prep":
        problems.append("download prep is not allowed in GP471-GP480 authorized view protocol")

    if protocol_action not in VIEW_ALLOWED_PROTOCOL_ACTIONS and protocol_action != "request_authorized_download_prep":
        problems.append(f"unsupported protocol_action for authorized view: {protocol_action}")

    forbidden_hits = nested_forbidden_hits(protocol_request)
    if forbidden_hits:
        problems.append(f"raw Vault exposure blocked: {', '.join(forbidden_hits)}")

    return problems


def create_authorized_view_scope(protocol_request: Mapping[str, Any]) -> TowerAuthorizedViewScope:
    assert_no_raw_vault_exposure(protocol_request, "Tower Vault protocol request before view scope")

    problems = validate_protocol_request(protocol_request)
    if problems:
        raise ValueError("Invalid protocol request for authorized view: " + " | ".join(problems))

    payload_for_scope = {
        "pack_id": PACK_ID,
        "originating_teller_request_id": protocol_request["originating_teller_request_id"],
        "tower_protocol_request_id": protocol_request["protocol_request_id"],
        "tower_decision_receipt_id": protocol_request["tower_decision_receipt_id"],
        "created_at": utc_now(),
    }

    redaction_required = bool(protocol_request.get("redaction_required", True))

    scope = TowerAuthorizedViewScope(
        view_scope_id=receipt_hash("tower-vault-view-scope", payload_for_scope),
        originating_teller_request_id=str(protocol_request["originating_teller_request_id"]),
        tower_protocol_request_id=str(protocol_request["protocol_request_id"]),
        tower_decision_receipt_id=str(protocol_request["tower_decision_receipt_id"]),
        requested_output_type=str(protocol_request["requested_output_type"]),
        protocol_action=str(protocol_request["protocol_action"]),
        workflow_type=str(protocol_request["workflow_type"]),
        document_or_proof_type=str(protocol_request["document_or_proof_type"]),
        subject_person_or_vendor=str(protocol_request["subject_person_or_vendor"]),
        business_context=str(protocol_request["business_context"]),
        sensitivity_level=str(protocol_request["sensitivity_level"]),
        redaction_required=redaction_required,
        view_mode="tower_controlled_redacted_view" if redaction_required else "tower_controlled_view",
        max_view_seconds=300,
        copy_allowed=False,
        print_allowed=False,
        download_allowed=False,
        raw_links_allowed=False,
        raw_files_allowed_for_teller=False,
        teller_direct_vault_access_allowed=False,
        vault_answers_tower_only=True,
        created_at=utc_now(),
    )

    assert_no_raw_vault_exposure(asdict(scope), "Tower authorized view scope")

    return scope


def create_vault_authorized_view_request(
    protocol_request: Mapping[str, Any],
    view_scope: TowerAuthorizedViewScope,
) -> TowerVaultAuthorizedViewRequest:
    assert_no_raw_vault_exposure(protocol_request, "Protocol request before authorized view request")
    assert_no_raw_vault_exposure(asdict(view_scope), "View scope before authorized view request")

    payload_for_request = {
        "pack_id": PACK_ID,
        "view_scope_id": view_scope.view_scope_id,
        "tower_protocol_request_id": view_scope.tower_protocol_request_id,
        "tower_decision_receipt_id": view_scope.tower_decision_receipt_id,
        "created_at": utc_now(),
    }

    request = TowerVaultAuthorizedViewRequest(
        authorized_view_request_id=receipt_hash("tower-vault-authorized-view", payload_for_request),
        source_app="tower",
        target_app="vault",
        request_kind="authorized_view_only",
        originating_teller_request_id=view_scope.originating_teller_request_id,
        tower_protocol_request_id=view_scope.tower_protocol_request_id,
        tower_decision_receipt_id=view_scope.tower_decision_receipt_id,
        vault_view_scope_id=view_scope.view_scope_id,
        requested_vault_output="view_safe_redacted_payload"
        if view_scope.redaction_required
        else "view_safe_payload",
        document_or_proof_type=view_scope.document_or_proof_type,
        subject_person_or_vendor=view_scope.subject_person_or_vendor,
        business_context=view_scope.business_context,
        redaction_required=view_scope.redaction_required,
        view_only=True,
        download_allowed=False,
        raw_links_allowed=False,
        public_links_allowed=False,
        shared_folder_allowed=False,
        vault_answers_tower_only=True,
        teller_direct_vault_access_allowed=False,
        created_at=utc_now(),
    )

    assert_no_raw_vault_exposure(asdict(request), "Tower Vault authorized view request")

    return request


def create_view_safe_return_for_teller(
    protocol_request: Mapping[str, Any],
    view_scope: TowerAuthorizedViewScope,
    view_request: TowerVaultAuthorizedViewRequest,
) -> TowerAuthorizedViewSafeReturnForTeller:
    receipt_payload = {
        "pack_id": PACK_ID,
        "originating_teller_request_id": view_scope.originating_teller_request_id,
        "view_scope_id": view_scope.view_scope_id,
        "authorized_view_request_id": view_request.authorized_view_request_id,
        "created_at": utc_now(),
    }

    authorized_view_receipt_id = receipt_hash("tower-view-safe-return", receipt_payload)

    safe_return = TowerAuthorizedViewSafeReturnForTeller(
        request_id=view_scope.originating_teller_request_id,
        status=TowerAuthorizedViewDecision.VIEW_PREPARED_REDACTED.value
        if view_scope.redaction_required
        else TowerAuthorizedViewDecision.VIEW_PREPARED.value,
        display_status="Tower prepared an authorized view request for Vault.",
        workflow_safe_summary=(
            "Tower prepared a view-only Vault request. Vault access remains Tower-controlled. "
            "No raw Vault file, raw link, public link, shared folder, or download access is exposed to Teller."
        ),
        workflow_safe_receipt_id=authorized_view_receipt_id,
        tower_decision_receipt_id=view_scope.tower_decision_receipt_id,
        authorized_view_receipt_id=authorized_view_receipt_id,
        vault_proof_reference_safe_label=(
            "Vault view request prepared by Tower; result will return to Tower only."
        ),
        redaction_applied=view_scope.redaction_required,
        next_teller_action="wait_for_tower_view_result",
        final_for_teller=False,
        safe_to_display_to_requester=True,
        vault_direct_access_allowed=False,
        raw_files_included=False,
        raw_links_included=False,
        download_available=False,
    )

    assert_no_raw_vault_exposure(asdict(safe_return), "Authorized view safe return for Teller")

    return safe_return


def prepare_tower_authorized_view_protocol(
    gate_result: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Main GP471–GP480 corridor entry point.

    Accepts the GP461-GP470 gate result.
    If the gate did not create a Vault protocol request, this returns a safe blocked result.
    If the protocol request is valid, this prepares a Tower-controlled Vault view request.
    """
    assert_no_raw_vault_exposure(gate_result, "incoming Tower gate result")

    protocol_request = gate_result.get("vault_protocol_request")

    if not protocol_request:
        safe_result = {
            "pack_id": PACK_ID,
            "title": PACK_TITLE,
            "doctrine": DOCTRINE,
            "decision": TowerAuthorizedViewDecision.BLOCKED.value,
            "authorized_view_scope": None,
            "vault_authorized_view_request": None,
            "safe_return_for_teller": {
                "request_id": gate_result.get("safe_return_for_teller", {}).get("request_id", ""),
                "status": TowerAuthorizedViewDecision.BLOCKED.value,
                "display_status": "Tower did not prepare an authorized view because the protocol gate was not allowed.",
                "workflow_safe_summary": "Resolve the Tower gate requirement before requesting Vault view handling.",
                "workflow_safe_receipt_id": receipt_hash("tower-view-blocked", gate_result),
                "tower_decision_receipt_id": gate_result.get("tower_decision", {}).get(
                    "tower_decision_receipt_id",
                    "",
                ),
                "authorized_view_receipt_id": "",
                "vault_proof_reference_safe_label": "No Vault view request was created.",
                "redaction_applied": True,
                "next_teller_action": "resolve_tower_requirement",
                "final_for_teller": False,
                "safe_to_display_to_requester": True,
                "vault_direct_access_allowed": False,
                "raw_files_included": False,
                "raw_links_included": False,
                "download_available": False,
                "returned_at": utc_now(),
            },
            "vault_answers_tower_only": True,
            "teller_direct_vault_access_allowed": False,
            "raw_vault_links_included": False,
            "raw_vault_files_included": False,
            "download_protocol_created": False,
        }

        assert_no_raw_vault_exposure(safe_result, "blocked authorized view result")
        return safe_result

    protocol_action = str(protocol_request.get("protocol_action", ""))

    if protocol_action == "request_authorized_download_prep":
        blocked = {
            "pack_id": PACK_ID,
            "title": PACK_TITLE,
            "doctrine": DOCTRINE,
            "decision": TowerAuthorizedViewDecision.DOWNLOAD_NOT_ALLOWED_IN_VIEW_PROTOCOL.value,
            "authorized_view_scope": None,
            "vault_authorized_view_request": None,
            "safe_return_for_teller": {
                "request_id": protocol_request.get("originating_teller_request_id", ""),
                "status": TowerAuthorizedViewDecision.DOWNLOAD_NOT_ALLOWED_IN_VIEW_PROTOCOL.value,
                "display_status": "Download is not handled by the authorized view protocol.",
                "workflow_safe_summary": "Download handling belongs to GP481-GP490 and remains blocked here.",
                "workflow_safe_receipt_id": receipt_hash("tower-view-download-blocked", protocol_request),
                "tower_decision_receipt_id": protocol_request.get("tower_decision_receipt_id", ""),
                "authorized_view_receipt_id": "",
                "vault_proof_reference_safe_label": "No Vault download or view link was created.",
                "redaction_applied": True,
                "next_teller_action": "wait_for_download_protocol_corridor",
                "final_for_teller": False,
                "safe_to_display_to_requester": True,
                "vault_direct_access_allowed": False,
                "raw_files_included": False,
                "raw_links_included": False,
                "download_available": False,
                "returned_at": utc_now(),
            },
            "vault_answers_tower_only": True,
            "teller_direct_vault_access_allowed": False,
            "raw_vault_links_included": False,
            "raw_vault_files_included": False,
            "download_protocol_created": False,
        }

        assert_no_raw_vault_exposure(blocked, "download blocked authorized view result")
        return blocked

    view_scope = create_authorized_view_scope(protocol_request)
    view_request = create_vault_authorized_view_request(protocol_request, view_scope)
    safe_return = create_view_safe_return_for_teller(protocol_request, view_scope, view_request)

    result = {
        "pack_id": PACK_ID,
        "title": PACK_TITLE,
        "doctrine": DOCTRINE,
        "decision": safe_return.status,
        "authorized_view_scope": asdict(view_scope),
        "vault_authorized_view_request": asdict(view_request),
        "safe_return_for_teller": asdict(safe_return),
        "vault_answers_tower_only": True,
        "teller_direct_vault_access_allowed": False,
        "raw_vault_links_included": False,
        "raw_vault_files_included": False,
        "download_protocol_created": False,
    }

    assert_no_raw_vault_exposure(result, "Tower authorized view protocol result")

    return result


def build_demo_gate_result(
    *,
    protocol_action: str = "request_authorized_view_prep",
    redaction_required: bool = True,
) -> Dict[str, Any]:
    protocol_request = {
        "protocol_request_id": "tower-vault-protocol-demo471",
        "source_app": "tower",
        "target_app": "vault",
        "originating_teller_request_id": "teller_tower_request_demo_gp471",
        "protocol_action": protocol_action,
        "workflow_type": "payment_receipt_request",
        "document_or_proof_type": "payment_receipt",
        "subject_person_or_vendor": "Demo Vendor",
        "business_context": "SimpleePay / Vendor Payment",
        "requester_entity": "SimpleePay",
        "requested_output_type": "preview" if protocol_action == "request_authorized_view_prep" else "receipt",
        "sensitivity_level": "sensitive",
        "tower_actor_id": "tower_actor_demo_001",
        "tower_actor_role": "manager",
        "tower_clearance_level": "payroll_and_payment_workflow",
        "tower_decision_receipt_id": "tower-vault-gate-demo471",
        "redaction_required": redaction_required,
        "vault_answers_tower_only": True,
        "teller_direct_vault_access_allowed": False,
        "raw_links_allowed": False,
        "raw_files_allowed_for_teller": False,
        "created_at": utc_now(),
    }

    gate_result = {
        "pack_id": "GP461-GP470",
        "title": "TOWER VAULT REQUEST PROTOCOL GATE",
        "doctrine": DOCTRINE,
        "tower_decision": {
            "decision": "redacted" if redaction_required else "allowed",
            "allowed": True,
            "tower_decision_receipt_id": "tower-vault-gate-demo471",
            "redaction_required": redaction_required,
        },
        "vault_protocol_request": protocol_request,
        "safe_return_for_teller": {
            "request_id": "teller_tower_request_demo_gp471",
            "status": "redacted" if redaction_required else "allowed",
            "vault_direct_access_allowed": False,
            "raw_files_included": False,
            "raw_links_included": False,
        },
        "teller_direct_vault_access_allowed": False,
        "vault_answers_tower_only": True,
        "raw_vault_links_included": False,
        "raw_vault_files_included": False,
    }

    assert_no_raw_vault_exposure(gate_result, "demo gate result")
    return gate_result


def get_tower_authorized_view_protocol_readiness() -> Dict[str, Any]:
    return {
        "pack_id": PACK_ID,
        "title": PACK_TITLE,
        "doctrine": DOCTRINE,
        "tower_prepares_authorized_view_request": True,
        "view_only_protocol": True,
        "download_protocol_created": False,
        "vault_answers_tower_only": True,
        "teller_direct_vault_access_allowed": False,
        "raw_vault_links_exposed_to_teller": False,
        "raw_vault_files_exposed_to_teller": False,
        "public_links_allowed": False,
        "shared_folders_allowed": False,
        "redaction_scope_carried": True,
        "workflow_safe_return_only": True,
        "ready_for_next_corridor": "GP481-GP490 — Tower Authorized Download Protocol",
    }
