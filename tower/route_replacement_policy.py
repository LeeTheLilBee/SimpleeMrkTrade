
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
ROUTE_REPLACEMENT_POLICY_PATH = DATA_DIR / "route_replacement_policy_list.json"


VALID_POLICY_DECISIONS = {
    "approved_to_replace",
    "keep_old_for_now",
    "needs_owner_review",
    "retire_or_redirect",
    "never_public",
    "Tower_only",
    "OB_protected",
    "Archive_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


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


def _normalize_path(path: Any) -> str:
    text = _safe_str(path, "/")
    if not text.startswith("/"):
        text = "/" + text
    return text.split("?")[0].strip() or "/"


def _path_matches(path: str, pattern: str) -> bool:
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)

    if path == pattern:
        return True

    # Convert Flask-ish dynamic segments into simple regex.
    escaped = re.escape(pattern)
    escaped = re.sub(r"\\<[^>]+\\>", r"[^/]+", escaped)
    regex = "^" + escaped + "$"
    try:
        return re.match(regex, path) is not None
    except Exception:
        return False


def _base_policy_for_route(item: Dict[str, Any]) -> Dict[str, Any]:
    path = _normalize_path(item.get("path"))
    category = _safe_str(item.get("category"), "later_review")
    reason_code = _safe_str(item.get("reason_code"), "needs_owner_review")
    classification = _safe_str(item.get("classification"), "unknown")
    priority = _safe_int(item.get("priority"), 5)
    lower = path.lower()

    # Tower surfaces are Tower-only. No OB replacement games.
    if lower.startswith("/tower"):
        return {
            "policy_decision": "Tower_only",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "critical",
            "step_up_required_later": True,
            "archive_handoff_required": True,
            "policy_reason": "Tower-owned routes are security command surfaces and must remain under Tower control.",
        }

    # Archive surfaces stay Archive-only.
    if lower.startswith("/archive") or "archive" in lower:
        return {
            "policy_decision": "Archive_only",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "restricted",
            "step_up_required_later": True,
            "archive_handoff_required": True,
            "policy_reason": "Archive/evidence routes must stay evidence-controlled and cannot become public.",
        }

    # Public-safe locked shell routes are allowed to be replaced with polished locked pages.
    if lower in {"/no-access", "/observatory-private", "/tower/polished-locked-preview"}:
        return {
            "policy_decision": "approved_to_replace",
            "owner_review_required": False,
            "replacement_allowed": True,
            "route_may_be_public": False,
            "required_clearance_level": "public_shell",
            "step_up_required_later": False,
            "archive_handoff_required": False,
            "policy_reason": "This route is only a locked/shell surface and may use polished Tower locked response.",
        }

    # Login/signup shell routes can remain public-safe but should not expose protected data.
    if lower in {"/", "/login", "/logout", "/signup", "/register"}:
        return {
            "policy_decision": "keep_old_for_now",
            "owner_review_required": False,
            "replacement_allowed": False,
            "route_may_be_public": True,
            "required_clearance_level": "public_shell",
            "step_up_required_later": False,
            "archive_handoff_required": False,
            "policy_reason": "Outer entry shell can remain reachable if it exposes no protected data.",
        }

    # Static/health surfaces can stay public-safe only if harmless.
    if lower.startswith("/static") or lower in {"/favicon.ico", "/health", "/ping"}:
        return {
            "policy_decision": "keep_old_for_now",
            "owner_review_required": False,
            "replacement_allowed": False,
            "route_may_be_public": True,
            "required_clearance_level": "public_shell",
            "step_up_required_later": False,
            "archive_handoff_required": False,
            "policy_reason": "Harmless static/health surfaces may remain public-safe.",
        }

    # Admin/debug/test surfaces are not casual replacements. Retire/redirect or move behind Tower admin.
    if category == "retire_or_redirect" or "admin_debug_or_test" in reason_code or any(
        token in lower for token in ["/admin", "debug", "diagnostic", "preview-tier", "refresh"]
    ):
        return {
            "policy_decision": "retire_or_redirect",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "critical",
            "step_up_required_later": True,
            "archive_handoff_required": True,
            "policy_reason": "Admin/debug/test surfaces should be retired, redirected, or moved behind explicit Tower admin clearance.",
        }

    # API/export/download surfaces require owner review and later route/action policy.
    if lower.startswith("/api") or "export" in lower or "download" in lower:
        return {
            "policy_decision": "needs_owner_review",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "critical",
            "step_up_required_later": True,
            "archive_handoff_required": True,
            "policy_reason": "API/export/download surfaces need explicit action policy before replacement or exposure changes.",
        }

    # Known OB private surfaces are OB-protected.
    if category == "keep_protected" or reason_code == "core_ob_private_surface":
        return {
            "policy_decision": "OB_protected",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "confidential",
            "step_up_required_later": False,
            "archive_handoff_required": False,
            "policy_reason": "Core Observatory surfaces stay protected behind Tower/OB clearance.",
        }

    # Dynamic objects should be mapped before any replacement.
    if category == "map_next" or reason_code == "dynamic_ob_object_surface":
        return {
            "policy_decision": "needs_owner_review",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "restricted",
            "step_up_required_later": False,
            "archive_handoff_required": False,
            "policy_reason": "Dynamic object routes need explicit object-level clearance mapping before route replacement.",
        }

    # Most unmapped private routes should stay denied until reviewed.
    if category == "later_review" or "unmapped" in classification or reason_code == "unmapped_default_deny_review_needed":
        return {
            "policy_decision": "needs_owner_review",
            "owner_review_required": True,
            "replacement_allowed": False,
            "route_may_be_public": False,
            "required_clearance_level": "internal",
            "step_up_required_later": False,
            "archive_handoff_required": False,
            "policy_reason": "Unmapped route stays default-denied until owner maps, retires, or explicitly approves replacement.",
        }

    # Final conservative fallback.
    return {
        "policy_decision": "never_public",
        "owner_review_required": True,
        "replacement_allowed": False,
        "route_may_be_public": False,
        "required_clearance_level": "restricted",
        "step_up_required_later": True,
        "archive_handoff_required": True,
        "policy_reason": "Fallback conservative policy: do not expose or replace until reviewed.",
    }


