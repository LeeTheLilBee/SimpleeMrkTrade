
from __future__ import annotations

import json
import os
import sys
import subprocess
import time
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
        "sk_live_should",
        "ghp_should",
    ]
    for item in bad:
        assert item not in s, item


def run_fast(label: str, code: str, timeout: int = 10):
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = round(time.time() - start, 2)
    show(label, {
        "elapsed": elapsed,
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    })
    assert result.returncode == 0
    assert elapsed < timeout


def run_tests():
    from tower.owner_action_center import build_owner_action_center_status
    from tower.owner_action_state_tracking import (
        apply_owner_action_state,
        build_owner_action_state_status,
        reset_owner_action_state_tracking_for_test,
    )
    from tower.owner_action_state_receipts import (
        OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH,
        OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH,
        OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH,
        build_owner_action_state_receipt_detail,
        build_owner_action_state_receipts_status,
        owner_action_state_receipts_status_card,
        render_owner_action_state_receipt_detail_section,
        render_owner_action_state_receipts_section,
        reset_owner_action_state_receipts_for_test,
        write_owner_action_state_receipt_detail_panel,
        write_owner_action_state_receipts_panel,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_state = reset_owner_action_state_tracking_for_test()
    reset_receipts = reset_owner_action_state_receipts_for_test()

    show("RESET PACK 142 STATE TRACKING", reset_state)
    show("RESET PACK 142 RECEIPTS", reset_receipts)

    assert reset_state.get("ok") is True
    assert reset_receipts.get("ok") is True

    action_status = build_owner_action_center_status(write_panel=True)
    actions = action_status.get("actions", []) if isinstance(action_status.get("actions"), list) else []
    assert actions

    action_id = actions[0].get("action_id")
    assert action_id

    ack = apply_owner_action_state(
        action_id=action_id,
        new_state="acknowledged",
        actor_user_id="owner_solice",
        reason="Pack 142 acknowledge receipt seed.",
        note="Receipt seed. Secret should_not_survive.",
        metadata={"pack": "142", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    investigate = apply_owner_action_state(
        action_id=action_id,
        new_state="investigating",
        actor_user_id="owner_solice",
        reason="Pack 142 investigate receipt seed.",
        note="Receipt seed two.",
        metadata={"pack": "142"},
    )
    resolved = apply_owner_action_state(
        action_id=action_id,
        new_state="resolved",
        actor_user_id="owner_solice",
        reason="Pack 142 resolved receipt seed.",
        note="Receipt seed three.",
        metadata={"pack": "142"},
    )

    assert ack.get("ok") is True
    assert investigate.get("ok") is True
    assert resolved.get("ok") is True

    no_secret(ack)
    no_secret(investigate)
    no_secret(resolved)

    state_status = build_owner_action_state_status(write_panel=True)
    assert state_status.get("receipt_count", 0) >= 3

    run_fast(
        "FAST OWNER ACTION STATE RECEIPTS",
        "from tower.owner_action_state_receipts import build_owner_action_state_receipts_status; "
        "s=build_owner_action_state_receipts_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('base_receipt_count'))",
        timeout=10,
    )

    all_receipts = build_owner_action_state_receipts_status(write_panel=True)
    resolved_receipts = build_owner_action_state_receipts_status(new_state="resolved", write_panel=False)
    ack_receipts = build_owner_action_state_receipts_status(new_state="acknowledged", write_panel=False)
    action_receipts = build_owner_action_state_receipts_status(action_id=action_id, write_panel=False)
    top_only = build_owner_action_state_receipts_status(top_only=True, write_panel=False)

    top_receipt = all_receipts.get("top_receipt", {}) if isinstance(all_receipts.get("top_receipt"), dict) else {}
    top_receipt_id = top_receipt.get("receipt_id")
    assert top_receipt_id

    detail = build_owner_action_state_receipt_detail(receipt_id=top_receipt_id, write_panel=True)
    fallback_detail = build_owner_action_state_receipt_detail(receipt_id="", write_panel=False)
    missing_detail = build_owner_action_state_receipt_detail(receipt_id="missing_owner_state_receipt_142", write_panel=False)
    card = owner_action_state_receipts_status_card()

    show("PACK 142 STATE STATUS", {
        "ok": state_status.get("ok"),
        "status": state_status.get("status"),
        "action_count": state_status.get("action_count"),
        "tracked_action_count": state_status.get("tracked_action_count"),
        "receipt_count": state_status.get("receipt_count"),
        "by_state": state_status.get("by_state"),
    })

    show("PACK 142 ALL RECEIPTS", {
        "ok": all_receipts.get("ok"),
        "pack": all_receipts.get("pack"),
        "status": all_receipts.get("status"),
        "base_receipt_count": all_receipts.get("base_receipt_count"),
        "filtered_receipt_count": all_receipts.get("filtered_receipt_count"),
        "filter_options": all_receipts.get("filter_options"),
        "top_receipt": all_receipts.get("top_receipt"),
        "no_secret_leakage": all_receipts.get("no_secret_leakage"),
    })

    show("PACK 142 RESOLVED FILTER", {
        "filtered_receipt_count": resolved_receipts.get("filtered_receipt_count"),
        "active_filters": resolved_receipts.get("active_filters"),
        "top_receipt": resolved_receipts.get("top_receipt"),
    })

    show("PACK 142 ACK FILTER", {
        "filtered_receipt_count": ack_receipts.get("filtered_receipt_count"),
        "active_filters": ack_receipts.get("active_filters"),
        "top_receipt": ack_receipts.get("top_receipt"),
    })

    show("PACK 142 ACTION FILTER", {
        "filtered_receipt_count": action_receipts.get("filtered_receipt_count"),
        "active_filters": action_receipts.get("active_filters"),
    })

    show("PACK 142 TOP ONLY", {
        "filtered_receipt_count": top_only.get("filtered_receipt_count"),
        "active_filters": top_only.get("active_filters"),
        "top_receipt": top_only.get("top_receipt"),
    })

    show("PACK 142 DETAIL", {
        "ok": detail.get("ok"),
        "pack": detail.get("pack"),
        "status": detail.get("status"),
        "requested_receipt_id": detail.get("requested_receipt_id"),
        "found_receipt_id": detail.get("found_receipt_id"),
        "detail": detail.get("detail"),
        "no_secret_leakage": detail.get("no_secret_leakage"),
    })

    show("PACK 142 FALLBACK DETAIL", {
        "ok": fallback_detail.get("ok"),
        "status": fallback_detail.get("status"),
        "found_receipt_id": fallback_detail.get("found_receipt_id"),
    })

    show("PACK 142 MISSING DETAIL", {
        "ok": missing_detail.get("ok"),
        "status": missing_detail.get("status"),
        "found_receipt_id": missing_detail.get("found_receipt_id"),
        "readiness_score": missing_detail.get("readiness_score"),
    })

    show("PACK 142 STATUS CARD", card)

    assert all_receipts.get("ok") is True
    assert all_receipts.get("pack") == "142"
    assert all_receipts.get("status") == "passed"
    assert all_receipts.get("base_receipt_count", 0) >= 3
    assert all_receipts.get("filtered_receipt_count", 0) >= 3
    assert all_receipts.get("readiness_score") == 100
    assert all_receipts.get("no_secret_leakage") is True
    assert OWNER_ACTION_STATE_RECEIPTS_STATUS_PATH.exists()
    assert OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH.exists()

    options = all_receipts.get("filter_options", {})
    assert "new_state" in options
    assert "prior_state" in options
    assert "actor_user_id" in options
    assert "event_type" in options
    assert "action_type" in options

    assert resolved_receipts.get("ok") is True
    assert resolved_receipts.get("active_filters", {}).get("new_state") == "resolved"
    assert resolved_receipts.get("filtered_receipt_count", 0) >= 1
    assert all(
        receipt.get("new_state") == "resolved"
        for receipt in resolved_receipts.get("receipts", [])
        if isinstance(receipt, dict)
    )

    assert ack_receipts.get("ok") is True
    assert ack_receipts.get("active_filters", {}).get("new_state") == "acknowledged"
    assert ack_receipts.get("filtered_receipt_count", 0) >= 1

    assert action_receipts.get("ok") is True
    assert action_receipts.get("active_filters", {}).get("action_id") == action_id.lower()
    assert action_receipts.get("filtered_receipt_count", 0) >= 3

    assert top_only.get("ok") is True
    assert top_only.get("active_filters", {}).get("top_only") is True
    assert top_only.get("filtered_receipt_count") == 1

    assert detail.get("ok") is True
    assert detail.get("pack") == "142"
    assert detail.get("status") == "passed"
    assert detail.get("requested_receipt_id") == top_receipt_id
    assert detail.get("found_receipt_id") == top_receipt_id
    assert detail.get("detail", {}).get("receipt_id") == top_receipt_id
    assert detail.get("detail", {}).get("new_state")
    assert detail.get("no_secret_leakage") is True

    assert fallback_detail.get("ok") is True
    assert fallback_detail.get("status") == "passed"
    assert fallback_detail.get("found_receipt_id")

    assert missing_detail.get("ok") is False
    assert missing_detail.get("status") == "not_found"
    assert missing_detail.get("readiness_score") == 80

    assert card.get("ok") is True
    assert card.get("pack") == "142"
    assert card.get("readiness_score") == 100
    assert card.get("base_receipt_count", 0) >= 3

    no_secret(all_receipts)
    no_secret(resolved_receipts)
    no_secret(ack_receipts)
    no_secret(action_receipts)
    no_secret(top_only)
    no_secret(detail)
    no_secret(fallback_detail)
    no_secret(missing_detail)
    no_secret(card)

    receipts_section = render_owner_action_state_receipts_section(all_receipts)
    detail_section = render_owner_action_state_receipt_detail_section(detail)

    show("PACK 142 RECEIPTS HTML CHECK", {
        "html_length": len(receipts_section),
        "has_marker": "PACK142_OWNER_ACTION_STATE_RECEIPTS_SECTION" in receipts_section,
        "has_title": "Owner Action State Receipts" in receipts_section,
        "has_filtered_receipts": "Filtered receipts" in receipts_section,
    })

    show("PACK 142 DETAIL HTML CHECK", {
        "html_length": len(detail_section),
        "has_marker": "PACK142_OWNER_ACTION_STATE_RECEIPT_DETAIL_SECTION" in detail_section,
        "has_receipt_detail": "Receipt Detail" in detail_section or "RECEIPT DETAIL" in detail_section,
    })

    assert "PACK142_OWNER_ACTION_STATE_RECEIPTS_SECTION" in receipts_section
    assert "Owner Action State Receipts" in receipts_section
    assert "Filtered receipts" in receipts_section
    assert "SHOULD_NOT_SURVIVE" not in receipts_section
    assert "tower_keycard=" not in receipts_section

    assert "PACK142_OWNER_ACTION_STATE_RECEIPT_DETAIL_SECTION" in detail_section
    assert "SHOULD_NOT_SURVIVE" not in detail_section
    assert "tower_keycard=" not in detail_section

    panel = write_owner_action_state_receipts_panel(all_receipts)
    detail_panel = write_owner_action_state_receipt_detail_panel(detail)

    show("PACK 142 PANEL WRITE", panel)
    show("PACK 142 DETAIL PANEL WRITE", detail_panel)

    assert panel.get("ok") is True
    assert detail_panel.get("ok") is True
    assert OWNER_ACTION_STATE_RECEIPTS_PANEL_PATH.exists()
    assert OWNER_ACTION_STATE_RECEIPT_DETAIL_PANEL_PATH.exists()

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 142 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": checkpoint.get("status"),
        "checkpoint_readiness": checkpoint.get("readiness_score"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("helper_wrapped_count") == 0

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    route_checks = {
        "pack142_route_marker": "PACK142_OWNER_ACTION_STATE_RECEIPTS_ROUTE" in app_text,
        "pack142_route_path": "/tower/owner-action-state-receipts.json" in app_text,
        "pack142_route_guard": "pack142_owner_action_state_receipts_route" in app_text,
    }
    show("PACK 142 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_state_receipts.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_142.py",
        PROJECT_ROOT / "tower" / "owner_action_state_tracking.py",
        PROJECT_ROOT / "tower" / "owner_action_center.py",
        PROJECT_ROOT / "web" / "app.py",
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
        "pack": "142",
        "status": "passed",
        "readiness_score": 100,
        "base_receipt_count": all_receipts.get("base_receipt_count"),
        "filtered_receipt_count": all_receipts.get("filtered_receipt_count"),
        "resolved_filter_count": resolved_receipts.get("filtered_receipt_count"),
        "ack_filter_count": ack_receipts.get("filtered_receipt_count"),
        "top_only_count": top_only.get("filtered_receipt_count"),
        "detail_new_state": detail.get("detail", {}).get("new_state"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action state receipts layer is working.",
    }
    show("PACK 142 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
