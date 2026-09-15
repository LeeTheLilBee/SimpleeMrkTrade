from __future__ import annotations

import json
from pathlib import Path

import pytest

from web.ob_candidate_evidence_sufficiency import (
    SufficiencyReason,
    SufficiencyState,
    assess_candidate_evidence_sufficiency,
    assess_category_sufficiency,
    build_candidate_evidence_support,
    build_evidence_requirement,
    candidate_evidence_sufficiency_snapshot,
    sufficient_for_analytical_reasoning,
)


ROOT = Path(__file__).resolve().parents[1]

MODULE = (
    ROOT
    / "web"
    / "ob_candidate_evidence_sufficiency.py"
)

EVIDENCE = (
    ROOT
    / "ob_evidence"
    / "authority_foundation"
    / "obdata091_095_candidate_evidence_sufficiency_authority.json"
)

HANDOFF = (
    ROOT
    / "ob_evidence"
    / "authority_foundation"
    / "obdata091_095_candidate_evidence_sufficiency_authority_handoff.md"
)


def requirement(
    category: str,
    *,
    observations: int = 1,
    independent: int = 1,
    required: bool = True,
):
    return build_evidence_requirement(
        category=category,
        minimum_observations=observations,
        minimum_independent_confirmations=independent,
        required=required,
    )


def evidence(
    observation_id: str,
    category: str,
    family: str,
    *,
    dependency_known: bool = True,
):
    return build_candidate_evidence_support(
        observation_id=observation_id,
        observation_version=1,
        category=category,
        independence_family_id=family,
        dependency_known=dependency_known,
    )


def test_obdata091_requirement_normalizes_category():
    item = requirement(
        " price ",
        observations=2,
        independent=1,
    )

    assert item.category == "PRICE"
    assert item.minimum_observations == 2
    assert item.minimum_independent_confirmations == 1
    assert item.required is True


@pytest.mark.parametrize(
    ("observations", "independent"),
    (
        (0, 1),
        (1, 0),
        (1, 2),
    ),
)
def test_obdata091_invalid_requirement_rejected(
    observations,
    independent,
):
    with pytest.raises(ValueError):
        requirement(
            "PRICE",
            observations=observations,
            independent=independent,
        )


def test_obdata091_blank_category_rejected():
    with pytest.raises(ValueError):
        requirement(
            " ",
        )


def test_obdata092_category_coverage_counts_observations_and_families():
    req = requirement(
        "PRICE",
        observations=3,
        independent=2,
    )

    items = (
        evidence(
            "obs-1",
            "PRICE",
            "family-a",
        ),
        evidence(
            "obs-2",
            "PRICE",
            "family-a",
        ),
        evidence(
            "obs-3",
            "PRICE",
            "family-b",
        ),
    )

    assessment = assess_category_sufficiency(
        requirement=req,
        evidence=items,
    )

    assert assessment.observation_count == 3
    assert assessment.independent_confirmation_count == 2
    assert assessment.satisfied is True


def test_obdata092_wrong_category_does_not_satisfy_requirement():
    req = requirement(
        "PRICE",
    )

    items = (
        evidence(
            "obs-1",
            "VOLUME",
            "family-a",
        ),
    )

    assessment = assess_category_sufficiency(
        requirement=req,
        evidence=items,
    )

    assert assessment.observation_count == 0
    assert assessment.independent_confirmation_count == 0
    assert assessment.satisfied is False


def test_obdata093_raw_count_cannot_replace_independent_support():
    req = requirement(
        "PRICE",
        observations=3,
        independent=2,
    )

    items = (
        evidence(
            "obs-1",
            "PRICE",
            "same-family",
        ),
        evidence(
            "obs-2",
            "PRICE",
            "same-family",
        ),
        evidence(
            "obs-3",
            "PRICE",
            "same-family",
        ),
    )

    assessment = assess_category_sufficiency(
        requirement=req,
        evidence=items,
    )

    assert assessment.observation_count == 3
    assert assessment.independent_confirmation_count == 1
    assert assessment.satisfied is False


def test_obdata093_unknown_dependency_gets_no_independent_credit():
    req = requirement(
        "PRICE",
        observations=2,
        independent=2,
    )

    items = (
        evidence(
            "obs-1",
            "PRICE",
            "family-a",
        ),
        evidence(
            "obs-2",
            "PRICE",
            "family-b",
            dependency_known=False,
        ),
    )

    assessment = assess_category_sufficiency(
        requirement=req,
        evidence=items,
    )

    assert assessment.observation_count == 2
    assert assessment.independent_confirmation_count == 1
    assert assessment.unresolved_dependency_count == 1
    assert assessment.satisfied is False


