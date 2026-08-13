import ast
from pathlib import Path

import pytest

from clouds.executive_owner_action_intent_review import (
    HandoffPreparationState,
    IntentReviewDecision,
    IntentReviewState,
)

from clouds.executive_owner_action_intent_review_service import (
    filter_owner_intent_review_packets,
    get_clouds_gp012_status_payload,
    get_owner_intent_review_packet,
    get_owner_intent_review_packet_payload,
    get_owner_intent_review_packets,
    get_owner_intent_review_surface,
    get_owner_intent_review_surface_payload,
)


def test_gp012_has_18_review_packets():
    reviews = (
        get_owner_intent_review_packets()
    )

    assert len(reviews) == 18


def test_gp012_review_ids_are_unique():
    reviews = (
        get_owner_intent_review_packets()
    )

    ids = [
        review.review_id
        for review in reviews
    ]

    assert len(ids) == len(set(ids))


def test_gp012_every_review_is_undecided():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert review.decision == (
            IntentReviewDecision
            .UNDECIDED.value
        )


def test_gp012_no_owner_approval_is_recorded():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert (
            review.owner_approval_recorded
            is False
        )

        assert (
            review
            .handoff_preparation
            .owner_approval_recorded
            is False
        )


def test_gp012_no_tower_request_is_created():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert (
            review.tower_request_created
            is False
        )

        assert (
            review
            .handoff_preparation
            .tower_request_created
            is False
        )


def test_gp012_no_handoff_is_executed():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert (
            review
            .handoff_preparation
            .tower_handoff_executed
            is False
        )

        assert review.execution_performed is False


def test_gp012_no_downstream_execution():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert (
            review
            .handoff_preparation
            .downstream_execution_performed
            is False
        )


def test_gp012_focus_is_tower_handoff_prepared():
    review = (
        get_owner_intent_review_packet(
            "workspace-now-focus"
        )
    )

    assert review.review_state == (
        IntentReviewState
        .TOWER_HANDOFF_PREPARED.value
    )

    assert review.preparation_state == (
        HandoffPreparationState
        .PREPARED.value
    )

    assert (
        review
        .handoff_preparation
        .requires_tower
        is True
    )

    assert (
        review
        .handoff_preparation
        .requires_owner_permission
        is True
    )

    assert (
        review
        .handoff_preparation
        .requires_step_up
        is True
    )


def test_gp012_internal_clouds_item_is_prepared():
    review = (
        get_owner_intent_review_packet(
            "workspace-section-today"
        )
    )

    assert review.review_state == (
        IntentReviewState
        .INTERNAL_REVIEW_PREPARED.value
    )

    assert review.preparation_state == (
        HandoffPreparationState
        .PREPARED.value
    )

    assert (
        review
        .handoff_preparation
        .requires_tower
        is False
    )


def test_gp012_blocked_item_can_block_preparation():
    blocked = (
        filter_owner_intent_review_packets(
            blocked=True
        )
    )

    assert blocked

    assert all(
        review.review_state
        == IntentReviewState.BLOCKED.value
        for review in blocked
    )

    assert all(
        review.preparation_state
        == HandoffPreparationState
        .NOT_PREPARED.value
        for review in blocked
    )


def test_gp012_every_review_has_requirements():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert review.requirements


def test_gp012_tower_reviews_include_tower_requirement():
    reviews = (
        filter_owner_intent_review_packets(
            requires_tower=True
        )
    )

    assert reviews

    for review in reviews:
        labels = {
            requirement.label
            for requirement
            in review.requirements
        }

        assert (
            "Tower mediation required"
            in labels
        )


def test_gp012_tower_reviews_include_permission_requirement():
    reviews = (
        filter_owner_intent_review_packets(
            requires_tower=True
        )
    )

    assert reviews

    for review in reviews:
        labels = {
            requirement.label
            for requirement
            in review.requirements
        }

        assert (
            "Owner permission check required"
            in labels
        )


def test_gp012_tower_reviews_include_step_up_requirement():
    reviews = (
        filter_owner_intent_review_packets(
            requires_tower=True
        )
    )

    assert reviews

    for review in reviews:
        labels = {
            requirement.label
            for requirement
            in review.requirements
        }

        assert (
            "Step-up evaluation required"
            in labels
        )


