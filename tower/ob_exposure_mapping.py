
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
EXPOSURE_MAPPING_PATH = DATA_DIR / "ob_exposure_mapping_pass.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


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


def _route_bucket(path: str, classification: str = "") -> Dict[str, Any]:
    path = _normalize_path(path)
    lower = path.lower()
    classification = _safe_str(classification, "unknown")

    # Tower-owned routes stay Tower-owned.
    if lower.startswith("/tower"):
        return {
            "category": "keep_protected",
            "priority": 1,
            "reason_code": "tower_owned_security_surface",
            "plain": "Tower security/admin surfaces stay protected and should not become public.",
        }

    # Static and health-ish surfaces can stay safe if harmless.
    if lower.startswith("/static") or lower in {"/favicon.ico", "/health", "/ping"}:
        return {
            "category": "keep_public_safe",
            "priority": 5,
            "reason_code": "static_or_health_safe_surface",
            "plain": "Static/health surfaces can remain harmless shell surfaces if they expose no protected data.",
        }

    # Login and entry shell routes are allowed as outer shell only.
    if lower in {"/", "/login", "/logout", "/signup", "/register", "/no-access", "/observatory-private", "/tower/polished-locked-preview"}:
        return {
            "category": "keep_public_safe",
            "priority": 2,
            "reason_code": "outer_shell_or_locked_surface",
            "plain": "Outer-shell and locked-preview routes may stay reachable because they expose no Observatory data.",
        }

    # Known core OB surfaces should stay protected.
    core_protected_exact = {
        "/dashboard",
        "/signals",
        "/my-positions",
        "/positions",
        "/analytics",
        "/analytics-overview",
        "/research",
        "/research-overview",
        "/analysis-vault",
        "/premium",
        "/premium-analysis",
        "/trade-review",
        "/why-this-trade",
        "/all-symbols",
    }
    if lower in core_protected_exact:
        return {
            "category": "keep_protected",
            "priority": 1,
            "reason_code": "core_ob_private_surface",
            "plain": "Core Observatory surfaces stay protected behind Tower clearance.",
        }

    # Dynamic symbol/signal/position detail routes are mapping candidates.
    dynamic_patterns = [
        r"^/signals/[^/]+$",
        r"^/symbol/[^/]+$",
        r"^/symbols/[^/]+$",
        r"^/positions/[^/]+$",
        r"^/my-positions/[^/]+$",
        r"^/trade/[^/]+$",
        r"^/trades/[^/]+$",
    ]
    if any(re.match(pattern, lower) for pattern in dynamic_patterns):
        return {
            "category": "map_next",
            "priority": 2,
            "reason_code": "dynamic_ob_object_surface",
            "plain": "Dynamic OB object routes should be explicitly mapped to object-level clearance policies.",
        }

    # Export/download routes need critical handling.
    if "export" in lower or "download" in lower:
        return {
            "category": "map_next",
            "priority": 1,
            "reason_code": "export_or_download_surface",
            "plain": "Export/download routes need explicit critical clearance and audit behavior.",
        }

    # Admin-ish routes need stronger mapping.
    if "admin" in lower or "debug" in lower or "dev" in lower or "test" in lower:
        return {
            "category": "retire_or_redirect",
            "priority": 1,
            "reason_code": "admin_debug_or_test_surface",
            "plain": "Admin/debug/test routes should be retired, redirected, or moved behind explicit Tower admin clearance.",
        }

    # API routes need explicit API clearance policy.
    if lower.startswith("/api"):
        return {
            "category": "map_next",
            "priority": 2,
            "reason_code": "api_surface_needs_policy",
            "plain": "API routes need explicit route/action/object clearance policy.",
        }

    # Unknown unmapped defaults should stay denied until reviewed.
    if "unmapped" in classification or classification in {"unknown", "unmapped_default_deny"}:
        return {
            "category": "later_review",
            "priority": 4,
            "reason_code": "unmapped_default_deny_review_needed",
            "plain": "Unmapped routes stay default-denied until owner maps, retires, or redirects them.",
        }

    return {
        "category": "later_review",
        "priority": 5,
        "reason_code": "needs_owner_review",
        "plain": "This surface needs owner review before mapping or retirement.",
    }


