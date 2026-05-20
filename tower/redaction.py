# =============================================================================
# THE TOWER — REDACTION + DATA CLASSIFICATION
# FILE: tower/redaction.py
# =============================================================================

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from tower.audit import write_audit_event
from tower.object_access import (
    CLASS_ADMIN_ONLY,
    CLASS_CONFIDENTIAL,
    CLASS_INTERNAL,
    CLASS_PUBLIC,
    CLASS_RESTRICTED,
    CLASS_TRUST_INTERNAL,
    CLASS_USER_PRIVATE,
)


# =============================================================================
# DATA CLASSES
# =============================================================================

DATA_PUBLIC = "public"
DATA_INTERNAL = "internal"
DATA_PRIVATE = "private"
DATA_CONFIDENTIAL = "confidential"
DATA_RESTRICTED = "restricted"
DATA_SECRET = "secret"
DATA_TRUST_INTERNAL = "trust_internal"
DATA_BROKER_SENSITIVE = "broker_sensitive"
DATA_PAYROLL_SENSITIVE = "payroll_sensitive"
DATA_SECURITY_SENSITIVE = "security_sensitive"


# =============================================================================
# DEFAULT FIELD SENSITIVITY
# =============================================================================

FIELD_CLASSIFICATIONS = {
    # Identity/contact
    "email": DATA_PRIVATE,
    "phone": DATA_PRIVATE,
    "address": DATA_CONFIDENTIAL,
    "ip_address": DATA_SECURITY_SENSITIVE,
    "ip_hash": DATA_SECURITY_SENSITIVE,
    "device_fingerprint": DATA_SECURITY_SENSITIVE,
    "device_id": DATA_SECURITY_SENSITIVE,
    "session_id": DATA_SECURITY_SENSITIVE,

    # Auth/security
    "password": DATA_SECRET,
    "password_hash": DATA_SECRET,
    "token": DATA_SECRET,
    "access_token": DATA_SECRET,
    "refresh_token": DATA_SECRET,
    "api_key": DATA_SECRET,
    "secret": DATA_SECRET,
    "signature": DATA_SECURITY_SENSITIVE,
    "clearance_token": DATA_SECURITY_SENSITIVE,

    # Money/broker/payroll
    "account_number": DATA_BROKER_SENSITIVE,
    "broker_account": DATA_BROKER_SENSITIVE,
    "broker_token": DATA_SECRET,
    "routing_number": DATA_PAYROLL_SENSITIVE,
    "ssn": DATA_SECRET,
    "ein": DATA_CONFIDENTIAL,
    "payroll_amount": DATA_PAYROLL_SENSITIVE,
    "salary": DATA_PAYROLL_SENSITIVE,
    "owner_draw": DATA_PAYROLL_SENSITIVE,

    # Trading/internal strategy
    "strategy_core": DATA_SECRET,
    "raw_signal_payload": DATA_CONFIDENTIAL,
    "internal_score": DATA_INTERNAL,
    "admin_notes": DATA_INTERNAL,
    "trust_notes": DATA_TRUST_INTERNAL,

    # Legal/compliance/security
    "legal_notes": DATA_CONFIDENTIAL,
    "compliance_notes": DATA_CONFIDENTIAL,
    "security_notes": DATA_SECURITY_SENSITIVE,
    "audit_hash": DATA_SECURITY_SENSITIVE,
    "event_hash": DATA_SECURITY_SENSITIVE,
    "capsule_hash": DATA_SECURITY_SENSITIVE,
}


ROLE_CLEARANCE = {
    "owner": {
        DATA_PUBLIC,
        DATA_INTERNAL,
        DATA_PRIVATE,
        DATA_CONFIDENTIAL,
        DATA_RESTRICTED,
        DATA_SECRET,
        DATA_TRUST_INTERNAL,
        DATA_BROKER_SENSITIVE,
        DATA_PAYROLL_SENSITIVE,
        DATA_SECURITY_SENSITIVE,
    },
    "admin": {
        DATA_PUBLIC,
        DATA_INTERNAL,
        DATA_PRIVATE,
        DATA_CONFIDENTIAL,
        DATA_RESTRICTED,
        DATA_SECURITY_SENSITIVE,
    },
    "user": {
        DATA_PUBLIC,
        DATA_PRIVATE,
    },
    "viewer": {
        DATA_PUBLIC,
    },
}


