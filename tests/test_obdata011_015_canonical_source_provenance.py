
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from web.ob_source_provenance import (
    ProvenanceStatus,
    SourceAuthority,
    SourceKind,
    attach_provenance,
    canonical_source,
    provenance_for,
)


UTC = timezone.utc


def test_obdata011_canonical_source_identity_is_explicit():
    source = canonical_source(
        source_id="market.primary",
        display_name="Primary Market Feed",
        source_kind=SourceKind.MARKET_DATA,
        authority=SourceAuthority.AUTHORITATIVE,
    )

    assert source.source_id == "market.primary"
    assert source.display_name == "Primary Market Feed"
    assert source.source_kind is SourceKind.MARKET_DATA
    assert source.authority is SourceAuthority.AUTHORITATIVE


def test_obdata011_source_identity_cannot_be_blank():
    with pytest.raises(ValueError):
        canonical_source(
            source_id="",
            display_name="Primary Feed",
            source_kind=SourceKind.MARKET_DATA,
            authority=SourceAuthority.AUTHORITATIVE,
        )

    with pytest.raises(ValueError):
        canonical_source(
            source_id="market.primary",
            display_name="",
            source_kind=SourceKind.MARKET_DATA,
            authority=SourceAuthority.AUTHORITATIVE,
        )


def test_obdata012_observation_and_retrieval_times_are_preserved():
    source = canonical_source(
        source_id="market.primary",
        display_name="Primary Market Feed",
        source_kind=SourceKind.MARKET_DATA,
        authority=SourceAuthority.AUTHORITATIVE,
    )

    observed = datetime(2026, 9, 14, 14, 0, tzinfo=UTC)
    retrieved = observed + timedelta(seconds=2)

    provenance = provenance_for(
        source=source,
        observed_at=observed,
        retrieved_at=retrieved,
        instrument="AAPL",
        provider_event_id="evt-123",
        sequence="991",
    )

    assert provenance.observed_at == observed
    assert provenance.retrieved_at == retrieved
    assert provenance.instrument == "AAPL"
    assert provenance.provider_event_id == "evt-123"
    assert provenance.sequence == "991"
    assert provenance.status is ProvenanceStatus.COMPLETE


def test_obdata012_naive_timestamps_are_rejected():
    source = canonical_source(
        source_id="market.primary",
        display_name="Primary Market Feed",
        source_kind=SourceKind.MARKET_DATA,
        authority=SourceAuthority.AUTHORITATIVE,
    )

    with pytest.raises(ValueError):
        provenance_for(
            source=source,
            observed_at=datetime(2026, 9, 14, 14, 0),
            retrieved_at=datetime(2026, 9, 14, 14, 0, tzinfo=UTC),
        )


def test_obdata012_retrieval_cannot_precede_observation():
    source = canonical_source(
        source_id="market.primary",
        display_name="Primary Market Feed",
        source_kind=SourceKind.MARKET_DATA,
        authority=SourceAuthority.AUTHORITATIVE,
    )

    observed = datetime(2026, 9, 14, 14, 0, 5, tzinfo=UTC)
    retrieved = datetime(2026, 9, 14, 14, 0, 4, tzinfo=UTC)

    with pytest.raises(ValueError):
        provenance_for(
            source=source,
            observed_at=observed,
            retrieved_at=retrieved,
        )


def test_obdata013_authority_is_data_authority_not_trade_authority():
    source = canonical_source(
        source_id="market.primary",
        display_name="Primary Market Feed",
        source_kind=SourceKind.MARKET_DATA,
        authority=SourceAuthority.AUTHORITATIVE,
    )

    observed = datetime(2026, 9, 14, 14, 0, tzinfo=UTC)

    wrapped = attach_provenance(
        241.55,
        provenance_for(
            source=source,
            observed_at=observed,
            retrieved_at=observed,
            instrument="AAPL",
        ),
    )

    payload = wrapped.as_dict()

    assert payload["value"] == 241.55
    assert payload["provenance"]["source"]["authority"] == "AUTHORITATIVE"

    # No execution authority is emitted by the provenance object.
    forbidden = {
        "submit_order",
        "broker_submission",
        "execute",
        "execution_authorized",
        "move_capital",
        "capital_authorized",
        "manual_live_authorized",
        "hybrid_authorized",
        "automated_authorized",
        "operating_mode",
        "mode_policy",
    }

    assert forbidden.isdisjoint(payload.keys())
    assert forbidden.isdisjoint(payload["provenance"].keys())


def test_obdata014_provenance_attachment_does_not_mutate_value():
    source = canonical_source(
        source_id="derived.candidate-score",
        display_name="OB Candidate Score",
        source_kind=SourceKind.DERIVED,
        authority=SourceAuthority.ADVISORY,
    )

    observed = datetime(2026, 9, 14, 14, 0, tzinfo=UTC)

    value = {
        "symbol": "AAPL",
        "score": 0.84,
        "direction": "CALL",
    }

    wrapped = attach_provenance(
        value,
        provenance_for(
            source=source,
            observed_at=observed,
            retrieved_at=observed,
            instrument="AAPL",
        ),
    )

    assert wrapped.value is value
    assert wrapped.value == value


def test_obdata015_no_default_or_implicit_operating_mode_is_introduced():
    import web.ob_source_provenance as provenance_module

    source_text = provenance_module.__file__

    module_text = open(source_text, "r", encoding="utf-8").read().lower()

    forbidden_literals = (
        "default_mode",
        "implicit_mode",
        "manual_live_authorized",
        "hybrid_execution",
        "automated_execution",
        "broker.submit",
        "submit_order(",
        "move_capital(",
    )

    for forbidden in forbidden_literals:
        assert forbidden not in module_text
