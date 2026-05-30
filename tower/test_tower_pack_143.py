
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
    from tower.owner_action_notes import (
        OWNER_ACTION_NOTE_DETAIL_PANEL_PATH,
        OWNER_ACTION_NOTE_RECEIPTS_PATH,
        OWNER_ACTION_NOTES_PANEL_PATH,
        OWNER_ACTION_NOTES_PATH,
        OWNER_ACTION_NOTES_STATUS_PATH,
        build_owner_action_note_detail,
        build_owner_action_notes_status,
        create_owner_action_note,
        owner_action_notes_status_card,
        render_owner_action_note_detail_section,
        render_owner_action_notes_section,
        reset_owner_action_notes_for_test,
        write_owner_action_note_detail_panel,
        write_owner_action_notes_panel,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_notes = reset_owner_action_notes_for_test()
    show("RESET PACK 143 NOTES", reset_notes)
    assert reset_notes.get("ok") is True

    action_status = build_owner_action_center_status(write_panel=True)
    actions = action_status.get("actions", []) if isinstance(action_status.get("actions"), list) else []
    assert actions

    action_id = actions[0].get("action_id")
    assert action_id

    missing_action_id = create_owner_action_note(
        action_id="",
        note_body="Missing action id test.",
        actor_user_id="owner_solice",
        note_type="general",
        visibility="owner_only",
    )

    missing_body = create_owner_action_note(
        action_id=action_id,
        note_body="",
        actor_user_id="owner_solice",
        note_type="general",
        visibility="owner_only",
    )

    invalid_type = create_owner_action_note(
        action_id=action_id,
        note_body="Invalid type test.",
        actor_user_id="owner_solice",
        note_type="not_a_type",
        visibility="owner_only",
    )

    invalid_visibility = create_owner_action_note(
        action_id=action_id,
        note_body="Invalid visibility test.",
        actor_user_id="owner_solice",
        note_type="general",
        visibility="world_public",
    )

    not_found = create_owner_action_note(
        action_id="missing_owner_action_143",
        note_body="Action not found test.",
        actor_user_id="owner_solice",
        note_type="general",
        visibility="owner_only",
    )

    note_one = create_owner_action_note(
        action_id=action_id,
        note_body="Investigating this command. Secret should_not_survive. tower_keycard=NOPE.",
        actor_user_id="owner_solice",
        note_type="investigation",
        visibility="owner_only",
        metadata={"pack": "143", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )

    note_two = create_owner_action_note(
        action_id=action_id,
        note_body="Resolved after confirming the action path.",
        actor_user_id="owner_solice",
        note_type="resolution",
        visibility="admin_visible",
        metadata={"pack": "143"},
    )

    note_three = create_owner_action_note(
        action_id=action_id,
        note_body="Follow up later if related incidents reappear.",
        actor_user_id="tower_system",
        note_type="follow_up",
        visibility="system_internal",
        metadata={"pack": "143"},
    )

    show("PACK 143 CREATE NOTE RESULTS", {
        "missing_action_id": missing_action_id,
        "missing_body": missing_body,
        "invalid_type": invalid_type,
        "invalid_visibility": invalid_visibility,
        "not_found": not_found,
        "note_one": note_one,
        "note_two": note_two,
        "note_three": note_three,
    })

    assert missing_action_id.get("ok") is False
    assert missing_action_id.get("reason_code") == "missing_action_id"

    assert missing_body.get("ok") is False
    assert missing_body.get("reason_code") == "missing_note_body"

    assert invalid_type.get("ok") is False
    assert invalid_type.get("reason_code") == "invalid_note_type"

    assert invalid_visibility.get("ok") is False
    assert invalid_visibility.get("reason_code") == "invalid_visibility"

    assert not_found.get("ok") is False
    assert not_found.get("reason_code") == "owner_action_not_found"

    for result in [note_one, note_two, note_three]:
        assert result.get("ok") is True
        assert result.get("pack") == "143"
        assert result.get("decision") == "owner_action_note_created"
        assert result.get("note_id")
        assert result.get("receipt_id")
        assert result.get("no_secret_leakage") is True
        no_secret(result)

    assert note_one.get("note", {}).get("note_body") == "[REDACTED_OWNER_ACTION_NOTE_VALUE]"
    assert "token" not in note_one.get("note", {}).get("metadata", {})

    run_fast(
        "FAST OWNER ACTION NOTES",
        "from tower.owner_action_notes import build_owner_action_notes_status; "
        "s=build_owner_action_notes_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('base_note_count'))",
        timeout=10,
    )

    all_notes = build_owner_action_notes_status(write_panel=True)
    investigation_notes = build_owner_action_notes_status(note_type="investigation", write_panel=False)
    owner_only_notes = build_owner_action_notes_status(visibility="owner_only", write_panel=False)
    action_notes = build_owner_action_notes_status(action_id=action_id, write_panel=False)
    top_only = build_owner_action_notes_status(top_only=True, write_panel=False)

    top_note = all_notes.get("top_note", {}) if isinstance(all_notes.get("top_note"), dict) else {}
    top_note_id = top_note.get("note_id")
    assert top_note_id

    detail = build_owner_action_note_detail(note_id=top_note_id, write_panel=True)
    fallback_detail = build_owner_action_note_detail(note_id="", write_panel=False)
    missing_detail = build_owner_action_note_detail(note_id="missing_owner_action_note_143", write_panel=False)
    card = owner_action_notes_status_card()

    show("PACK 143 ALL NOTES", {
        "ok": all_notes.get("ok"),
        "pack": all_notes.get("pack"),
        "status": all_notes.get("status"),
        "base_note_count": all_notes.get("base_note_count"),
        "filtered_note_count": all_notes.get("filtered_note_count"),
        "receipt_count": all_notes.get("receipt_count"),
        "filter_options": all_notes.get("filter_options"),
        "top_note": all_notes.get("top_note"),
        "no_secret_leakage": all_notes.get("no_secret_leakage"),
    })

    show("PACK 143 INVESTIGATION FILTER", {
        "filtered_note_count": investigation_notes.get("filtered_note_count"),
        "active_filters": investigation_notes.get("active_filters"),
        "top_note": investigation_notes.get("top_note"),
    })

    show("PACK 143 OWNER ONLY FILTER", {
        "filtered_note_count": owner_only_notes.get("filtered_note_count"),
        "active_filters": owner_only_notes.get("active_filters"),
        "top_note": owner_only_notes.get("top_note"),
    })

    show("PACK 143 ACTION FILTER", {
        "filtered_note_count": action_notes.get("filtered_note_count"),
        "active_filters": action_notes.get("active_filters"),
    })

    show("PACK 143 TOP ONLY", {
        "filtered_note_count": top_only.get("filtered_note_count"),
        "active_filters": top_only.get("active_filters"),
        "top_note": top_only.get("top_note"),
    })

    show("PACK 143 DETAIL", {
        "ok": detail.get("ok"),
        "pack": detail.get("pack"),
        "status": detail.get("status"),
        "requested_note_id": detail.get("requested_note_id"),
        "found_note_id": detail.get("found_note_id"),
        "detail": detail.get("detail"),
        "no_secret_leakage": detail.get("no_secret_leakage"),
    })

    show("PACK 143 FALLBACK DETAIL", {
        "ok": fallback_detail.get("ok"),
        "status": fallback_detail.get("status"),
        "found_note_id": fallback_detail.get("found_note_id"),
    })

    show("PACK 143 MISSING DETAIL", {
        "ok": missing_detail.get("ok"),
        "status": missing_detail.get("status"),
        "found_note_id": missing_detail.get("found_note_id"),
        "readiness_score": missing_detail.get("readiness_score"),
    })

    show("PACK 143 STATUS CARD", card)

    assert all_notes.get("ok") is True
    assert all_notes.get("pack") == "143"
    assert all_notes.get("status") == "passed"
    assert all_notes.get("base_note_count") == 3
    assert all_notes.get("filtered_note_count") == 3
    assert all_notes.get("receipt_count") == 3
    assert all_notes.get("readiness_score") == 100
    assert all_notes.get("no_secret_leakage") is True
    assert OWNER_ACTION_NOTES_PATH.exists()
    assert OWNER_ACTION_NOTE_RECEIPTS_PATH.exists()
    assert OWNER_ACTION_NOTES_STATUS_PATH.exists()
    assert OWNER_ACTION_NOTES_PANEL_PATH.exists()

    options = all_notes.get("filter_options", {})
    assert "note_type" in options
    assert "visibility" in options
    assert "actor_user_id" in options
    assert "action_type" in options

    assert investigation_notes.get("ok") is True
    assert investigation_notes.get("active_filters", {}).get("note_type") == "investigation"
    assert investigation_notes.get("filtered_note_count") == 1
    assert all(
        note.get("note_type") == "investigation"
        for note in investigation_notes.get("notes", [])
        if isinstance(note, dict)
    )

    assert owner_only_notes.get("ok") is True
    assert owner_only_notes.get("active_filters", {}).get("visibility") == "owner_only"
    assert owner_only_notes.get("filtered_note_count") == 1

    assert action_notes.get("ok") is True
    assert action_notes.get("active_filters", {}).get("action_id") == action_id.lower()
    assert action_notes.get("filtered_note_count") == 3

    assert top_only.get("ok") is True
    assert top_only.get("active_filters", {}).get("top_only") is True
    assert top_only.get("filtered_note_count") == 1

    assert detail.get("ok") is True
    assert detail.get("pack") == "143"
    assert detail.get("status") == "passed"
    assert detail.get("requested_note_id") == top_note_id
    assert detail.get("found_note_id") == top_note_id
    assert detail.get("detail", {}).get("note_id") == top_note_id
    assert detail.get("detail", {}).get("note_body")
    assert detail.get("detail", {}).get("receipt_count", 0) >= 1
    assert detail.get("no_secret_leakage") is True

    assert fallback_detail.get("ok") is True
    assert fallback_detail.get("status") == "passed"
    assert fallback_detail.get("found_note_id")

    assert missing_detail.get("ok") is False
    assert missing_detail.get("status") == "not_found"
    assert missing_detail.get("readiness_score") == 80

    assert card.get("ok") is True
    assert card.get("pack") == "143"
    assert card.get("readiness_score") == 100
    assert card.get("base_note_count") == 3
    assert card.get("receipt_count") == 3

    no_secret(all_notes)
    no_secret(investigation_notes)
    no_secret(owner_only_notes)
    no_secret(action_notes)
    no_secret(top_only)
    no_secret(detail)
    no_secret(fallback_detail)
    no_secret(missing_detail)
    no_secret(card)

    notes_section = render_owner_action_notes_section(all_notes)
    detail_section = render_owner_action_note_detail_section(detail)

    show("PACK 143 NOTES HTML CHECK", {
        "html_length": len(notes_section),
        "has_marker": "PACK143_OWNER_ACTION_NOTES_SECTION" in notes_section,
        "has_title": "Owner Action Notes" in notes_section,
        "has_filtered_notes": "Filtered notes" in notes_section,
    })

    show("PACK 143 DETAIL HTML CHECK", {
        "html_length": len(detail_section),
        "has_marker": "PACK143_OWNER_ACTION_NOTE_DETAIL_SECTION" in detail_section,
        "has_note_detail": "Note Detail" in detail_section or "NOTE DETAIL" in detail_section,
    })

    assert "PACK143_OWNER_ACTION_NOTES_SECTION" in notes_section
    assert "Owner Action Notes" in notes_section
    assert "Filtered notes" in notes_section
    assert "SHOULD_NOT_SURVIVE" not in notes_section
    assert "tower_keycard=" not in notes_section

    assert "PACK143_OWNER_ACTION_NOTE_DETAIL_SECTION" in detail_section
    assert "SHOULD_NOT_SURVIVE" not in detail_section
    assert "tower_keycard=" not in detail_section

    panel = write_owner_action_notes_panel(all_notes)
    detail_panel = write_owner_action_note_detail_panel(detail)

    show("PACK 143 PANEL WRITE", panel)
    show("PACK 143 DETAIL PANEL WRITE", detail_panel)

    assert panel.get("ok") is True
    assert detail_panel.get("ok") is True
    assert OWNER_ACTION_NOTES_PANEL_PATH.exists()
    assert OWNER_ACTION_NOTE_DETAIL_PANEL_PATH.exists()

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 143 FINAL HEALTH", {
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
        "pack143_route_marker": "PACK143_OWNER_ACTION_NOTES_ROUTE" in app_text,
        "pack143_route_path": "/tower/owner-action-notes.json" in app_text,
        "pack143_route_guard": "pack143_owner_action_notes_route" in app_text,
    }
    show("PACK 143 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_notes.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_143.py",
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
        "pack": "143",
        "status": "passed",
        "readiness_score": 100,
        "base_note_count": all_notes.get("base_note_count"),
        "filtered_note_count": all_notes.get("filtered_note_count"),
        "receipt_count": all_notes.get("receipt_count"),
        "investigation_filter_count": investigation_notes.get("filtered_note_count"),
        "owner_only_filter_count": owner_only_notes.get("filtered_note_count"),
        "top_only_count": top_only.get("filtered_note_count"),
        "detail_note_type": detail.get("detail", {}).get("note_type"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action note system with redaction/audit receipt is working.",
    }
    show("PACK 143 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
