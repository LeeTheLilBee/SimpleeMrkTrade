
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH = DATA_DIR / "owner_action_review_focus_lanes_status.json"
OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH = DATA_DIR / "owner_action_review_focus_lanes_panel.html"


FOCUS_LANE_MAP = {
    "all": {
        "title": "All Review Cards",
        "card_ids": [
            "review_health",
            "action_state",
            "state_receipts",
            "notes",
            "assignments",
            "route_wall",
            "object_checkpoint",
        ],
        "human_reason": "Show every Owner Action review dashboard card.",
    },
    "review_health": {
        "title": "Review Health",
        "card_ids": ["review_health"],
        "human_reason": "Focus on overall review readiness.",
    },
    "state": {
        "title": "State",
        "card_ids": ["action_state"],
        "human_reason": "Focus on Owner Action state tracking.",
    },
    "receipts": {
        "title": "Receipts",
        "card_ids": ["state_receipts"],
        "human_reason": "Focus on Owner Action state receipts.",
    },
    "notes": {
        "title": "Notes",
        "card_ids": ["notes"],
        "human_reason": "Focus on Owner Action notes.",
    },
    "assignments": {
        "title": "Assignments",
        "card_ids": ["assignments"],
        "human_reason": "Focus on Owner Action assignment ownership.",
    },
    "route": {
        "title": "Route Wall",
        "card_ids": ["route_wall"],
        "human_reason": "Focus on route wall coverage and gaps.",
    },
    "object": {
        "title": "Object Checkpoint",
        "card_ids": ["object_checkpoint"],
        "human_reason": "Focus on object checkpoint / helper wrapping health.",
    },
    "attention": {
        "title": "Attention Lane",
        "card_ids": [],
        "human_reason": "Show any cards that are not success/ready/sealed/clean/tracked.",
    },
}


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


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def _load_cached_dashboard_cards() -> Dict[str, Any]:
    try:
        from tower.owner_action_review_dashboard_cards import load_owner_action_review_dashboard_cards_status
        status = load_owner_action_review_dashboard_cards_status()
        if isinstance(status, dict) and status:
            return status
    except Exception:
        pass

    data = _load_json(DATA_DIR / "owner_action_review_dashboard_cards_status.json", {})
    return data if isinstance(data, dict) else {}


def _is_attention_card(card: Dict[str, Any]) -> bool:
    severity = _norm(card.get("severity"))
    status = _norm(card.get("status"))

    if severity in {"warning", "danger", "critical"}:
        return True

    healthy_statuses = {"ready", "tracked", "sealed", "clean"}
    if status and status not in healthy_statuses:
        return True

    return False


def _filter_cards(
    cards: List[Dict[str, Any]],
    *,
    card_id: str = "",
    lane: str = "all",
    severity: str = "",
    status: str = "",
    top_only: bool = False,
    limit: int = 24,
) -> List[Dict[str, Any]]:
    card_id = _norm(card_id)
    lane = _norm(lane) or "all"
    severity = _norm(severity)
    status = _norm(status)

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 24
    limit_int = max(1, min(limit_int, 100))

    filtered = [card for card in cards if isinstance(card, dict)]

    if lane == "attention":
        filtered = [card for card in filtered if _is_attention_card(card)]
    elif lane in FOCUS_LANE_MAP and lane != "all":
        allowed = set(FOCUS_LANE_MAP.get(lane, {}).get("card_ids", []))
        filtered = [card for card in filtered if str(card.get("card_id", "")) in allowed]

    if card_id:
        filtered = [card for card in filtered if _norm(card.get("card_id")) == card_id]

    if severity:
        filtered = [card for card in filtered if _norm(card.get("severity")) == severity]

    if status:
        filtered = [card for card in filtered if _norm(card.get("status")) == status]

    if top_only:
        filtered = filtered[:1]

    return filtered[:limit_int]


