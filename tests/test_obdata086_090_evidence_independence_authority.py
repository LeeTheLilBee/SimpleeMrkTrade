from __future__ import annotations

from pathlib import Path

import pytest

from web.ob_evidence_independence import (
    CorroborationIntegrityState,
    DependencyReason,
    DependencyState,
    EvidenceOriginIdentity,
    assess_corroboration_weight_integrity,
    assess_pairwise_independence,
    build_evidence_origin_identity,
    compose_independence_groups,
    corroboration_weight_snapshot,
    independent_confirmation_count,
)


ROOT = Path(__file__).resolve().parents[1]

MODULE = ROOT / "web" / "ob_evidence_independence.py"

EVIDENCE = (
    ROOT
    / "ob_evidence"
    / "authority_foundation"
    / "obdata086_090_evidence_independence_authority.json"
)

HANDOFF = (
    ROOT
    / "ob_evidence"
    / "authority_foundation"
    / "obdata086_090_evidence_independence_authority_handoff.md"
)


def identity(
    *,
    observation_id: str,
    source_id: str,
    source_family_id: str,
    origin_family_id: str,
    independence_family_id: str,
    dependency_ids=(),
    dependency_known: bool = True,
    lineage_hash: str | None = None,
) -> EvidenceOriginIdentity:
    return build_evidence_origin_identity(
        observation_id=observation_id,
        observation_version=1,
        lineage_hash=(
            lineage_hash
            or f"lineage-{observation_id}"
        ),
        source_id=source_id,
        source_family_id=source_family_id,
        origin_family_id=origin_family_id,
        independence_family_id=independence_family_id,
        dependency_ids=dependency_ids,
        dependency_known=dependency_known,
    )


def test_obdata086_origin_identity_is_explicit_and_normalized():
    item = identity(
        observation_id="obs-1",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
        dependency_ids=(
            "upstream-2",
            "upstream-1",
            "upstream-1",
        ),
    )

    assert item.observation_id == "obs-1"
    assert item.observation_version == 1
    assert item.lineage_hash == "lineage-obs-1"
    assert item.source_id == "source-a"
    assert item.source_family_id == "family-a"
    assert item.origin_family_id == "origin-a"
    assert item.independence_family_id == "independent-a"
    assert item.dependency_ids == (
        "upstream-1",
        "upstream-2",
    )
    assert item.dependency_known is True


@pytest.mark.parametrize(
    "field",
    (
        "observation_id",
        "lineage_hash",
        "source_id",
        "source_family_id",
        "origin_family_id",
        "independence_family_id",
    ),
)
def test_obdata086_required_identity_fields_reject_blank(field):
    kwargs = dict(
        observation_id="obs-1",
        observation_version=1,
        lineage_hash="lineage-1",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
    )

    kwargs[field] = " "

    with pytest.raises(ValueError):
        build_evidence_origin_identity(
            **kwargs
        )


def test_obdata086_version_must_be_positive():
    with pytest.raises(ValueError):
        build_evidence_origin_identity(
            observation_id="obs-1",
            observation_version=0,
            lineage_hash="lineage-1",
            source_id="source-a",
            source_family_id="family-a",
            origin_family_id="origin-a",
            independence_family_id="independent-a",
        )


def test_obdata087_distinct_families_are_pairwise_independent():
    left = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
    )

    right = identity(
        observation_id="obs-b",
        source_id="source-b",
        source_family_id="family-b",
        origin_family_id="origin-b",
        independence_family_id="independent-b",
    )

    assessment = assess_pairwise_independence(
        left=left,
        right=right,
    )

    assert assessment.state is DependencyState.INDEPENDENT
    assert (
        assessment.reason
        is DependencyReason.DISTINCT_INDEPENDENCE_FAMILY
    )


def test_obdata087_same_source_is_dependent():
    left = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
    )

    right = identity(
        observation_id="obs-b",
        source_id="source-a",
        source_family_id="family-b",
        origin_family_id="origin-b",
        independence_family_id="independent-b",
    )

    assessment = assess_pairwise_independence(
        left=left,
        right=right,
    )

    assert assessment.state is DependencyState.DEPENDENT
    assert assessment.reason is DependencyReason.SAME_SOURCE


