
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

from tower.ui_endpoint_archive_transition_checkpoint import build_ui_endpoint_archive_transition_checkpoint


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    checkpoint = build_ui_endpoint_archive_transition_checkpoint()

    _print("UI ENDPOINT / ARCHIVE TRANSITION CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "proof": checkpoint.get("proof"),
        "dashboard_summary": checkpoint.get("dashboard_summary"),
        "next_block": checkpoint.get("next_block"),
        "current_boundary": checkpoint.get("current_boundary"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("readiness_label") == "Ready for audited form wiring and receipt dashboard"
    assert checkpoint.get("no_secret_leakage") is True

    proof = checkpoint.get("proof", {})
    required_true = [
        "smoke_ok",
        "privacy_checkpoint_ok",
        "audited_ui_endpoint_workflow_ready",
        "ui_action_audit_ok",
        "ui_action_audit_total_present",
        "ui_action_successes_present",
        "ui_action_failures_present",
        "archive_handoff_ok",
        "archive_handoff_total_present",
        "archive_handoff_queued_present",
        "object_inbox_ok",
        "tower_status_has_archive",
        "tower_status_has_archive_total",
        "dashboard_ok",
        "dashboard_has_object_forms",
        "dashboard_has_archive_panel",
        "dashboard_html_ok",
    ]

    for key in required_true:
        assert proof.get(key) is True, key

    # This is allowed to be false until Pack 076.
    assert "dashboard_has_audited_endpoint" in proof

    ui_summary = checkpoint.get("ui_action_audit_summary", {})
    assert ui_summary.get("ok") is True
    assert ui_summary.get("total", 0) >= 1
    assert ui_summary.get("action_ok", 0) >= 1
    assert ui_summary.get("action_failed", 0) >= 1

    archive_summary = checkpoint.get("archive_vault_handoff_summary", {})
    assert archive_summary.get("ok") is True
    assert archive_summary.get("total", 0) >= 1
    assert archive_summary.get("queued", 0) >= 1

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["071", "072", "073", "074", "075"]:
        assert pack in built

    next_block = json.dumps(checkpoint.get("next_block", []), sort_keys=True)
    for pack in ["076", "077", "078", "079", "080"]:
        assert pack in next_block

    boundary = json.dumps(checkpoint.get("current_boundary", {}), sort_keys=True)
    assert "Security Command forms still point at the original /action endpoint" in boundary
    assert "Older privacy-wall deny paths have not all been replaced" in boundary

    serialized = json.dumps(checkpoint, sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "075",
        "status": "passed",
        "human_reason": "UI endpoint and Archive Vault surfacing block is closed and ready for audited form wiring.",
    }
    _print("PACK 075 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