def build_owner_action_review_focus_lanes(
    *,
    card_id: str = "",
    lane: str = "all",
    severity: str = "",
    status: str = "",
    top_only: bool = False,
    limit: int = 24,
    write_panel: bool = True,
) -> Dict[str, Any]:
    dashboard = _load_cached_dashboard_cards()
    cards = dashboard.get("cards", []) if isinstance(dashboard.get("cards"), list) else []

    lane_norm = _norm(lane) or "all"
    if lane_norm not in FOCUS_LANE_MAP:
        lane_norm = "all"

    filtered_cards = _filter_cards(
        cards,
        card_id=card_id,
        lane=lane_norm,
        severity=severity,
        status=status,
        top_only=top_only,
        limit=limit,
    )

    by_card_id: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    lane_counts: Dict[str, int] = {}

    for card in cards:
        if not isinstance(card, dict):
            continue
        cid = str(card.get("card_id", "") or "unknown")
        sev = _norm(card.get("severity")) or "unknown"
        stat = _norm(card.get("status")) or "unknown"
        by_card_id[cid] = by_card_id.get(cid, 0) + 1
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_status[stat] = by_status.get(stat, 0) + 1

    for lane_key, lane_info in FOCUS_LANE_MAP.items():
        if lane_key == "attention":
            lane_counts[lane_key] = len([card for card in cards if isinstance(card, dict) and _is_attention_card(card)])
        elif lane_key == "all":
            lane_counts[lane_key] = len(cards)
        else:
            allowed = set(lane_info.get("card_ids", []))
            lane_counts[lane_key] = len([
                card for card in cards
                if isinstance(card, dict) and str(card.get("card_id", "")) in allowed
            ])

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 24
    limit_int = max(1, min(limit_int, 100))

    lane_info = FOCUS_LANE_MAP.get(lane_norm, FOCUS_LANE_MAP["all"])
    summary = dashboard.get("summary", {}) if isinstance(dashboard.get("summary"), dict) else {}

    checks = {
        "dashboard_loaded": bool(dashboard),
        "dashboard_passed": dashboard.get("status") == "passed",
        "dashboard_card_count_7": _num(dashboard.get("card_count"), len(cards)) == 7,
        "cards_available": len(cards) >= 7,
        "lane_valid": lane_norm in FOCUS_LANE_MAP,
        "filtered_cards_non_empty_for_non_attention": len(filtered_cards) >= 1 if lane_norm != "attention" else True,
        "route_coverage_100": _num(summary.get("route_coverage_pct"), 0) == 100,
        "helper_wrapped_zero": _num(summary.get("helper_wrapped_count"), 0) == 0,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    result = {
        "ok": not failed_checks,
        "pack": "149",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "lane": lane_norm,
        "lane_title": lane_info.get("title", "All Review Cards"),
        "lane_human_reason": lane_info.get("human_reason", "Owner Action review focus lane loaded."),
        "base_card_count": len(cards),
        "filtered_card_count": len(filtered_cards),
        "cards": filtered_cards,
        "active_filters": {
            "card_id": _norm(card_id),
            "lane": lane_norm,
            "severity": _norm(severity),
            "status": _norm(status),
            "top_only": bool(top_only),
            "limit": limit_int,
        },
        "filter_options": {
            "card_id": by_card_id,
            "severity": by_severity,
            "status": by_status,
            "lane": lane_counts,
        },
        "available_lanes": {
            key: {
                "title": value.get("title"),
                "count": lane_counts.get(key, 0),
                "human_reason": value.get("human_reason"),
            }
            for key, value in FOCUS_LANE_MAP.items()
        },
        "summary": {
            "dashboard_card_count": dashboard.get("card_count", len(cards)),
            "review_depth_score": summary.get("review_depth_score", 0),
            "route_coverage_pct": summary.get("route_coverage_pct", 0),
            "helper_wrapped_count": summary.get("helper_wrapped_count", 0),
            "attention_count": lane_counts.get("attention", 0),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 5)),
        "human_reason": "Owner Action review focus lanes are ready from cached dashboard cards.",
        "soulaana_translation": "Soulaana: Owner Action review cards can now be narrowed into focus lanes.",
    }

    scan = _safe_scan(result)
    result["no_secret_leakage"] = scan.get("ok") is True
    result["leakage_scan"] = scan
    result["status_fingerprint"] = _fingerprint(result)

    _write_json(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH, result)

    if write_panel:
        write_owner_action_review_focus_lanes_panel(result)

    return result


