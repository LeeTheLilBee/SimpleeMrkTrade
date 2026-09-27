"""First Manual Live L1 lifecycle is source-only and not a self-granted toggle."""
from web.ob_manual_live_beta_gate_report import REQUIRED_EXTERNAL_GATES
from web.ob_manual_live_l1_phase_contract import (
    AFTER_HUMAN_ORDER, BEFORE_EACH_HUMAN_ORDER, BEFORE_L1_MODE_ACCESS,
    owner_l1_first_live_phase_contract,
)


def test_obml021_every_existing_external_gate_has_an_explicit_lifecycle_phase():
    known = {key for key, _description in REQUIRED_EXTERNAL_GATES}
    assert set(BEFORE_L1_MODE_ACCESS + BEFORE_EACH_HUMAN_ORDER + AFTER_HUMAN_ORDER) == known
    report = owner_l1_first_live_phase_contract()
    assert report["all_external_gate_ids_covered"] is True
    assert len(report["phase_records"]) == 3
    assert all(item["action_allowed"] is False for item in report["phase_records"])


def test_obml022_first_review_access_does_not_require_an_impossible_preexisting_fill():
    report = owner_l1_first_live_phase_contract()
    first, order, last = report["phase_records"]
    assert first["phase"] == "MODE_ACCESS"
    assert "EXTERNAL_MANUAL_ORDER_RECONCILIATION" not in first["required_gate_ids"]
    assert "EXTERNAL_MANUAL_ORDER_RECONCILIATION" not in order["required_gate_ids"]
    assert last["phase"] == "POST_ORDER_RECONCILIATION"
    assert last["required_gate_ids"] == ("EXTERNAL_MANUAL_ORDER_RECONCILIATION",)
    assert last["state"] == "NOT_DUE_BEFORE_HUMAN_BROKER_PLACEMENT"
    assert report["post_fill_reconciliation_is_still_mandatory"] is True


def test_obml023_review_grant_alone_never_authorizes_any_human_broker_order():
    report = owner_l1_first_live_phase_contract()
    assert report["mode_permission_is_not_order_permission"] is True
    assert report["each_order_requires_a_new_owner_review_and_fresh_rechecks"] is True
    assert "HUMAN_REVIEW_CENTER_DECISION" in BEFORE_EACH_HUMAN_ORDER
    for gate in (
        "PROVIDER_ACCOUNT_AND_OPTIONS_PERMISSIONS",
        "PROVIDER_SETTLEMENT_AND_PROTECTED_FLOORS",
        "CURRENT_SOURCE_RISK_AND_MARKET",
    ):
        assert gate in BEFORE_L1_MODE_ACCESS
        assert gate in BEFORE_EACH_HUMAN_ORDER
    assert report["execution_model"] == "HUMAN_PLACES_ORDER_AT_INDEPENDENT_BROKER_ONLY"


def test_obml024_no_rehearsal_namespace_or_tower_generic_step_up_can_self_grant_live():
    report = owner_l1_first_live_phase_contract()
    for flag in (
        "signed_namespace_is_tower_owner_grant",
        "generic_tower_step_up_is_obml_purpose_step_up",
        "simulation_or_beta_checklist_is_live_permission",
        "actual_tower_issuer_receiver_verified",
        "authenticated_broker_options_and_capital_verified",
        "real_manual_live_activated",
        "broker_api_order_submission",
        "automatic_contract_selection",
        "hybrid_or_automated_execution",
        "protected_floor_release",
        "capital_movement",
        "tester_manual_live_access",
        "direct_buybox_balance_access",
    ):
        assert report[flag] is False


def test_obml025_source_report_cannot_accept_user_provided_verified_toggle():
    report = owner_l1_first_live_phase_contract()
    assert report["source_only_not_an_activation_endpoint"] is True
    assert "verified" not in owner_l1_first_live_phase_contract.__code__.co_varnames
    assert report["phase_records"][0]["state"].startswith("HOLD")
    assert report["phase_records"][1]["state"].startswith("HOLD")
