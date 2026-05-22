
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
    proof = smoke.get("checks", {}).get("audited_forms_and_receipt_panel_ready")

    _print("PRIVACY WALL SMOKE WITH AUDITED FORMS + RECEIPT PANEL", {
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
    assert detail.get("dashboard_ok") is True
    assert detail.get("has_audited_form_action") is True
    assert detail.get("has_old_form_action") is False
    assert detail.get("panel_ok") is True
    assert detail.get("receipt_ok") is True
    assert detail.get("no_secret_leakage") is True
    assert detail.get("note_status") == 200
    assert detail.get("receipt_id_present") is True

    checkpoint = build_ob_privacy_wall_checkpoint()

    _print("PRIVACY WALL CHECKPOINT WITH AUDITED FORMS + RECEIPT PANEL", {
        "ok": checkpoint.get("ok"),
        "readiness_score": checkpoint.get("readiness_score"),
        "readiness_label": checkpoint.get("readiness_label"),
        "audited_forms_and_receipt_panel_ready": checkpoint.get("audited_forms_and_receipt_panel_ready"),
        "ui_action_audit_summary": checkpoint.get("ui_action_audit_summary"),
        "next_steps": checkpoint.get("next_steps"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("readiness_label") == "Ready for controlled deny-path replacement"
    assert checkpoint.get("audited_forms_and_receipt_panel_ready", {}).get("ok") is True
    assert checkpoint.get("ui_action_audit_summary", {}).get("ok") is True
    assert checkpoint.get("tower_status_ui_action_audit", {}).get("ok") is True

    built = json.dumps(checkpoint.get("built_packs", []), sort_keys=True)
    for pack in ["076", "077", "078"]:
        assert pack in built

    next_steps = json.dumps(checkpoint.get("next_steps", []), sort_keys=True)
    assert "Begin controlled deny-path replacement" in next_steps

    serialized = json.dumps([smoke, checkpoint], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in checkpoint.get("soulaana_translation", "")

    final = {
        "pack": "078",
        "status": "passed",
        "human_reason": "Privacy wall smoke/checkpoint now prove audited forms and UI action receipt panel.",
    }
    _print("PACK 078 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
