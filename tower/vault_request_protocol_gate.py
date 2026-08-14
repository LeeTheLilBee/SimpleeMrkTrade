"""
THE TOWER
GP461–GP470
TOWER VAULT REQUEST PROTOCOL GATE

Locked doctrine:
    Tower is the face.
    Teller is the workflow.
    Vault is the sealed memory.

Key rule:
    Teller can ask.
    Tower must decide.
    Vault only answers Tower.

This module receives workflow request packets from Teller and creates
Tower-authorized Vault protocol requests when allowed.

It does not expose raw Vault files, raw Vault links, preview URLs,
download URLs, shared folders, or external collaborator access.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Mapping, Optional, Tuple


PACK_ID = "GP461-GP470"
PACK_TITLE = "TOWER VAULT REQUEST PROTOCOL GATE"
DOCTRINE = "Teller can ask. Tower must decide. Vault only answers Tower."


class TowerDecision(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    NEEDS_STEP_UP = "needs_step_up"
    NEEDS_OWNER_APPROVAL = "needs_owner_approval"
    READ_ONLY = "read_only"
    REDACTED = "redacted"
    EXPIRED_CLEARANCE = "expired_clearance"
    ROLE_MISMATCH = "role_mismatch"
    LANE_MISMATCH = "lane_mismatch"
    INVALID_PACKET = "invalid_packet"


class TowerVaultProtocolAction(str, Enum):
    REQUEST_STATUS = "request_status"
    REQUEST_PROOF = "request_proof"
    REQUEST_RECEIPT = "request_receipt"
    REQUEST_AUTHORIZED_VIEW_PREP = "request_authorized_view_prep"
    REQUEST_AUTHORIZED_DOWNLOAD_PREP = "request_authorized_download_prep"


TELLER_ALLOWED_OUTPUT_TO_TOWER_PROTOCOL_ACTION = {
    "status": TowerVaultProtocolAction.REQUEST_STATUS.value,
    "proof": TowerVaultProtocolAction.REQUEST_PROOF.value,
    "receipt": TowerVaultProtocolAction.REQUEST_RECEIPT.value,
    "preview": TowerVaultProtocolAction.REQUEST_AUTHORIZED_VIEW_PREP.value,
    "download": TowerVaultProtocolAction.REQUEST_AUTHORIZED_DOWNLOAD_PREP.value,
}


REQUIRED_TELLER_PACKET_FIELDS = [
    "request_id",
    "source_app",
    "target_app",
    "workflow_type",
    "requester_role",
    "requester_entity",
    "subject_person_or_vendor",
    "document_or_proof_type",
    "reason_for_request",
    "deadline",
    "sensitivity_level",
    "requested_output_type",
    "business_context",
    "teller_workflow_receipt_hash",
    "tower_approval_required",
    "vault_direct_access_allowed",
]


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
}


SENSITIVE_LEVELS_REQUIRING_STEP_UP = {"sensitive", "owner_only"}
SENSITIVE_LEVELS_REQUIRING_OWNER = {"owner_only"}
OUTPUT_TYPES_REQUIRING_STEP_UP = {"preview", "download"}
OUTPUT_TYPES_REQUIRING_OWNER = {"download"}


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
class TowerActorContext:
    actor_id: str
    role: str
    entity: str
    clearance_active: bool
    clearance_level: str = "standard"
    step_up_active: bool = False
    owner_approval_active: bool = False
    allowed_entities: Tuple[str, ...] = field(default_factory=tuple)
    allowed_roles: Tuple[str, ...] = field(default_factory=tuple)
    allowed_business_contexts: Tuple[str, ...] = field(default_factory=tuple)
    export_allowed: bool = False
    sensitive_view_allowed: bool = False
    disabled_or_frozen: bool = False


@dataclass(frozen=True)
class TowerVaultGateDecision:
    decision: str
    allowed: bool
    reason: str
    redaction_required: bool
    step_up_required: bool
    owner_approval_required: bool
    read_only: bool
    tower_decision_receipt_id: str
    safe_message_for_teller: str
    created_at: str


@dataclass(frozen=True)
class TowerVaultProtocolRequest:
    protocol_request_id: str
    source_app: str
    target_app: str
    originating_teller_request_id: str
    protocol_action: str
    workflow_type: str
    document_or_proof_type: str
    subject_person_or_vendor: str
    business_context: str
    requester_entity: str
    requested_output_type: str
    sensitivity_level: str
    tower_actor_id: str
    tower_actor_role: str
    tower_clearance_level: str
    tower_decision_receipt_id: str
    redaction_required: bool
    vault_answers_tower_only: bool
    teller_direct_vault_access_allowed: bool
    raw_links_allowed: bool
    raw_files_allowed_for_teller: bool
    created_at: str


@dataclass(frozen=True)
class TowerWorkflowSafeReturnForTeller:
    request_id: str
    status: str
    allowed_output_type: str
    display_status: str
    workflow_safe_summary: str
    workflow_safe_receipt_id: str
    redaction_applied: bool
    tower_decision_receipt_id: str
    vault_proof_reference_safe_label: str
    next_teller_action: str
    final_for_teller: bool
    safe_to_display_to_requester: bool
    vault_direct_access_allowed: bool = False
    raw_files_included: bool = False
    raw_links_included: bool = False
    returned_at: str = field(default_factory=utc_now)


def validate_teller_packet(packet: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    problems: List[str] = []

    missing = [
        field_name
        for field_name in REQUIRED_TELLER_PACKET_FIELDS
        if field_name not in packet or packet.get(field_name) in (None, "")
    ]

    if missing:
        problems.append(f"missing required fields: {', '.join(missing)}")

    if packet.get("source_app") != "teller":
        problems.append("source_app must be teller")

    if packet.get("target_app") != "tower":
        problems.append("target_app must be tower")

    if packet.get("tower_approval_required") is not True:
        problems.append("tower_approval_required must be true")

    if packet.get("vault_direct_access_allowed") is not False:
        problems.append("vault_direct_access_allowed must be false")

    if packet.get("vault_answers_tower_only") is not True:
        problems.append("vault_answers_tower_only must be true")

    requested_output_type = str(packet.get("requested_output_type", ""))
    if requested_output_type not in TELLER_ALLOWED_OUTPUT_TO_TOWER_PROTOCOL_ACTION:
        problems.append(f"unsupported requested_output_type: {requested_output_type}")

    forbidden_hits = nested_forbidden_hits(packet)
    if forbidden_hits:
        problems.append(f"packet includes forbidden raw Vault exposure: {', '.join(forbidden_hits)}")

    return len(problems) == 0, problems


def _contains_allowed_value(value: str, allowed_values: Tuple[str, ...]) -> bool:
    if not allowed_values:
        return True

    lowered_value = value.lower()
    lowered_allowed = tuple(item.lower() for item in allowed_values)

    return lowered_value in lowered_allowed or any(
        lowered_value.startswith(item) or item in lowered_value
        for item in lowered_allowed
    )


def evaluate_tower_vault_gate(
    teller_packet: Mapping[str, Any],
    actor_context: TowerActorContext,
) -> TowerVaultGateDecision:
    valid, problems = validate_teller_packet(teller_packet)

    base_for_receipt = {
        "pack_id": PACK_ID,
        "teller_request_id": teller_packet.get("request_id"),
        "actor_id": actor_context.actor_id,
        "actor_role": actor_context.role,
        "requested_output_type": teller_packet.get("requested_output_type"),
        "sensitivity_level": teller_packet.get("sensitivity_level"),
        "created_at": utc_now(),
    }

    def make_decision(
        decision: TowerDecision,
        reason: str,
        allowed: bool = False,
        redaction_required: bool = True,
        step_up_required: bool = False,
        owner_approval_required: bool = False,
        read_only: bool = True,
    ) -> TowerVaultGateDecision:
        receipt_payload = {
            **base_for_receipt,
            "decision": decision.value,
            "reason": reason,
            "allowed": allowed,
            "redaction_required": redaction_required,
            "step_up_required": step_up_required,
            "owner_approval_required": owner_approval_required,
            "read_only": read_only,
        }

        return TowerVaultGateDecision(
            decision=decision.value,
            allowed=allowed,
            reason=reason,
            redaction_required=redaction_required,
            step_up_required=step_up_required,
            owner_approval_required=owner_approval_required,
            read_only=read_only,
            tower_decision_receipt_id=receipt_hash("tower-vault-gate", receipt_payload),
            safe_message_for_teller=_safe_message(decision, reason),
            created_at=utc_now(),
        )

    if not valid:
        return make_decision(
            TowerDecision.INVALID_PACKET,
            "Teller request packet failed Tower validation: " + " | ".join(problems),
        )

    if actor_context.disabled_or_frozen:
        return make_decision(
            TowerDecision.BLOCKED,
            "Actor is disabled, frozen, or suspended in Tower.",
        )

    if not actor_context.clearance_active:
        return make_decision(
            TowerDecision.EXPIRED_CLEARANCE,
            "Tower clearance is not active.",
        )

    requester_role = str(teller_packet.get("requester_role", ""))
    requester_entity = str(teller_packet.get("requester_entity", ""))
    business_context = str(teller_packet.get("business_context", ""))
    sensitivity_level = str(teller_packet.get("sensitivity_level", ""))
    requested_output_type = str(teller_packet.get("requested_output_type", ""))

    if actor_context.allowed_roles and requester_role not in actor_context.allowed_roles:
        return make_decision(
            TowerDecision.ROLE_MISMATCH,
            f"Requester role {requester_role} is not allowed for this actor context.",
        )

    if actor_context.allowed_entities and requester_entity not in actor_context.allowed_entities:
        return make_decision(
            TowerDecision.LANE_MISMATCH,
            f"Requester entity {requester_entity} is not allowed for this actor context.",
        )

    if not _contains_allowed_value(business_context, actor_context.allowed_business_contexts):
        return make_decision(
            TowerDecision.LANE_MISMATCH,
            f"Business context {business_context} is outside the actor's allowed lanes.",
        )

    step_up_required = (
        sensitivity_level in SENSITIVE_LEVELS_REQUIRING_STEP_UP
        or requested_output_type in OUTPUT_TYPES_REQUIRING_STEP_UP
    )

    owner_approval_required = (
        sensitivity_level in SENSITIVE_LEVELS_REQUIRING_OWNER
        or requested_output_type in OUTPUT_TYPES_REQUIRING_OWNER
    )

    if step_up_required and not actor_context.step_up_active:
        return make_decision(
            TowerDecision.NEEDS_STEP_UP,
            "Tower step-up is required before this Vault protocol request can proceed.",
            step_up_required=True,
            owner_approval_required=owner_approval_required,
        )

    if owner_approval_required and not actor_context.owner_approval_active:
        return make_decision(
            TowerDecision.NEEDS_OWNER_APPROVAL,
            "Owner/admin approval is required before this Vault protocol request can proceed.",
            step_up_required=step_up_required,
            owner_approval_required=True,
        )

    redaction_required = not actor_context.sensitive_view_allowed

    return make_decision(
        TowerDecision.ALLOWED if not redaction_required else TowerDecision.REDACTED,
        "Tower approved a Vault protocol request with workflow-safe restrictions.",
        allowed=True,
        redaction_required=redaction_required,
        step_up_required=step_up_required,
        owner_approval_required=owner_approval_required,
        read_only=True,
    )


def _safe_message(decision: TowerDecision, reason: str) -> str:
    if decision == TowerDecision.ALLOWED:
        return "Tower approved the request for Vault protocol handling."
    if decision == TowerDecision.REDACTED:
        return "Tower approved the request with redaction required."
    if decision == TowerDecision.NEEDS_STEP_UP:
        return "Tower requires step-up before continuing."
    if decision == TowerDecision.NEEDS_OWNER_APPROVAL:
        return "Tower requires owner/admin approval before continuing."
    if decision == TowerDecision.EXPIRED_CLEARANCE:
        return "Tower clearance is expired or inactive."
    if decision == TowerDecision.ROLE_MISMATCH:
        return "Tower blocked the request because the role does not match."
    if decision == TowerDecision.LANE_MISMATCH:
        return "Tower blocked the request because the lane/entity does not match."
    if decision == TowerDecision.INVALID_PACKET:
        return "Tower rejected the request packet because it is invalid."
    if decision == TowerDecision.BLOCKED:
        return "Tower blocked the request."
    return reason


def create_tower_vault_protocol_request(
    teller_packet: Mapping[str, Any],
    actor_context: TowerActorContext,
    decision: TowerVaultGateDecision,
) -> TowerVaultProtocolRequest:
    if not decision.allowed:
        raise PermissionError(
            f"Tower cannot create Vault protocol request unless allowed. Decision: {decision.decision}"
        )

    assert_no_raw_vault_exposure(teller_packet, "Teller packet before protocol request")

    requested_output_type = str(teller_packet["requested_output_type"])
    protocol_action = TELLER_ALLOWED_OUTPUT_TO_TOWER_PROTOCOL_ACTION[requested_output_type]

    payload_for_id = {
        "pack_id": PACK_ID,
        "teller_request_id": teller_packet["request_id"],
        "protocol_action": protocol_action,
        "tower_actor_id": actor_context.actor_id,
        "tower_decision_receipt_id": decision.tower_decision_receipt_id,
        "created_at": utc_now(),
    }

    protocol_request = TowerVaultProtocolRequest(
        protocol_request_id=receipt_hash("tower-vault-protocol", payload_for_id),
        source_app="tower",
        target_app="vault",
        originating_teller_request_id=str(teller_packet["request_id"]),
        protocol_action=protocol_action,
        workflow_type=str(teller_packet["workflow_type"]),
        document_or_proof_type=str(teller_packet["document_or_proof_type"]),
        subject_person_or_vendor=str(teller_packet["subject_person_or_vendor"]),
        business_context=str(teller_packet["business_context"]),
        requester_entity=str(teller_packet["requester_entity"]),
        requested_output_type=requested_output_type,
        sensitivity_level=str(teller_packet["sensitivity_level"]),
        tower_actor_id=actor_context.actor_id,
        tower_actor_role=actor_context.role,
        tower_clearance_level=actor_context.clearance_level,
        tower_decision_receipt_id=decision.tower_decision_receipt_id,
        redaction_required=decision.redaction_required,
        vault_answers_tower_only=True,
        teller_direct_vault_access_allowed=False,
        raw_links_allowed=False,
        raw_files_allowed_for_teller=False,
        created_at=utc_now(),
    )

    assert_no_raw_vault_exposure(asdict(protocol_request), "Tower Vault protocol request")

    return protocol_request


def create_tower_safe_return_for_teller(
    teller_packet: Mapping[str, Any],
    decision: TowerVaultGateDecision,
    protocol_request: Optional[TowerVaultProtocolRequest] = None,
) -> TowerWorkflowSafeReturnForTeller:
    if protocol_request:
        summary = (
            "Tower accepted the workflow request and prepared it for Vault protocol handling. "
            "No raw Vault file or link is exposed to Teller."
        )
        receipt_id = protocol_request.protocol_request_id
        safe_label = "Vault protocol request prepared by Tower; Vault access remains Tower-controlled."
        next_action = "wait_for_tower_vault_result"
        final_for_teller = False
    else:
        summary = decision.safe_message_for_teller
        receipt_id = decision.tower_decision_receipt_id
        safe_label = "No Vault protocol request was created."
        next_action = "resolve_tower_requirement"
        final_for_teller = decision.decision in {
            TowerDecision.BLOCKED.value,
            TowerDecision.INVALID_PACKET.value,
            TowerDecision.EXPIRED_CLEARANCE.value,
            TowerDecision.ROLE_MISMATCH.value,
            TowerDecision.LANE_MISMATCH.value,
        }

    safe_return = TowerWorkflowSafeReturnForTeller(
        request_id=str(teller_packet.get("request_id", "")),
        status=decision.decision,
        allowed_output_type=str(teller_packet.get("requested_output_type", "status")),
        display_status=decision.safe_message_for_teller,
        workflow_safe_summary=summary,
        workflow_safe_receipt_id=receipt_id,
        redaction_applied=decision.redaction_required,
        tower_decision_receipt_id=decision.tower_decision_receipt_id,
        vault_proof_reference_safe_label=safe_label,
        next_teller_action=next_action,
        final_for_teller=final_for_teller,
        safe_to_display_to_requester=True,
    )

    assert_no_raw_vault_exposure(asdict(safe_return), "Tower safe return for Teller")

    return safe_return


def evaluate_and_prepare_vault_protocol_request(
    teller_packet: Mapping[str, Any],
    actor_context: TowerActorContext,
) -> Dict[str, Any]:
    """
    Main GP461–GP470 corridor entry point.

    Returns a safe Tower gate result. If allowed, includes a Tower→Vault protocol
    request object. If not allowed, returns a workflow-safe Teller result only.
    """
    assert_no_raw_vault_exposure(teller_packet, "incoming Teller packet")

    decision = evaluate_tower_vault_gate(teller_packet, actor_context)

    protocol_request: Optional[TowerVaultProtocolRequest] = None
    if decision.allowed:
        protocol_request = create_tower_vault_protocol_request(
            teller_packet=teller_packet,
            actor_context=actor_context,
            decision=decision,
        )

    safe_return = create_tower_safe_return_for_teller(
        teller_packet=teller_packet,
        decision=decision,
        protocol_request=protocol_request,
    )

    result = {
        "pack_id": PACK_ID,
        "title": PACK_TITLE,
        "doctrine": DOCTRINE,
        "tower_decision": asdict(decision),
        "vault_protocol_request": asdict(protocol_request) if protocol_request else None,
        "safe_return_for_teller": asdict(safe_return),
        "teller_direct_vault_access_allowed": False,
        "vault_answers_tower_only": True,
        "raw_vault_links_included": False,
        "raw_vault_files_included": False,
    }

    assert_no_raw_vault_exposure(result, "Tower Vault protocol gate result")

    return result


def build_demo_teller_packet(
    *,
    requested_output_type: str = "receipt",
    sensitivity_level: str = "sensitive",
) -> Dict[str, Any]:
    packet = {
        "request_id": "teller_tower_request_demo_gp461",
        "source_app": "teller",
        "target_app": "tower",
        "workflow_type": "payment_receipt_request",
        "requester_role": "manager",
        "requester_entity": "SimpleePay",
        "subject_person_or_vendor": "Demo Vendor",
        "document_or_proof_type": "payment_receipt",
        "reason_for_request": "Manager needs workflow-safe payment receipt status.",
        "deadline": "2026-08-21",
        "sensitivity_level": sensitivity_level,
        "requested_output_type": requested_output_type,
        "business_context": "SimpleePay / Vendor Payment",
        "teller_workflow_receipt_hash": "teller-fnv1a-demo461",
        "tower_approval_required": True,
        "vault_direct_access_allowed": False,
        "vault_answers_tower_only": True,
    }
    assert_no_raw_vault_exposure(packet, "demo Teller packet")
    return packet


def build_demo_actor_context(
    *,
    clearance_active: bool = True,
    step_up_active: bool = True,
    owner_approval_active: bool = False,
    sensitive_view_allowed: bool = False,
    role: str = "manager",
) -> TowerActorContext:
    return TowerActorContext(
        actor_id="tower_actor_demo_001",
        role=role,
        entity="SimpleePay",
        clearance_active=clearance_active,
        clearance_level="payroll_and_payment_workflow",
        step_up_active=step_up_active,
        owner_approval_active=owner_approval_active,
        allowed_entities=("SimpleePay",),
        allowed_roles=("manager", "owner", "payroll_admin"),
        allowed_business_contexts=("SimpleePay",),
        export_allowed=False,
        sensitive_view_allowed=sensitive_view_allowed,
        disabled_or_frozen=False,
    )


def get_tower_vault_protocol_gate_readiness() -> Dict[str, Any]:
    return {
        "pack_id": PACK_ID,
        "title": PACK_TITLE,
        "doctrine": DOCTRINE,
        "tower_receives_teller_packets": True,
        "tower_validates_teller_packets": True,
        "tower_checks_clearance": True,
        "tower_checks_role": True,
        "tower_checks_lane": True,
        "tower_checks_step_up": True,
        "tower_checks_owner_approval": True,
        "tower_sets_redaction": True,
        "tower_prepares_vault_protocol_request_when_allowed": True,
        "vault_answers_tower_only": True,
        "teller_direct_vault_access_allowed": False,
        "raw_vault_links_exposed_to_teller": False,
        "ready_for_next_corridor": "GP471-GP480 — Tower Authorized View Protocol",
    }
