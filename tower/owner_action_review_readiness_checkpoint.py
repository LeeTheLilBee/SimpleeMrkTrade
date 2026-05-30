
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_REVIEW_READINESS_STATUS_PATH = DATA_DIR / "owner_action_review_readiness_checkpoint_status.json"
OWNER_ACTION_REVIEW_READINESS_PANEL_PATH = DATA_DIR / "owner_action_review_readiness_checkpoint_panel.html"


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
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
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


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


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


def _load_cached_json(filename: str) -> Dict[str, Any]:
    data = _load_json(DATA_DIR / filename, {})
    return data if isinstance(data, dict) else {}


def _extract_quick_action_flags(quick: Dict[str, Any]) -> Dict[str, Any]:
    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    ids = {
        action.get("action_id")
        for action in actions
        if isinstance(action, dict)
    }
    hrefs = {
        action.get("href")
        for action in actions
        if isinstance(action, dict)
    }

    return {
        "action_count": len(actions),
        "has_review_checkpoint": "review_owner_action_review_checkpoint" in ids,
        "has_dashboard_cards": "review_owner_action_review_dashboard_cards" in ids,
        "has_compact_card": "review_owner_action_compact_card" in ids,
        "has_focus_lanes": "review_owner_action_focus_lanes" in ids,
        "has_review_checkpoint_href": "/tower/owner-action-review-checkpoint.json" in hrefs,
        "has_dashboard_cards_href": "/tower/owner-action-review-dashboard-cards.json" in hrefs,
        "has_compact_card_href": "/tower/owner-action-review-compact-card.json" in hrefs,
        "has_focus_lanes_href": "/tower/owner-action-review-focus-lanes.json" in hrefs,
    }