def build_route_replacement_policy_list() -> Dict[str, Any]:
    from tower.ob_exposure_mapping import build_ob_exposure_mapping_pass

    mapping = build_ob_exposure_mapping_pass()
    items = mapping.get("items", []) if isinstance(mapping.get("items"), list) else []

    policy_items: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {}
    clearance_counts: Dict[str, int] = {}

    replacement_allowed_count = 0
    owner_review_count = 0
    public_allowed_count = 0
    archive_handoff_count = 0
    step_up_count = 0

    for item in items:
        route_path = _normalize_path(item.get("path"))
        policy = _base_policy_for_route(item)
        decision = _safe_str(policy.get("policy_decision"), "needs_owner_review")

        if decision not in VALID_POLICY_DECISIONS:
            decision = "needs_owner_review"
            policy["policy_decision"] = decision
            policy["policy_reason"] = "Invalid generated decision corrected to needs_owner_review."

        policy_item = {
            "route_path": route_path,
            "policy_decision": decision,
            "replacement_allowed": bool(policy.get("replacement_allowed")),
            "route_may_be_public": bool(policy.get("route_may_be_public")),
            "owner_review_required": bool(policy.get("owner_review_required")),
            "required_clearance_level": _safe_str(policy.get("required_clearance_level"), "internal"),
            "step_up_required_later": bool(policy.get("step_up_required_later")),
            "archive_handoff_required": bool(policy.get("archive_handoff_required")),
            "policy_reason": _safe_str(policy.get("policy_reason"), "Policy generated from exposure mapping."),
            "source_category": item.get("category"),
            "source_reason_code": item.get("reason_code"),
            "source_classification": item.get("classification"),
            "source_priority": item.get("priority"),
            "generated_at": _utc_now(),
            "policy_version": "pack089.v1",
            "status": "active",
            "owner_notes": [],
            "last_owner_review_at": "",
            "last_owner_review_by": "",
        }
        policy_items.append(policy_item)

        counts[decision] = counts.get(decision, 0) + 1
        clearance = policy_item["required_clearance_level"]
        clearance_counts[clearance] = clearance_counts.get(clearance, 0) + 1

        if policy_item["replacement_allowed"]:
            replacement_allowed_count += 1
        if policy_item["owner_review_required"]:
            owner_review_count += 1
        if policy_item["route_may_be_public"]:
            public_allowed_count += 1
        if policy_item["archive_handoff_required"]:
            archive_handoff_count += 1
        if policy_item["step_up_required_later"]:
            step_up_count += 1

    policy_items.sort(key=lambda item: (
        0 if item.get("policy_decision") in {"retire_or_redirect", "Tower_only", "Archive_only"} else 1,
        item.get("policy_decision", ""),
        item.get("route_path", ""),
    ))

    payload = {
        "ok": bool(policy_items),
        "pack": "089",
        "generated_at": _utc_now(),
        "path": str(ROUTE_REPLACEMENT_POLICY_PATH),
        "policy_version": "pack089.v1",
        "total": len(policy_items),
        "counts": counts,
        "clearance_counts": clearance_counts,
        "replacement_allowed_count": replacement_allowed_count,
        "owner_review_count": owner_review_count,
        "public_allowed_count": public_allowed_count,
        "archive_handoff_count": archive_handoff_count,
        "step_up_count": step_up_count,
        "valid_policy_decisions": sorted(VALID_POLICY_DECISIONS),
        "items": policy_items,
        "approved_to_replace": [item for item in policy_items if item.get("policy_decision") == "approved_to_replace"],
        "keep_old_for_now": [item for item in policy_items if item.get("policy_decision") == "keep_old_for_now"],
        "needs_owner_review": [item for item in policy_items if item.get("policy_decision") == "needs_owner_review"],
        "retire_or_redirect": [item for item in policy_items if item.get("policy_decision") == "retire_or_redirect"],
        "never_public": [item for item in policy_items if item.get("policy_decision") == "never_public"],
        "Tower_only": [item for item in policy_items if item.get("policy_decision") == "Tower_only"],
        "OB_protected": [item for item in policy_items if item.get("policy_decision") == "OB_protected"],
        "Archive_only": [item for item in policy_items if item.get("policy_decision") == "Archive_only"],
        "readiness_score": 100 if policy_items else 80,
        "readiness_label": "Route replacement policy list ready" if policy_items else "Route replacement policy list has no routes",
        "soulaana_translation": "Soulaana: The door policy sheet is live. No more replacing doors just because they exist on the map.",
        "human_reason": "Route replacement policy list generated from exposure mapping.",
    }

    _write_json(ROUTE_REPLACEMENT_POLICY_PATH, payload)
    return payload


