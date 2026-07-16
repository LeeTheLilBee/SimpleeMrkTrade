from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path

from tower.tower_ob_managed_staging_provider_authorization import (
    REQUIRED_CAPABILITIES,
    build_owner_authorization_challenge,
    freeze_provider_authorization_packet,
    provider_input_template,
)
from tower.tower_ob_managed_staging_no_call_provisioning_review import (
    REQUIRED_REVIEW_ATTESTATIONS,
    build_authorization_handoff,
    no_call_review_input_template,
)
from tower.tower_ob_managed_staging_provider_provisioning_authorization import (
    AUTHORIZE_DECISION as AUTHORIZE_PREPARATION,
    REQUIRED_SCOPE_ATTESTATIONS,
    build_completed_review_handoff,
    build_provisioning_authorization_challenge,
    provisioning_authorization_decision_template,
)
from tower.tower_ob_managed_staging_no_call_provisioning_execution_preparation import (
    REQUIRED_PREPARATION_ATTESTATIONS,
    build_provisioning_authorization_handoff,
    execution_preparation_input_template,
)
from tower.tower_ob_managed_staging_provider_provisioning_execution_authorization import (
    AUTHORIZE_DECISION,
    REQUIRED_EXECUTION_SCOPE_ATTESTATIONS,
    build_completed_execution_preparation_handoff,
    build_execution_authorization_challenge,
    execution_authorization_decision_template,
)
from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_preparation import (
    NON_SECRET_ENVIRONMENT_NAMES,
    READY_DECISION,
    REQUIRED_SESSION_PREPARATION_ATTESTATIONS,
    SECRET_REFERENCE_NAMES,
    blank_current_inputs,
    build_controlled_session_preparation_decision,
    build_current_controlled_session_preparation_state,
    build_duplicate_resource_lookup_preflight,
    build_environment_and_secret_registration_sequence,
    build_execution_authorization_handoff,
    build_inert_session_opening_authorization_plan,
    build_one_service_shell_request,
    build_operational_control_rehearsal,
    build_provider_session_identity_binding,
    build_receipt_chain_and_stop_gate,
    controlled_session_preparation_input_template,
    freeze_controlled_session_preparation_packet,
    validate_controlled_session_preparation_inputs,
    write_controlled_session_preparation_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "0e1bb39ae7e388ff6897ee82b2da12072c856333"


def _complete_provider_inputs() -> dict:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "managed-host-session-preparation",
        "account_or_team_ref": "simplee-staging-team",
        "deployment_region": "us-east-session-preparation",
        "billing_owner_ref": "simplee-owner-billing",
        "service_name": "simplee-tower-ob-staging",
        "repository_ref": "LeeTheLilBee/SimpleeMrkTrade",
        "source_branch": "tower-ob-integration-dev",
    })
    payload["capability_attestations"] = {
        name: True for name in REQUIRED_CAPABILITIES
    }
    return payload


def _complete_review_owner_decision(provider_inputs: dict) -> dict:
    frozen = freeze_provider_authorization_packet(ROOT, provider_inputs)
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"]
    )
    return {
        "decision": "APPROVE_FOR_PROVISIONING_REVIEW",
        "owner_id": "tower-owner-review",
        "tower_step_up_receipt_ref": "tower-step-up-review-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:05:00Z",
    }


def _complete_review_inputs(provider_inputs: dict, owner_decision: dict) -> dict:
    handoff = build_authorization_handoff(
        ROOT, provider_inputs, owner_decision
    )
    payload = no_call_review_input_template(handoff)
    payload.update({
        "provider_documentation_ref": "provider-docs/python-service",
        "account_access_evidence_ref": "review/account-access",
        "region_availability_evidence_ref": "review/region-availability",
        "cost_review_ref": "review/staging-cost-boundary",
        "secret_store_evidence_ref": "provider-docs/secret-store",
        "health_check_evidence_ref": "provider-docs/health-checks",
        "deployment_logging_evidence_ref": "provider-docs/deployment-logs",
        "access_logging_evidence_ref": "provider-docs/access-logs",
        "rollback_evidence_ref": "provider-docs/rollback",
        "reviewed_by": "tower-owner-review",
        "reviewed_at": "2026-07-16T16:06:00Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_REVIEW_ATTESTATIONS
    }
    return payload


def _complete_provisioning_decision(handoff: dict) -> dict:
    challenge = build_provisioning_authorization_challenge(handoff)
    payload = provisioning_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_PREPARATION,
        "owner_id": "tower-owner-provisioning",
        "tower_step_up_receipt_ref": "tower-step-up-provisioning-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:07:00Z",
        "authorization_expires_at": "2026-07-16T18:07:00Z",
        "monthly_cost_ceiling_usd": "100.00",
    })
    payload["authorized_scope"] = {
        "provider_console_access": True,
        "create_one_managed_web_service": True,
        "configure_non_secret_environment_names": True,
        "register_secret_references_without_readback": True,
        "configure_health_checks": True,
        "configure_deployment_and_access_logs": True,
        "configure_manual_deployment_control": True,
        "configure_rollback_target": True,
    }
    payload["scope_attestations"] = {
        name: True for name in REQUIRED_SCOPE_ATTESTATIONS
    }
    return payload


