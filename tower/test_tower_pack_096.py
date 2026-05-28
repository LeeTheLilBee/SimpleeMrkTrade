
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.secrets_vault_boundary import (
    DEFAULT_SECRET_POLICY,
    audit_tower_secret_storage_boundary,
    get_secret_reference,
    inspect_payload_for_secret_boundary,
    make_secret_reference_id,
    register_secret_reference,
    request_secret_status,
    reset_secrets_boundary_for_test,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_no_secret_material(payload):
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "tower_keycard=",
        "should_not_survive",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
    ]
    for item in forbidden:
        assert item not in serialized, item


def run_tests():
    reset = reset_secrets_boundary_for_test()
    _print("RESET SECRETS BOUNDARY", reset)
    assert reset.get("ok") is True

    ref_id = make_secret_reference_id(
        app_id="observatory",
        secret_type="broker_api_key",
        alias="interactive_brokers_paper",
    )
    _print("SECRET REFERENCE ID", {"secret_ref_id": ref_id})
    assert ref_id.startswith("secret_ref_observatory_broker_api_key_interactive_brokers_paper_")

    rejected = register_secret_reference(
        app_id="observatory",
        secret_type="broker_api_key",
        alias="interactive_brokers_live",
        actor_user_id="owner_solice",
        raw_secret_value="SHOULD_NOT_SURVIVE_RAW_BROKER_SECRET",
        metadata={
            "raw_token": "SHOULD_NOT_SURVIVE",
            "api_key": "SHOULD_NOT_SURVIVE",
            "pack": "096",
        },
    )
    _print("RAW SECRET REJECTED", rejected)

    assert rejected.get("ok") is False
    assert rejected.get("decision") == "reject_raw_secret"
    assert rejected.get("reason_code") == "tower_cannot_store_raw_secret_value"
    _assert_no_secret_material(rejected)

    broker_ref = register_secret_reference(
        app_id="observatory",
        secret_type="broker_api_key",
        alias="interactive_brokers_paper",
        actor_user_id="owner_solice",
        secret_status="configured_external",
        allowed_actions=["status_check", "permission_check", "access_request", "rotation_request"],
        requires_step_up=True,
        notes="IBKR paper reference only. No raw credential stored.",
        metadata={
            "environment": "paper",
            "raw_token": "SHOULD_NOT_SURVIVE",
            "tower_keycard": "SHOULD_NOT_SURVIVE",
        },
    )
    _print("BROKER SECRET REFERENCE REGISTERED", broker_ref)

    assert broker_ref.get("ok") is True
    assert broker_ref.get("decision") == "secret_reference_registered"
    assert broker_ref.get("reference", {}).get("tower_stores_raw_secret") is False
    assert broker_ref.get("reference", {}).get("external_vault_required") is True
    assert broker_ref.get("reference", {}).get("secrets_vault_is_source_of_truth") is True
    _assert_no_secret_material(broker_ref)

    github_ref = register_secret_reference(
        app_id="tower",
        secret_type="github_token",
        alias="repo_push_token",
        actor_user_id="owner_solice",
        secret_status="external_rotation_required",
        allowed_actions=["status_check", "permission_check", "rotation_request"],
        requires_step_up=True,
        notes="GitHub token reference only.",
        metadata={"provider": "github", "github_token": "ghp_SHOULD_NOT_SURVIVE"},
    )
    _print("GITHUB SECRET REFERENCE REGISTERED", github_ref)

    assert github_ref.get("ok") is True
    assert github_ref.get("reference", {}).get("secret_type") == "github_token"
    _assert_no_secret_material(github_ref)

    payment_ref = register_secret_reference(
        app_id="teller",
        secret_type="payment_processor_secret",
        alias="stripe_live_key",
        actor_user_id="owner_solice",
        secret_status="not_configured",
        allowed_actions=["status_check", "permission_check", "access_request"],
        requires_step_up=True,
        notes="Stripe secret reference only.",
        metadata={"provider": "stripe", "stripe_secret": "sk_live_SHOULD_NOT_SURVIVE"},
    )
    _print("PAYMENT SECRET REFERENCE REGISTERED", payment_ref)

    assert payment_ref.get("ok") is True
    assert payment_ref.get("reference", {}).get("app_id") == "teller"
    _assert_no_secret_material(payment_ref)

    found = get_secret_reference(broker_ref.get("secret_ref_id"))
    _print("GET SECRET REFERENCE", found)

    assert found.get("ok") is True
    assert found.get("reference", {}).get("secret_ref_id") == broker_ref.get("secret_ref_id")
    assert found.get("reference", {}).get("tower_stores_raw_secret") is False
    _assert_no_secret_material(found)

    missing = get_secret_reference("secret_ref_missing_096")
    _print("MISSING SECRET REFERENCE", missing)

    assert missing.get("ok") is False
    assert missing.get("decision") == "secret_reference_missing"

    status = request_secret_status(
        secret_ref_id=broker_ref.get("secret_ref_id"),
        actor_user_id="owner_solice",
        app_id="observatory",
        action="status_check",
        metadata={"access_token": "SHOULD_NOT_SURVIVE", "reason": "test status"},
    )
    _print("SECRET STATUS REQUEST", status)

    assert status.get("ok") is True
    assert status.get("decision") == "status_only"
    assert status.get("vault_status", {}).get("tower_has_raw_secret") is False
    assert status.get("vault_status", {}).get("external_vault_required") is True
    assert status.get("vault_status", {}).get("secrets_vault_is_source_of_truth") is True
    assert status.get("vault_status", {}).get("raw_value") is None
    _assert_no_secret_material(status)

    unsupported = request_secret_status(
        secret_ref_id=broker_ref.get("secret_ref_id"),
        actor_user_id="owner_solice",
        app_id="observatory",
        action="return_raw_secret",
        metadata={"password": "SHOULD_NOT_SURVIVE"},
    )
    _print("UNSUPPORTED SECRET ACTION DENIED", unsupported)

    assert unsupported.get("ok") is False
    assert unsupported.get("decision") == "deny"
    assert unsupported.get("reason_code") == "unsupported_secret_boundary_action"
    _assert_no_secret_material(unsupported)

    payload_scan = inspect_payload_for_secret_boundary({
        "safe": "hello",
        "raw_token": "SHOULD_NOT_SURVIVE",
        "nested": {
            "github_token": "ghp_SHOULD_NOT_SURVIVE",
            "notes": "keep this",
        },
        "list": [
            {"api_key": "SHOULD_NOT_SURVIVE"},
            {"public": "ok"},
        ],
    })
    _print("PAYLOAD SECRET INSPECTION", payload_scan)

    assert payload_scan.get("ok") is True
    assert payload_scan.get("original_had_secret_material") is True
    assert payload_scan.get("forbidden_after_sanitize", {}).get("ok") is True
    _assert_no_secret_material(payload_scan)

    audit = audit_tower_secret_storage_boundary(limit=50)
    _print("SECRETS BOUNDARY AUDIT", audit)

    assert audit.get("ok") is True
    assert audit.get("readiness_score") == 100
    assert audit.get("readiness_label") == "Secrets Vault separation boundary ready"
    assert audit.get("secret_reference_count") == 3
    assert audit.get("policy", {}).get("tower_may_store_raw_value") is False
    assert audit.get("policy", {}).get("secrets_vault_is_source_of_truth") is True
    assert audit.get("no_secret_material_leakage") is True
    assert audit.get("by_app", {}).get("observatory", 0) >= 1
    assert audit.get("by_app", {}).get("tower", 0) >= 1
    assert audit.get("by_app", {}).get("teller", 0) >= 1
    _assert_no_secret_material(audit)

    assert DEFAULT_SECRET_POLICY["raw_secret_storage_allowed"] is False
    assert DEFAULT_SECRET_POLICY["tower_may_store_raw_value"] is False
    assert DEFAULT_SECRET_POLICY["secrets_vault_is_source_of_truth"] is True

    final = {
        "pack": "096",
        "status": "passed",
        "human_reason": "Secrets Vault separation boundary rejects raw secrets, stores references only, returns status-only metadata, and audits no raw secret leakage.",
    }
    _print("PACK 096 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