def load_route_replacement_policy_list() -> Dict[str, Any]:
    return _load_json(ROUTE_REPLACEMENT_POLICY_PATH, {
        "ok": False,
        "total": 0,
        "items": [],
        "human_reason": "No route replacement policy list saved yet.",
    })


def summarize_route_replacement_policy_list(limit: int = 12) -> Dict[str, Any]:
    payload = load_route_replacement_policy_list()
    items = payload.get("items", []) if isinstance(payload.get("items"), list) else []

    try:
        limit = int(limit)
    except Exception:
        limit = 12
    limit = max(1, min(limit, 200))

    return {
        "ok": payload.get("ok") is True,
        "pack": payload.get("pack"),
        "path": payload.get("path", str(ROUTE_REPLACEMENT_POLICY_PATH)),
        "policy_version": payload.get("policy_version"),
        "total": payload.get("total", len(items)),
        "counts": payload.get("counts", {}),
        "clearance_counts": payload.get("clearance_counts", {}),
        "replacement_allowed_count": payload.get("replacement_allowed_count", 0),
        "owner_review_count": payload.get("owner_review_count", 0),
        "public_allowed_count": payload.get("public_allowed_count", 0),
        "archive_handoff_count": payload.get("archive_handoff_count", 0),
        "step_up_count": payload.get("step_up_count", 0),
        "approved_to_replace": payload.get("approved_to_replace", [])[:limit],
        "keep_old_for_now": payload.get("keep_old_for_now", [])[:limit],
        "needs_owner_review": payload.get("needs_owner_review", [])[:limit],
        "retire_or_redirect": payload.get("retire_or_redirect", [])[:limit],
        "never_public": payload.get("never_public", [])[:limit],
        "Tower_only": payload.get("Tower_only", [])[:limit],
        "OB_protected": payload.get("OB_protected", [])[:limit],
        "Archive_only": payload.get("Archive_only", [])[:limit],
        "recent": items[:limit],
        "readiness_score": payload.get("readiness_score"),
        "readiness_label": payload.get("readiness_label"),
        "human_reason": payload.get("human_reason"),
        "soulaana_translation": payload.get("soulaana_translation"),
    }