def _extract_exposure_items() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    # Preferred: use exposure report if available.
    try:
        from tower.ob_route_exposure_report import build_ob_route_exposure_report

        report = build_ob_route_exposure_report()
        raw_items = []

        if isinstance(report, dict):
            for key in ["routes", "items", "exposures", "surfaces", "attention_items"]:
                if isinstance(report.get(key), list):
                    raw_items.extend(report.get(key, []))

            # Some versions summarize counts only. Keep that report metadata too.
            if not raw_items and isinstance(report.get("attention"), list):
                raw_items.extend(report.get("attention", []))

        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            path = (
                raw.get("path")
                or raw.get("rule")
                or raw.get("route")
                or raw.get("surface")
                or raw.get("endpoint")
                or raw.get("url_rule")
            )
            if not path:
                continue
            items.append({
                "path": _normalize_path(path),
                "source": "ob_route_exposure_report",
                "classification": _safe_str(
                    raw.get("classification")
                    or raw.get("category")
                    or raw.get("match_type")
                    or raw.get("status")
                    or raw.get("sensitivity"),
                    "unknown",
                ),
                "raw": raw,
            })
    except Exception:
        pass

    # Fallback: inspect Flask routes directly.
    if not items:
        try:
            from web.app import app

            for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r.rule)):
                path = _normalize_path(str(rule.rule))
                methods = sorted([m for m in rule.methods if m not in {"HEAD", "OPTIONS"}])
                items.append({
                    "path": path,
                    "source": "flask_url_map",
                    "classification": "unknown",
                    "raw": {
                        "endpoint": rule.endpoint,
                        "methods": methods,
                    },
                })
        except Exception:
            pass

    # Deduplicate by path but keep first source.
    deduped: Dict[str, Dict[str, Any]] = {}
    for item in items:
        path = _normalize_path(item.get("path"))
        if path not in deduped:
            item["path"] = path
            deduped[path] = item

    return list(deduped.values())


def build_ob_exposure_mapping_pass() -> Dict[str, Any]:
    items = _extract_exposure_items()
    mapped_items: List[Dict[str, Any]] = []

    counts: Dict[str, int] = {}
    reason_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}

    for item in items:
        path = _normalize_path(item.get("path"))
        classification = _safe_str(item.get("classification"), "unknown")
        bucket = _route_bucket(path, classification)

        mapped = {
            "path": path,
            "source": item.get("source", "unknown"),
            "classification": classification,
            "category": bucket.get("category"),
            "priority": bucket.get("priority"),
            "reason_code": bucket.get("reason_code"),
            "plain": bucket.get("plain"),
            "raw": item.get("raw", {}),
        }
        mapped_items.append(mapped)

        category = mapped["category"]
        reason = mapped["reason_code"]
        priority = str(mapped["priority"])

        counts[category] = counts.get(category, 0) + 1
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    mapped_items.sort(key=lambda item: (item.get("priority", 9), item.get("category", ""), item.get("path", "")))

    top_next = [item for item in mapped_items if item.get("category") == "map_next"][:20]
    retire_or_redirect = [item for item in mapped_items if item.get("category") == "retire_or_redirect"][:20]
    later_review = [item for item in mapped_items if item.get("category") == "later_review"][:30]

    ok = bool(items)

    payload = {
        "ok": ok,
        "pack": "084",
        "generated_at": _utc_now(),
        "path": str(EXPOSURE_MAPPING_PATH),
        "total": len(mapped_items),
        "counts": counts,
        "reason_counts": reason_counts,
        "priority_counts": priority_counts,
        "top_next": top_next,
        "retire_or_redirect": retire_or_redirect,
        "later_review": later_review,
        "items": mapped_items,
        "readiness_label": "Exposure mapping pass ready" if ok else "Exposure mapping pass has no items",
        "readiness_score": 100 if ok else 80,
        "soulaana_translation": "Soulaana: The doors are sorted. Some stay locked, some get mapped next, some get retired, and the questionable ones wait for owner review.",
        "human_reason": "OB exposure report mapping pass created.",
    }

    _write_json(EXPOSURE_MAPPING_PATH, payload)
    return payload


def load_ob_exposure_mapping_pass() -> Dict[str, Any]:
    return _load_json(EXPOSURE_MAPPING_PATH, {
        "ok": False,
        "total": 0,
        "items": [],
        "human_reason": "No exposure mapping pass saved yet.",
    })


def summarize_ob_exposure_mapping_pass(limit: int = 20) -> Dict[str, Any]:
    payload = load_ob_exposure_mapping_pass()
    items = payload.get("items", []) if isinstance(payload.get("items"), list) else []

    try:
        limit = int(limit)
    except Exception:
        limit = 20
    limit = max(1, min(limit, 200))

    return {
        "ok": payload.get("ok") is True,
        "path": payload.get("path", str(EXPOSURE_MAPPING_PATH)),
        "total": payload.get("total", len(items)),
        "counts": payload.get("counts", {}),
        "reason_counts": payload.get("reason_counts", {}),
        "priority_counts": payload.get("priority_counts", {}),
        "top_next": payload.get("top_next", [])[:limit],
        "retire_or_redirect": payload.get("retire_or_redirect", [])[:limit],
        "later_review": payload.get("later_review", [])[:limit],
        "recent": items[:limit],
        "readiness_label": payload.get("readiness_label"),
        "readiness_score": payload.get("readiness_score"),
        "human_reason": payload.get("human_reason"),
        "soulaana_translation": payload.get("soulaana_translation"),
    }