def test_obdata087_same_source_family_is_dependent():
    left = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-shared",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
    )

    right = identity(
        observation_id="obs-b",
        source_id="source-b",
        source_family_id="family-shared",
        origin_family_id="origin-b",
        independence_family_id="independent-b",
    )

    assessment = assess_pairwise_independence(
        left=left,
        right=right,
    )

    assert assessment.state is DependencyState.DEPENDENT
    assert (
        assessment.reason
        is DependencyReason.SAME_SOURCE_FAMILY
    )


def test_obdata087_same_origin_family_is_dependent():
    left = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-shared",
        independence_family_id="independent-a",
    )

    right = identity(
        observation_id="obs-b",
        source_id="source-b",
        source_family_id="family-b",
        origin_family_id="origin-shared",
        independence_family_id="independent-b",
    )

    assessment = assess_pairwise_independence(
        left=left,
        right=right,
    )

    assert assessment.state is DependencyState.DEPENDENT
    assert (
        assessment.reason
        is DependencyReason.SAME_ORIGIN_FAMILY
    )


def test_obdata087_explicit_dependency_is_dependent():
    left = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
        dependency_ids=("root-feed",),
    )

    right = identity(
        observation_id="obs-b",
        source_id="source-b",
        source_family_id="family-b",
        origin_family_id="origin-b",
        independence_family_id="independent-b",
        dependency_ids=("root-feed",),
    )

    assessment = assess_pairwise_independence(
        left=left,
        right=right,
    )

    assert assessment.state is DependencyState.DEPENDENT
    assert (
        assessment.reason
        is DependencyReason.EXPLICIT_DEPENDENCY
    )


def test_obdata087_unknown_dependency_fails_closed_for_independence_credit():
    left = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
        dependency_known=False,
    )

    right = identity(
        observation_id="obs-b",
        source_id="source-b",
        source_family_id="family-b",
        origin_family_id="origin-b",
        independence_family_id="independent-b",
    )

    assessment = assess_pairwise_independence(
        left=left,
        right=right,
    )

    assert assessment.state is DependencyState.UNKNOWN
    assert (
        assessment.reason
        is DependencyReason.UNKNOWN_DEPENDENCY
    )


def test_obdata088_groups_are_deterministic():
    items = (
        identity(
            observation_id="obs-b",
            source_id="source-b",
            source_family_id="family-b",
            origin_family_id="origin-b",
            independence_family_id="family-2",
        ),
        identity(
            observation_id="obs-a",
            source_id="source-a",
            source_family_id="family-a",
            origin_family_id="origin-a",
            independence_family_id="family-1",
        ),
        identity(
            observation_id="obs-c",
            source_id="source-c",
            source_family_id="family-c",
            origin_family_id="origin-c",
            independence_family_id="family-1",
        ),
    )

    groups = compose_independence_groups(
        items
    )

    assert tuple(
        group.independence_family_id
        for group in groups
    ) == (
        "family-1",
        "family-2",
    )

    assert groups[0].observation_keys == (
        ("obs-a", 1),
        ("obs-c", 1),
    )


def test_obdata089_three_observations_same_family_count_once():
    items = (
        identity(
            observation_id="obs-a",
            source_id="source-a",
            source_family_id="family-a",
            origin_family_id="origin-a",
            independence_family_id="confirmation-family-1",
        ),
        identity(
            observation_id="obs-b",
            source_id="source-b",
            source_family_id="family-b",
            origin_family_id="origin-b",
            independence_family_id="confirmation-family-1",
        ),
        identity(
            observation_id="obs-c",
            source_id="source-c",
            source_family_id="family-c",
            origin_family_id="origin-c",
            independence_family_id="confirmation-family-1",
        ),
    )

    assessment = assess_corroboration_weight_integrity(
        items
    )

    assert assessment.state is CorroborationIntegrityState.VALID
    assert assessment.total_observations == 3
    assert assessment.independent_confirmation_count == 1
    assert assessment.dependent_observation_count == 2