def _complete_execution_preparation_inputs(handoff: dict) -> dict:
    payload = execution_preparation_input_template(handoff)
    payload.update({
        "provider_console_session_ref": "prep/provider-console-session",
        "provider_service_form_ref": "prep/one-service-form",
        "source_commit_ref": f"commit/{SOURCE_COMMIT}",
        "runtime_review_ref": "prep/runtime-target-review",
        "environment_name_review_ref": "prep/environment-name-review",
        "secret_reference_custody_ref": "prep/secret-reference-custody",
        "health_logging_review_ref": "prep/health-logging-review",
        "rollback_review_ref": "prep/rollback-review",
        "cost_guardrail_review_ref": "prep/cost-guardrail-review",
        "idempotency_guard_ref": "prep/idempotency-guard-review",
        "prepared_by": "tower-owner-preparation",
        "prepared_at": "2026-07-16T16:08:00Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_PREPARATION_ATTESTATIONS
    }
    return payload


def _complete_execution_authorization(
    handoff: dict,
    provisioning: dict,
    execution_preparation: dict,
) -> dict:
    challenge = build_execution_authorization_challenge(handoff)
    payload = execution_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_DECISION,
        "owner_id": "tower-owner-execution",
        "tower_step_up_receipt_ref": "tower-step-up-execution-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:09:00Z",
        "execution_window_starts_at": "2026-07-16T16:10:00Z",
        "execution_window_expires_at": "2026-07-16T17:10:00Z",
        "authorized_source_commit_ref": execution_preparation[
            "source_commit_ref"
        ],
        "monthly_cost_ceiling_usd": provisioning[
            "monthly_cost_ceiling_usd"
        ],
    })
    payload["authorized_scope"] = {
        "provider_console_login": True,
        "provider_account_team_access": True,
        "provider_region_access": True,
        "duplicate_resource_lookup": True,
        "create_one_inert_managed_web_service_shell": True,
        "bind_authorized_repository_branch_and_commit": True,
        "configure_non_secret_environment_names": True,
        "register_secret_references_without_readback": True,
        "configure_health_checks": True,
        "configure_deployment_and_access_logs": True,
        "configure_manual_deployment_control": True,
        "configure_rollback_target": True,
        "capture_non_secret_provider_resource_references": True,
    }
    payload["scope_attestations"] = {
        name: True for name in REQUIRED_EXECUTION_SCOPE_ATTESTATIONS
    }
    return payload


@lru_cache(maxsize=1)
def _cached_ready_execution_authorization() -> tuple:
    provider = _complete_provider_inputs()
    review_owner = _complete_review_owner_decision(provider)
    review = _complete_review_inputs(provider, review_owner)
    review_handoff = build_completed_review_handoff(
        ROOT, provider, review_owner, review
    )
    assert review_handoff["completed_review_ready"] is True
    provisioning = _complete_provisioning_decision(review_handoff)
    provisioning_handoff = build_provisioning_authorization_handoff(
        ROOT, provider, review_owner, review, provisioning
    )
    assert provisioning_handoff["handoff_ready"] is True
    execution_preparation = _complete_execution_preparation_inputs(
        provisioning_handoff
    )
    execution_preparation_handoff = (
        build_completed_execution_preparation_handoff(
            ROOT,
            provider,
            review_owner,
            review,
            provisioning,
            execution_preparation,
        )
    )
    assert execution_preparation_handoff[
        "completed_execution_preparation_ready"
    ] is True
    execution_authorization = _complete_execution_authorization(
        execution_preparation_handoff,
        provisioning,
        execution_preparation,
    )
    handoff = build_execution_authorization_handoff(
        ROOT,
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
    )
    assert handoff["execution_authorization_ready"] is True
    return (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        handoff,
    )


