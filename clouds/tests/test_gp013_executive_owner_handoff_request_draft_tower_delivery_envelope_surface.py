import ast
from pathlib import Path

import pytest

from clouds.executive_owner_handoff_request_draft import (
    DeliveryEnvelopeState,
    HandoffDraftDecision,
    HandoffDraftState,
)

from clouds.executive_owner_handoff_request_draft_service import (
    get_clouds_gp013_status_payload,
    get_handoff_draft_surface,
    get_handoff_draft_surface_payload,
    get_handoff_request_draft,
    get_handoff_request_draft_by_item,
    get_handoff_request_draft_payload,
    get_handoff_request_drafts,
    get_tower_delivery_envelope,
    get_tower_delivery_envelope_by_draft,
    get_tower_delivery_envelope_payload,
    get_tower_delivery_envelopes,
)


def test_gp013_builds_11_tower_drafts():
    drafts = get_handoff_request_drafts()

    assert len(drafts) == 11


def test_gp013_builds_11_envelopes():
    envelopes = (
        get_tower_delivery_envelopes()
    )

    assert len(envelopes) == 11


def test_gp013_draft_ids_are_unique():
    drafts = get_handoff_request_drafts()

    ids = [
        draft.draft_id
        for draft in drafts
    ]

    assert len(ids) == len(set(ids))


def test_gp013_envelope_ids_are_unique():
    envelopes = (
        get_tower_delivery_envelopes()
    )

    ids = [
        envelope.envelope_id
        for envelope in envelopes
    ]

    assert len(ids) == len(set(ids))


def test_gp013_every_draft_is_ready():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert draft.draft_state == (
            HandoffDraftState
            .DRAFT_READY.value
        )


def test_gp013_every_owner_decision_is_undecided():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert draft.owner_decision == (
            HandoffDraftDecision
            .UNDECIDED.value
        )


def test_gp013_no_owner_approval_recorded():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert (
            draft.owner_approval_recorded
            is False
        )


def test_gp013_no_submission_authorized():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert (
            draft.submission_authorized
            is False
        )


def test_gp013_no_tower_request_created():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert (
            draft.tower_request_created
            is False
        )


def test_gp013_no_delivery_to_tower():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert (
            draft.delivered_to_tower
            is False
        )


def test_gp013_no_handoff_executed():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert (
            draft.handoff_executed
            is False
        )


def test_gp013_no_downstream_execution():
    for draft in (
        get_handoff_request_drafts()
    ):
        assert (
            draft
            .downstream_execution_performed
            is False
        )


def test_gp013_observatory_focus_has_draft():
    draft = (
        get_handoff_request_draft_by_item(
            "workspace-now-focus"
        )
    )

    assert (
        draft.destination_id
        == "tower-observatory"
    )

    assert draft.requires_tower is True
    assert (
        draft.requires_owner_permission
        is True
    )
    assert draft.requires_step_up is True


def test_gp013_every_envelope_is_prepared():
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        assert envelope.state == (
            DeliveryEnvelopeState
            .PREPARED.value
        )


def test_gp013_envelopes_have_sha256_hashes():
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        assert len(
            envelope.payload_hash
        ) == 64

        int(
            envelope.payload_hash,
            16,
        )


def test_gp013_envelope_hashes_are_deterministic():
    first = [
        envelope.payload_hash
        for envelope
        in get_tower_delivery_envelopes()
    ]

    second = [
        envelope.payload_hash
        for envelope
        in get_tower_delivery_envelopes()
    ]

    assert first == second


def test_gp013_envelope_links_to_draft():
    for draft in (
        get_handoff_request_drafts()
    ):
        envelope = (
            get_tower_delivery_envelope_by_draft(
                draft.draft_id
            )
        )

        assert (
            envelope.draft_id
            == draft.draft_id
        )

        assert (
            envelope.review_id
            == draft.review_id
        )


def test_gp013_no_envelope_delivery_authorized():
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        assert (
            envelope.delivery_authorized
            is False
        )


def test_gp013_no_envelope_delivered():
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        assert envelope.delivered is False


