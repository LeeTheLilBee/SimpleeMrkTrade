from __future__ import annotations

import json
from pathlib import Path

from tower.tower_ob_managed_staging_provider_authorization import (
    OWNER_APPROVAL_DECISION,
    OWNER_HOLD_DECISION,
    OWNER_REJECT_DECISION,
    REQUIRED_CAPABILITIES,
    build_account_team_binding,
    build_billing_boundary,
    build_capability_attestation_record,
    build_current_provider_authorization_state,
    build_no_call_provisioning_readiness,
    build_owner_authorization_challenge,
    build_owner_authorization_record,
    build_provider_selection_record,
    build_region_binding,
    build_secret_custody_plan,
    freeze_provider_authorization_packet,
    owner_decision_template,
    provider_input_template,
    validate_owner_decision,
    validate_provider_inputs,
    write_bound_owner_decision_worksheet,
    write_operator_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]


def complete_provider_inputs() -> dict[str, object]:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "provider-example",
        "account_or_team_ref": "simplee-world-staging-team",
        "deployment_region": "us-example-1",
        "billing_owner_ref": "simplee-world-owner-billing",
        "service_name": "simplee-tower-ob-staging",
        "repository_ref": "LeeTheLilBee/SimpleeMrkTrade",
        "source_branch": "tower-ob-integration-dev",
    })
    payload["capability_attestations"] = {
        name: True for name in REQUIRED_CAPABILITIES
    }
    return payload


def complete_owner_decision(
    provider_inputs: dict[str, object],
) -> dict[str, str]:
    frozen = freeze_provider_authorization_packet(
        ROOT,
        provider_inputs,
    )
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"],
    )
    return {
        "decision": OWNER_APPROVAL_DECISION,
        "owner_id": "simplee_owner",
        "tower_step_up_receipt_ref": "tower-step-up-receipt-example",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T15:30:00Z",
    }


def test_provider_template_contains_no_secret_values():
    template = provider_input_template()
    rendered = json.dumps(template).lower()

    assert template["runtime_target"] == "web.managed_staging:app"
    assert template["provider_slug"] == ""
    assert "api_key=" not in rendered
    assert "postgresql://" not in rendered


def test_blank_provider_inputs_fail_closed():
    report = validate_provider_inputs(provider_input_template())

    assert report["valid"] is False
    assert report["error_count"] > 0
    assert report["raw_values_returned"] is False


def test_complete_provider_inputs_validate():
    report = validate_provider_inputs(complete_provider_inputs())

    assert report["valid"] is True
    assert report["error_count"] == 0
    assert report["attested_required_capability_count"] == len(
        REQUIRED_CAPABILITIES
    )


def test_sensitive_material_is_rejected():
    payload = complete_provider_inputs()
    payload["account_or_team_ref"] = "token=do-not-record-this"

    report = validate_provider_inputs(payload)

    assert report["valid"] is False
    assert report["sensitive_material_detected"] is True


def test_provider_selection_record_fingerprints_values():
    payload = complete_provider_inputs()
    record = build_provider_selection_record(payload)
    rendered = json.dumps(record)

    assert record["selection_valid"] is True
    assert payload["provider_slug"] not in rendered
    assert record["raw_provider_name_recorded"] is False


def test_capability_record_requires_all_attestations():
    payload = complete_provider_inputs()
    payload["capability_attestations"][
        "rollback_support"
    ] = False

    record = build_capability_attestation_record(payload)

    assert record["all_required_capabilities_attested"] is False
    assert record["provider_calls_authorized"] is False


def test_account_binding_records_only_fingerprints():
    payload = complete_provider_inputs()
    record = build_account_team_binding(payload)
    rendered = json.dumps(record)

    assert record["binding_complete"] is True
    assert payload["account_or_team_ref"] not in rendered
    assert record["production_resource_binding_authorized"] is False


def test_region_binding_does_not_claim_provider_verification():
    record = build_region_binding(complete_provider_inputs())

    assert record["region_binding_ready_for_review"] is True
    assert record["region_verified_against_provider"] is False
    assert record["provider_calls_authorized"] is False


def test_billing_boundary_blocks_automatic_spend():
    record = build_billing_boundary(complete_provider_inputs())

    assert record["billing_owner_reference_present"] is True
    assert record["automatic_scale_up_authorized"] is False
    assert record["resource_creation_authorized"] is False


def test_secret_custody_plan_prohibits_git_values():
    plan = build_secret_custody_plan()

    assert plan["rules"]["raw_secret_values_in_git"] is False
    assert plan["rules"]["production_secret_reuse_in_staging"] is False
    assert plan["secrets_created"] is False


def test_frozen_packet_is_hash_bound_and_sanitized():
    payload = complete_provider_inputs()
    packet = freeze_provider_authorization_packet(ROOT, payload)
    rendered = json.dumps(packet)

    assert packet["provider_inputs_valid"] is True
    assert packet["frozen"] is True
    assert len(packet["frozen_packet_hash"]) == 64
    assert payload["provider_slug"] not in rendered
    assert packet["provider_calls_authorized"] is False


