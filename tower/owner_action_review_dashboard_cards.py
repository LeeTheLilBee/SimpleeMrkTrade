
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH = DATA_DIR / "owner_action_review_dashboard_cards_status.json"
OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH = DATA_DIR / "owner_action_review_dashboard_cards_panel.html"


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


def _load_cached_checkpoint() -> Dict[str, Any]:
    try:
        from tower.owner_action_review_checkpoint import load_owner_action_review_checkpoint
        status = load_owner_action_review_checkpoint()
        if isinstance(status, dict) and status:
            return status
    except Exception:
        pass

    data = _load_json(DATA_DIR / "owner_action_review_checkpoint_status.json", {})
    return data if isinstance(data, dict) else {}


def _card(
    *,
    card_id: str,
    title: str,
    value: Any,
    subtitle: str,
    status: str = "ready",
    severity: str = "info",
    href: str = "",
    pack: str = "147",
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "card_id": card_id,
        "title": title,
        "value": value,
        "subtitle": subtitle,
        "status": status,
        "severity": severity,
        "href": href,
        "pack": pack,
        "details": details if isinstance(details, dict) else {},
    }


def build_owner_action_review_dashboard_cards(write_panel: bool = True) -> Dict[str, Any]:
    checkpoint = _load_cached_checkpoint()

    owner_action = checkpoint.get("owner_action_center", {}) if isinstance(checkpoint.get("owner_action_center"), dict) else {}
    state = checkpoint.get("state_tracking", {}) if isinstance(checkpoint.get("state_tracking"), dict) else {}
    receipts = checkpoint.get("state_receipts", {}) if isinstance(checkpoint.get("state_receipts"), dict) else {}
    notes = checkpoint.get("notes", {}) if isinstance(checkpoint.get("notes"), dict) else {}
    assignments = checkpoint.get("assignments", {}) if isinstance(checkpoint.get("assignments"), dict) else {}
    route = checkpoint.get("route_health", {}) if isinstance(checkpoint.get("route_health"), dict) else {}
    obj = checkpoint.get("object_checkpoint", {}) if isinstance(checkpoint.get("object_checkpoint"), dict) else {}
    depth = checkpoint.get("review_depth", {}) if isinstance(checkpoint.get("review_depth"), dict) else {}

    review_depth_score = _num(depth.get("score"), 0)
    action_count = _num(owner_action.get("action_count"), 0)
    open_action_count = _num(owner_action.get("open_action_count"), 0)

    tracked_action_count = _num(state.get("tracked_action_count"), 0)
    closed_action_count = _num(state.get("closed_action_count"), 0)
    state_receipt_count = _num(receipts.get("base_receipt_count"), _num(state.get("receipt_count"), 0))

    note_count = _num(notes.get("base_note_count"), 0)
    note_receipt_count = _num(notes.get("receipt_count"), 0)

    assignment_count = _num(assignments.get("base_assignment_count"), 0)
    assignment_receipt_count = _num(assignments.get("receipt_count"), 0)
    unassigned_action_count = _num(assignments.get("unassigned_action_count"), max(0, action_count - assignment_count))

    route_coverage = _num(route.get("coverage_pct"), 0)
    unguarded_needed = _num(route.get("unguarded_needed_count"), 0)
    unguarded_high = _num(route.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _num(obj.get("helper_wrapped_count"), 0)

    checkpoint_ok = checkpoint.get("ok") is True and checkpoint.get("status") == "passed"
    wall_sealed = route_coverage == 100 and unguarded_needed == 0 and unguarded_high == 0
    helper_clean = helper_wrapped == 0

    health_status = "ready" if checkpoint_ok and review_depth_score == 100 else "review"
    wall_status = "sealed" if wall_sealed else "review"
    helper_status = "clean" if helper_clean else "review"

    cards = [
        _card(
            card_id="review_health",
            title="Review Health",
            value=f"{review_depth_score}%",
            subtitle="State, receipts, notes, and assignments connected",
            status=health_status,
            severity="success" if health_status == "ready" else "warning",
            href="/tower/owner-action-review-checkpoint.json",
            pack="145+147",
            details={
                "checkpoint_status": checkpoint.get("status"),
                "checkpoint_readiness": checkpoint.get("readiness_score"),
                "review_depth_score": review_depth_score,
                "total_review_records": depth.get("total_review_records"),
            },
        ),
        _card(
            card_id="action_state",
            title="Action State",
            value=f"{tracked_action_count}/{action_count}",
            subtitle=f"{closed_action_count} closed · {open_action_count} open",
            status="tracked" if tracked_action_count >= 1 else "empty",
            severity="success" if tracked_action_count >= 1 else "info",
            href="/tower/owner-action-state.json",
            pack="141+147",
            details={
                "tracked_action_count": tracked_action_count,
                "action_count": action_count,
                "closed_action_count": closed_action_count,
                "by_state": state.get("by_state", {}),
            },
        ),
        _card(
            card_id="state_receipts",
            title="State Receipts",
            value=state_receipt_count,
            subtitle=f"Top state: {receipts.get('top_new_state', '')}",
            status="ready" if state_receipt_count >= 1 else "empty",
            severity="success" if state_receipt_count >= 1 else "info",
            href="/tower/owner-action-state-receipts.json",
            pack="142+147",
            details={
                "base_receipt_count": state_receipt_count,
                "filtered_receipt_count": receipts.get("filtered_receipt_count"),
                "top_new_state": receipts.get("top_new_state"),
            },
        ),
        _card(
            card_id="notes",
            title="Notes",
            value=note_count,
            subtitle=f"{note_receipt_count} note receipts · top: {notes.get('top_note_type', '')}",
            status="ready" if note_count >= 1 else "empty",
            severity="success" if note_count >= 1 else "info",
            href="/tower/owner-action-notes.json",
            pack="143+147",
            details={
                "base_note_count": note_count,
                "receipt_count": note_receipt_count,
                "top_note_type": notes.get("top_note_type"),
            },
        ),
        _card(
            card_id="assignments",
            title="Assignments",
            value=assignment_count,
            subtitle=f"{unassigned_action_count} unassigned · top: {assignments.get('top_assignment_status', '')}",
            status="ready" if assignment_count >= 1 else "empty",
            severity="success" if assignment_count >= 1 else "info",
            href="/tower/owner-action-assignments.json",
            pack="144+147",
            details={
                "base_assignment_count": assignment_count,
                "receipt_count": assignment_receipt_count,
                "unassigned_action_count": unassigned_action_count,
                "top_assignment_status": assignments.get("top_assignment_status"),
                "top_assigned_to": assignments.get("top_assigned_to"),
            },
        ),
        _card(
            card_id="route_wall",
            title="Route Wall",
            value=f"{route_coverage}%",
            subtitle=f"{unguarded_needed} unguarded · {unguarded_high} high-risk",
            status=wall_status,
            severity="success" if wall_status == "sealed" else "danger",
            href="/tower/ob-guard-status.json",
            pack="105+147",
            details={
                "coverage_pct": route_coverage,
                "needs_guard_count": route.get("needs_guard_count"),
                "guarded_needed_count": route.get("guarded_needed_count"),
                "unguarded_needed_count": unguarded_needed,
                "unguarded_high_risk_count": unguarded_high,
            },
        ),
        _card(
            card_id="object_checkpoint",
            title="Object Checkpoint",
            value=helper_wrapped,
            subtitle="helper_wrapped_count",
            status=helper_status,
            severity="success" if helper_status == "clean" else "warning",
            href="/tower/object-permission-checkpoint.json",
            pack="114+147",
            details={
                "status": obj.get("status"),
                "readiness_score": obj.get("readiness_score"),
                "helper_wrapped_count": helper_wrapped,
            },
        ),
    ]

    checks = {
        "checkpoint_loaded": bool(checkpoint),
        "checkpoint_passed": checkpoint.get("status") == "passed",
        "review_depth_100": review_depth_score == 100,
        "cards_present": len(cards) == 7,
        "state_card_present": any(card.get("card_id") == "action_state" for card in cards),
        "receipt_card_present": any(card.get("card_id") == "state_receipts" for card in cards),
        "notes_card_present": any(card.get("card_id") == "notes" for card in cards),
        "assignments_card_present": any(card.get("card_id") == "assignments" for card in cards),
        "route_wall_sealed": wall_sealed,
        "helper_wrapped_zero": helper_clean,
    }
    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "147",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "card_count": len(cards),
        "cards": cards,
        "summary": {
            "review_depth_score": review_depth_score,
            "action_count": action_count,
            "tracked_action_count": tracked_action_count,
            "state_receipt_count": state_receipt_count,
            "note_count": note_count,
            "assignment_count": assignment_count,
            "route_coverage_pct": route_coverage,
            "helper_wrapped_count": helper_wrapped,
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 5)),
        "human_reason": "Owner Action review dashboard cards are ready from cached checkpoint state.",
        "soulaana_translation": "Soulaana: Owner Action review is now readable as dashboard cards.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH, status)

    if write_panel:
        write_owner_action_review_dashboard_cards_panel(status)

    return status