def render_owner_action_review_focus_lanes_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_review_focus_lanes(write_panel=False)
    cards = status.get("cards", []) if isinstance(status.get("cards"), list) else []
    lanes = status.get("available_lanes", {}) if isinstance(status.get("available_lanes"), dict) else {}

    lane_chips = []
    for key, lane in lanes.items():
        if not isinstance(lane, dict):
            continue
        lane_chips.append(f"""
        <a class="owner-action-focus-chip" href="/tower/owner-action-review-focus-lanes.json?lane={_html_escape(key)}">
          {_html_escape(lane.get('title', key))} · {_html_escape(lane.get('count', 0))}
        </a>
        """)

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
        <article class="owner-action-focus-card" style="border-color:{border};">
          <div class="owner-action-focus-card__eyebrow">{_html_escape(card.get('card_id', 'card'))} · {_html_escape(card.get('status', 'ready'))}</div>
          <h3>{_html_escape(card.get('value', ''))}</h3>
          <h4>{_html_escape(card.get('title', 'Focus Card'))}</h4>
          <p>{_html_escape(card.get('subtitle', ''))}</p>
          <a href="{_html_escape(card.get('href', '#'))}">Open source</a>
        </article>
        """)

    if not card_html:
        card_html.append("""
        <article class="owner-action-focus-card">
          <div class="owner-action-focus-card__eyebrow">empty</div>
          <h3>0</h3>
          <h4>No cards in this lane</h4>
          <p>This lane is currently calm.</p>
        </article>
        """)

    html = f"""
