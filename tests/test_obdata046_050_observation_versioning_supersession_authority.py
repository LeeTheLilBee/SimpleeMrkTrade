from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from web.ob_observation_versioning import (
    ObservationVersion,
    SupersessionReason,
    VersionStatus,
    build_version_history,
    create_initial_version,
    current_observation,
    supersede_observation,
    supersession_chain,
    version_history_snapshot,
    version_status,
)


ROOT = Path(__file__).resolve().parents[1]


def initial():
    return create_initial_version(
        observation_id="obs-001",
        effective_state="TRUSTED",
        confidence="HIGH",
        lineage_hash="hash-v1",
    )


def second(prior=None):
    if prior is None:
        prior = initial()

    return supersede_observation(
        prior=prior,
        effective_state="CAUTION",
        confidence="MODERATE",
        lineage_hash="hash-v2",
        reason=SupersessionReason.FRESHER_EVIDENCE,
    )


def test_obdata046_version_identity():
    assert [item.value for item in VersionStatus] == [
        "CURRENT",
        "SUPERSEDED",
        "HISTORICAL",
        "UNKNOWN",
    ]

    assert [item.value for item in SupersessionReason] == [
        "FRESHER_EVIDENCE",
        "CORROBORATION_CHANGED",
        "QUALITY_CHANGED",
        "CONFLICT_CHANGED",
        "MANUAL_REVIEW",
        "OTHER",
        "UNKNOWN",
    ]


def test_obdata046_initial_version_is_version_one():
    item = initial()

    assert item.version == 1
    assert item.supersedes_version is None
    assert item.supersession_reason is None


def test_obdata047_versions_are_immutable():
    item = initial()

    with pytest.raises(FrozenInstanceError):
        item.effective_state = "CAUTION"


def test_obdata047_superseding_creates_new_object_not_mutation():
    first = initial()

    later = second(first)

    assert first.version == 1
    assert first.effective_state == "TRUSTED"
    assert first.lineage_hash == "hash-v1"

    assert later is not first
    assert later.version == 2
    assert later.effective_state == "CAUTION"
    assert later.lineage_hash == "hash-v2"


def test_obdata048_supersession_requires_explicit_prior_identity():
    first = initial()
    later = second(first)

    assert later.supersedes_version == 1
    assert (
        later.supersession_reason
        is SupersessionReason.FRESHER_EVIDENCE
    )


def test_obdata048_supersession_reason_without_predecessor_rejected():
    with pytest.raises(ValueError):
        ObservationVersion(
            observation_id="obs-001",
            version=2,
            effective_state="CAUTION",
            confidence="MODERATE",
            lineage_hash="hash-v2",
            supersession_reason=SupersessionReason.FRESHER_EVIDENCE,
        )


def test_obdata048_predecessor_without_reason_rejected():
    with pytest.raises(ValueError):
        ObservationVersion(
            observation_id="obs-001",
            version=2,
            effective_state="CAUTION",
            confidence="MODERATE",
            lineage_hash="hash-v2",
            supersedes_version=1,
        )


def test_obdata048_version_cannot_supersede_itself_or_future():
    with pytest.raises(ValueError):
        ObservationVersion(
            observation_id="obs-001",
            version=2,
            effective_state="CAUTION",
            confidence="MODERATE",
            lineage_hash="hash-v2",
            supersedes_version=2,
            supersession_reason=SupersessionReason.FRESHER_EVIDENCE,
        )


def test_obdata049_history_resolves_one_current_version():
    first = initial()
    later = second(first)

    history = build_version_history(
        [
            first,
            later,
        ]
    )

    assert history.current_version == 2
    assert current_observation(history) == later

    assert version_status(
        history,
        1,
    ) is VersionStatus.SUPERSEDED

    assert version_status(
        history,
        2,
    ) is VersionStatus.CURRENT


def test_obdata049_superseded_history_remains_present():
    first = initial()
    later = second(first)

    history = build_version_history(
        [
            first,
            later,
        ]
    )

    assert len(history.versions) == 2
    assert history.versions[0] == first
    assert history.versions[1] == later


