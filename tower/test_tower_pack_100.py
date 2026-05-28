
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

from tower.tower_fortress_readiness_checkpoint import (
    FORTRESS_CHECKPOINT_PATH,
    FORTRESS_PANEL_PATH,
    FORTRESS_PROOF_BUNDLE_PATH,
    FORTRESS_DOMAINS,
    build_tower_fortress_checkpoint,
    build_tower_fortress_proof_bundle,
    reset_tower_fortress_checkpoint_for_test,
    summarize_tower_fortress_checkpoint,
    write_tower_fortress_readiness_panel,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_no_secret_leakage(payload):
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
    reset = reset_tower_fortress_checkpoint_for_test()
    _print("RESET FORTRESS CHECKPOINT", reset)

    assert reset.get("ok") is True
    assert len(FORTRESS_DOMAINS) == 10
    assert "secrets_boundary" in FORTRESS_DOMAINS
    assert "redaction_reveal" in FORTRESS_DOMAINS
    assert "security_rehearsal" in FORTRESS_DOMAINS
    assert "owner_admin_receipts" in FORTRESS_DOMAINS

    checkpoint = build_tower_fortress_checkpoint(actor_user_id="owner_solice", write_panel=True)
    _print("TOWER FORTRESS CHECKPOINT", checkpoint)

    assert checkpoint.get("pack") == "100"
    assert checkpoint.get("readiness_score", 0) >= 90
    assert checkpoint.get("readiness_label") in {
        "Tower fortress ready for OB integration",
        "Tower fortress needs review before OB integration",
    }
    assert checkpoint.get("no_secret_leakage") is True
    assert checkpoint.get("leakage_scan", {}).get("ok") is True
    assert FORTRESS_CHECKPOINT_PATH.exists()
    assert FORTRESS_PROOF_BUNDLE_PATH.exists()
    assert FORTRESS_PANEL_PATH.exists()

    readiness_items = checkpoint.get("readiness_items", {})
    assert isinstance(readiness_items, dict)
    assert len(readiness_items) == 10

    required_ready = [
        "tamper_chain",
        "step_up",
        "lockdown",
        "quarantine",
        "risk_scoring",
        "secrets_boundary",
        "redaction_reveal",
        "security_rehearsal",
        "owner_admin_receipts",
    ]
    for domain in required_ready:
        assert domain in readiness_items, domain
        assert readiness_items[domain].get("score", 0) >= 50, domain

    # These late fortress domains must be fully ready because we just passed 096–099.
    for domain in ["secrets_boundary", "redaction_reveal", "security_rehearsal", "owner_admin_receipts"]:
        assert readiness_items[domain].get("ok") is True, domain
        assert readiness_items[domain].get("score") == 100, domain

    assert checkpoint.get("module_status", {}).get("ok") is True
    assert checkpoint.get("required_data_status", {}).get("present_count", 0) >= 12

    ob_gate = checkpoint.get("ob_integration_gate", {})
    assert isinstance(ob_gate, dict)
    assert "safe_next_step" in ob_gate
    assert "OB/Tower bridge" in ob_gate.get("safe_next_step", "")

    _assert_no_secret_leakage(checkpoint)

    bundle = build_tower_fortress_proof_bundle(checkpoint=checkpoint)
    _print("TOWER FORTRESS PROOF BUNDLE", bundle)

    assert bundle.get("pack") == "100"
    assert bundle.get("checkpoint_id") == checkpoint.get("checkpoint_id")
    assert bundle.get("readiness_score") == checkpoint.get("readiness_score")
    assert bundle.get("no_secret_leakage") is True
    assert "before_ob_integration_statement" in bundle
    assert len(bundle.get("included_domains", [])) == 10
    _assert_no_secret_leakage(bundle)

    panel = write_tower_fortress_readiness_panel(checkpoint)
    _print("TOWER FORTRESS PANEL", panel)

    assert panel.get("ok") is True
    assert FORTRESS_PANEL_PATH.exists()

    html = FORTRESS_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · Fortress Readiness Checkpoint" in html
    assert "Secrets Vault separation boundary" in html
    assert "Owner/admin action receipts" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    summary = summarize_tower_fortress_checkpoint()
    _print("TOWER FORTRESS SUMMARY", summary)

    assert summary.get("pack") == "100"
    assert summary.get("readiness_score", 0) >= 90
    assert summary.get("summary_no_secret_leakage") is True
    assert summary.get("leakage_scan", {}).get("ok") is True
    _assert_no_secret_leakage(summary)

    final = {
        "pack": "100",
        "status": "passed",
        "human_reason": "Final Tower fortress readiness checkpoint and before-OB-integration proof bundle completed.",
    }
    _print("PACK 100 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
