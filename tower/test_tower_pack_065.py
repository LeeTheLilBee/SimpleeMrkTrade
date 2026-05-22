
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
    ui_archive = smoke.get("checks", {}).get("ui_actions_and_archive_handoff_ready")

    _print("FINAL PRIVACY WALL SMOKE", {
        "ok": smoke.get("ok"),
        "failures": smoke.get("failures"),
        "ui_archive": ui_archive,
        "checks": sorted(list(smoke.get("checks", {}).keys())),
    })

    assert smoke.get("ok") is True
    assert not smoke.get("failures")
    assert isinstance(ui_archive, dict)
    assert ui_archive.get("ok") is True

    checkpoint = build_ob_privacy_wall_checkpoint()

    _print("FINAL PRIVACY WALL CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "ui_actions_and_archive_handoff_ready": checkpoint.get("ui_actions_and_archive_handoff_ready"),
        "archive_vault_handoff_summary": checkpoint.get("archive_vault_handoff_summary"),
        "next_steps": checkpoint.get("next_steps"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("readiness_label") == "Ready for polished locked-state templates"
    assert checkpoint.get("ui_actions_and_archive_handoff_ready", {}).get("ok") is True
    assert checkpoint.get("archive_vault_handoff_summary", {}).get("ok") is True
    assert checkpoint.get("archive_vault_handoff_summary", {}).get("total", 0) >= 1

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["061", "062", "063", "064", "065"]:
        assert pack in built

    next_steps = json.dumps(checkpoint.get("next_steps", []), sort_keys=True)
    assert "polished locked-state templates" in next_steps
    assert "Wire the UI action endpoint" in next_steps

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "065",
        "status": "passed",
        "human_reason": "Final privacy wall checkpoint proves UI action forms, Archive Vault handoff queue, object inbox workflow, and no secret leakage before locked-state polish.",
    }
    _print("PACK 065 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