ACCOUNT_TYPE_CLEARANCE = {
    "owner": ROLE_CLEARANCE["owner"],
    "internal": {
        DATA_PUBLIC,
        DATA_INTERNAL,
        DATA_PRIVATE,
        DATA_CONFIDENTIAL,
        DATA_RESTRICTED,
        DATA_TRUST_INTERNAL,
        DATA_SECURITY_SENSITIVE,
    },
    "trust": {
        DATA_PUBLIC,
        DATA_INTERNAL,
        DATA_PRIVATE,
        DATA_CONFIDENTIAL,
        DATA_RESTRICTED,
        DATA_TRUST_INTERNAL,
        DATA_BROKER_SENSITIVE,
        DATA_SECURITY_SENSITIVE,
    },
    "beta_user": {
        DATA_PUBLIC,
        DATA_PRIVATE,
    },
    "public_user": {
        DATA_PUBLIC,
    },
}


CLASSIFICATION_TO_DATA_CLASS = {
    CLASS_PUBLIC: DATA_PUBLIC,
    CLASS_USER_PRIVATE: DATA_PRIVATE,
    CLASS_INTERNAL: DATA_INTERNAL,
    CLASS_CONFIDENTIAL: DATA_CONFIDENTIAL,
    CLASS_RESTRICTED: DATA_RESTRICTED,
    CLASS_TRUST_INTERNAL: DATA_TRUST_INTERNAL,
    CLASS_ADMIN_ONLY: DATA_SECURITY_SENSITIVE,
}


REDACTION_TEXT = "[REDACTED]"


def get_user_clearance_classes(user: Dict[str, Any]) -> set:
    role = user.get("role", "viewer")
    account_type = user.get("account_type", "public_user")

    allowed = set()
    allowed.update(ROLE_CLEARANCE.get(role, set()))
    allowed.update(ACCOUNT_TYPE_CLEARANCE.get(account_type, set()))

    return allowed


def classify_field(field_name: str, value: Any = None, parent_path: str = "") -> str:
    """
    Classifies a field by name.

    Baby version:
    This says what kind of sticker the field gets:
    public, private, secret, broker sensitive, etc.
    """

    key = str(field_name or "").strip()
    lowered = key.lower()

    if lowered in FIELD_CLASSIFICATIONS:
        return FIELD_CLASSIFICATIONS[lowered]

    # Soft pattern matching for common sensitive names.
    sensitive_fragments = {
        "password": DATA_SECRET,
        "secret": DATA_SECRET,
        "token": DATA_SECRET,
        "api_key": DATA_SECRET,
        "ssn": DATA_SECRET,
        "broker": DATA_BROKER_SENSITIVE,
        "payroll": DATA_PAYROLL_SENSITIVE,
        "salary": DATA_PAYROLL_SENSITIVE,
        "audit": DATA_SECURITY_SENSITIVE,
        "hash": DATA_SECURITY_SENSITIVE,
        "session": DATA_SECURITY_SENSITIVE,
        "device": DATA_SECURITY_SENSITIVE,
        "ip_": DATA_SECURITY_SENSITIVE,
        "legal": DATA_CONFIDENTIAL,
        "compliance": DATA_CONFIDENTIAL,
        "trust": DATA_TRUST_INTERNAL,
    }

    for fragment, classification in sensitive_fragments.items():
        if fragment in lowered:
            return classification

    return DATA_PUBLIC


def can_view_data_class(user: Dict[str, Any], data_class: str) -> bool:
    allowed = get_user_clearance_classes(user)
    return data_class in allowed


def _redact_value(value: Any, style: str = "mask") -> Any:
    if style == "null":
        return None

    if style == "remove":
        return None

    if isinstance(value, (int, float)):
        return None

    if isinstance(value, bool):
        return None

    if value is None:
        return None

    return REDACTION_TEXT


