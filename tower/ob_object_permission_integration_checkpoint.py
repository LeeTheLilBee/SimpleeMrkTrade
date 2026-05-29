
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_APP_PATH = PROJECT_ROOT / "web" / "app.py"
DATA_DIR = PROJECT_ROOT / "tower" / "data"

CHECKPOINT_PATH = DATA_DIR / "ob_object_permission_integration_checkpoint.json"
PANEL_PATH = DATA_DIR / "ob_object_permission_integration_checkpoint.html"


PACK109_MARKER = "PACK109: Tower object-level permission check."
PACK109_HELPER_MARKER = "PACK109_OBJECT_PERMISSION_ROUTE_HELPERS"
PACK104_HELPER_MARKER = "PACK104_TOWER_OB_FLASK_GUARD_HELPERS"
PACK105_STATUS_MARKER = "PACK105_TOWER_OB_GUARD_STATUS_ROUTE"
PACK106_MARKER = "PACK106: Tower guard for high-risk Observatory route."
PACK107_MARKER = "PACK107: Tower guard for remaining protected Observatory route."


EXPECTED_OBJECT_ROUTE_FUNCTIONS = {
    "signal_symbol_page": "symbol",
    "my_position_detail_page": "position",
    "edit_my_position": "position",
    "close_my_position": "position",
    "my_positions_archived_page": "position",
    "analyze_my_trades_page": "analysis",
    "trade_detail_page": "trade",
    "reports_page": "export",
}


