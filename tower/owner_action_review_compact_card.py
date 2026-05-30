
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH = DATA_DIR / "owner_action_review_compact_card_status.json"
OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH = DATA_DIR / "owner_action_review_compact_card_panel.html"


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


def _load_cached_dashboard() -> Dict[str, Any]:
    try:
        from tower.owner_action_review_dashboard_cards import load_owner_action_review_dashboard_cards_status
        status = load_owner_action_review_dashboard_cards_status()
        if isinstance(status, dict) and status:
            return status
    except Exception:
        pass

    data = _load_json(DATA_DIR / "owner_action_review_dashboard_cards_status.json", {})
    return data if isinstance(data, dict) else {}


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


def build_owner_action_review_compact_card(write_panel: bool = True) -> Dict[str, Any]:
    dashboard = _load_cached_dashboard()
    checkpoint = _load_cached_checkpoint()

    summary = dashboard.get("summary", {}) if isinstance(dashboard.get("summary"), dict) else {}
    route = checkpoint.get("route_health", {}) if isinstance(checkpoint.get("route_health"), dict) else {}
    obj = checkpoint.get("object_checkpoint", {}) if isinstance(checkpoint.get("object_checkpoint"), dict) else {}
    depth = checkpoint.get("review_depth", {}) if isinstance(checkpoint.get("review_depth"), dict) else {}

    card_count = _num(dashboard.get("card_count"), 0)
    review_depth_score = _num(summary.get("review_depth_score"), _num(depth.get("score"), 0))
    action_count = _num(summary.get("action_count"), 0)
    tracked_action_count = _num(summary.get("tracked_action_count"), 0)
    state_receipt_count = _num(summary.get("state_receipt_count"), 0)
    note_count = _num(summary.get("note_count"), 0)
    assignment_count = _num(summary.get("assignment_count"), 0)

    route_coverage = _num(summary.get("route_coverage_pct"), _num(route.get("coverage_pct"), 0))
    unguarded_needed = _num(route.get("unguarded_needed_count"), 0)
    unguarded_high = _num(route.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _num(summary.get("helper_wrapped_count"), _num(obj.get("helper_wrapped_count"), 0))

    wall_sealed = route_coverage == 100 and unguarded_needed == 0 and unguarded_high == 0
    review_ready = review_depth_score == 100 and card_count >= 7
    helper_clean = helper_wrapped == 0

    if review_ready and wall_sealed and helper_clean:
        compact_status = "ready"
        compact_label = "Owner Review Ready"
        owner_message = "Owner Action review is organized, dashboard cards are visible, and the route wall is sealed."
        recommended_action = "review_dashboard_cards"
    elif not wall_sealed:
        compact_status = "route_review"
        compact_label = "Route Review Needed"
        owner_message = "Owner Action review exists, but the route wall needs attention first."
        recommended_action = "review_route_wall"
    elif not helper_clean:
        compact_status = "helper_review"
        compact_label = "Helper Review Needed"
        owner_message = "Owner Action review exists, but helper wrapping needs review."
        recommended_action = "review_object_checkpoint"
    else:
        compact_status = "review"
        compact_label = "Review Needed"
        owner_message = "Owner Action review needs attention before it is fully ready."
        recommended_action = "review_owner_action_checkpoint"

    checks = {
        "dashboard_loaded": bool(dashboard),
        "dashboard_passed": dashboard.get("status") == "passed",
        "dashboard_card_count_7": card_count == 7,
        "checkpoint_loaded": bool(checkpoint),
        "checkpoint_passed": checkpoint.get("status") == "passed",
        "review_depth_100": review_depth_score == 100,
        "route_wall_sealed": wall_sealed,
        "helper_wrapped_zero": helper_clean,
    }
    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "148",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "compact_status": compact_status,
        "compact_label": compact_label,
        "owner_message": owner_message,
        "recommended_action": recommended_action,
        "quick_links": [
            {
                "title": "Dashboard Cards",
                "href": "/tower/owner-action-review-dashboard-cards.json",
                "kind": "status_json",
            },
            {
                "title": "Review Checkpoint",
                "href": "/tower/owner-action-review-checkpoint.json",
                "kind": "status_json",
            },
            {
                "title": "Owner Action Center",
                "href": "/tower/owner-action-center.json",
                "kind": "status_json",
            },
        ],
        "metrics": {
            "card_count": card_count,
            "review_depth_score": review_depth_score,
            "action_count": action_count,
            "tracked_action_count": tracked_action_count,
            "state_receipt_count": state_receipt_count,
            "note_count": note_count,
            "assignment_count": assignment_count,
            "route_coverage_pct": route_coverage,
            "unguarded_needed_count": unguarded_needed,
            "unguarded_high_risk_count": unguarded_high,
            "helper_wrapped_count": helper_wrapped,
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 5)),
        "human_reason": "Compact Owner Action review command card is ready from cached dashboard/checkpoint state.",
        "soulaana_translation": "Soulaana: Owner Action review is now condensed into one command card.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH, status)

    if write_panel:
        write_owner_action_review_compact_card_panel(status)

    return status


