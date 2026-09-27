"""TWR–OBML handoff-request contract: assertions here never grant Tower permission."""
import json
from pathlib import Path

DOCUMENT = Path(__file__).resolve().parents[1] / "tower/contracts/twr_obml_owner_handoff_request_v1.json"


def test_obml_tower_contract_is_a_request_not_a_clearance():
    value = json.loads(DOCUMENT.read_text(encoding="utf-8"))
    assert value["schema_version"] == "TOWER_OBML_OWNER_HANDOFF_REQUEST_V1"
    assert value["status"] == "SOURCE_ONLY_UNIMPLEMENTED_NO_LIVE_GRANT"
    assert value["purpose"] == "OBML_OWNER_REVIEW"
    assert value["product_app_id"] == "observatory"
    assert value["protected_destination"] == "/ob/dashboard"
    assert value["budget_constraint"] == "DO_NOT_PROVISION_PAID_RENDER_OR_EXTERNAL_SERVICES"


def test_obml_tower_handoff_requires_real_authenticated_owner_binding():
    value = json.loads(DOCUMENT.read_text(encoding="utf-8"))
    required = set(value["handoff_required_fields"])
    assert {"principal_id", "owner_session_id", "account_key", "account_identity_fingerprint",
            "purpose", "nonce", "step_up_event_ref", "step_up_at_utc", "revocation_epoch",
            "verified_tower_attestation", "expires_at_utc", "decision_id"} <= required
    assert len(value["deny_if"]) == len(set(value["deny_if"]))
    assert {"NON_OWNER_FAILS_CLOSED", "REVOKED_OR_REPLAYED_ASSERTION_FAILS_CLOSED",
            "SOURCE_HASH_ONLY_IS_NOT_AUTHENTICATION"} <= set(value["implementation_acceptance_tests"])


def test_obml_tower_handoff_is_review_only_not_live_or_money_permission():
    value = json.loads(DOCUMENT.read_text(encoding="utf-8"))
    caps = value["capability_scope"]
    assert caps["owner_readiness_review_only"] is True
    assert caps["manual_broker_placement_by_human_outside_ob"] is True
    assert all(caps[name] is False for name in (
        "trade_intent_creation", "order_authorized", "broker_order_api",
        "automatic_execution", "hybrid_execution", "capital_movement",
        "protected_floor_release", "safety_clearance_override",
    ))
    assert "LIVE_ACTIVATION" in value["not_authorized_by_this_contract"]
    assert "ACTUAL_BANK_OR_BROKER_PROVENANCE" in value["not_authorized_by_this_contract"]