<!-- PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION -->
<section class="owner-action-focus-lanes" data-pack="149">
  <style>
    .owner-action-focus-lanes {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top left, rgba(143,221,158,.12), transparent 34%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.12), transparent 36%),
        linear-gradient(135deg, rgba(10,34,25,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-focus-lanes__eyebrow {{
      color: rgba(143,221,158,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-focus-lanes h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-focus-lanes p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-focus-chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 9px;
      margin-top: 14px;
    }}
    .owner-action-focus-chip {{
      display: inline-flex;
      border: 1px solid rgba(143,221,158,.28);
      border-radius: 999px;
      padding: 7px 10px;
      color: rgba(245,234,210,.88);
      text-decoration: none;
      background: rgba(255,255,255,.035);
      font-size: 12px;
    }}
    .owner-action-focus-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-focus-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      min-height: 150px;
    }}
    .owner-action-focus-card__eyebrow {{
      color: rgba(143,221,158,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 8px;
    }}
    .owner-action-focus-card h3 {{
      margin: 0 0 8px;
      font-size: 22px;
      line-height: 1;
    }}
    .owner-action-focus-card h4 {{
      margin: 0 0 8px;
      font-size: 14px;
      color: #f5ead2;
    }}
    .owner-action-focus-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .owner-action-focus-card a {{
      display: inline-flex;
      margin-top: 12px;
      color: rgba(143,221,158,.95);
      font-size: 12px;
      text-decoration: none;
    }}
    @media (max-width: 1100px) {{
      .owner-action-focus-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 760px) {{
      .owner-action-focus-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-focus-lanes__eyebrow">PACK 149 · OWNER ACTION REVIEW FOCUS LANES</div>
  <h2>{_html_escape(status.get('lane_title', 'Owner Action Review Focus Lanes'))}</h2>
  <p>{_html_escape(status.get('lane_human_reason', status.get('human_reason', 'Owner Action review focus lanes loaded.')))}</p>

  <div class="owner-action-focus-chip-row">
    {''.join(lane_chips)}
  </div>

  <div class="owner-action-focus-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION -->
"""
    return html


def write_owner_action_review_focus_lanes_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_review_focus_lanes(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Review Focus Lanes</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1280px;margin:auto;">
{render_owner_action_review_focus_lanes_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "149",
        "decision": "owner_action_review_focus_lanes_panel_written",
        "path": str(OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH),
        "human_reason": "Owner Action Review Focus Lanes panel written.",
        "soulaana_translation": "Soulaana: Owner Action review focus lanes posted.",
    }


def load_owner_action_review_focus_lanes_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH, {})
    if not data:
        data = build_owner_action_review_focus_lanes(write_panel=True)
    return data if isinstance(data, dict) else {}


def owner_action_review_focus_lanes_status_card() -> Dict[str, Any]:
    status = load_owner_action_review_focus_lanes_status()
    summary = status.get("summary", {}) if isinstance(status.get("summary"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "149",
        "title": "Owner Action Review Focus Lanes",
        "readiness_score": status.get("readiness_score", 0),
        "lane": status.get("lane"),
        "lane_title": status.get("lane_title"),
        "base_card_count": status.get("base_card_count", 0),
        "filtered_card_count": status.get("filtered_card_count", 0),
        "attention_count": summary.get("attention_count", 0),
        "review_depth_score": summary.get("review_depth_score", 0),
        "route_coverage_pct": summary.get("route_coverage_pct", 0),
        "helper_wrapped_count": summary.get("helper_wrapped_count", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH)),
        "human_reason": "Owner Action Review Focus Lanes status card loaded.",
        "soulaana_translation": "Soulaana: Owner Action review focus lanes are visible.",
    }


def reset_owner_action_review_focus_lanes_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH, {
        "ok": True,
        "pack": "149",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action Review Focus Lanes reset for test.",
    })
    if OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH.exists():
        try:
            OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_review_focus_lanes_reset_for_test",
        "soulaana_translation": "Soulaana: Owner Action review focus lanes reset for a clean test lane.",
    }



# ================================================================================
# PACK149B_FOCUS_LANES_STATUS_CARD_DEFAULT_LANE_CACHE_FIX
# ================================================================================
# Rescue:
# Status card must summarize the default all-lane view, not whichever filtered lane
# happened to be written last.
# ================================================================================

def _pack149b_cached_focus_status_is_default_all_lane(status: Dict[str, Any]) -> bool:
    if not isinstance(status, dict):
        return False

    filters = status.get("active_filters", {}) if isinstance(status.get("active_filters"), dict) else {}

    return (
        status.get("pack") == "149"
        and status.get("status") == "passed"
        and status.get("lane") == "all"
        and status.get("base_card_count") == 7
        and status.get("filtered_card_count") == 7
        and not filters.get("card_id")
        and not filters.get("severity")
        and not filters.get("status")
        and filters.get("top_only") is not True
    )


def load_owner_action_review_focus_lanes_status() -> Dict[str, Any]:
    data = _load_json(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH, {})
    if _pack149b_cached_focus_status_is_default_all_lane(data):
        return data

    return build_owner_action_review_focus_lanes(
        lane="all",
        card_id="",
        severity="",
        status="",
        top_only=False,
        limit=24,
        write_panel=True,
    )


def owner_action_review_focus_lanes_status_card() -> Dict[str, Any]:
    # Always use the canonical all-lane status for the compact card.
    status = build_owner_action_review_focus_lanes(
        lane="all",
        card_id="",
        severity="",
        status="",
        top_only=False,
        limit=24,
        write_panel=True,
    )

    summary = status.get("summary", {}) if isinstance(status.get("summary"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "149",
        "title": "Owner Action Review Focus Lanes",
        "readiness_score": status.get("readiness_score", 0),
        "lane": status.get("lane"),
        "lane_title": status.get("lane_title"),
        "base_card_count": status.get("base_card_count", 0),
        "filtered_card_count": status.get("filtered_card_count", 0),
        "attention_count": summary.get("attention_count", 0),
        "review_depth_score": summary.get("review_depth_score", 0),
        "route_coverage_pct": summary.get("route_coverage_pct", 0),
        "helper_wrapped_count": summary.get("helper_wrapped_count", 0),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH)),
        "human_reason": "Owner Action Review Focus Lanes status card loaded from canonical all-lane view.",
        "soulaana_translation": "Soulaana: Owner Action review focus lanes are visible from the full dashboard lane.",
    }

# ================================================================================
# END PACK149B_FOCUS_LANES_STATUS_CARD_DEFAULT_LANE_CACHE_FIX
# ================================================================================