def test_obdata089_three_distinct_independent_families_count_three():
    items = (
        identity(
            observation_id="obs-a",
            source_id="source-a",
            source_family_id="family-a",
            origin_family_id="origin-a",
            independence_family_id="independent-a",
        ),
        identity(
            observation_id="obs-b",
            source_id="source-b",
            source_family_id="family-b",
            origin_family_id="origin-b",
            independence_family_id="independent-b",
        ),
        identity(
            observation_id="obs-c",
            source_id="source-c",
            source_family_id="family-c",
            origin_family_id="origin-c",
            independence_family_id="independent-c",
        ),
    )

    assessment = assess_corroboration_weight_integrity(
        items
    )

    assert assessment.state is CorroborationIntegrityState.VALID
    assert assessment.independent_confirmation_count == 3
    assert assessment.dependent_observation_count == 0


def test_obdata089_unknown_dependency_receives_no_independent_credit():
    items = (
        identity(
            observation_id="obs-a",
            source_id="source-a",
            source_family_id="family-a",
            origin_family_id="origin-a",
            independence_family_id="independent-a",
        ),
        identity(
            observation_id="obs-b",
            source_id="source-b",
            source_family_id="family-b",
            origin_family_id="origin-b",
            independence_family_id="independent-b",
            dependency_known=False,
        ),
    )

    assessment = assess_corroboration_weight_integrity(
        items
    )

    assert (
        assessment.state
        is CorroborationIntegrityState.REVIEW_REQUIRED
    )

    assert assessment.independent_confirmation_count == 1
    assert assessment.unresolved_dependency_count == 1


def test_obdata089_cross_family_dependency_conflict_blocks_weight():
    items = (
        identity(
            observation_id="obs-a",
            source_id="source-a",
            source_family_id="shared-family",
            origin_family_id="origin-a",
            independence_family_id="declared-independent-a",
        ),
        identity(
            observation_id="obs-b",
            source_id="source-b",
            source_family_id="shared-family",
            origin_family_id="origin-b",
            independence_family_id="declared-independent-b",
        ),
    )

    assessment = assess_corroboration_weight_integrity(
        items
    )

    assert assessment.state is CorroborationIntegrityState.BLOCKED
    assert assessment.independent_confirmation_count == 0


def test_obdata089_exact_duplicate_blocks_weight():
    item = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
    )

    assessment = assess_corroboration_weight_integrity(
        (
            item,
            item,
        )
    )

    assert assessment.state is CorroborationIntegrityState.BLOCKED
    assert assessment.independent_confirmation_count == 0


def test_obdata089_empty_set_blocks_weight():
    assessment = assess_corroboration_weight_integrity(
        ()
    )

    assert assessment.state is CorroborationIntegrityState.BLOCKED
    assert assessment.independent_confirmation_count == 0


def test_obdata089_helper_never_counts_blocked_set():
    items = (
        identity(
            observation_id="obs-a",
            source_id="source-a",
            source_family_id="shared-family",
            origin_family_id="origin-a",
            independence_family_id="declared-a",
        ),
        identity(
            observation_id="obs-b",
            source_id="source-b",
            source_family_id="shared-family",
            origin_family_id="origin-b",
            independence_family_id="declared-b",
        ),
    )

    assert independent_confirmation_count(
        items
    ) == 0


def test_obdata090_snapshot_keeps_execution_authority_false():
    item = identity(
        observation_id="obs-a",
        source_id="source-a",
        source_family_id="family-a",
        origin_family_id="origin-a",
        independence_family_id="independent-a",
    )

    assessment = assess_corroboration_weight_integrity(
        (item,)
    )

    snapshot = corroboration_weight_snapshot(
        assessment
    )

    assert snapshot["state"] == "VALID"
    assert snapshot["independent_confirmation_count"] == 1

    boundary = snapshot["authority_boundary"]

    assert boundary["corroboration_counting_only"] is True
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_obdata090_evidence_and_handoff_exist():
    assert MODULE.is_file()
    assert EVIDENCE.is_file()
    assert HANDOFF.is_file()


def test_obdata090_evidence_declares_boundary():
    payload = __import__("json").loads(
        EVIDENCE.read_text(
            encoding="utf-8"
        )
    )

    assert payload["pack"] == "OBDATA086-090"
    assert payload["status"] in {
        "PENDING",
        "SEALED",
    }

    boundary = payload["authority_boundary"]

    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_obdata090_module_contains_no_execution_surface():
    source = MODULE.read_text(
        encoding="utf-8"
    ).lower()

    forbidden = (
        "placeorder(",
        "submitorder(",
        "executetrade(",
        "autoselectcontract(",
        "broker.submit(",
    )

    for token in forbidden:
        assert token not in source
