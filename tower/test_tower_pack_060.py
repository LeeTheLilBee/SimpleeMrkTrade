
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
    _print("UPDATED PRIVACY WALL SMOKE", {
        "ok": smoke.get("ok"),
        "failures": smoke.get("failures"),
        "checks": sorted(list(smoke.get("checks", {}).keys())),
    })

    assert smoke.get("ok") is True
    assert not smoke.get("failures")

    for key in [
        "route_guard_allows_owner_blocks_beta_default_denies",
        "object_guard_symbols_trades_exports_unmapped",
        "mode_guard_survey_paper_live_auto",
        "flask_routes_lock_private_surfaces",
        "exposure_report_loads",
        "object_audit_capsules_active",
        "object_security_inbox_active",
        "tower_status_has_object_audit_and_inbox",
        "security_command_ui_has_object_inbox_panel",
        "no_raw_keycard_leakage",
    ]:
        assert key in smoke.get("checks", {})
        assert smoke["checks"][key]["ok"] is True

    checkpoint = build_ob_privacy_wall_checkpoint()
    _print("UPDATED PRIVACY WALL CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "object_audit_summary": checkpoint.get("object_audit_summary"),
        "object_security_inbox_summary": checkpoint.get("object_security_inbox_summary"),
        "next_steps": checkpoint.get("next_steps"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score", 0) >= 95
    assert checkpoint.get("object_audit_summary", {}).get("total", 0) >= 1
    assert checkpoint.get("object_security_inbox_summary", {}).get("total", 0) >= 1
    assert "056" in json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    assert "060" in json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized

    final = {
        "pack": "060",
        "status": "passed",
        "human_reason": "Privacy wall smoke and checkpoint now prove object audit capsules, object security inbox, Tower status surfacing, and Security Command UI panel.",
    }
    _print("PACK 060 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