def render_owner_action_review_dashboard_cards_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_review_dashboard_cards(write_panel=False)
    cards = status.get("cards", []) if isinstance(status.get("cards"), list) else []

    card_html = []
    for card in cards:
        if not isinstance(card, dict):
            continue

        severity = str(card.get("severity", "info") or "info")
        border = {
            "success": "rgba(143,221,158,.42)",
            "warning": "rgba(220,183,94,.42)",
            "danger": "rgba(255,120,120,.42)",
            "info": "rgba(168,175,255,.42)",
        }.get(severity, "rgba(168,175,255,.42)")

        card_html.append(f"""
        <article class="owner-action-dashboard-card" style="border-color:{border};">
          <div class="owner-action-dashboard-card__eyebrow">{_html_escape(card.get('status', 'ready'))}</div>
          <h3>{_html_escape(card.get('value', ''))}</h3>
          <h4>{_html_escape(card.get('title', 'Dashboard Card'))}</h4>
          <p>{_html_escape(card.get('subtitle', ''))}</p>
          <a href="{_html_escape(card.get('href', '#'))}">Open source</a>
        </article>
        """)

    html = f"""
<!-- PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION -->
<section class="owner-action-dashboard-cards" data-pack="147">
  <style>
    .owner-action-dashboard-cards {{
      margin: 24px 0;
      border: 1px solid rgba(168,175,255,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(168,175,255,.14), transparent 34%),
        linear-gradient(135deg, rgba(22,20,48,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-dashboard-cards__eyebrow {{
      color: rgba(168,175,255,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-dashboard-cards h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-dashboard-cards p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-dashboard-grid {{
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-dashboard-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      min-height: 160px;
    }}
    .owner-action-dashboard-card__eyebrow {{
      color: rgba(168,175,255,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 8px;
    }}
    .owner-action-dashboard-card h3 {{
      margin: 0 0 8px;
      font-size: 22px;
      line-height: 1;
    }}
    .owner-action-dashboard-card h4 {{
      margin: 0 0 8px;
      font-size: 14px;
      color: #f5ead2;
    }}
    .owner-action-dashboard-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .owner-action-dashboard-card a {{
      display: inline-flex;
      margin-top: 12px;
      color: rgba(168,175,255,.95);
      font-size: 12px;
      text-decoration: none;
    }}
    @media (max-width: 1200px) {{
      .owner-action-dashboard-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 760px) {{
      .owner-action-dashboard-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-dashboard-cards__eyebrow">PACK 147 · OWNER ACTION REVIEW DASHBOARD</div>
  <h2>Owner Action Review Dashboard Cards</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action review dashboard cards loaded.'))}</p>

  <div class="owner-action-dashboard-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION -->
"""
    return html


