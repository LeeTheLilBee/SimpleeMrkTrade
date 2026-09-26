"""External-system response contracts; shape checks are not identity verification."""
from datetime import datetime, timezone
from .registry import get_vertical

def future(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.tzinfo is not None and dt > datetime.now(timezone.utc)
    except (AttributeError, ValueError, TypeError):
        return False

def validate_teller(response):
    if not isinstance(response, dict) or response.get("source") != "teller":
        return False
    if not response.get("authority_reference") or not future(response.get("valid_until")):
        return False
    valid = ("READY", "PARTIAL", "BLOCKED", "UNKNOWN")
    if response.get("money_status") not in valid or response.get("management_status") not in valid:
        return False
    if response.get("status") not in valid:
        return False
    if response["status"] == "READY" and (response["money_status"] != "READY" or response["management_status"] != "READY"):
        return False
    return True

def validate_tower(response, action, opportunity_id):
    if not isinstance(response, dict) or response.get("source") != "tower":
        return False
    return (response.get("action") == action
            and response.get("opportunity_id") == opportunity_id
            and response.get("decision") == "APPROVED"
            and bool(response.get("receipt_reference"))
            and future(response.get("valid_until")))

def grounds_reference(response):
    if not isinstance(response, dict) or response.get("source") != "grounds":
        return None
    if not response.get("property_reference"):
        return None
    return {"property_reference": response["property_reference"],
            "snapshot_at": response.get("snapshot_at"), "summary": response.get("summary", {})}

def prepare_handoff(opportunity, evaluation, tower_receipt):
    if opportunity["lifecycle"] != "ACQUIRED" or not tower_receipt:
        raise ValueError("HANDOFF_NOT_AUTHORIZED")
    return {"opportunity_id": opportunity["id"], "vertical": opportunity["vertical"],
            "destination": get_vertical(opportunity["vertical"])["handoff"],
            "asset_data": opportunity.get("vertical_data", {}),
            "closing_evaluation": evaluation, "tower_receipt": tower_receipt,
            "transfer_state": "PENDING_DESTINATION_ACCEPTANCE"}

# In production, verifying an authority_reference also requires authenticated
# transport, issuer identity, request/snapshot binding and receipt verification.
# A locally supplied dictionary must never be treated as a live authorization.
