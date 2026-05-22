
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

from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
from tower.ob_privacy_wall_checkpoint import build_ob_privacy_wall_checkpoint


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    smoke = run_ob_privacy_wall_smoke()
    workflow = smoke.get("checks", {}).get("audited_ui_endpoint_workflow_ready")

    _print("PRIVACY WALL SMOKE WITH AUDITED UI ENDPOINT", {
        "ok": smoke.get("ok"),
        "failures": smoke.get("failures"),
        "audited_workflow": workflow,
        "checks": sorted(list(smoke.get("checks", {}).keys())),
    })

    assert smoke.get("ok") is True
    assert not smoke.get("failures")
    assert isinstance(workflow, dict)
    assert workflow.get("ok") is True

    detail = workflow.get("detail", {})
    assert detail.get("note_status") == 200
    assert detail.get("review_status") == 200
    assert detail.get("review_new_status") == "reviewing"
    assert detail.get("resolve_status") == 200
    assert detail.get("resolve_new_status") == "resolved"
    assert detail.get("resolve_reason") == "pack073_smoke_resolved"
    assert detail.get("bad_status") == 400
    assert detail.get("bad_reason") == "invalid_object_inbox_action_type"
    assert detail.get("missing_status") == 400
    assert detail.get("missing_reason") == "object_inbox_item_id_required"
    assert detail.get("receipt_ids_present") is True
    assert detail.get("no_secret_leakage") is True

    checkpoint = build_ob_privacy_wall_checkpoint()

    _print("PRIVACY WALL CHECKPOINT WITH AUDITED UI ENDPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "audited_ui_endpoint_workflow_ready": checkpoint.get("audited_ui_endpoint_workflow_ready"),
        "ui_action_audit_summary": checkpoint.get("ui_action_audit_summary"),
        "next_steps": checkpoint.get("next_steps"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("audited_ui_endpoint_workflow_ready", {}).get("ok") is True
    assert checkpoint.get("ui_action_audit_summary", {}).get("ok") is True
    assert checkpoint.get("ui_action_audit_summary", {}).get("total", 0) >= 5
    assert checkpoint.get("readiness_label") == "Ready to surface Archive Vault handoff summary"

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["071", "072", "073"]:
        assert pack in built

    next_steps = json.dumps(checkpoint.get("next_steps", []), sort_keys=True)
    assert "Surface Archive Vault handoff summary in Tower status/UI" in next_steps

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "073",
        "status": "passed",
        "human_reason": "Privacy wall smoke/checkpoint now prove audited object inbox UI endpoint workflow.",
    }
    _print("PACK 073 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