def test_owner_template_defaults_to_hold():
    frozen = freeze_provider_authorization_packet(
        ROOT,
        complete_provider_inputs(),
    )
    template = owner_decision_template(frozen)

    assert template["decision"] == OWNER_HOLD_DECISION
    assert template["owner_id"] == ""
    assert "AUTHORIZE TOWER OB" in template[
        "expected_challenge_phrase"
    ]


def test_owner_approval_requires_tower_step_up_binding():
    payload = complete_provider_inputs()
    frozen = freeze_provider_authorization_packet(ROOT, payload)
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"],
    )
    decision = complete_owner_decision(payload)
    decision["tower_step_up_receipt_ref"] = ""

    report = validate_owner_decision(
        decision,
        challenge=challenge,
    )

    assert report["approval_valid"] is False
    assert report["checks"][
        "tower_step_up_receipt_ref_present"
    ] is False


def test_owner_approval_requires_exact_challenge_phrase():
    payload = complete_provider_inputs()
    frozen = freeze_provider_authorization_packet(ROOT, payload)
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"],
    )
    decision = complete_owner_decision(payload)
    decision["challenge_phrase_confirmation"] = "wrong"

    report = validate_owner_decision(
        decision,
        challenge=challenge,
    )

    assert report["approval_valid"] is False
    assert report["checks"]["challenge_phrase_matches"] is False


def test_complete_owner_approval_opens_only_separate_review():
    inputs = complete_provider_inputs()
    decision = complete_owner_decision(inputs)
    record = build_owner_authorization_record(
        ROOT,
        inputs,
        decision,
    )

    assert record["owner_approval_valid"] is True
    assert record[
        "ready_for_separate_no_call_provisioning_review"
    ] is True
    assert record["final_decision"] == (
        "READY_FOR_SEPARATE_NO_CALL_PROVISIONING_REVIEW"
    )
    assert record["provider_calls_authorized"] is False
    assert record["resource_creation_authorized"] is False
    assert record["deployment_authorized"] is False


def test_owner_rejection_is_fail_closed():
    inputs = complete_provider_inputs()
    decision = complete_owner_decision(inputs)
    decision["decision"] = OWNER_REJECT_DECISION

    record = build_owner_authorization_record(
        ROOT,
        inputs,
        decision,
    )

    assert record["owner_approval_valid"] is False
    assert record["final_decision"] == (
        "NO_GO_OWNER_REJECTED_PROVIDER_AUTHORIZATION"
    )


def test_no_call_readiness_plan_is_inert():
    inputs = complete_provider_inputs()
    decision = complete_owner_decision(inputs)
    plan = build_no_call_provisioning_readiness(
        ROOT,
        inputs,
        decision,
    )

    assert plan[
        "ready_for_separate_no_call_provisioning_review"
    ] is True
    assert plan["dry_run_only"] is True
    assert plan["shell_invoked"] is False
    assert plan["provider_api_invoked"] is False
    assert plan["resources_created"] is False
    assert plan["deployment_performed"] is False
    assert plan["live_auto_locked"] is True


def test_current_blank_state_remains_held():
    state = build_current_provider_authorization_state(
        ROOT,
        provider_input_template(),
        {},
    )

    assert state["closed_through_step"] == 50
    assert state["provider_inputs_valid"] is False
    assert state["owner_approval_valid"] is False
    assert state["provider_calls_authorized"] is False
    assert state["final_decision"] == (
        "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    )


def test_operator_worksheets_are_written_outside_repo(tmp_path):
    manifest = write_operator_worksheets(
        tmp_path,
        repository_root=ROOT,
    )

    for path in manifest.values():
        assert Path(path).is_file()

    provider_payload = json.loads(
        Path(manifest["provider_input_path"]).read_text(
            encoding="utf-8"
        )
    )
    owner_payload = json.loads(
        Path(manifest["owner_decision_path"]).read_text(
            encoding="utf-8"
        )
    )

    assert provider_payload["provider_slug"] == ""
    assert owner_payload["decision"] == OWNER_HOLD_DECISION
    assert owner_payload["challenge_ready"] is False
    assert owner_payload["challenge_id"] == ""


def test_bound_owner_worksheet_uses_valid_provider_packet(tmp_path):
    inputs = complete_provider_inputs()
    output = tmp_path / "owner.json"

    written = write_bound_owner_decision_worksheet(
        output,
        repository_root=ROOT,
        provider_inputs=inputs,
    )
    payload = json.loads(written.read_text(encoding="utf-8"))

    assert payload["challenge_ready"] is True
    assert payload["challenge_id"]
    assert "AUTHORIZE TOWER OB" in payload[
        "expected_challenge_phrase"
    ]