def _ready_execution_authorization() -> tuple:
    return copy.deepcopy(_cached_ready_execution_authorization())


def _complete_session_preparation(handoff: dict) -> dict:
    payload = controlled_session_preparation_input_template(handoff)
    payload.update({
        "owner_execution_session_receipt_ref": "tower/session-prep-receipt",
        "provider_console_access_preflight_ref": "session/provider-console-preflight",
        "provider_account_team_binding_ref": "session/account-team-binding",
        "provider_region_binding_ref": "session/region-binding",
        "duplicate_resource_lookup_plan_ref": "session/duplicate-lookup-plan",
        "service_creation_form_review_ref": "session/one-service-form-review",
        "repository_binding_review_ref": "session/repository-binding-review",
        "non_secret_environment_registration_review_ref": "session/environment-names-review",
        "secret_reference_registration_review_ref": "session/secret-reference-review",
        "health_logging_review_ref": "session/health-logging-review",
        "manual_deployment_control_review_ref": "session/manual-control-review",
        "rollback_review_ref": "session/rollback-review",
        "cost_ceiling_review_ref": "session/cost-ceiling-review",
        "receipt_chain_review_ref": "session/receipt-chain-review",
        "stop_conditions_review_ref": "session/stop-conditions-review",
        "prepared_by": "tower-owner-session-preparation",
        "prepared_at": "2026-07-16T16:09:30Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_SESSION_PREPARATION_ATTESTATIONS
    }
    return payload

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_authorization import (
    AUTHORIZE_DECISION as AUTHORIZE_SESSION_OPENING,
    READY_DECISION as SESSION_OPENING_READY,
    REQUIRED_OPENING_SCOPE_ATTESTATIONS,
    blank_current_inputs as blank_opening_inputs,
    build_completed_session_preparation_handoff,
    build_current_session_opening_authorization_state,
    build_inert_session_opening_preparation_plan,
    build_session_identity_and_window_manifest,
    build_session_opening_authorization_challenge,
    build_session_opening_authorization_decision,
    build_session_opening_receipt_and_stop_contract,
    build_session_opening_scope_manifest,
    freeze_session_opening_authorization_record,
    session_opening_authorization_decision_template,
    validate_session_opening_authorization_decision,
    write_session_opening_authorization_worksheets,
)


@lru_cache(maxsize=1)
def _cached_ready_session_preparation() -> tuple:
    (
        provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization, execution_handoff,
    ) = _cached_ready_execution_authorization()
    session_preparation = _complete_session_preparation(execution_handoff)
    handoff = build_completed_session_preparation_handoff(
        ROOT, provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization, session_preparation,
    )
    assert handoff["completed_session_preparation_ready"] is True
    return (
        provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization,
        session_preparation, handoff,
    )


def _ready_session_preparation() -> tuple:
    return copy.deepcopy(_cached_ready_session_preparation())


def _complete_opening_decision(handoff: dict) -> dict:
    challenge = build_session_opening_authorization_challenge(handoff)
    payload = session_opening_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_SESSION_OPENING,
        "owner_id": "tower-owner-session-opening",
        "tower_step_up_receipt_ref": "tower-step-up-session-opening-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:09:35Z",
        "authorization_expires_at": "2026-07-16T16:30:00Z",
    })
    payload["authorized_scope"] = {
        "open_one_manual_provider_console_session": True,
        "authenticate_to_bound_provider_account_team": True,
        "perform_duplicate_resource_lookup": True,
        "prepare_one_inert_managed_web_service_shell": True,
        "capture_non_secret_provider_references": True,
    }
    payload["scope_attestations"] = {
        name: True for name in REQUIRED_OPENING_SCOPE_ATTESTATIONS
    }
    return payload


def test_blank_completed_session_preparation_handoff_is_held():
    *inputs, _ = blank_opening_inputs(ROOT)
    handoff = build_completed_session_preparation_handoff(ROOT, *inputs)
    assert handoff["completed_session_preparation_ready"] is False
    assert handoff["provider_session_opened"] is False


def test_complete_session_preparation_handoff_is_ready_for_decision_only():
    *_, handoff = _ready_session_preparation()
    assert handoff["completed_session_preparation_ready"] is True
    assert handoff["provider_session_opening_authorized"] is False