def write_owner_action_review_dashboard_cards_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_review_dashboard_cards(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Review Dashboard Cards</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1280px;margin:auto;">
{render_owner_action_review_dashboard_cards_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "147",
        "decision": "owner_action_review_dashboard_cards_panel_written",
        "path": str(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH),
        "human_reason": "Owner Action Review Dashboard Cards panel written.",
        "soulaana_translation": "Soulaana: Owner Action review dashboard cards posted.",
    }


def load_owner_action_review_dashboard_cards_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH, {})
    if not data:
        data = build_owner_action_review_dashboard_cards(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_review_dashboard_cards_status_card() -> Dict[str, Any]:
    status = load_owner_action_review_dashboard_cards_status()
    summary = status.get("summary", {}) if isinstance(status.get("summary"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "147",
        "title": "Owner Action Review Dashboard Cards",
        "readiness_score": status.get("readiness_score", 0),
        "card_count": status.get("card_count", 0),
        "review_depth_score": summary.get("review_depth_score", 0),
        "route_coverage_pct": summary.get("route_coverage_pct", 0),
        "helper_wrapped_count": summary.get("helper_wrapped_count", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH)),
        "human_reason": "Owner Action Review Dashboard Cards status card loaded.",
        "soulaana_translation": "Soulaana: Owner Action review dashboard cards are visible.",
    }


def reset_owner_action_review_dashboard_cards_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH, {
        "ok": True,
        "pack": "147",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action Review Dashboard Cards reset for test.",
    })
    if OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH.exists():
        try:
            OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_review_dashboard_cards_reset_for_test",
        "soulaana_translation": "Soulaana: Owner Action dashboard cards reset for a clean test lane.",
    }