HELPER_FUNCTION_PREFIXES = (
    "_pack",
    "_tower",
    "_safe",
    "_load",
    "_write",
    "_normalize",
    "_extract",
    "_register",
    "_should",
    "_build",
    "_render",
)


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


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


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
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def _leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_functions_with_object_guards(text: str | None = None) -> List[Dict[str, Any]]:
    text = text if isinstance(text, str) else WEB_APP_PATH.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    functions: List[Dict[str, Any]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("def ") and stripped.endswith(":"):
            function_name = stripped.split("def ", 1)[1].split("(", 1)[0].strip()
            def_indent = _leading_spaces(line)

            body_lines = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()

                if next_stripped and _leading_spaces(next_line) <= def_indent:
                    if (
                        next_stripped.startswith("@app.route(")
                        or next_stripped.startswith("def ")
                        or next_stripped.startswith("class ")
                    ):
                        break

                body_lines.append(next_line)
                j += 1

            body = "\n".join(body_lines)
            has_object_guard = PACK109_MARKER in body or "_tower_object_permission_response_109" in body

            if has_object_guard:
                object_type = ""
                action = ""
                object_type_match = re.search(r"object_type\s*=\s*['\"]([^'\"]+)['\"]", body)
                action_match = re.search(r"action\s*=\s*['\"]([^'\"]+)['\"]", body)
                if object_type_match:
                    object_type = object_type_match.group(1)
                if action_match:
                    action = action_match.group(1)

                functions.append({
                    "function_name": function_name,
                    "object_type": object_type,
                    "action": action,
                    "is_expected_route_target": function_name in EXPECTED_OBJECT_ROUTE_FUNCTIONS,
                    "expected_object_type": EXPECTED_OBJECT_ROUTE_FUNCTIONS.get(function_name, ""),
                    "looks_like_helper_or_internal": function_name.startswith(HELPER_FUNCTION_PREFIXES),
                    "guard_marker_present": PACK109_MARKER in body,
                    "guard_helper_call_present": "_tower_object_permission_response_109" in body,
                })

            i = j
            continue

        i += 1

    return functions


def build_object_permission_integration_checkpoint(write_panel: bool = True) -> Dict[str, Any]:
    text = WEB_APP_PATH.read_text(encoding="utf-8", errors="replace")

    object_guarded_functions = parse_functions_with_object_guards(text)

    expected_present = {
        fn: any(item.get("function_name") == fn for item in object_guarded_functions)
        for fn in EXPECTED_OBJECT_ROUTE_FUNCTIONS
    }

    expected_missing = [
        fn for fn, present in expected_present.items()
        if not present
    ]

    expected_wrong_type = []
    for item in object_guarded_functions:
        fn = item.get("function_name")
        expected_type = EXPECTED_OBJECT_ROUTE_FUNCTIONS.get(fn)
        if expected_type and item.get("object_type") and item.get("object_type") != expected_type:
            expected_wrong_type.append({
                "function_name": fn,
                "expected_object_type": expected_type,
                "actual_object_type": item.get("object_type"),
            })

    helper_wrapped = [
        item for item in object_guarded_functions
        if item.get("looks_like_helper_or_internal") and not item.get("is_expected_route_target")
    ]

    marker_checks = {
        "pack104_helper_present": PACK104_HELPER_MARKER in text,
        "pack105_status_present": PACK105_STATUS_MARKER in text,
        "pack106_high_risk_marker_present": PACK106_MARKER in text,
        "pack107_remaining_marker_present": PACK107_MARKER in text,
        "pack109_helper_present": PACK109_HELPER_MARKER in text,
        "pack109_object_marker_present": PACK109_MARKER in text,
    }

    route_coverage = {}
    object_status = {}

    try:
        from tower.ob_route_coverage_report import build_ob_route_coverage_report
        route_coverage = build_ob_route_coverage_report(write_panel=True)
    except Exception as exc:
        route_coverage = {
            "ok": False,
            "error_type": type(exc).__name__,
            "human_reason": "Route coverage report failed during Pack 110 checkpoint.",
        }

    try:
        from tower.ob_object_permission_tightening import summarize_ob_object_permissions
        object_status = summarize_ob_object_permissions(limit=80)
    except Exception as exc:
        object_status = {
            "ok": False,
            "error_type": type(exc).__name__,
            "human_reason": "Object permission status failed during Pack 110 checkpoint.",
        }

    checks = {
        "web_app_exists": WEB_APP_PATH.exists(),
        "all_markers_present": all(marker_checks.values()),
        "expected_object_route_targets_present": len(expected_missing) == 0,
        "expected_object_types_match": len(expected_wrong_type) == 0,
        "route_coverage_ok": route_coverage.get("ok") is True,
        "route_coverage_100": route_coverage.get("coverage_pct") == 100,
        "unguarded_needed_zero": route_coverage.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route_coverage.get("unguarded_high_risk_count") == 0,
        "object_permission_status_ok": object_status.get("ok") is True,
        "object_permission_readiness_100": object_status.get("readiness_score") == 100,
        "object_permission_no_secret_leakage": object_status.get("no_secret_leakage") is True,
    }

    warnings = []
    if helper_wrapped:
        warnings.append({
            "warning_code": "helper_or_internal_functions_have_object_guards",
            "human_reason": "Some helper/internal functions contain object permission guards. They compiled and tests passed, but Pack 111 should review whether these are intentional or should be moved to route-level wrappers only.",
            "count": len(helper_wrapped),
        })

    if expected_missing:
        warnings.append({
            "warning_code": "expected_object_route_target_missing",
            "missing": expected_missing,
        })

    if expected_wrong_type:
        warnings.append({
            "warning_code": "expected_object_type_mismatch",
            "mismatches": expected_wrong_type,
        })

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = "passed" if not failed_checks else "failed"

    # Helper-wrapped functions are warnings, not failures, because Pack 109 compiled
    # and passed. This checkpoint makes them visible for cleanup.
    readiness_score = 100 if status == "passed" else max(0, 100 - (len(failed_checks) * 10))

    checkpoint = {
        "ok": status == "passed",
        "pack": "110",
        "status": status,
        "created_at": _utc_now(),
        "web_app_path": str(WEB_APP_PATH),
        "checkpoint_path": str(CHECKPOINT_PATH),
        "panel_path": str(PANEL_PATH),
        "marker_checks": marker_checks,
        "checks": checks,
        "failed_checks": failed_checks,
        "warnings": warnings,
        "object_guard_count": len(object_guarded_functions),
        "expected_object_route_count": len(EXPECTED_OBJECT_ROUTE_FUNCTIONS),
        "expected_present": expected_present,
        "expected_missing": expected_missing,
        "expected_wrong_type": expected_wrong_type,
        "helper_wrapped_count": len(helper_wrapped),
        "helper_wrapped_functions": helper_wrapped,
        "object_guarded_functions": object_guarded_functions,
        "route_coverage_summary": {
            "coverage_pct": route_coverage.get("coverage_pct"),
            "guarded_needed_count": route_coverage.get("guarded_needed_count"),
            "needs_guard_count": route_coverage.get("needs_guard_count"),
            "unguarded_needed_count": route_coverage.get("unguarded_needed_count"),
            "unguarded_high_risk_count": route_coverage.get("unguarded_high_risk_count"),
            "readiness_score": route_coverage.get("readiness_score"),
        },
        "object_permission_summary": {
            "event_count": object_status.get("event_count"),
            "by_decision": object_status.get("by_decision"),
            "by_object_type": object_status.get("by_object_type"),
            "readiness_score": object_status.get("readiness_score"),
            "no_secret_leakage": object_status.get("no_secret_leakage"),
        },
        "readiness_score": readiness_score,
        "readiness_label": (
            "OB route and object permission integration checkpoint passed"
            if status == "passed"
            else "OB route and object permission integration checkpoint needs review"
        ),
        "human_reason": "Pack 110 checkpoint verifies route coverage, object guard wiring, object permission readiness, and visibility.",
        "soulaana_translation": "Soulaana: The hallway doors and object keys have a checkpoint board now.",
    }

    scan = _safe_scan(checkpoint)
    checkpoint["no_secret_leakage"] = scan.get("ok") is True
    checkpoint["leakage_scan"] = scan
    checkpoint["checkpoint_fingerprint"] = _fingerprint(checkpoint)

    _write_json(CHECKPOINT_PATH, checkpoint)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_ob_object_permission_integration_checkpoint",
            source_name="ob_object_permission_integration_checkpoint",
            source_path=str(CHECKPOINT_PATH),
            source_hash=_fingerprint(checkpoint),
            record_count=len(object_guarded_functions),
            actor_user_id="tower_system",
            reason="Pack 110 OB route/object permission integration checkpoint.",
            metadata={
                "pack": "110",
                "status": status,
                "object_guard_count": len(object_guarded_functions),
                "route_coverage_pct": route_coverage.get("coverage_pct"),
                "helper_wrapped_count": len(helper_wrapped),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_object_permission_integration_panel(checkpoint)

    return checkpoint


def write_object_permission_integration_panel(checkpoint: Dict[str, Any] | None = None) -> Dict[str, Any]:
    checkpoint = checkpoint if isinstance(checkpoint, dict) else _load_json(CHECKPOINT_PATH, {})
    guards = checkpoint.get("object_guarded_functions", []) if isinstance(checkpoint.get("object_guarded_functions"), list) else []
    helper_wrapped = checkpoint.get("helper_wrapped_functions", []) if isinstance(checkpoint.get("helper_wrapped_functions"), list) else []
    warnings = checkpoint.get("warnings", []) if isinstance(checkpoint.get("warnings"), list) else []

    cards = []
    for item in guards[:24]:
        label = "EXPECTED" if item.get("is_expected_route_target") else "EXTRA"
        if item.get("looks_like_helper_or_internal"):
            label = "HELPER REVIEW"
        cards.append(f"""
        <article class="card {'good' if item.get('is_expected_route_target') else 'review'}">
          <div class="eyebrow">{label} · {item.get('object_type', 'object')} · {item.get('action', 'action')}</div>
          <h2>{item.get('function_name', '')}</h2>
          <p>Expected: {item.get('expected_object_type', 'n/a')}</p>
        </article>
        """)

    warning_cards = []
    for warning in warnings[:8]:
        warning_cards.append(f"""
        <article class="card warning">
          <div class="eyebrow">WARNING · {warning.get('warning_code', '')}</div>
          <h2>{warning.get('count', '')}</h2>
          <p>{warning.get('human_reason', '')}</p>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · OB Object Integration Checkpoint</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .hero {{
      border: 1px solid rgba(220,183,94,.36);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(135deg, rgba(75,48,18,.74), rgba(12,13,10,.96));
      box-shadow: 0 22px 90px rgba(0,0,0,.42);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      letter-spacing: -.04em;
    }}
    .hero p {{
      margin: 0;
      color: rgba(245,234,210,.76);
      line-height: 1.55;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 20px 0;
    }}
    .stat {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 20px;
      padding: 16px;
      background: rgba(255,255,255,.045);
    }}
    .stat b {{
      display: block;
      font-size: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .card {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,.045);
    }}
    .card.good {{
      border-color: rgba(143,221,158,.34);
    }}
    .card.review, .card.warning {{
      border-color: rgba(220,183,94,.45);
    }}
    .eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .card p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · OB Object Integration Checkpoint</h1>
    <p>{checkpoint.get('human_reason', 'Integration checkpoint loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{checkpoint.get('readiness_score', 0)}</b><span>Readiness</span></div>
    <div class="stat"><b>{checkpoint.get('object_guard_count', 0)}</b><span>Object Guards</span></div>
    <div class="stat"><b>{checkpoint.get('route_coverage_summary', {}).get('coverage_pct', 0) if isinstance(checkpoint.get('route_coverage_summary'), dict) else 0}%</b><span>Route Coverage</span></div>
    <div class="stat"><b>{checkpoint.get('helper_wrapped_count', 0)}</b><span>Helper Reviews</span></div>
  </section>
  <section class="grid">{''.join(warning_cards + cards)}</section>
</main>
</body>
</html>
"""
    PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "ob_object_permission_integration_panel_written",
        "path": str(PANEL_PATH),
        "human_reason": "OB object permission integration checkpoint panel written.",
        "soulaana_translation": "Soulaana: Integration checkpoint board posted.",
    }


def load_object_permission_integration_checkpoint() -> Dict[str, Any]:
    checkpoint = _load_json(CHECKPOINT_PATH, {})
    if not checkpoint:
        checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
    return checkpoint


def reset_object_permission_integration_checkpoint_for_test() -> Dict[str, Any]:
    _write_json(CHECKPOINT_PATH, {
        "ok": True,
        "pack": "110",
        "reset_at": _utc_now(),
        "human_reason": "Pack 110 checkpoint reset for test.",
    })
    if PANEL_PATH.exists():
        try:
            PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "object_permission_integration_checkpoint_reset",
        "soulaana_translation": "Soulaana: Integration checkpoint reset for a clean test lane.",
    }
