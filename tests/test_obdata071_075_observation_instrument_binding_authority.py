from datetime import date
from pathlib import Path

import pytest

from web.ob_observation_instrument_binding import (
    InstrumentKind,
    OptionRight,
    ScopeBindingState,
    ScopeReasoningEligibility,
    assess_instrument_binding,
    binding_snapshot,
    blocked_by_instrument_scope,
    build_instrument_identity,
    eligible_for_current_instrument_reasoning,
)


ROOT = Path(__file__).resolve().parents[1]


EXPIRY = date(2026, 9, 18)


def spy_equity():
    return build_instrument_identity(
        symbol="SPY",
        instrument_kind=InstrumentKind.ETF,
    )


def qqq_equity():
    return build_instrument_identity(
        symbol="QQQ",
        instrument_kind=InstrumentKind.ETF,
    )


def spy_call_650():
    return build_instrument_identity(
        symbol="SPY-20260918-C-650",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="SPY",
        option_right=OptionRight.CALL,
        strike=650.0,
        expiration=EXPIRY,
        contract_id="SPY|2026-09-18|C|650",
    )


def test_obdata071_identity_enums():
    assert [item.value for item in InstrumentKind] == [
        "EQUITY",
        "ETF",
        "OPTION",
        "INDEX",
        "FUTURE",
        "FOREX",
        "CRYPTO",
        "UNKNOWN",
    ]

    assert [item.value for item in OptionRight] == [
        "CALL",
        "PUT",
        "NOT_APPLICABLE",
        "UNKNOWN",
    ]

    assert [item.value for item in ScopeBindingState] == [
        "MATCH",
        "SYMBOL_MISMATCH",
        "UNDERLYING_MISMATCH",
        "INSTRUMENT_KIND_MISMATCH",
        "OPTION_RIGHT_MISMATCH",
        "STRIKE_MISMATCH",
        "EXPIRATION_MISMATCH",
        "CONTRACT_MISMATCH",
        "UNKNOWN",
    ]

    assert [item.value for item in ScopeReasoningEligibility] == [
        "ELIGIBLE",
        "INELIGIBLE",
        "UNKNOWN",
    ]


def test_obdata071_symbol_normalized():
    identity = build_instrument_identity(
        symbol=" spy ",
        instrument_kind="ETF",
    )

    assert identity.symbol == "SPY"
    assert identity.underlying_symbol == "SPY"


def test_obdata071_unknown_kind_rejected():
    with pytest.raises(ValueError):
        build_instrument_identity(
            symbol="SPY",
            instrument_kind="BANANA",
        )


def test_obdata072_exact_equity_scope_match():
    observation = spy_equity()
    target = spy_equity()

    result = assess_instrument_binding(
        observation=observation,
        target=target,
    )

    assert result.state is ScopeBindingState.MATCH
    assert (
        result.reasoning_eligibility
        is ScopeReasoningEligibility.ELIGIBLE
    )
    assert eligible_for_current_instrument_reasoning(result)
    assert not blocked_by_instrument_scope(result)


def test_obdata072_cross_symbol_bleed_blocked():
    result = assess_instrument_binding(
        observation=spy_equity(),
        target=qqq_equity(),
    )

    assert result.state is ScopeBindingState.SYMBOL_MISMATCH
    assert blocked_by_instrument_scope(result)
    assert not eligible_for_current_instrument_reasoning(result)


def test_obdata072_stock_option_substitution_blocked():
    result = assess_instrument_binding(
        observation=spy_equity(),
        target=spy_call_650(),
    )

    assert result.state is ScopeBindingState.INSTRUMENT_KIND_MISMATCH
    assert blocked_by_instrument_scope(result)


def test_obdata073_option_requires_contract_identity():
    with pytest.raises(ValueError):
        build_instrument_identity(
            symbol="SPY-C",
            instrument_kind=InstrumentKind.OPTION,
            underlying_symbol="SPY",
            option_right=OptionRight.CALL,
            strike=650,
            expiration=EXPIRY,
            contract_id=None,
        )


def test_obdata073_option_requires_underlying():
    with pytest.raises(ValueError):
        build_instrument_identity(
            symbol="SPY-C",
            instrument_kind=InstrumentKind.OPTION,
            underlying_symbol="",
            option_right=OptionRight.CALL,
            strike=650,
            expiration=EXPIRY,
            contract_id="contract",
        )


def test_obdata073_option_requires_call_or_put():
    with pytest.raises(ValueError):
        build_instrument_identity(
            symbol="SPY-C",
            instrument_kind=InstrumentKind.OPTION,
            underlying_symbol="SPY",
            option_right=OptionRight.UNKNOWN,
            strike=650,
            expiration=EXPIRY,
            contract_id="contract",
        )


def test_obdata073_non_option_cannot_carry_contract_fields():
    with pytest.raises(ValueError):
        build_instrument_identity(
            symbol="SPY",
            instrument_kind=InstrumentKind.ETF,
            strike=650,
        )