def get_policy_for_route(route_path: str) -> Dict[str, Any]:
    payload = load_route_replacement_policy_list()
    items = payload.get("items", []) if isinstance(payload.get("items"), list) else []
    route_path = _normalize_path(route_path)

    for item in items:
        if _path_matches(route_path, item.get("route_path", "")):
            result = dict(item)
            result["ok"] = True
            result["match_type"] = "policy_match"
            result["requested_route_path"] = route_path
            return result

    return {
        "ok": False,
        "match_type": "no_policy_match",
        "requested_route_path": route_path,
        "policy_decision": "needs_owner_review",
        "replacement_allowed": False,
        "route_may_be_public": False,
        "owner_review_required": True,
        "required_clearance_level": "internal",
        "policy_reason": "No route replacement policy exists for this path. Default owner review required.",
        "soulaana_translation": "Soulaana: This door has no policy card yet. I am not moving it without owner review.",
    }



# ================================================================================
# PACK089B_STRONG_DYNAMIC_ROUTE_MATCHER
# ================================================================================
# Overrides route matching so Flask-style dynamic rules match concrete paths:
# /signals/<symbol>       -> /signals/AAPL
# /trade/<trade_id>       -> /trade/abc123
# /static/<path:filename> -> /static/css/app.css
# ================================================================================

def _pack089b_flask_rule_to_regex(pattern: str) -> str:
    pattern = _normalize_path(pattern)

    parts = pattern.strip("/").split("/")
    regex_parts = []

    for part in parts:
        if not part:
            continue

        if part.startswith("<") and part.endswith(">"):
            inside = part[1:-1].strip()

            # Flask converter form: <path:filename>, <int:id>, <uuid:id>, etc.
            if ":" in inside:
                converter, _name = inside.split(":", 1)
                converter = converter.strip().lower()
            else:
                converter = "default"

            if converter == "path":
                regex_parts.append(r".+")
            elif converter in {"int", "float", "uuid", "string", "default"}:
                regex_parts.append(r"[^/]+")
            else:
                regex_parts.append(r"[^/]+")
        else:
            regex_parts.append(re.escape(part))

    if not regex_parts:
        return r"^/$"

    return r"^/" + r"/".join(regex_parts) + r"$"


def _path_matches(path: str, pattern: str) -> bool:
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)

    if path == pattern:
        return True

    # If the stored pattern is concrete, it cannot match a different concrete path.
    if "<" not in pattern or ">" not in pattern:
        return False

    try:
        regex = _pack089b_flask_rule_to_regex(pattern)
        return re.match(regex, path) is not None
    except Exception:
        return False