def test_obdata094_all_required_categories_satisfied():
    requirements = (
        requirement(
            "PRICE",
            observations=2,
            independent=2,
        ),
        requirement(
            "LIQUIDITY",
            observations=1,
            independent=1,
        ),
    )

    items = (
        evidence(
            "price-1",
            "PRICE",
            "price-family-a",
        ),
        evidence(
            "price-2",
            "PRICE",
            "price-family-b",
        ),
        evidence(
            "liq-1",
            "LIQUIDITY",
            "liq-family-a",
        ),
    )

    assessment = assess_candidate_evidence_sufficiency(
        requirements=requirements,
        evidence=items,
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.SUFFICIENT
    assert (
        assessment.reason
        is SufficiencyReason.REQUIREMENTS_SATISFIED
    )

    assert sufficient_for_analytical_reasoning(
        assessment
    ) is True


def test_obdata094_missing_required_category_is_insufficient():
    requirements = (
        requirement(
            "PRICE",
        ),
        requirement(
            "LIQUIDITY",
        ),
    )

    items = (
        evidence(
            "price-1",
            "PRICE",
            "family-a",
        ),
    )

    assessment = assess_candidate_evidence_sufficiency(
        requirements=requirements,
        evidence=items,
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.INSUFFICIENT
    assert (
        assessment.reason
        is SufficiencyReason.REQUIRED_CATEGORY_MISSING
    )
    assert assessment.missing_required_categories == (
        "LIQUIDITY",
    )


def test_obdata094_missing_independent_support_is_insufficient():
    requirements = (
        requirement(
            "PRICE",
            observations=3,
            independent=2,
        ),
    )

    items = (
        evidence(
            "price-1",
            "PRICE",
            "same-family",
        ),
        evidence(
            "price-2",
            "PRICE",
            "same-family",
        ),
        evidence(
            "price-3",
            "PRICE",
            "same-family",
        ),
    )

    assessment = assess_candidate_evidence_sufficiency(
        requirements=requirements,
        evidence=items,
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.INSUFFICIENT
    assert (
        assessment.reason
        is SufficiencyReason.INDEPENDENT_SUPPORT_MISSING
    )
    assert assessment.insufficient_independent_categories == (
        "PRICE",
    )


def test_obdata094_blocked_independence_integrity_blocks_sufficiency():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="BLOCKED",
    )

    assert assessment.state is SufficiencyState.BLOCKED
    assert (
        assessment.reason
        is SufficiencyReason.INDEPENDENCE_INTEGRITY_BLOCKED
    )

    assert sufficient_for_analytical_reasoning(
        assessment
    ) is False


def test_obdata094_review_required_independence_cannot_become_sufficient():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="REVIEW_REQUIRED",
    )

    assert assessment.state is SufficiencyState.REVIEW_REQUIRED
    assert (
        assessment.reason
        is SufficiencyReason.INDEPENDENCE_REVIEW_REQUIRED
    )

    assert sufficient_for_analytical_reasoning(
        assessment
    ) is False


def test_obdata094_unknown_independence_fails_closed():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="UNKNOWN",
    )

    assert assessment.state is SufficiencyState.UNKNOWN

    assert sufficient_for_analytical_reasoning(
        assessment
    ) is False


def test_obdata094_unknown_dependency_cannot_establish_sufficiency():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
                observations=1,
                independent=1,
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
                dependency_known=False,
            ),
        ),
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.INSUFFICIENT
    assert (
        assessment.reason
        is SufficiencyReason.INDEPENDENT_SUPPORT_MISSING
    )

    assert sufficient_for_analytical_reasoning(
        assessment
    ) is False


def test_obdata094_empty_requirements_fail_closed():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.BLOCKED
    assert (
        assessment.reason
        is SufficiencyReason.EMPTY_REQUIREMENTS
    )


def test_obdata094_empty_evidence_is_insufficient():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
        ),
        evidence=(),
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.INSUFFICIENT
    assert (
        assessment.reason
        is SufficiencyReason.EMPTY_EVIDENCE
    )


def test_obdata094_duplicate_requirement_categories_fail_closed():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
            requirement(
                "price",
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.BLOCKED


def test_obdata094_optional_category_does_not_block_sufficiency():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
            requirement(
                "NEWS",
                required=False,
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="VALID",
    )

    assert assessment.state is SufficiencyState.SUFFICIENT


def test_obdata095_snapshot_preserves_authority_boundary():
    assessment = assess_candidate_evidence_sufficiency(
        requirements=(
            requirement(
                "PRICE",
            ),
        ),
        evidence=(
            evidence(
                "price-1",
                "PRICE",
                "family-a",
            ),
        ),
        independence_integrity_state="VALID",
    )

    snapshot = candidate_evidence_sufficiency_snapshot(
        assessment
    )

    assert snapshot["state"] == "SUFFICIENT"

    boundary = snapshot["authority_boundary"]

    assert boundary["analytical_reasoning_sufficiency_only"] is True
    assert boundary["analytical_conclusion"] is False
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_obdata095_evidence_and_handoff_exist():
    assert MODULE.is_file()
    assert EVIDENCE.is_file()
    assert HANDOFF.is_file()


def test_obdata095_evidence_declares_boundary():
    payload = json.loads(
        EVIDENCE.read_text(
            encoding="utf-8"
        )
    )

    assert payload["pack"] == "OBDATA091-095"

    assert payload["status"] in {
        "PENDING",
        "SEALED",
    }

    boundary = payload["authority_boundary"]

    assert boundary["analytical_conclusion"] is False
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_obdata095_module_contains_no_execution_surface():
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