def test_obdata073_call_put_substitution_blocked():
    observation = spy_call_650()

    target = build_instrument_identity(
        symbol="SPY-20260918-C-650",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="SPY",
        option_right=OptionRight.PUT,
        strike=650,
        expiration=EXPIRY,
        contract_id="SPY|2026-09-18|C|650",
    )

    result = assess_instrument_binding(
        observation=observation,
        target=target,
    )

    assert result.state is ScopeBindingState.OPTION_RIGHT_MISMATCH


def test_obdata073_strike_substitution_blocked():
    observation = spy_call_650()

    target = build_instrument_identity(
        symbol="SPY-20260918-C-650",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="SPY",
        option_right=OptionRight.CALL,
        strike=655,
        expiration=EXPIRY,
        contract_id="SPY|2026-09-18|C|650",
    )

    result = assess_instrument_binding(
        observation=observation,
        target=target,
    )

    assert result.state is ScopeBindingState.STRIKE_MISMATCH


def test_obdata073_expiration_substitution_blocked():
    observation = spy_call_650()

    target = build_instrument_identity(
        symbol="SPY-20260918-C-650",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="SPY",
        option_right=OptionRight.CALL,
        strike=650,
        expiration=date(2026, 9, 25),
        contract_id="SPY|2026-09-18|C|650",
    )

    result = assess_instrument_binding(
        observation=observation,
        target=target,
    )

    assert result.state is ScopeBindingState.EXPIRATION_MISMATCH


def test_obdata073_contract_id_substitution_blocked():
    observation = spy_call_650()

    target = build_instrument_identity(
        symbol="SPY-20260918-C-650",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="SPY",
        option_right=OptionRight.CALL,
        strike=650,
        expiration=EXPIRY,
        contract_id="different-contract-id",
    )

    result = assess_instrument_binding(
        observation=observation,
        target=target,
    )

    assert result.state is ScopeBindingState.CONTRACT_MISMATCH


def test_obdata074_underlying_mismatch_blocked():
    observation = build_instrument_identity(
        symbol="CONTRACT-X",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="SPY",
        option_right=OptionRight.CALL,
        strike=650,
        expiration=EXPIRY,
        contract_id="contract-x",
    )

    target = build_instrument_identity(
        symbol="CONTRACT-X",
        instrument_kind=InstrumentKind.OPTION,
        underlying_symbol="QQQ",
        option_right=OptionRight.CALL,
        strike=650,
        expiration=EXPIRY,
        contract_id="contract-x",
    )

    result = assess_instrument_binding(
        observation=observation,
        target=target,
    )

    assert result.state is ScopeBindingState.UNDERLYING_MISMATCH


def test_obdata074_exact_option_contract_matches():
    result = assess_instrument_binding(
        observation=spy_call_650(),
        target=spy_call_650(),
    )

    assert result.state is ScopeBindingState.MATCH
    assert eligible_for_current_instrument_reasoning(result)


def test_obdata074_snapshot_preserves_both_identities():
    result = assess_instrument_binding(
        observation=spy_equity(),
        target=qqq_equity(),
    )

    snapshot = binding_snapshot(
        result
    )

    assert snapshot["state"] == "SYMBOL_MISMATCH"
    assert snapshot["observation"]["symbol"] == "SPY"
    assert snapshot["target"]["symbol"] == "QQQ"


def test_obdata074_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_instrument_binding.py"
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


def test_obdata074_no_scope_override_or_substitution_api():
    source = (
        ROOT
        / "web/ob_observation_instrument_binding.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "ignoreSymbolMismatch(",
        "forceInstrumentMatch(",
        "reuseAcrossSymbol(",
        "reuseAcrossContract(",
        "substituteStrike(",
        "substituteExpiration(",
        "substituteOptionRight(",
        "promoteUnderlyingToContract(",
        "promoteContractToUnderlying(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata075_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata071_075_observation_instrument_binding_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata071_075_observation_instrument_binding_authority_handoff.md"
    ).is_file()


def test_obdata075_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata071_075_observation_instrument_binding_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"contract_auto_selection": false' in evidence
    assert '"manual_live_unlock": false' in evidence
    assert '"hybrid_execution": false' in evidence
    assert '"automated_execution": false' in evidence

    assert '"mode_policy_override": false' in evidence
    assert '"source_authority_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"corroboration_override": false' in evidence
    assert '"quality_override": false' in evidence
    assert '"anomaly_override": false' in evidence
    assert '"synthesis_override": false' in evidence
    assert '"conflict_resolution_override": false' in evidence
    assert '"lineage_override": false' in evidence
    assert '"lifecycle_override": false' in evidence
    assert '"revocation_override": false' in evidence
    assert '"rehabilitation_override": false' in evidence
    assert '"temporal_override": false' in evidence

    assert '"symbol_substitution": false' in evidence
    assert '"underlying_substitution": false' in evidence
    assert '"stock_option_substitution": false' in evidence
    assert '"option_right_substitution": false' in evidence
    assert '"strike_substitution": false' in evidence
    assert '"expiration_substitution": false' in evidence
    assert '"cross_contract_promotion": false' in evidence
