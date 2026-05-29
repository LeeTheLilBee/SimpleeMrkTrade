
from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def show(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def no_secret(payload):
    s = json.dumps(payload, sort_keys=True, default=str).lower()
    bad = [
        "should_not_survive",
        "tower_keycard=",
        '"raw_token":',
        '"api_key":',
        '"password":',
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
    ]
    for item in bad:
        assert item not in s, item


def run_tests():
    from tower.ob_object_permission_tightening import (
        OBJECT_EVENTS_PATH,
        OBJECT_PANEL_PATH,
        OBJECT_POLICY_PATH,
        OBJECT_STATUS_PATH,
        check_export_permission,
        check_position_permission,
        check_symbol_permission,
        check_trade_permission,
        evaluate_ob_object_permission,
        initialize_object_permission_policy,
        reset_ob_object_permissions_for_test,
        summarize_ob_object_permissions,
    )

    reset = reset_ob_object_permissions_for_test()
    show("RESET OBJECT PERMISSIONS", reset)
    assert reset.get("ok") is True

    policy = initialize_object_permission_policy()
    show("OBJECT PERMISSION POLICY", policy)

    assert policy.get("object_permissions_enabled") is True
    assert policy.get("export_policy", {}).get("requires_step_up") is True
    assert policy.get("live_mode_policy", {}).get("locked_until_compliance") is True
    assert OBJECT_POLICY_PATH.exists()
    no_secret(policy)

    symbol = check_symbol_permission(
        user_id="public_user",
        role="public",
        symbol="aapl",
        metadata={"raw_token": "SHOULD_NOT_SURVIVE"},
    )
    show("SYMBOL PERMISSION", symbol)

    assert symbol.get("decision") == "allow"
    assert symbol.get("allowed") is True
    assert symbol.get("object_id") == "AAPL"
    no_secret(symbol)

    owner_position = check_position_permission(
        user_id="owner_solice",
        role="owner",
        position_id="pos_108_owner",
        action="view",
        object_payload={"owner_user_id": "someone_else", "private_notes": "secret position notes"},
    )
    show("OWNER POSITION PERMISSION", owner_position)

    assert owner_position.get("decision") == "allow"
    assert owner_position.get("allowed") is True
    no_secret(owner_position)

    beta_own_position = check_position_permission(
        user_id="beta_user_108",
        role="beta",
        position_id="pos_108_beta",
        action="view",
        object_payload={"owner_user_id": "beta_user_108"},
    )
    show("BETA OWN POSITION PERMISSION", beta_own_position)

    assert beta_own_position.get("decision") == "allow"
    assert beta_own_position.get("allowed") is True
    no_secret(beta_own_position)

    beta_other_position = check_position_permission(
        user_id="beta_user_108",
        role="beta",
        position_id="pos_108_other",
        action="view",
        object_payload={"owner_user_id": "other_user_108"},
    )
    show("BETA OTHER POSITION DENIED", beta_other_position)

    assert beta_other_position.get("decision") == "deny"
    assert beta_other_position.get("allowed") is False
    assert beta_other_position.get("reason_code") == "position_owner_mismatch"
    no_secret(beta_other_position)

    beta_close_own_position = check_position_permission(
        user_id="beta_user_108",
        role="beta",
        position_id="pos_108_beta",
        action="close",
        object_payload={"owner_user_id": "beta_user_108"},
    )
    show("BETA CLOSE OWN POSITION STEP-UP", beta_close_own_position)

    assert beta_close_own_position.get("decision") == "step_up_required"
    assert beta_close_own_position.get("requires_step_up") is True
    assert beta_close_own_position.get("requires_receipt") is True
    no_secret(beta_close_own_position)

    owner_trade = check_trade_permission(
        user_id="owner_solice",
        role="owner",
        trade_id="trade_108",
        action="view",
        object_payload={"owner_user_id": "other_user_108"},
    )
    show("OWNER TRADE PERMISSION", owner_trade)

    assert owner_trade.get("decision") == "allow"
    assert owner_trade.get("allowed") is True
    no_secret(owner_trade)

    beta_other_trade = check_trade_permission(
        user_id="beta_user_108",
        role="beta",
        trade_id="trade_108_other",
        action="view",
        object_payload={"owner_user_id": "other_user_108"},
    )
    show("BETA OTHER TRADE DENIED", beta_other_trade)

    assert beta_other_trade.get("decision") == "deny"
    assert beta_other_trade.get("reason_code") == "trade_owner_mismatch"
    no_secret(beta_other_trade)

    owner_export = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_108",
        action="export",
        object_payload={"document_text": "Sensitive export text should redact."},
    )
    show("OWNER EXPORT STEP-UP", owner_export)

    assert owner_export.get("decision") == "step_up_required"
    assert owner_export.get("requires_step_up") is True
    assert owner_export.get("requires_receipt") is True
    assert owner_export.get("requires_archive_handoff") is True
    no_secret(owner_export)

    beta_export = check_export_permission(
        user_id="beta_user_108",
        role="beta",
        export_id="export_108_beta",
        action="export",
    )
    show("BETA EXPORT DENIED", beta_export)

    assert beta_export.get("decision") == "deny"
    assert beta_export.get("reason_code") == "export_owner_only"
    no_secret(beta_export)

    admin_object = evaluate_ob_object_permission(
        user_id="owner_solice",
        role="owner",
        object_type="admin_panel",
        object_id="tower_admin_panel_108",
        action="view",
    )
    show("ADMIN OBJECT STEP-UP", admin_object)

    assert admin_object.get("decision") == "step_up_required"
    assert admin_object.get("requires_step_up") is True
    assert admin_object.get("requires_receipt") is True
    no_secret(admin_object)

    live_mode = evaluate_ob_object_permission(
        user_id="owner_solice",
        role="owner",
        object_type="mode",
        object_id="live_manual",
        action="enable",
    )
    show("LIVE MODE OBJECT DENIED", live_mode)

    assert live_mode.get("decision") == "deny"
    assert live_mode.get("reason_code") == "live_mode_object_locked_until_compliance"
    no_secret(live_mode)

    analysis = evaluate_ob_object_permission(
        user_id="beta_user_108",
        role="beta",
        object_type="analysis",
        object_id="analysis_108",
        action="view",
    )
    show("ANALYSIS SUMMARY ONLY", analysis)

    assert analysis.get("decision") == "summary_only"
    assert analysis.get("requires_summary_only") is True
    no_secret(analysis)

    status = summarize_ob_object_permissions(limit=120)
    show("OBJECT PERMISSION STATUS", status)

    assert status.get("ok") is True
    assert status.get("readiness_score") == 100
    assert status.get("readiness_label") == "OB object-level permission tightening ready"
    assert status.get("event_count", 0) >= 11
    assert status.get("by_object_type", {}).get("symbol", 0) >= 1
    assert status.get("by_object_type", {}).get("position", 0) >= 4
    assert status.get("by_object_type", {}).get("trade", 0) >= 2
    assert status.get("by_object_type", {}).get("export", 0) >= 2
    assert status.get("by_decision", {}).get("allow", 0) >= 4
    assert status.get("by_decision", {}).get("deny", 0) >= 4
    assert status.get("by_decision", {}).get("step_up_required", 0) >= 3
    assert status.get("by_decision", {}).get("summary_only", 0) >= 1
    assert status.get("no_secret_leakage") is True
    assert OBJECT_EVENTS_PATH.exists()
    assert OBJECT_STATUS_PATH.exists()
    assert OBJECT_PANEL_PATH.exists()
    no_secret(status)

    panel = OBJECT_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · OB Object Permissions" in panel
    assert "SHOULD_NOT_SURVIVE" not in panel
    assert "tower_keycard=" not in panel

    for path in [
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_108.py",
        PROJECT_ROOT / "web" / "app.py",
    ]:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        show("PY_COMPILE " + str(path), {
            "returncode": result.returncode,
            "stderr": result.stderr,
        })
        assert result.returncode == 0

    final = {
        "pack": "108",
        "status": "passed",
        "event_count": status.get("event_count"),
        "human_reason": "OB object-level permission tightening is ready for symbols, positions, trades, exports, admin objects, analysis objects, and live mode objects.",
    }
    show("PACK 108 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