def redact_record(
    record: Dict[str, Any],
    user: Dict[str, Any],
    classification: Optional[str] = None,
    field_policy: Optional[Dict[str, str]] = None,
    redaction_style: str = "mask",
    path_prefix: str = "",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Redacts a record for a user.

    Baby version:
    This takes a record and covers the parts the user cannot see.
    """

    field_policy = field_policy or {}
    record_copy = deepcopy(record)
    redacted_fields: List[str] = []
    visible_fields: List[str] = []

    base_data_class = None
    if classification:
        base_data_class = CLASSIFICATION_TO_DATA_CLASS.get(classification, classification)

    def walk(value: Any, path: str = "") -> Any:
        if isinstance(value, dict):
            output = {}
            for key, subvalue in value.items():
                child_path = f"{path}.{key}" if path else str(key)

                data_class = field_policy.get(child_path) or field_policy.get(str(key))

                if not data_class:
                    data_class = classify_field(str(key), subvalue, parent_path=path)

                # If the whole object is restricted, public-looking fields still inherit that
                # unless they are simple display/safe fields.
                safe_display_fields = {"title", "name", "display_name", "status", "created_at", "updated_at", "object_id", "object_type", "app_name", "classification"}
                if base_data_class and base_data_class not in {DATA_PUBLIC, DATA_PRIVATE} and str(key) not in safe_display_fields:
                    if data_class == DATA_PUBLIC:
                        data_class = base_data_class

                if can_view_data_class(user, data_class):
                    visible_fields.append(child_path)
                    output[key] = walk(subvalue, child_path)
                else:
                    redacted_fields.append(child_path)
                    if redaction_style == "remove":
                        continue
                    output[key] = _redact_value(subvalue, style=redaction_style)

            return output

        if isinstance(value, list):
            return [walk(item, f"{path}[{idx}]") for idx, item in enumerate(value)]

        return value

    redacted = walk(record_copy, path_prefix)

    report = {
        "user_id": user.get("user_id"),
        "role": user.get("role"),
        "account_type": user.get("account_type"),
        "classification": classification,
        "redaction_style": redaction_style,
        "redacted_count": len(redacted_fields),
        "visible_count": len(visible_fields),
        "redacted_fields": redacted_fields,
        "visible_fields": visible_fields,
    }

    return redacted, report


def classify_record(
    record: Dict[str, Any],
    default_classification: str = CLASS_PUBLIC,
) -> Dict[str, Any]:
    """
    Creates a field classification map for a record.

    Baby version:
    This labels every field.
    """

    field_map = {}

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, subvalue in value.items():
                child_path = f"{path}.{key}" if path else str(key)
                field_map[child_path] = classify_field(str(key), subvalue, parent_path=path)
                walk(subvalue, child_path)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                walk(item, f"{path}[{idx}]")

    walk(record)

    return {
        "default_classification": default_classification,
        "field_map": field_map,
        "total_fields": len(field_map),
    }


def redact_and_audit(
    record: Dict[str, Any],
    user: Dict[str, Any],
    classification: Optional[str] = None,
    field_policy: Optional[Dict[str, str]] = None,
    redaction_style: str = "mask",
    actor_user_id: str = "tower_redaction",
    app_name: str = "tower_admin",
    object_type: str = "record",
    object_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Redacts a record and writes an audit receipt.

    Baby version:
    This covers the private parts and writes down what got covered.
    """

    redacted, report = redact_record(
        record=record,
        user=user,
        classification=classification,
        field_policy=field_policy,
        redaction_style=redaction_style,
    )

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=str(user.get("user_id", "unknown")),
        action="redact_record",
        app_name=app_name,
        object_type=object_type,
        object_id=object_id,
        result="allow",
        reason_code="record_redacted",
        human_reason="Tower redaction was applied to a record.",
        risk_score=25 if report.get("redacted_count") else 10,
        risk_state="clear",
        metadata={
            "redaction_report": report,
        },
    )

    return {
        "record": redacted,
        "redaction_report": report,
    }
