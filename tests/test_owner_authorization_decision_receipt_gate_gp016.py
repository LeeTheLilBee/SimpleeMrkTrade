from ob_owner_experience.owner_authorization_decision_receipt_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_authorization_decision_receipt_gate_bundle,
    build_owner_authorization_decision_receipt_gate_handoff,
    build_owner_authorization_decision_receipt_gate_status,
    build_owner_authorization_decision_receipt_schema,
)


def test_gp016_schema_closed():
    schema = build_owner_authorization_decision_receipt_schema()
    assert schema["append_only"] is True
    assert schema["redaction_required"] is True
    assert schema["emission_allowed_now"] is False
    assert "receipt_id" in schema["required_fields"]


def test_gp016_status_locked():
    status = build_owner_authorization_decision_receipt_gate_status()
    assert status["gp015_receipt_draft_prepared"] is True
    assert status["receipt_gate_closed"] is True
    assert status["room_scope_count"] == 6
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp016_bundle_and_handoff():
    bundle = build_owner_authorization_decision_receipt_gate_bundle()
    assert bundle["package"] == "ob_owner_authorization_decision_receipt_gate_gp016"
    assert bundle["gate_prepared"] is True
    assert bundle["gate_state"] == "closed_pending_future_authorized_receipt_emission"
    assert bundle["release_boundary"]["receipt_gate_open"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_owner_authorization_decision_receipt_gate_handoff()
    assert "Do not emit a decision receipt." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
