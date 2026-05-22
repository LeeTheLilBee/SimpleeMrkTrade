
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
    workflow = smoke.get("checks", {}).get("object_security_inbox_action_workflow")

    _print("UPDATED PRIVACY WALL SMOKE", {
        "ok": smoke.get("ok"),
        "failures": smoke.get("failures"),
        "workflow": workflow,
        "checks": sorted(list(smoke.get("checks", {}).keys())),
    })

    assert smoke.get("ok") is True
    assert not smoke.get("failures")
    assert isinstance(workflow, dict)
    assert workflow.get("ok") is True

    checkpoint = build_ob_privacy_wall_checkpoint()
    _print("UPDATED PRIVACY WALL CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "workflow": checkpoint.get("object_security_inbox_action_workflow"),
        "object_security_inbox_summary": checkpoint.get("object_security_inbox_summary"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score", 0) >= 95
    assert checkpoint.get("object_security_inbox_action_workflow", {}).get("ok") is True
    assert checkpoint.get("object_security_inbox_summary", {}).get("by_status", {}).get("resolved", 0) >= 1
    assert checkpoint.get("object_security_inbox_summary", {}).get("by_status", {}).get("ignored", 0) >= 1

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    assert "061" in built
    assert "062" in built
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized

    final = {
        "pack": "062",
        "status": "passed",
        "human_reason": "Privacy wall smoke and checkpoint now prove object inbox note/review/resolve/ignore workflow.",
    }
    _print("PACK 062 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
