import ast
from pathlib import Path

import pytest

from clouds.executive_owner_handoff_submission_authorization import (
    OwnerHandoffDecision,
    OwnerReviewConfirmationState,
    SubmissionAuthorizationState,
)

from clouds.executive_owner_handoff_submission_authorization_service import (
    filter_submission_authorizations,
    get_clouds_gp014_status_payload,
    get_owner_handoff_authorization_surface,
    get_owner_handoff_authorization_surface_payload,
    get_owner_handoff_decision,
    get_owner_handoff_decision_by_draft,
    get_owner_handoff_decisions,
    get_submission_authorization,
    get_submission_authorization_by_draft,
    get_submission_authorizations,
)


def test_gp014_has_11_owner_decisions():
    decisions = (
        get_owner_handoff_decisions()
    )

    assert len(decisions) == 11


def test_gp014_has_11_submission_authorizations():
    records = (
        get_submission_authorizations()
    )

    assert len(records) == 11


def test_gp014_decision_ids_are_unique():
    decisions = (
        get_owner_handoff_decisions()
    )

    ids = [
        item.decision_id
        for item in decisions
    ]

    assert len(ids) == len(set(ids))


def test_gp014_every_decision_is_approve():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert decision.decision == (
            OwnerHandoffDecision
            .APPROVE.value
        )


def test_gp014_every_review_is_confirmed():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision.review_confirmation
            == OwnerReviewConfirmationState
            .CONFIRMED.value
        )


def test_gp014_decision_flags_are_consistent():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision.decision_recorded
            is True
        )

        assert (
            decision.approval_recorded
            is True
        )

        assert (
            decision.decline_recorded
            is False
        )

        assert (
            decision.hold_recorded
            is False
        )


def test_gp014_owner_review_flags_are_true():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision
            .owner_reviewed_destination
            is True
        )

        assert (
            decision
            .owner_reviewed_permission_requirement
            is True
        )

        assert (
            decision
            .owner_reviewed_step_up_requirement
            is True
        )

        assert (
            decision
            .owner_reviewed_boundary_notice
            is True
        )


def test_gp014_source_integrity_verified():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision.source_integrity_verified
            is True
        )


def test_gp014_submission_authorization_is_true():
    records = (
        get_submission_authorizations()
    )

    assert all(
        record.submission_authorized
        is True
        for record in records
    )


def test_gp014_authorization_state_is_authorized():
    for record in (
        get_submission_authorizations()
    ):
        assert record.state == (
            SubmissionAuthorizationState
            .AUTHORIZED.value
        )


def test_gp014_owner_permission_requirement_preserved():
    for record in (
        get_submission_authorizations()
    ):
        assert (
            record
            .owner_permission_requirement_preserved
            is True
        )


def test_gp014_step_up_requirement_preserved():
    for record in (
        get_submission_authorizations()
    ):
        assert (
            record
            .step_up_requirement_preserved
            is True
        )


def test_gp014_tower_boundary_preserved():
    for record in (
        get_submission_authorizations()
    ):
        assert (
            record.tower_boundary_preserved
            is True
        )


def test_gp014_no_tower_request_created():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision.tower_request_created
            is False
        )

    for record in (
        get_submission_authorizations()
    ):
        assert (
            record.tower_request_created
            is False
        )


def test_gp014_no_delivery_performed():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision.delivery_performed
            is False
        )

    for record in (
        get_submission_authorizations()
    ):
        assert (
            record.delivery_performed
            is False
        )


def test_gp014_no_tower_receipt_created():
    for record in (
        get_submission_authorizations()
    ):
        assert (
            record.tower_receipt_created
            is False
        )


def test_gp014_no_handoff_executed():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision.handoff_executed
            is False
        )

    for record in (
        get_submission_authorizations()
    ):
        assert (
            record.handoff_executed
            is False
        )


def test_gp014_no_downstream_execution():
    for decision in (
        get_owner_handoff_decisions()
    ):
        assert (
            decision
            .downstream_execution_performed
            is False
        )

    for record in (
        get_submission_authorizations()
    ):
        assert (
            record
            .downstream_execution_performed
            is False
        )


def test_gp014_lookup_decision_by_draft():
    decision = (
        get_owner_handoff_decisions()[0]
    )

    fetched = (
        get_owner_handoff_decision_by_draft(
            decision.draft_id
        )
    )

    assert (
        fetched.decision_id
        == decision.decision_id
    )


def test_gp014_lookup_authorization_by_draft():
    record = (
        get_submission_authorizations()[0]
    )

    fetched = (
        get_submission_authorization_by_draft(
            record.draft_id
        )
    )

    assert (
        fetched.authorization_id
        == record.authorization_id
    )


def test_gp014_filter_authorized():
    records = (
        filter_submission_authorizations(
            submission_authorized=True
        )
    )

    assert len(records) == 11


def test_gp014_filter_by_owner_decision():
    records = (
        filter_submission_authorizations(
            owner_decision="approve"
        )
    )

    assert len(records) == 11


def test_gp014_unknown_decision_fails_closed():
    with pytest.raises(KeyError):
        get_owner_handoff_decision(
            "missing-decision"
        )


def test_gp014_unknown_draft_decision_fails_closed():
    with pytest.raises(KeyError):
        get_owner_handoff_decision_by_draft(
            "missing-draft"
        )


def test_gp014_unknown_authorization_fails_closed():
    with pytest.raises(KeyError):
        get_submission_authorization(
            "missing-authorization"
        )


def test_gp014_unknown_draft_authorization_fails_closed():
    with pytest.raises(KeyError):
        get_submission_authorization_by_draft(
            "missing-draft"
        )


def test_gp014_surface_counts():
    surface = (
        get_owner_handoff_authorization_surface()
    )

    assert surface.decision_count == 11
    assert surface.authorized_count == 11
    assert surface.declined_count == 0
    assert surface.held_count == 0


def test_gp014_surface_boundary_notice():
    surface = (
        get_owner_handoff_authorization_surface()
    )

    text = (
        surface.boundary_notice.lower()
    )

    assert "do not mean" in text
    assert "tower request" in text
    assert "handoff" in text


def test_gp014_surface_payload_is_json_ready():
    payload = (
        get_owner_handoff_authorization_surface_payload()
    )

    assert payload["decision_count"] == 11
    assert payload["authorized_count"] == 11

    assert len(
        payload["decisions"]
    ) == 11

    assert len(
        payload["authorizations"]
    ) == 11


def test_gp014_status_is_ready_and_safe():
    status = (
        get_clouds_gp014_status_payload()
    )

    assert status["pack"] == "GP014"

    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["decision_count"] == 11
    assert status["authorized_count"] == 11
    assert status["declined_count"] == 0
    assert status["held_count"] == 0

    assert (
        status["owner_decision_recorded"]
        is True
    )

    assert (
        status["owner_approval_recorded"]
        is True
    )

    assert (
        status["submission_authorized"]
        is True
    )

    assert (
        status["tower_boundary_preserved"]
        is True
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
        "GP015 — EXECUTIVE OWNER HANDOFF "
        "SUBMISSION / TOWER INTAKE "
        "PREPARATION SURFACE"
    )


def test_gp014_no_cross_app_python_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root
        / "clouds"
        / "executive_owner_handoff_submission_authorization.py",
        root
        / "clouds"
        / "executive_owner_handoff_submission_authorization_service.py",
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
