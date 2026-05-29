
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

WEB_APP = PROJECT_ROOT / "web" / "app.py"


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
    from tower.ob_object_permission_integration_checkpoint import (
        CHECKPOINT_PATH,
        PANEL_PATH,
        build_object_permission_integration_checkpoint,
        load_object_permission_integration_checkpoint,
        parse_functions_with_object_guards,
        reset_object_permission_integration_checkpoint_for_test,
    )

    reset = reset_object_permission_integration_checkpoint_for_test()
    show("RESET PACK 110 CHECKPOINT", reset)
    assert reset.get("ok") is True

    text = WEB_APP.read_text(encoding="utf-8", errors="replace")

    marker_checks = {
        "pack104": "PACK104_TOWER_OB_FLASK_GUARD_HELPERS" in text,
        "pack105": "PACK105_TOWER_OB_GUARD_STATUS_ROUTE" in text,
        "pack106": "PACK106: Tower guard for high-risk Observatory route." in text,
        "pack107": "PACK107: Tower guard for remaining protected Observatory route." in text,
        "pack109": "PACK109_OBJECT_PERMISSION_ROUTE_HELPERS" in text,
        "pack109_marker": "PACK109: Tower object-level permission check." in text,
    }
    show("PACK 110 MARKER CHECKS", marker_checks)
    assert all(marker_checks.values())

    guards = parse_functions_with_object_guards(text)
    show("PACK 110 OBJECT GUARD SCAN", {
        "object_guard_count": len(guards),
        "guards": guards,
    })

    assert len(guards) >= 7
    assert any(item.get("function_name") == "signal_symbol_page" for item in guards)
    assert any(item.get("function_name") == "my_position_detail_page" for item in guards)
    assert any(item.get("function_name") == "trade_detail_page" for item in guards)

    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
    show("PACK 110 CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "object_guard_count": checkpoint.get("object_guard_count"),
        "expected_missing": checkpoint.get("expected_missing"),
        "expected_wrong_type": checkpoint.get("expected_wrong_type"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "failed_checks": checkpoint.get("failed_checks"),
        "warnings": checkpoint.get("warnings"),
        "route_coverage_summary": checkpoint.get("route_coverage_summary"),
        "object_permission_summary": checkpoint.get("object_permission_summary"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("route_coverage_summary", {}).get("coverage_pct") == 100
    assert checkpoint.get("route_coverage_summary", {}).get("unguarded_needed_count") == 0
    assert checkpoint.get("route_coverage_summary", {}).get("unguarded_high_risk_count") == 0
    assert checkpoint.get("object_permission_summary", {}).get("readiness_score") == 100
    assert checkpoint.get("expected_missing") == []
    assert checkpoint.get("expected_wrong_type") == []
    assert checkpoint.get("no_secret_leakage") is True
    assert CHECKPOINT_PATH.exists()
    assert PANEL_PATH.exists()
    no_secret(checkpoint)

    loaded = load_object_permission_integration_checkpoint()
    show("PACK 110 LOADED CHECKPOINT", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "checkpoint_path": loaded.get("checkpoint_path"),
        "panel_path": loaded.get("panel_path"),
    })

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(loaded)

    html = PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · OB Object Integration Checkpoint" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    for path in [
        WEB_APP,
        PROJECT_ROOT / "tower" / "ob_object_permission_integration_checkpoint.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_110.py",
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
        "pack": "110",
        "status": "passed",
        "readiness_score": checkpoint.get("readiness_score"),
        "object_guard_count": checkpoint.get("object_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Object permission integration checkpoint passed and visibility panel was generated.",
    }
    show("PACK 110 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
