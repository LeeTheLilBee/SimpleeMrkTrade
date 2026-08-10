from ob_owner_experience.owner_authorization_receipt_draft import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_authorization_receipt_draft,
    build_owner_authorization_receipt_draft_bundle,
    build_owner_authorization_receipt_draft_handoff,
    build_owner_authorization_receipt_draft_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp015_receipt_draft_only():
    draft = build_owner_authorization_receipt_draft()
    assert draft["draft_only"] is True
    assert draft["final"] is False
    assert draft["emitted"] is False
    assert draft["append_only_required"] is True
    assert draft["redaction_required"] is True
    assert len(draft["room_scope"]) == 6
    assert [item["room"] for item in draft["room_scope"]] == list(SIX_ROOM_REAL_SURFACE_ORDER)


def test_gp015_status_safety_locked():
    status = build_owner_authorization_receipt_draft_status()
    assert status["gp014_decision_recording_gate_prepared"] is True
    assert status["receipt_draft_prepared"] is True
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp015_bundle_and_handoff():
    bundle = build_owner_authorization_receipt_draft_bundle()
    assert bundle["package"] == "ob_owner_authorization_receipt_draft_gp015"
    assert bundle["draft_prepared"] is True
    assert bundle["source_dependency"] == "GP014"
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert bundle["release_boundary"]["decision_receipt_emitted"] is False
    assert bundle["release_boundary"]["controlled_run_gate_open"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True

    handoff = build_owner_authorization_receipt_draft_handoff()
    assert handoff["draft_prepared"] is True
    assert "Do not emit a receipt from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