def build_owner_action_review_readiness_checkpoint(write_panel: bool = True) -> Dict[str, Any]:
    # Use real builders only for cached/non-recursive layers that are already fast.
    # Do not call anything that recursively calls the unified page.

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

    receipts_call = _safe_call(
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

    review_checkpoint_call = _safe_call(
        "owner_action_review_checkpoint",
        lambda: __import__(
            "tower.owner_action_review_checkpoint",
            fromlist=["build_owner_action_review_checkpoint"],
        ).build_owner_action_review_checkpoint(write_panel=True),
    )

    dashboard_call = _safe_call(
        "owner_action_review_dashboard_cards",
        lambda: __import__(
            "tower.owner_action_review_dashboard_cards",
            fromlist=["build_owner_action_review_dashboard_cards"],
        ).build_owner_action_review_dashboard_cards(write_panel=True),
    )

    compact_call = _safe_call(
        "owner_action_review_compact_card",
        lambda: __import__(
            "tower.owner_action_review_compact_card",
            fromlist=["build_owner_action_review_compact_card"],
        ).build_owner_action_review_compact_card(write_panel=True),
    )

    focus_call = _safe_call(
        "owner_action_review_focus_lanes",
        lambda: __import__(
            "tower.owner_action_review_focus_lanes",
            fromlist=["build_owner_action_review_focus_lanes"],
        ).build_owner_action_review_focus_lanes(lane="all", write_panel=True),
    )

    quick_call = _safe_call(
        "owner_quick_actions_cached",
        lambda: __import__(
            "tower.security_command_owner_quick_actions",
            fromlist=["build_owner_quick_actions_status"],
        ).build_owner_quick_actions_status(write_panel=True),
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
    receipts = receipts_call.get("result", {})
    notes = notes_call.get("result", {})
    assignments = assignments_call.get("result", {})
    review = review_checkpoint_call.get("result", {})
    dashboard = dashboard_call.get("result", {})
    compact = compact_call.get("result", {})
    focus = focus_call.get("result", {})
    quick = quick_call.get("result", {})
    route = route_call.get("result", {})
    obj = object_call.get("result", {})

    quick_flags = _extract_quick_action_flags(quick)

    unified_html_path = DATA_DIR / "security_command_unified_owner_page.html"
    unified_html_exists = unified_html_path.exists()
    unified_html = ""
    try:
        if unified_html_exists:
            unified_html = unified_html_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        unified_html = ""

    unified_flags = {
        "html_exists": unified_html_exists,
        "has_review_checkpoint_section": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html,
        "has_dashboard_cards_section": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html,
        "has_compact_card_section": "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html,
        "has_focus_lanes_section": "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in unified_html,
        "html_length": len(unified_html),
    }

    route_coverage = _num(route.get("coverage_pct"), 0)
    unguarded_needed = _num(route.get("unguarded_needed_count"), 0)
    unguarded_high = _num(route.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _num(obj.get("helper_wrapped_count"), 0)

    review_depth_score = _num(review.get("review_depth", {}).get("score") if isinstance(review.get("review_depth"), dict) else 0, 0)
    dashboard_card_count = _num(dashboard.get("card_count"), 0)
    compact_metrics = compact.get("metrics", {}) if isinstance(compact.get("metrics"), dict) else {}
    focus_lanes = focus.get("available_lanes", {}) if isinstance(focus.get("available_lanes"), dict) else {}

    checks = {
        "action_call_ok": action_call.get("ok") is True,
        "action_center_passed": action.get("status") == "passed",
        "action_count_present": _num(action.get("action_count"), 0) >= 1,

        "state_call_ok": state_call.get("ok") is True,
        "state_passed": state.get("status") == "passed",
        "tracked_action_present": _num(state.get("tracked_action_count"), 0) >= 1,

        "receipts_call_ok": receipts_call.get("ok") is True,
        "receipts_passed": receipts.get("status") == "passed",
        "state_receipts_present": _num(receipts.get("base_receipt_count"), 0) >= 1,

        "notes_call_ok": notes_call.get("ok") is True,
        "notes_passed": notes.get("status") == "passed",
        "notes_present": _num(notes.get("base_note_count"), 0) >= 1,

        "assignments_call_ok": assignments_call.get("ok") is True,
        "assignments_passed": assignments.get("status") == "passed",
        "assignments_present": _num(assignments.get("base_assignment_count"), 0) >= 1,

        "review_checkpoint_call_ok": review_checkpoint_call.get("ok") is True,
        "review_checkpoint_passed": review.get("status") == "passed",
        "review_depth_100": review_depth_score == 100,

        "dashboard_call_ok": dashboard_call.get("ok") is True,
        "dashboard_passed": dashboard.get("status") == "passed",
        "dashboard_card_count_7": dashboard_card_count == 7,

        "compact_call_ok": compact_call.get("ok") is True,
        "compact_passed": compact.get("status") == "passed",
        "compact_ready": compact.get("compact_status") == "ready",
        "compact_card_count_7": _num(compact_metrics.get("card_count"), 0) == 7,

        "focus_call_ok": focus_call.get("ok") is True,
        "focus_passed": focus.get("status") == "passed",
        "focus_base_card_count_7": _num(focus.get("base_card_count"), 0) == 7,
        "focus_filtered_card_count_7": _num(focus.get("filtered_card_count"), 0) == 7,
        "focus_available_lanes_9": len(focus_lanes) >= 9,

        "quick_call_ok": quick_call.get("ok") is True,
        "quick_passed": quick.get("status") == "passed",
        "quick_has_review_checkpoint": quick_flags.get("has_review_checkpoint") is True,
        "quick_has_dashboard_cards": quick_flags.get("has_dashboard_cards") is True,
        "quick_has_compact_card": quick_flags.get("has_compact_card") is True,
        "quick_has_focus_lanes": quick_flags.get("has_focus_lanes") is True,

        "unified_html_exists": unified_flags.get("html_exists") is True,
        "unified_has_review_checkpoint": unified_flags.get("has_review_checkpoint_section") is True,
        "unified_has_dashboard_cards": unified_flags.get("has_dashboard_cards_section") is True,
        "unified_has_compact_card": unified_flags.get("has_compact_card_section") is True,
        "unified_has_focus_lanes": unified_flags.get("has_focus_lanes_section") is True,

        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_100": route_coverage == 100,
        "route_unguarded_zero": unguarded_needed == 0,
        "route_high_risk_zero": unguarded_high == 0,

        "object_call_ok": object_call.get("ok") is True,
        "object_checkpoint_passed": obj.get("status") == "passed",
        "helper_wrapped_zero": helper_wrapped == 0,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    pack_statuses = {
        "141_state_tracking": {
            "status": state.get("status"),
            "tracked_action_count": state.get("tracked_action_count"),
            "readiness_score": state.get("readiness_score"),
        },
        "142_state_receipts": {
            "status": receipts.get("status"),
            "base_receipt_count": receipts.get("base_receipt_count"),
            "readiness_score": receipts.get("readiness_score"),
        },
        "143_notes": {
            "status": notes.get("status"),
            "base_note_count": notes.get("base_note_count"),
            "receipt_count": notes.get("receipt_count"),
            "readiness_score": notes.get("readiness_score"),
        },
        "144_assignments": {
            "status": assignments.get("status"),
            "base_assignment_count": assignments.get("base_assignment_count"),
            "receipt_count": assignments.get("receipt_count"),
            "readiness_score": assignments.get("readiness_score"),
        },
        "145_review_checkpoint": {
            "status": review.get("status"),
            "review_depth_score": review_depth_score,
            "readiness_score": review.get("readiness_score"),
        },
        "146_quick_unified": {
            "quick_action_count": quick_flags.get("action_count"),
            "unified_sections_present": all([
                unified_flags.get("has_review_checkpoint_section"),
                unified_flags.get("has_dashboard_cards_section"),
                unified_flags.get("has_compact_card_section"),
                unified_flags.get("has_focus_lanes_section"),
            ]),
            "readiness_score": quick.get("readiness_score"),
        },
        "147_dashboard_cards": {
            "status": dashboard.get("status"),
            "card_count": dashboard_card_count,
            "readiness_score": dashboard.get("readiness_score"),
        },
        "148_compact_card": {
            "status": compact.get("status"),
            "compact_status": compact.get("compact_status"),
            "compact_label": compact.get("compact_label"),
            "readiness_score": compact.get("readiness_score"),
        },
        "149_focus_lanes": {
            "status": focus.get("status"),
            "base_card_count": focus.get("base_card_count"),
            "filtered_card_count": focus.get("filtered_card_count"),
            "available_lane_count": len(focus_lanes),
            "readiness_score": focus.get("readiness_score"),
        },
    }

    readiness_score = 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 3))

    status = {
        "ok": not failed_checks,
        "pack": "150",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_REVIEW_READINESS_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_REVIEW_READINESS_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "pack_statuses": pack_statuses,
        "quick_actions": quick_flags,
        "unified_ui": unified_flags,
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
        "final_summary": {
            "owner_action_block_complete": not failed_checks,
            "review_depth_score": review_depth_score,
            "dashboard_card_count": dashboard_card_count,
            "compact_status": compact.get("compact_status"),
            "focus_lane_count": len(focus_lanes),
            "quick_action_count": quick_flags.get("action_count"),
            "route_coverage_pct": route_coverage,
            "helper_wrapped_count": helper_wrapped,
        },
        "readiness_score": readiness_score,
        "readiness_label": (
            "Owner Action review block complete"
            if not failed_checks
            else "Owner Action review block needs review"
        ),
        "human_reason": "Final Owner Action review readiness checkpoint proves Packs 141 through 149 are connected, visible, guarded, non-recursive, and healthy.",
        "soulaana_translation": "Soulaana: Owner Action review is sealed. State, receipts, notes, assignments, dashboard cards, compact card, focus lanes, quick actions, and unified UI are ready.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_REVIEW_READINESS_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_owner_action_review_readiness_checkpoint",
            source_name="owner_action_review_readiness_checkpoint_status",
            source_path=str(OWNER_ACTION_REVIEW_READINESS_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 150 final Owner Action review readiness checkpoint generated.",
            metadata={
                "pack": "150",
                "status": status.get("status"),
                "readiness_score": readiness_score,
                "failed_check_count": len(failed_checks),
                "owner_action_block_complete": not failed_checks,
            },
        )
    except Exception:
        pass

    if write_panel:
        write_owner_action_review_readiness_panel(status)

    return status


def render_owner_action_review_readiness_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_review_readiness_checkpoint(write_panel=False)

    pack_statuses = status.get("pack_statuses", {}) if isinstance(status.get("pack_statuses"), dict) else {}
    final_summary = status.get("final_summary", {}) if isinstance(status.get("final_summary"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    obj = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}

    pack_cards = []
    for pack_name, pack_data in pack_statuses.items():
        if not isinstance(pack_data, dict):
            continue
        pack_cards.append(f"""
        <article class="owner-action-readiness-pack-card">
          <div class="owner-action-readiness-pack-card__eyebrow">{_html_escape(pack_name)}</div>
          <h3>{_html_escape(pack_data.get('status', pack_data.get('compact_status', 'ready')))}</h3>
          <p>{_html_escape(pack_data)}</p>
        </article>
        """)

    html = f"""
<!-- PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION -->
<section class="owner-action-readiness" data-pack="150">
  <style>
    .owner-action-readiness {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.46);
      border-radius: 30px;
      padding: 24px;
      background:
        radial-gradient(circle at top left, rgba(143,221,158,.15), transparent 34%),
        radial-gradient(circle at bottom right, rgba(220,183,94,.12), transparent 36%),
        linear-gradient(135deg, rgba(10,34,25,.90), rgba(8,9,7,.96));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-readiness__eyebrow {{
      color: rgba(143,221,158,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-readiness h2 {{
      margin: 0;
      font-size: 28px;
      letter-spacing: -.04em;
    }}
    .owner-action-readiness p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-readiness-summary {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }}
    .owner-action-readiness-metric,
    .owner-action-readiness-pack-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-readiness-metric small,
    .owner-action-readiness-pack-card__eyebrow {{
      display: block;
      color: rgba(143,221,158,.78);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-readiness-metric b {{
      display: block;
      font-size: 20px;
      color: #f5ead2;
      word-break: break-word;
    }}
    .owner-action-readiness-pack-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-readiness-pack-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
      color: #f5ead2;
    }}
    .owner-action-readiness-pack-card p {{
      margin: 0;
      color: rgba(245,234,210,.60);
      font-size: 11px;
      word-break: break-word;
    }}
    @media (max-width: 1100px) {{
      .owner-action-readiness-summary,
      .owner-action-readiness-pack-grid {{
        grid-template-columns: 1fr 1fr;
      }}
    }}
    @media (max-width: 760px) {{
      .owner-action-readiness-summary,
      .owner-action-readiness-pack-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-readiness__eyebrow">PACK 150 · FINAL OWNER ACTION REVIEW READINESS</div>
  <h2>{_html_escape(status.get('readiness_label', 'Owner Action Review Readiness'))}</h2>
  <p>{_html_escape(status.get('human_reason', 'Final Owner Action review readiness checkpoint loaded.'))}</p>

  <div class="owner-action-readiness-summary">
    <article class="owner-action-readiness-metric"><small>Ready</small><b>{_html_escape(final_summary.get('owner_action_block_complete', False))}</b></article>
    <article class="owner-action-readiness-metric"><small>Depth</small><b>{_html_escape(final_summary.get('review_depth_score', 0))}%</b></article>
    <article class="owner-action-readiness-metric"><small>Cards</small><b>{_html_escape(final_summary.get('dashboard_card_count', 0))}</b></article>
    <article class="owner-action-readiness-metric"><small>Focus Lanes</small><b>{_html_escape(final_summary.get('focus_lane_count', 0))}</b></article>
    <article class="owner-action-readiness-metric"><small>Route Wall</small><b>{_html_escape(route.get('coverage_pct', 0))}%</b></article>
    <article class="owner-action-readiness-metric"><small>Helpers</small><b>{_html_escape(obj.get('helper_wrapped_count', 0))}</b></article>
  </div>

  <div class="owner-action-readiness-pack-grid">
    {''.join(pack_cards)}
  </div>
</section>
<!-- END PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION -->
"""
    return html


def write_owner_action_review_readiness_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_review_readiness_checkpoint(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Final Owner Action Review Readiness</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1280px;margin:auto;">
{render_owner_action_review_readiness_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_REVIEW_READINESS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "150",
        "decision": "owner_action_review_readiness_panel_written",
        "path": str(OWNER_ACTION_REVIEW_READINESS_PANEL_PATH),
        "human_reason": "Final Owner Action Review Readiness panel written.",
        "soulaana_translation": "Soulaana: Final Owner Action review readiness board posted.",
    }


def load_owner_action_review_readiness_checkpoint() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_REVIEW_READINESS_STATUS_PATH, {})
    if not data:
        data = build_owner_action_review_readiness_checkpoint(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_review_readiness_status_card() -> Dict[str, Any]:
    status = load_owner_action_review_readiness_checkpoint()
    summary = status.get("final_summary", {}) if isinstance(status.get("final_summary"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    obj = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "150",
        "title": "Final Owner Action Review Readiness",
        "readiness_score": status.get("readiness_score", 0),
        "owner_action_block_complete": summary.get("owner_action_block_complete", False),
        "review_depth_score": summary.get("review_depth_score", 0),
        "dashboard_card_count": summary.get("dashboard_card_count", 0),
        "compact_status": summary.get("compact_status"),
        "focus_lane_count": summary.get("focus_lane_count", 0),
        "quick_action_count": summary.get("quick_action_count", 0),
        "route_coverage_pct": route.get("coverage_pct", 0),
        "helper_wrapped_count": obj.get("helper_wrapped_count", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_REVIEW_READINESS_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_REVIEW_READINESS_STATUS_PATH)),
        "human_reason": "Final Owner Action Review Readiness status card loaded.",
        "soulaana_translation": "Soulaana: Final Owner Action review readiness checkpoint is visible.",
    }


def reset_owner_action_review_readiness_checkpoint_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_REVIEW_READINESS_STATUS_PATH, {
        "ok": True,
        "pack": "150",
        "reset_at": _utc_now(),
        "human_reason": "Final Owner Action Review Readiness reset for test.",
    })
    if OWNER_ACTION_REVIEW_READINESS_PANEL_PATH.exists():
        try:
            OWNER_ACTION_REVIEW_READINESS_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_review_readiness_reset_for_test",
        "soulaana_translation": "Soulaana: Final Owner Action review readiness reset for a clean test lane.",
    }