def test_gp013_no_tower_receipt_created():
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        assert (
            envelope.tower_receipt_created
            is False
        )


def test_gp013_no_envelope_execution():
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        assert (
            envelope.execution_performed
            is False
        )


def test_gp013_unknown_draft_fails_closed():
    with pytest.raises(KeyError):
        get_handoff_request_draft(
            "missing-draft"
        )


def test_gp013_unknown_item_fails_closed():
    with pytest.raises(KeyError):
        get_handoff_request_draft_by_item(
            "missing-item"
        )


def test_gp013_unknown_envelope_fails_closed():
    with pytest.raises(KeyError):
        get_tower_delivery_envelope(
            "missing-envelope"
        )


def test_gp013_unknown_draft_envelope_fails_closed():
    with pytest.raises(KeyError):
        get_tower_delivery_envelope_by_draft(
            "missing-draft"
        )


def test_gp013_draft_payload_is_json_ready():
    draft = get_handoff_request_drafts()[0]

    payload = (
        get_handoff_request_draft_payload(
            draft.draft_id
        )
    )

    assert payload["draft_id"] == (
        draft.draft_id
    )

    assert (
        payload["submission_authorized"]
        is False
    )


def test_gp013_envelope_payload_is_json_ready():
    envelope = (
        get_tower_delivery_envelopes()[0]
    )

    payload = (
        get_tower_delivery_envelope_payload(
            envelope.envelope_id
        )
    )

    assert (
        payload["envelope_id"]
        == envelope.envelope_id
    )

    assert payload["delivered"] is False


def test_gp013_surface_payload_is_json_ready():
    payload = (
        get_handoff_draft_surface_payload()
    )

    assert payload["draft_count"] == 11
    assert payload["envelope_count"] == 11

    assert (
        "does not mean approved"
        in payload["boundary_notice"].lower()
    )


def test_gp013_surface_is_repeatable():
    first = (
        get_handoff_draft_surface_payload()
    )

    second = (
        get_handoff_draft_surface_payload()
    )

    assert first == second


def test_gp013_status_is_ready_and_safe():
    status = (
        get_clouds_gp013_status_payload()
    )

    assert status["pack"] == "GP013"

    assert status["section"] == (
        "EXECUTIVE OWNER HANDOFF REQUEST DRAFT "
        "/ TOWER DELIVERY ENVELOPE SURFACE"
    )

    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["draft_count"] == 11
    assert status["envelope_count"] == 11

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert (
        status["tower_boundary_preserved"]
        is True
    )

    assert (
        status["owner_decision_recorded"]
        is False
    )

    assert (
        status["owner_approval_recorded"]
        is False
    )

    assert (
        status["submission_authorized"]
        is False
    )

    assert (
        status["tower_request_created"]
        is False
    )

    assert (
        status["delivery_performed"]
        is False
    )

    assert (
        status["tower_receipt_created"]
        is False
    )

    assert (
        status["handoff_executed"]
        is False
    )

    assert (
        status["downstream_execution_performed"]
        is False
    )

    assert (
        status["cross_app_imports_used"]
        is False
    )

    assert status["next_pack"] == (
        "GP014 — EXECUTIVE OWNER HANDOFF REQUEST "
        "OWNER DECISION / SUBMISSION AUTHORIZATION SURFACE"
    )


def test_gp013_no_cross_app_python_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root
        / "clouds"
        / "executive_owner_handoff_request_draft.py",
        root
        / "clouds"
        / "executive_owner_handoff_request_draft_service.py",
    )

    forbidden_roots = {
        "tower",
        "observatory",
        "vault",
        "teller",
        "grounds",
    }

    for path in production_files:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    root_name = (
                        alias.name
                        .split(".")[0]
                        .lower()
                    )

                    assert (
                        root_name
                        not in forbidden_roots
                    )

            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module
                    or ""
                )

                root_name = (
                    module
                    .lstrip(".")
                    .split(".")[0]
                    .lower()
                )

                assert (
                    root_name
                    not in forbidden_roots
                )
