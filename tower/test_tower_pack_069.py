
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
    polished = smoke.get("checks", {}).get("polished_locked_pages_ready")

    _print("PRIVACY WALL SMOKE WITH POLISHED LOCKED PAGES", {
        "ok": smoke.get("ok"),
        "failures": smoke.get("failures"),
        "polished": polished,
        "checks": sorted(list(smoke.get("checks", {}).keys())),
    })

    assert smoke.get("ok") is True
    assert not smoke.get("failures")
    assert isinstance(polished, dict)
    assert polished.get("ok") is True

    detail = polished.get("detail", {})
    assert detail.get("status_ok") is True
    assert detail.get("content_ok") is True
    assert detail.get("safe_ok") is True
    assert detail.get("preview_status") == 403

    checkpoint = build_ob_privacy_wall_checkpoint()

    _print("PRIVACY WALL CHECKPOINT WITH POLISHED LOCKED PAGES", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "polished_locked_pages_ready": checkpoint.get("polished_locked_pages_ready"),
        "next_steps": checkpoint.get("next_steps"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("polished_locked_pages_ready", {}).get("ok") is True
    assert checkpoint.get("readiness_label") == "Ready to wire polished locked pages into deny paths"

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["066", "067", "068", "069"]:
        assert pack in built

    next_steps = json.dumps(checkpoint.get("next_steps", []), sort_keys=True)
    assert "Wire polished locked pages into the actual privacy wall deny paths" in next_steps

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    # Safe proof labels like "no_raw_token": true are allowed.
    # Dangerous secret-bearing patterns are not.
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "'raw_token':" not in serialized
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "069",
        "status": "passed",
        "human_reason": "Privacy wall smoke/checkpoint now prove polished route/object/mode/export/unmapped locked pages.",
    }
    _print("PACK 069 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
