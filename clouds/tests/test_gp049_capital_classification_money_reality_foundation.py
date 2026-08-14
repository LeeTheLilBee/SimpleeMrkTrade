import pytest

from clouds.capital_classification_service import (
    build_capital_entry,
    get_clouds_gp049_status_payload,
    get_gp049_certification_entries,
)


def test_gp049_certification_has_no_real_money():
    entries = (
        get_gp049_certification_entries()
    )

    assert len(entries) == 7

    assert all(
        item.source_claims_real
        is False
        for item in entries
    )

    assert all(
        item.reality
        != "verified_real"
        for item in entries
    )


def test_gp049_fake_real_without_connection_fails():
    with pytest.raises(ValueError):
        build_capital_entry(
            entry_id="bad",
            source_id="observatory",
            source_label="The Observatory",
            classification="available",
            reality="verified_real",
            amount_cents=100,
            source_claims_real=True,
        )


def test_gp049_verified_real_contract_can_accept_real_later():
    entry = build_capital_entry(
        entry_id="future-real-test",
        source_id="teller",
        source_label="The Teller",
        classification="available",
        reality="verified_real",
        amount_cents=100_00,
        source_claims_real=True,
        external_source_connected=True,
        external_connection_verified=True,
        certification_fixture_only=False,
        evidence_reference="test-reference",
    )

    assert (
        entry
        .counts_as_verified_real_available
        is True
    )

    assert (
        entry
        .counts_as_simulated
        is False
    )


def test_gp049_status():
    status = (
        get_clouds_gp049_status_payload()
    )

    assert status["status"] == "ready"

    assert (
        status["real_money_claimed"]
        is False
    )

    assert (
        status[
            "simulation_can_count_as_available"
        ]
        is False
    )