def test_opening_challenge_is_bound_to_frozen_session_preparation():
    *_, handoff = _ready_session_preparation()
    challenge = build_session_opening_authorization_challenge(handoff)
    assert challenge["challenge_ready"] is True
    assert handoff["frozen_session_preparation_packet_hash"] in json.dumps(challenge)


def test_blank_template_defaults_to_hold_and_contains_no_secrets():
    *_, handoff = _ready_session_preparation()
    payload = session_opening_authorization_decision_template(handoff)
    assert payload["decision"] == "HOLD"
    assert "ghp_" not in json.dumps(payload).lower()


def test_blank_opening_decision_fails_closed():
    *_, handoff = _ready_session_preparation()
    report = validate_session_opening_authorization_decision(
        session_opening_authorization_decision_template(handoff), handoff=handoff
    )
    assert report["valid"] is False


def test_complete_opening_decision_validates():
    *_, handoff = _ready_session_preparation()
    report = validate_session_opening_authorization_decision(
        _complete_opening_decision(handoff), handoff=handoff
    )
    assert report["valid"] is True
    assert report["errors"] == []


def test_owner_step_up_receipt_is_required():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["tower_step_up_receipt_ref"] = ""
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_exact_challenge_phrase_is_required():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["challenge_phrase_confirmation"] = "WRONG"
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_frozen_session_preparation_hash_binding_is_required():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["frozen_session_preparation_packet_hash"] = "0" * 64
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_session_preparation_decision_hash_binding_is_required():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["session_preparation_decision_hash"] = "1" * 64
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_authorized_source_commit_binding_is_required():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["authorized_source_commit_ref"] = "commit/" + "2" * 40
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_session_window_must_match_frozen_preparation():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["authorized_session_expires_at"] = "2026-07-16T17:09:00Z"
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_authorization_expiry_must_be_inside_session_window():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["authorization_expires_at"] = "2026-07-16T18:00:00Z"
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_cost_ceiling_must_match_frozen_preparation():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["monthly_cost_ceiling_usd"] = "999.00"
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_all_opening_scope_attestations_are_required():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["scope_attestations"][REQUIRED_OPENING_SCOPE_ATTESTATIONS[0]] = False
    assert validate_session_opening_authorization_decision(payload, handoff=handoff)["valid"] is False


def test_sensitive_material_is_rejected():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["tower_step_up_receipt_ref"] = "password=hunter2"
    report = validate_session_opening_authorization_decision(payload, handoff=handoff)
    assert report["valid"] is False
    assert report["checks"]["contains_sensitive_material"] is True


def test_invalid_scope_manifest_authorizes_nothing():
    manifest = build_session_opening_scope_manifest({"valid": False})
    assert not any(manifest["future_scope"].values())
    assert manifest["resource_ceiling"]["managed_web_service_shells"] == 0


def test_valid_scope_manifest_allows_only_later_one_service_scope():
    manifest = build_session_opening_scope_manifest({"valid": True})
    assert manifest["future_scope"]["open_one_manual_provider_console_session"] is True
    assert manifest["resource_ceiling"] == {"managed_web_service_shells": 1, "databases": 0, "object_storage_buckets": 0, "dns_changes": 0}
    assert manifest["provider_session_opened"] is False


def test_identity_window_manifest_records_fingerprints_not_raw_provider_values():
    *_, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    validation = validate_session_opening_authorization_decision(payload, handoff=handoff)
    manifest = build_session_identity_and_window_manifest(handoff, payload, validation)
    assert manifest["provider_slug_sha256"]
    assert manifest["raw_provider_values_recorded"] is False
    assert "managed-host-session-preparation" not in json.dumps(manifest)


def test_receipt_contract_stops_before_resource_creation_build_and_deploy():
    contract = build_session_opening_receipt_and_stop_contract()
    rendered = json.dumps(contract).lower()
    assert "stop_before_resource_creation_receipt" in rendered
    assert "build" in rendered and "deployment" in rendered


def test_frozen_opening_authorization_record_is_sanitized():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    frozen = freeze_session_opening_authorization_record(ROOT, *inputs, payload)
    assert frozen["authorization_valid"] is True
    assert frozen["raw_secret_values_recorded"] is False
    assert frozen["provider_session_opened"] is False


def test_frozen_record_has_stable_hash_binding():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    a = freeze_session_opening_authorization_record(ROOT, *inputs, payload)
    b = freeze_session_opening_authorization_record(ROOT, *inputs, payload)
    assert a["frozen_session_opening_authorization_record_hash"] == b["frozen_session_opening_authorization_record_hash"]


