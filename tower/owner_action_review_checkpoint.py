
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH = DATA_DIR / "owner_action_review_checkpoint_status.json"
OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH = DATA_DIR / "owner_action_review_checkpoint_panel.html"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _html_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def _safe_scan(payload: Any) -> Dict[str, Any]:
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "should_not_survive",
        "tower_keycard=",
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
        "sk_live_",
        "ghp_",
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def _safe_call(label: str, fn) -> Dict[str, Any]:
    try:
        result = fn()
        return {
            "ok": True,
            "label": label,
            "result": result if isinstance(result, dict) else {},
            "error_type": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "label": label,
            "result": {},
            "error_type": type(exc).__name__,
        }


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def build_owner_action_review_checkpoint(write_panel: bool = True) -> Dict[str, Any]:
    action_call = _safe_call(
        "owner_action_center",
        lambda: __import__(
            "tower.owner_action_center",
            fromlist=["build_owner_action_center_status"],
        ).build_owner_action_center_status(write_panel=True),
    )

    state_call = _safe_call(
        "owner_action_state_tracking",
        lambda: __import__(
            "tower.owner_action_state_tracking",
            fromlist=["build_owner_action_state_status"],
        ).build_owner_action_state_status(write_panel=True),
    )

    state_receipts_call = _safe_call(
        "owner_action_state_receipts",
        lambda: __import__(
            "tower.owner_action_state_receipts",
            fromlist=["build_owner_action_state_receipts_status"],
        ).build_owner_action_state_receipts_status(write_panel=True),
    )

    notes_call = _safe_call(
        "owner_action_notes",
        lambda: __import__(
            "tower.owner_action_notes",
            fromlist=["build_owner_action_notes_status"],
        ).build_owner_action_notes_status(write_panel=True),
    )

    assignments_call = _safe_call(
        "owner_action_assignments",
        lambda: __import__(
            "tower.owner_action_assignments",
            fromlist=["build_owner_action_assignments_status"],
        ).build_owner_action_assignments_status(write_panel=True),
    )

    route_call = _safe_call(
        "route_coverage",
        lambda: __import__(
            "tower.ob_route_coverage_report",
            fromlist=["build_ob_route_coverage_report"],
        ).build_ob_route_coverage_report(write_panel=True),
    )

    object_call = _safe_call(
        "object_checkpoint",
        lambda: __import__(
            "tower.ob_object_permission_integration_checkpoint",
            fromlist=["build_object_permission_integration_checkpoint"],
        ).build_object_permission_integration_checkpoint(write_panel=True),
    )

    action = action_call.get("result", {})
    state = state_call.get("result", {})
    receipts = state_receipts_call.get("result", {})
    notes = notes_call.get("result", {})
    assignments = assignments_call.get("result", {})
    route = route_call.get("result", {})
    obj = object_call.get("result", {})

    action_count = _num(action.get("action_count"), 0)
    open_action_count = _num(action.get("open_action_count"), 0)

    tracked_action_count = _num(state.get("tracked_action_count"), 0)
    closed_action_count = _num(state.get("closed_action_count"), 0)
    state_receipt_count = _num(state.get("receipt_count"), 0)

    base_receipt_count = _num(receipts.get("base_receipt_count"), 0)
    filtered_receipt_count = _num(receipts.get("filtered_receipt_count"), 0)

    base_note_count = _num(notes.get("base_note_count"), 0)
    note_receipt_count = _num(notes.get("receipt_count"), 0)

    base_assignment_count = _num(assignments.get("base_assignment_count"), 0)
    assignment_receipt_count = _num(assignments.get("receipt_count"), 0)
    unassigned_action_count = _num(assignments.get("unassigned_action_count"), action_count)

    route_coverage = _num(route.get("coverage_pct"), 0)
    unguarded_needed = _num(route.get("unguarded_needed_count"), 0)
    unguarded_high = _num(route.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _num(obj.get("helper_wrapped_count"), 0)

    checks = {
        "action_call_ok": action_call.get("ok") is True,
        "action_center_passed": action.get("status") == "passed",
        "action_center_readiness_100": action.get("readiness_score") == 100,
        "actions_present": action_count >= 1,

        "state_call_ok": state_call.get("ok") is True,
        "state_passed": state.get("status") == "passed",
        "state_pack_141": str(state.get("pack")) == "141",
        "state_readiness_100": state.get("readiness_score") == 100,
        "state_receipts_present": state_receipt_count >= 1,
        "tracked_actions_present": tracked_action_count >= 1,

        "state_receipts_call_ok": state_receipts_call.get("ok") is True,
        "state_receipts_passed": receipts.get("status") == "passed",
        "state_receipts_pack_142": str(receipts.get("pack")) == "142",
        "state_receipts_readiness_100": receipts.get("readiness_score") == 100,
        "state_receipts_present": base_receipt_count >= 1,
        "state_receipt_filters_present": filtered_receipt_count >= 1,

        "notes_call_ok": notes_call.get("ok") is True,
        "notes_passed": notes.get("status") == "passed",
        "notes_pack_143": str(notes.get("pack")) == "143",
        "notes_readiness_100": notes.get("readiness_score") == 100,
        "notes_present": base_note_count >= 1,
        "note_receipts_present": note_receipt_count >= 1,

        "assignments_call_ok": assignments_call.get("ok") is True,
        "assignments_passed": assignments.get("status") == "passed",
        "assignments_pack_144": str(assignments.get("pack")) == "144",
        "assignments_readiness_100": assignments.get("readiness_score") == 100,
        "assignments_present": base_assignment_count >= 1,
        "assignment_receipts_present": assignment_receipt_count >= 1,

        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_100": route_coverage == 100,
        "route_unguarded_zero": unguarded_needed == 0,
        "route_high_risk_zero": unguarded_high == 0,

        "object_call_ok": object_call.get("ok") is True,
        "object_checkpoint_passed": obj.get("status") == "passed",
        "object_checkpoint_readiness_100": obj.get("readiness_score") == 100,
        "helper_wrapped_zero": helper_wrapped == 0,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    total_review_records = (
        tracked_action_count
        + base_receipt_count
        + base_note_count
        + base_assignment_count
    )

    review_depth_score = 0
    if tracked_action_count >= 1:
        review_depth_score += 25
    if base_receipt_count >= 1:
        review_depth_score += 25
    if base_note_count >= 1:
        review_depth_score += 25
    if base_assignment_count >= 1:
        review_depth_score += 25

    status = {
        "ok": not failed_checks,
        "pack": "145",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "owner_action_center": {
            "status": action.get("status"),
            "readiness_score": action.get("readiness_score"),
            "action_count": action_count,
            "open_action_count": open_action_count,
            "top_action_type": (
                action.get("top_action", {}).get("action_type")
                if isinstance(action.get("top_action"), dict)
                else ""
            ),
        },
        "state_tracking": {
            "status": state.get("status"),
            "readiness_score": state.get("readiness_score"),
            "action_count": state.get("action_count"),
            "tracked_action_count": tracked_action_count,
            "open_action_count": state.get("open_action_count"),
            "closed_action_count": closed_action_count,
            "receipt_count": state_receipt_count,
            "by_state": state.get("by_state", {}),
        },
        "state_receipts": {
            "status": receipts.get("status"),
            "readiness_score": receipts.get("readiness_score"),
            "base_receipt_count": base_receipt_count,
            "filtered_receipt_count": filtered_receipt_count,
            "top_new_state": (
                receipts.get("top_receipt", {}).get("new_state")
                if isinstance(receipts.get("top_receipt"), dict)
                else ""
            ),
        },
        "notes": {
            "status": notes.get("status"),
            "readiness_score": notes.get("readiness_score"),
            "base_note_count": base_note_count,
            "filtered_note_count": notes.get("filtered_note_count"),
            "receipt_count": note_receipt_count,
            "top_note_type": (
                notes.get("top_note", {}).get("note_type")
                if isinstance(notes.get("top_note"), dict)
                else ""
            ),
        },
        "assignments": {
            "status": assignments.get("status"),
            "readiness_score": assignments.get("readiness_score"),
            "base_assignment_count": base_assignment_count,
            "filtered_assignment_count": assignments.get("filtered_assignment_count"),
            "unassigned_action_count": unassigned_action_count,
            "receipt_count": assignment_receipt_count,
            "top_assignment_status": (
                assignments.get("top_assignment", {}).get("assignment_status")
                if isinstance(assignments.get("top_assignment"), dict)
                else ""
            ),
            "top_assigned_to": (
                assignments.get("top_assignment", {}).get("assigned_to")
                if isinstance(assignments.get("top_assignment"), dict)
                else ""
            ),
        },
        "route_health": {
            "coverage_pct": route_coverage,
            "needs_guard_count": route.get("needs_guard_count"),
            "guarded_needed_count": route.get("guarded_needed_count"),
            "unguarded_needed_count": unguarded_needed,
            "unguarded_high_risk_count": unguarded_high,
        },
        "object_checkpoint": {
            "status": obj.get("status"),
            "readiness_score": obj.get("readiness_score"),
            "helper_wrapped_count": helper_wrapped,
        },
        "review_depth": {
            "score": review_depth_score,
            "total_review_records": total_review_records,
            "has_state": tracked_action_count >= 1,
            "has_receipts": base_receipt_count >= 1,
            "has_notes": base_note_count >= 1,
            "has_assignments": base_assignment_count >= 1,
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Owner Action review-state checkpoint passed"
            if not failed_checks
            else "Owner Action review-state checkpoint needs review"
        ),
        "human_reason": "Owner Action review-state checkpoint proves state tracking, receipts, notes, assignments, route guards, and object checkpoint are healthy.",
        "soulaana_translation": "Soulaana: Owner Action review stack is connected. The Tower can track action state, receipts, notes, and assignment ownership.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_owner_action_review_checkpoint",
            source_name="owner_action_review_checkpoint_status",
            source_path=str(OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 145 Owner Action review-state checkpoint generated.",
            metadata={
                "pack": "145",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "review_depth_score": review_depth_score,
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_panel:
        write_owner_action_review_checkpoint_panel(status)

    return status


def render_owner_action_review_checkpoint_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_review_checkpoint(write_panel=False)

    action = status.get("owner_action_center", {}) if isinstance(status.get("owner_action_center"), dict) else {}
    state = status.get("state_tracking", {}) if isinstance(status.get("state_tracking"), dict) else {}
    receipts = status.get("state_receipts", {}) if isinstance(status.get("state_receipts"), dict) else {}
    notes = status.get("notes", {}) if isinstance(status.get("notes"), dict) else {}
    assignments = status.get("assignments", {}) if isinstance(status.get("assignments"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    obj = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    depth = status.get("review_depth", {}) if isinstance(status.get("review_depth"), dict) else {}

    cards = [
        ("Actions", action.get("action_count", 0), "Queue"),
        ("Tracked", state.get("tracked_action_count", 0), "State"),
        ("State Receipts", receipts.get("base_receipt_count", 0), "Receipts"),
        ("Notes", notes.get("base_note_count", 0), "Notes"),
        ("Assignments", assignments.get("base_assignment_count", 0), "Owners"),
        ("Depth", depth.get("score", 0), "Review Score"),
        ("Route", f"{route.get('coverage_pct', 0)}%", "Wall"),
        ("Helpers", obj.get("helper_wrapped_count", 0), "Clean"),
    ]

    card_html = []
    for title, value, label in cards:
        card_html.append(f"""
        <article class="owner-action-review-checkpoint-card">
          <div class="owner-action-review-checkpoint-card__eyebrow">{_html_escape(label)}</div>
          <h3>{_html_escape(value)}</h3>
          <p>{_html_escape(title)}</p>
        </article>
        """)

    html = f"""
<!-- PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION -->
<section class="owner-action-review-checkpoint" data-pack="145">
  <style>
    .owner-action-review-checkpoint {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(143,221,158,.13), transparent 34%),
        linear-gradient(135deg, rgba(10,34,25,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-review-checkpoint__eyebrow {{
      color: rgba(143,221,158,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-review-checkpoint h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-review-checkpoint p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-review-checkpoint-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-review-checkpoint-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-review-checkpoint-card__eyebrow {{
      color: rgba(143,221,158,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-review-checkpoint-card h3 {{
      margin: 0 0 6px;
      font-size: 18px;
      word-break: break-word;
    }}
    .owner-action-review-checkpoint-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .owner-action-review-checkpoint-note {{
      margin-top: 14px;
      border: 1px solid rgba(143,221,158,.22);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.035);
      color: rgba(245,234,210,.72);
    }}
    @media (max-width: 1000px) {{
      .owner-action-review-checkpoint-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-review-checkpoint__eyebrow">PACK 145 · OWNER ACTION REVIEW CHECKPOINT</div>
  <h2>Owner Action Review-State Checkpoint</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action review checkpoint loaded.'))}</p>

  <div class="owner-action-review-checkpoint-grid">
    {''.join(card_html)}
  </div>

  <div class="owner-action-review-checkpoint-note">
    <strong>Top state:</strong> {_html_escape(receipts.get('top_new_state', ''))}<br>
    <strong>Top note type:</strong> {_html_escape(notes.get('top_note_type', ''))}<br>
    <strong>Top assignment:</strong> {_html_escape(assignments.get('top_assignment_status', ''))} · {_html_escape(assignments.get('top_assigned_to', ''))}
  </div>
</section>
<!-- END PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION -->
"""
    return html


def write_owner_action_review_checkpoint_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_review_checkpoint(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Review Checkpoint</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_review_checkpoint_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "145",
        "decision": "owner_action_review_checkpoint_panel_written",
        "path": str(OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH),
        "human_reason": "Owner Action Review Checkpoint panel written.",
        "soulaana_translation": "Soulaana: Owner Action review checkpoint board posted.",
    }


def load_owner_action_review_checkpoint() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH, {})
    if not data:
        data = build_owner_action_review_checkpoint(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_review_checkpoint_status_card() -> Dict[str, Any]:
    status = load_owner_action_review_checkpoint()
    state = status.get("state_tracking", {}) if isinstance(status.get("state_tracking"), dict) else {}
    notes = status.get("notes", {}) if isinstance(status.get("notes"), dict) else {}
    assignments = status.get("assignments", {}) if isinstance(status.get("assignments"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    depth = status.get("review_depth", {}) if isinstance(status.get("review_depth"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "145",
        "title": "Owner Action Review Checkpoint",
        "readiness_score": status.get("readiness_score", 0),
        "review_depth_score": depth.get("score", 0),
        "tracked_action_count": state.get("tracked_action_count", 0),
        "state_receipt_count": state.get("receipt_count", 0),
        "note_count": notes.get("base_note_count", 0),
        "assignment_count": assignments.get("base_assignment_count", 0),
        "route_coverage_pct": route.get("coverage_pct", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH)),
        "human_reason": "Owner Action Review Checkpoint status card loaded.",
        "soulaana_translation": "Soulaana: Owner Action review checkpoint is visible.",
    }


def reset_owner_action_review_checkpoint_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH, {
        "ok": True,
        "pack": "145",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action Review Checkpoint reset for test.",
    })
    if OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH.exists():
        try:
            OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_review_checkpoint_reset_for_test",
        "soulaana_translation": "Soulaana: Owner Action review checkpoint reset for a clean test lane.",
    }