def test_obdata049_supersession_chain_is_explicit():
    first = initial()
    v2 = second(first)

    v3 = supersede_observation(
        prior=v2,
        effective_state="TRUSTED",
        confidence="HIGH",
        lineage_hash="hash-v3",
        reason=SupersessionReason.CORROBORATION_CHANGED,
    )

    history = build_version_history(
        [
            first,
            v2,
            v3,
        ]
    )

    assert supersession_chain(history) == (
        (1, 2),
        (2, 3),
    )


def test_obdata049_mixed_observation_ids_rejected():
    a = initial()

    b = create_initial_version(
        observation_id="obs-002",
        effective_state="TRUSTED",
        confidence="HIGH",
        lineage_hash="other",
    )

    with pytest.raises(ValueError):
        build_version_history(
            [
                a,
                b,
            ]
        )


def test_obdata049_duplicate_versions_rejected():
    a = initial()

    duplicate = create_initial_version(
        observation_id="obs-001",
        effective_state="CAUTION",
        confidence="LOW",
        lineage_hash="duplicate",
    )

    with pytest.raises(ValueError):
        build_version_history(
            [
                a,
                duplicate,
            ]
        )


def test_obdata049_noncontiguous_history_rejected():
    first = initial()

    third = ObservationVersion(
        observation_id="obs-001",
        version=3,
        effective_state="CAUTION",
        confidence="LOW",
        lineage_hash="hash-v3",
        supersedes_version=2,
        supersession_reason=SupersessionReason.OTHER,
    )

    with pytest.raises(ValueError):
        build_version_history(
            [
                first,
                third,
            ]
        )


def test_obdata049_wrong_supersession_link_rejected():
    first = initial()

    v2 = ObservationVersion(
        observation_id="obs-001",
        version=2,
        effective_state="CAUTION",
        confidence="LOW",
        lineage_hash="hash-v2",
        supersedes_version=1,
        supersession_reason=SupersessionReason.OTHER,
    )

    v3 = ObservationVersion(
        observation_id="obs-001",
        version=3,
        effective_state="TRUSTED",
        confidence="HIGH",
        lineage_hash="hash-v3",
        supersedes_version=1,
        supersession_reason=SupersessionReason.OTHER,
    )

    with pytest.raises(ValueError):
        build_version_history(
            [
                first,
                v2,
                v3,
            ]
        )


def test_obdata049_snapshot_preserves_all_versions_and_current_truth():
    first = initial()
    later = second(first)

    history = build_version_history(
        [
            first,
            later,
        ]
    )

    snapshot = version_history_snapshot(
        history
    )

    assert snapshot["current_version"] == 2
    assert snapshot["current_effective_state"] == "CAUTION"
    assert snapshot["current_confidence"] == "MODERATE"

    assert snapshot["versions"][0]["status"] == "SUPERSEDED"
    assert snapshot["versions"][1]["status"] == "CURRENT"

    assert snapshot["versions"][0]["lineage_hash"] == "hash-v1"
    assert snapshot["versions"][1]["lineage_hash"] == "hash-v2"


def test_obdata049_empty_history_has_no_fake_current_version():
    history = build_version_history(
        []
    )

    assert history.current_version is None
    assert current_observation(history) is None


def test_obdata049_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_versioning.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
        "autoSelectContract(",
        "moveCapital(",
        "unlockHybrid(",
        "unlockAutomated(",
        "unlockManualLive(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata049_no_history_deletion_or_rewrite_api():
    source = (
        ROOT
        / "web/ob_observation_versioning.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "deleteVersion(",
        "rewriteVersion(",
        "replaceHistory(",
        "removeSuperseded(",
        "eraseVersion(",
        "mutatePrevious(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata050_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata046_050_observation_versioning_supersession_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata046_050_observation_versioning_supersession_authority_handoff.md"
    ).is_file()


def test_obdata050_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata046_050_observation_versioning_supersession_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"mode_policy_override": false' in evidence
    assert '"source_authority_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"corroboration_override": false' in evidence
    assert '"quality_override": false' in evidence
    assert '"anomaly_override": false' in evidence
    assert '"synthesis_override": false' in evidence
    assert '"conflict_resolution_override": false' in evidence
    assert '"lineage_override": false' in evidence
    assert '"retroactive_observation_mutation": false' in evidence
    assert '"delete_superseded_history": false' in evidence
    assert '"ambiguous_current_version": false' in evidence