def test_blank_current_decision_preserves_prior_hold():
    inputs = blank_opening_inputs(ROOT)
    decision = build_session_opening_authorization_decision(ROOT, *inputs)
    assert decision["ready_for_separate_controlled_provider_session_opening_preparation"] is False
    assert decision["provider_session_opened"] is False


def test_complete_approval_opens_only_separate_opening_preparation():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    decision = build_session_opening_authorization_decision(ROOT, *inputs, payload)
    assert decision["final_decision"] == SESSION_OPENING_READY
    assert decision["ready_for_separate_controlled_provider_session_opening_preparation"] is True
    assert decision["resource_creation_authorized"] is False


def test_owner_rejection_is_fail_closed():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff); payload["decision"] = "REJECT"
    decision = build_session_opening_authorization_decision(ROOT, *inputs, payload)
    assert decision["ready_for_separate_controlled_provider_session_opening_preparation"] is False


def test_inert_opening_preparation_plan_invokes_nothing():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    plan = build_inert_session_opening_preparation_plan(ROOT, *inputs, payload)
    assert plan["dry_run_only"] is True
    assert plan["provider_cli_commands"] == []
    assert plan["provider_api_requests"] == []
    assert plan["browser_actions"] == []


def test_current_blank_state_closes_step_110_fail_closed():
    state = build_current_session_opening_authorization_state(ROOT, *blank_opening_inputs(ROOT))
    assert state["closed_through_step"] == 110
    assert state["session_opening_authorization_valid"] is False
    assert state["provider_session_opened"] is False


def test_current_complete_state_is_ready_for_separate_preparation_only():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    state = build_current_session_opening_authorization_state(ROOT, *inputs, payload)
    assert state["ready_for_separate_controlled_provider_session_opening_preparation"] is True
    assert state["provider_session_opened"] is False
    assert state["resources_created"] is False


def test_current_state_preserves_all_operational_locks():
    state = build_current_session_opening_authorization_state(ROOT, *blank_opening_inputs(ROOT))
    for key in ("resource_creation_authorized", "secret_reference_registration_authorized", "build_authorized", "deployment_authorized", "provider_session_opened", "provider_login_performed", "provider_calls_performed", "resources_created", "secrets_registered", "build_performed", "deployment_performed", "official_walkthrough_performed", "production_manual_live_authorized", "broker_submission_enabled", "real_capital_movement_enabled", "direct_vault_upload_enabled"):
        assert state[key] is False
    assert state["live_auto_locked"] is True


def test_opening_authorization_worksheets_are_written_outside_repo(tmp_path):
    result = write_session_opening_authorization_worksheets(tmp_path / "worksheets", repository_root=ROOT)
    assert Path(result["session_opening_authorization_decision_path"]).is_file()
    assert ROOT not in Path(result["session_opening_authorization_decision_path"]).parents


def test_opening_preparation_placeholder_defaults_to_hold(tmp_path):
    result = write_session_opening_authorization_worksheets(tmp_path / "worksheets", repository_root=ROOT)
    payload = json.loads(Path(result["session_opening_preparation_placeholder_path"]).read_text())
    assert payload["decision"] == "HOLD"
    assert payload["provider_session_opened"] is False


def test_worksheet_manifest_reports_no_actions(tmp_path):
    result = write_session_opening_authorization_worksheets(tmp_path / "worksheets", repository_root=ROOT)
    manifest = json.loads(Path(result["manifest_path"]).read_text())
    assert manifest["contains_secret_values"] is False
    assert manifest["provider_session_opened"] is False
    assert manifest["provider_calls_performed"] is False
    assert manifest["resources_created"] is False


def test_valid_decision_still_performs_no_provider_actions():
    *inputs, handoff = _ready_session_preparation()
    payload = _complete_opening_decision(handoff)
    decision = build_session_opening_authorization_decision(ROOT, *inputs, payload)
    for key in ("provider_session_opened", "provider_login_performed", "provider_calls_performed", "resources_created", "secrets_registered", "build_performed", "deployment_performed"):
        assert decision[key] is False


def test_future_resource_ceiling_never_authorizes_database_storage_or_dns():
    manifest = build_session_opening_scope_manifest({"valid": True})
    assert manifest["resource_ceiling"]["databases"] == 0
    assert manifest["resource_ceiling"]["object_storage_buckets"] == 0
    assert manifest["resource_ceiling"]["dns_changes"] == 0
