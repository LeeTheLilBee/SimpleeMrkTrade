
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
    proof = smoke.get("checks", {}).get("replacement_and_exposure_panels_ready")

    _print("PRIVACY WALL SMOKE WITH REPLACEMENT + EXPOSURE PANELS", {
        "ok": smoke.get("ok"),
        "failures": smoke.get("failures"),
        "proof": proof,
        "checks": sorted(list(smoke.get("checks", {}).keys())),
    })

    assert smoke.get("ok") is True
    assert not smoke.get("failures")
    assert isinstance(proof, dict)
    assert proof.get("ok") is True

    detail = proof.get("detail", {})
    assert detail.get("tower_status_deny_ok") is True
    assert detail.get("tower_status_exposure_ok") is True
    assert detail.get("dashboard_ok") is True
    assert detail.get("dashboard_deny_panel_ok") is True
    assert detail.get("dashboard_exposure_panel_ok") is True
    assert detail.get("dashboard_has_pack086") is True
    assert detail.get("dashboard_has_pack087") is True
    assert detail.get("no_secret_leakage") is True

    checkpoint = build_ob_privacy_wall_checkpoint()

    _print("PRIVACY WALL CHECKPOINT WITH REPLACEMENT + EXPOSURE PANELS", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "replacement_and_exposure_panels_ready": checkpoint.get("replacement_and_exposure_panels_ready"),
        "deny_path_replacement_ui_summary": checkpoint.get("deny_path_replacement_ui_summary"),
        "exposure_mapping_ui_summary": checkpoint.get("exposure_mapping_ui_summary"),
        "next_steps": checkpoint.get("next_steps"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("readiness_label") == "Ready for route replacement policy list"
    assert checkpoint.get("replacement_and_exposure_panels_ready", {}).get("ok") is True

    deny = checkpoint.get("deny_path_replacement_ui_summary", {})
    assert deny.get("ok") is True
    assert deny.get("total", 0) >= 1
    assert deny.get("verified", 0) >= 1
    assert deny.get("by_route", {}).get("/no-access", 0) >= 1

    exposure = checkpoint.get("exposure_mapping_ui_summary", {})
    assert exposure.get("ok") is True
    assert exposure.get("total", 0) >= 1
    assert exposure.get("readiness_score") == 100
    assert exposure.get("readiness_label") == "Exposure mapping pass ready"
    assert isinstance(exposure.get("counts"), dict)

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["086", "087", "088"]:
        assert pack in built

    next_steps = json.dumps(checkpoint.get("next_steps", []), sort_keys=True)
    assert "Create route replacement policy list" in next_steps

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "088",
        "status": "passed",
        "human_reason": "Privacy wall smoke/checkpoint now prove deny-path replacement and exposure mapping UI panels.",
    }
    _print("PACK 088 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