def test_gp012_blockers_are_not_resolvable_in_clouds():
    for review in (
        get_owner_intent_review_packets()
    ):
        for blocker in review.blockers:
            assert (
                blocker.resolvable_in_clouds
                is False
            )


def test_gp012_every_review_has_owner_questions():
    for review in (
        get_owner_intent_review_packets()
    ):
        assert len(
            review.owner_review_questions
        ) >= 3


def test_gp012_filter_by_tower():
    reviews = (
        filter_owner_intent_review_packets(
            requires_tower=True
        )
    )

    assert reviews

    assert all(
        review
        .handoff_preparation
        .requires_tower
        is True
        for review in reviews
    )


def test_gp012_filter_by_app():
    reviews = (
        filter_owner_intent_review_packets(
            source_app_id="observatory"
        )
    )

    assert reviews

    assert all(
        review.source_app_id
        == "observatory"
        for review in reviews
    )


def test_gp012_filter_by_lane():
    reviews = (
        filter_owner_intent_review_packets(
            source_lane_id="investment_engine"
        )
    )

    assert reviews

    assert all(
        review.source_lane_id
        == "investment_engine"
        for review in reviews
    )


def test_gp012_filter_by_review_state():
    reviews = (
        filter_owner_intent_review_packets(
            review_state=(
                "tower_handoff_prepared"
            )
        )
    )

    assert reviews

    assert all(
        review.review_state
        == "tower_handoff_prepared"
        for review in reviews
    )


def test_gp012_filter_by_preparation_state():
    reviews = (
        filter_owner_intent_review_packets(
            preparation_state="prepared"
        )
    )

    assert reviews

    assert all(
        review.preparation_state
        == "prepared"
        for review in reviews
    )


def test_gp012_unknown_review_fails_closed():
    with pytest.raises(KeyError):
        get_owner_intent_review_packet(
            "missing-review"
        )


def test_gp012_packet_payload_is_json_ready():
    payload = (
        get_owner_intent_review_packet_payload(
            "workspace-now-focus"
        )
    )

    assert payload["item_id"] == (
        "workspace-now-focus"
    )

    assert isinstance(
        payload["requirements"],
        list,
    )

    assert isinstance(
        payload["blockers"],
        list,
    )

    assert (
        payload["decision"]
        == "undecided"
    )

    assert (
        payload["tower_request_created"]
        is False
    )


def test_gp012_surface_payload_is_json_ready():
    payload = (
        get_owner_intent_review_surface_payload()
    )

    assert payload["review_count"] == 18

    assert isinstance(
        payload["reviews"],
        list,
    )

    assert (
        "does not mean approved"
        in payload["boundary_notice"].lower()
    )


def test_gp012_surface_counts_are_consistent():
    surface = (
        get_owner_intent_review_surface()
    )

    assert surface.review_count == 18

    assert (
        surface.prepared_count
        + surface.blocked_count
        <= surface.review_count
    )

    assert (
        surface.tower_prepared_count
        > 0
    )


def test_gp012_status_is_ready_and_safe():
    status = (
        get_clouds_gp012_status_payload()
    )

    assert status["pack"] == "GP012"

    assert status["section"] == (
        "EXECUTIVE OWNER ACTION INTENT REVIEW "
        "/ HANDOFF PREPARATION SURFACE"
    )

    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["review_count"] == 18

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
        status["tower_request_created"]
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
        "GP013 — EXECUTIVE OWNER HANDOFF "
        "REQUEST DRAFT / TOWER DELIVERY "
        "ENVELOPE SURFACE"
    )


def test_gp012_no_cross_app_python_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root
        / "clouds"
        / "executive_owner_action_intent_review.py",
        root
        / "clouds"
        / "executive_owner_action_intent_review_service.py",
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


def test_gp012_surface_is_repeatable():
    first = (
        get_owner_intent_review_surface_payload()
    )

    second = (
        get_owner_intent_review_surface_payload()
    )

    assert first == second