def render_owner_action_review_compact_card_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_review_compact_card(write_panel=False)
    metrics = status.get("metrics", {}) if isinstance(status.get("metrics"), dict) else {}
    links = status.get("quick_links", []) if isinstance(status.get("quick_links"), list) else []

    link_html = []
    for link in links:
        if not isinstance(link, dict):
            continue
        link_html.append(f"""
        <a class="owner-action-compact-link" href="{_html_escape(link.get('href', '#'))}">
          {_html_escape(link.get('title', 'Open'))}
        </a>
        """)

    html = f"""
<!-- PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION -->
<section class="owner-action-compact-card" data-pack="148">
  <style>
    .owner-action-compact-card {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.16), transparent 34%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.12), transparent 36%),
        linear-gradient(135deg, rgba(54,35,11,.88), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-compact-card__eyebrow {{
      color: rgba(220,183,94,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-compact-card h2 {{
      margin: 0;
      font-size: 26px;
      letter-spacing: -.035em;
    }}
    .owner-action-compact-card p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
      max-width: 860px;
    }}
    .owner-action-compact-grid {{
      display: grid;
      grid-template-columns: 1.4fr repeat(4, minmax(0, .8fr));
      gap: 12px;
      margin-top: 14px;
      align-items: stretch;
    }}
    .owner-action-compact-primary,
    .owner-action-compact-metric {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-compact-primary h3 {{
      margin: 0 0 8px;
      font-size: 20px;
    }}
    .owner-action-compact-primary span {{
      display: inline-flex;
      border: 1px solid rgba(220,183,94,.32);
      border-radius: 999px;
      padding: 5px 9px;
      color: rgba(220,183,94,.94);
      font-size: 12px;
      margin-bottom: 10px;
    }}
    .owner-action-compact-metric small {{
      display: block;
      color: rgba(220,183,94,.78);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-compact-metric b {{
      display: block;
      font-size: 18px;
      color: #f5ead2;
      word-break: break-word;
    }}
    .owner-action-compact-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }}
    .owner-action-compact-link {{
      display: inline-flex;
      border: 1px solid rgba(220,183,94,.28);
      border-radius: 999px;
      padding: 8px 12px;
      color: rgba(245,234,210,.88);
      text-decoration: none;
      background: rgba(255,255,255,.035);
      font-size: 13px;
    }}
    @media (max-width: 1100px) {{
      .owner-action-compact-grid {{
        grid-template-columns: 1fr 1fr;
      }}
    }}
    @media (max-width: 760px) {{
      .owner-action-compact-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-compact-card__eyebrow">PACK 148 · COMPACT OWNER ACTION REVIEW</div>
  <h2>{_html_escape(status.get('compact_label', 'Owner Action Review'))}</h2>
  <p>{_html_escape(status.get('owner_message', 'Owner Action review compact card loaded.'))}</p>

  <div class="owner-action-compact-grid">
    <article class="owner-action-compact-primary">
      <span>{_html_escape(status.get('compact_status', 'ready'))}</span>
      <h3>{_html_escape(status.get('recommended_action', 'review_dashboard_cards'))}</h3>
      <p>{_html_escape(status.get('human_reason', 'Compact Owner Action review card loaded.'))}</p>
    </article>

    <article class="owner-action-compact-metric"><small>Cards</small><b>{_html_escape(metrics.get('card_count', 0))}</b></article>
    <article class="owner-action-compact-metric"><small>Depth</small><b>{_html_escape(metrics.get('review_depth_score', 0))}%</b></article>
    <article class="owner-action-compact-metric"><small>Wall</small><b>{_html_escape(metrics.get('route_coverage_pct', 0))}%</b></article>
    <article class="owner-action-compact-metric"><small>Helpers</small><b>{_html_escape(metrics.get('helper_wrapped_count', 0))}</b></article>
  </div>

  <div class="owner-action-compact-links">
    {''.join(link_html)}
  </div>
</section>
<!-- END PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION -->
"""
    return html


def write_owner_action_review_compact_card_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_review_compact_card(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Compact Owner Action Review Card</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1280px;margin:auto;">
{render_owner_action_review_compact_card_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "148",
        "decision": "owner_action_review_compact_card_panel_written",
        "path": str(OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH),
        "human_reason": "Compact Owner Action Review Card panel written.",
        "soulaana_translation": "Soulaana: Compact owner action review card posted.",
    }


def load_owner_action_review_compact_card_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH, {})
    if not data:
        data = build_owner_action_review_compact_card(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_review_compact_card_status_card() -> Dict[str, Any]:
    status = load_owner_action_review_compact_card_status()
    metrics = status.get("metrics", {}) if isinstance(status.get("metrics"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "148",
        "title": "Compact Owner Action Review Card",
        "readiness_score": status.get("readiness_score", 0),
        "compact_status": status.get("compact_status"),
        "compact_label": status.get("compact_label"),
        "recommended_action": status.get("recommended_action"),
        "card_count": metrics.get("card_count", 0),
        "review_depth_score": metrics.get("review_depth_score", 0),
        "route_coverage_pct": metrics.get("route_coverage_pct", 0),
        "helper_wrapped_count": metrics.get("helper_wrapped_count", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH)),
        "human_reason": "Compact Owner Action Review Card status card loaded.",
        "soulaana_translation": "Soulaana: Compact owner action review card is visible.",
    }


def reset_owner_action_review_compact_card_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH, {
        "ok": True,
        "pack": "148",
        "reset_at": _utc_now(),
        "human_reason": "Compact Owner Action Review Card reset for test.",
    })
    if OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH.exists():
        try:
            OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_review_compact_card_reset_for_test",
        "soulaana_translation": "Soulaana: Compact owner action review card reset for a clean test lane.",
    }
