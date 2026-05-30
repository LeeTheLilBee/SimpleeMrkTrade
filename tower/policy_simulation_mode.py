
"""
PACK 152 - Policy Simulation Mode foundation.

This module is intentionally simulated-only.

It does NOT enforce policy.
It does NOT mutate access.
It does NOT call unified UI builders.
It reads Pack 151 policy registry/status when available, then produces clear
hypothetical policy decisions for safety review.

Design goals:
- cached
- non-recursive
- fail-closed in simulation output
- clear Soulaana-readable explanations
- safe if Pack 151 function names shift slightly
"""

from __future__ import annotations

import copy
import datetime
import importlib
from functools import lru_cache
from typing import Any, Dict, List, Optional


PACK_ID = "PACK_152"
SIMULATION_ENDPOINT = "/tower/policy-simulation-mode.json"


# ------------------------------------------------------------------------------
# Local policy fallback
# ------------------------------------------------------------------------------

# This mirrors the Pack 151 default registry IDs so Pack 152 can still explain
# itself if the Pack 151 module changes shape or returns a smaller status payload.
DEFAULT_POLICY_FALLBACK: List[Dict[str, Any]] = [
    {
        "policy_id": "tower.default_deny",
        "title": "Default deny",
        "effect": "deny",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_default_deny",
        "owner_reason": "Unknown or unapproved actions are denied by default.",
    },
    {
        "policy_id": "tower.no_clearance_no_ob",
        "title": "No Tower clearance means no Observatory access",
        "effect": "deny",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_tower_clearance",
        "owner_reason": "The Observatory cannot open unless The Tower grants clearance.",
    },
    {
        "policy_id": "live.public_automated_locked",
        "title": "Public Automated Live locked",
        "effect": "deny",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_live_automated",
        "owner_reason": "Public users cannot access Automated Live trading.",
    },
    {
        "policy_id": "secrets.vault_boundary",
        "title": "Secrets Vault boundary",
        "effect": "deny",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_secret_boundary",
        "owner_reason": "Raw secrets must stay sealed inside the Secrets Vault boundary.",
    },
    {
        "policy_id": "export.sensitive_step_up",
        "title": "Sensitive export requires step-up",
        "effect": "step_up",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_export_step_up",
        "owner_reason": "Sensitive exports require extra owner confirmation before release.",
    },
    {
        "policy_id": "privacy.redact_by_default",
        "title": "Privacy redaction by default",
        "effect": "redact",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_redaction",
        "owner_reason": "Sensitive user/private data should be redacted unless reveal is approved.",
    },
    {
        "policy_id": "admin.owner_receipt_required",
        "title": "Owner/admin receipt required",
        "effect": "step_up",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_owner_receipt",
        "owner_reason": "Owner/admin actions require a receipt trail and reason.",
    },
    {
        "policy_id": "route.unknown_route_quarantine",
        "title": "Unknown route quarantine",
        "effect": "quarantine",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_unknown_route",
        "owner_reason": "Unknown protected routes should be quarantined instead of trusted.",
    },
    {
        "policy_id": "object.least_privilege",
        "title": "Object least privilege",
        "effect": "deny",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_object_access",
        "owner_reason": "Object access requires explicit object-level permission.",
    },
    {
        "policy_id": "dependency.fail_closed",
        "title": "Dependency failure fail-closed",
        "effect": "fail_closed",
        "enforcement_mode": "simulated",
        "receipt_type": "policy_simulation_dependency_fail_closed",
        "owner_reason": "If a required dependency fails, the safe answer is to stop closed.",
    },
]


# ------------------------------------------------------------------------------
# Scenario registry
# ------------------------------------------------------------------------------

DEFAULT_SCENARIOS: List[Dict[str, Any]] = [
    {
        "scenario_id": "no_tower_clearance_open_ob",
        "label": "No Tower clearance trying to open OB",
        "actor_type": "user",
        "tower_clearance": False,
        "target_app": "observatory",
        "requested_action": "open_app",
        "expected_policy_id": "tower.no_clearance_no_ob",
    },
    {
        "scenario_id": "public_user_live_automated",
        "label": "Public user requesting Live Automated",
        "actor_type": "public_user",
        "tower_clearance": True,
        "target_app": "observatory",
        "mode": "live",
        "automation_level": "automated",
        "requested_action": "trade_live_automated",
        "expected_policy_id": "live.public_automated_locked",
    },
    {
        "scenario_id": "sensitive_export_step_up",
        "label": "Sensitive export requiring step-up",
        "actor_type": "owner",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "export",
        "data_classification": "sensitive",
        "step_up_completed": False,
        "expected_policy_id": "export.sensitive_step_up",
    },
    {
        "scenario_id": "raw_secret_request_denied",
        "label": "Raw secret request denied",
        "actor_type": "admin",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "read_raw_secret",
        "resource_type": "secret",
        "expected_policy_id": "secrets.vault_boundary",
    },
    {
        "scenario_id": "unknown_route_quarantined",
        "label": "Unknown route quarantined",
        "actor_type": "user",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "open_route",
        "route_known": False,
        "route": "/tower/unknown-sensitive-room",
        "expected_policy_id": "route.unknown_route_quarantine",
    },
    {
        "scenario_id": "object_without_permission_denied",
        "label": "Object access without object permission denied",
        "actor_type": "user",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "read_object",
        "object_permission": False,
        "object_id": "sensitive_record_001",
        "expected_policy_id": "object.least_privilege",
    },
    {
        "scenario_id": "dependency_failure_fail_closed",
        "label": "Dependency failure fail-closed",
        "actor_type": "service",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "use_dependency",
        "dependency_ok": False,
        "dependency_name": "broker_status_bridge",
        "expected_policy_id": "dependency.fail_closed",
    },
    {
        "scenario_id": "privacy_redact_by_default",
        "label": "Private data view redacted by default",
        "actor_type": "user",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "view_private_data",
        "data_classification": "private",
        "reveal_approved": False,
        "expected_policy_id": "privacy.redact_by_default",
    },
    {
        "scenario_id": "normal_allowed_monitor_only",
        "label": "Normal allowed / monitor-only case when explicitly allowed",
        "actor_type": "owner",
        "tower_clearance": True,
        "target_app": "tower",
        "requested_action": "view_policy_dashboard",
        "explicit_allow": True,
        "expected_policy_id": "simulation.explicit_allow_monitor",
    },
]


# ------------------------------------------------------------------------------
# Pack 151 status / registry loading
# ------------------------------------------------------------------------------

def _safe_call(fn: Any) -> Optional[Any]:
    try:
        return fn()
    except TypeError:
        try:
            return fn(force_refresh=False)
        except Exception:
            return None
    except Exception:
        return None


def _extract_policies_from_payload(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]

    if not isinstance(payload, dict):
        return []

    direct_keys = [
        "policies",
        "policy_registry",
        "registry",
        "policy_rows",
        "enabled_policies",
    ]
    for key in direct_keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [p for p in value if isinstance(p, dict)]

    nested_keys = [
        "policy_as_code",
        "policy_as_code_engine",
        "policy_status",
        "registry_status",
        "summary",
        "details",
        "data",
    ]
    for key in nested_keys:
        value = payload.get(key)
        policies = _extract_policies_from_payload(value)
        if policies:
            return policies

    return []


def _normalize_policy(raw: Dict[str, Any]) -> Dict[str, Any]:
    policy_id = (
        raw.get("policy_id")
        or raw.get("id")
        or raw.get("name")
        or raw.get("key")
        or "unknown.policy"
    )

    effect = (
        raw.get("effect")
        or raw.get("default_effect")
        or raw.get("decision")
        or "deny"
    )

    enforcement_mode = (
        raw.get("enforcement_mode")
        or raw.get("mode")
        or "simulated"
    )

    return {
        "policy_id": str(policy_id),
        "title": str(raw.get("title") or raw.get("name") or policy_id),
        "effect": str(effect).lower(),
        "enforcement_mode": str(enforcement_mode).lower(),
        "receipt_type": str(raw.get("receipt_type") or f"policy_simulation_{str(policy_id).replace('.', '_')}"),
        "owner_reason": str(raw.get("owner_reason") or raw.get("description") or raw.get("reason") or "Policy matched during simulated review."),
        "enabled": bool(raw.get("enabled", True)),
        "source": str(raw.get("source") or "pack_151_registry"),
    }


@lru_cache(maxsize=1)
def load_pack_151_policy_status_cached() -> Dict[str, Any]:
    status_payload: Dict[str, Any] = {}
    policies: List[Dict[str, Any]] = []

    try:
        module = importlib.import_module("tower.policy_as_code_engine")
        candidate_names = [
            "build_policy_as_code_status",
            "get_policy_as_code_status",
            "build_policy_registry_status",
            "get_policy_registry_status",
            "build_policy_registry",
            "get_policy_registry",
            "get_default_policy_registry",
        ]

        for name in candidate_names:
            fn = getattr(module, name, None)
            if callable(fn):
                payload = _safe_call(fn)
                if isinstance(payload, dict) and not status_payload:
                    status_payload = payload
                extracted = _extract_policies_from_payload(payload)
                if extracted:
                    policies = extracted
                    break

    except Exception as exc:
        status_payload = {
            "pack_151_load_error": str(exc),
            "status": "fallback",
        }

    if not policies:
        policies = DEFAULT_POLICY_FALLBACK
        status_payload.setdefault("registry_source", "pack_152_local_fallback")
    else:
        status_payload.setdefault("registry_source", "pack_151")

    normalized = [_normalize_policy(p) for p in policies]

    policy_map = {p["policy_id"]: p for p in normalized}

    return {
        "pack_id": PACK_ID,
        "loaded_at": datetime.datetime.utcnow().isoformat() + "Z",
        "source_status": status_payload,
        "policy_count": len(normalized),
        "enabled_policy_count": sum(1 for p in normalized if p.get("enabled", True)),
        "policies": normalized,
        "policy_map": policy_map,
        "pack_151_status_available": bool(status_payload),
    }


def get_policy_by_id(policy_id: str) -> Dict[str, Any]:
    registry = load_pack_151_policy_status_cached()
    policy = registry.get("policy_map", {}).get(policy_id)
    if policy:
        return copy.deepcopy(policy)

    fallback = _normalize_policy({
        "policy_id": policy_id,
        "title": policy_id,
        "effect": "deny",
        "enforcement_mode": "simulated",
        "receipt_type": f"policy_simulation_{policy_id.replace('.', '_')}",
        "owner_reason": "Fallback policy generated for simulation review.",
        "source": "pack_152_generated_fallback",
    })
    return fallback


# ------------------------------------------------------------------------------
# Simulation rules
# ------------------------------------------------------------------------------

def _soulaana_translation(decision: str, matched_policy_id: str, owner_reason: str) -> str:
    decision_clean = str(decision or "unknown").lower()

    if decision_clean == "allow":
        return "This is only a practice run. The request looks allowed because it was explicitly cleared, but nothing real was opened or changed."

    if decision_clean == "step_up":
        return "This is only a practice run. The Tower would pause here and ask for an extra confirmation before letting this continue."

    if decision_clean == "redact":
        return "This is only a practice run. The Tower would hide sensitive details first, then only reveal them with the right approval."

    if decision_clean == "quarantine":
        return "This is only a practice run. The Tower would move this into a holding area instead of trusting it."

    if decision_clean == "fail_closed":
        return "This is only a practice run. Something important failed, so the safest answer is to stop closed instead of guessing."

    if decision_clean == "deny":
        return "This is only a practice run. The Tower would block this request because it does not have the right clearance."

    return f"This is only a practice run. Matched {matched_policy_id}: {owner_reason}"


def _result_from_policy(
    scenario: Dict[str, Any],
    policy_id: str,
    decision_override: Optional[str] = None,
) -> Dict[str, Any]:
    policy = get_policy_by_id(policy_id)
    effect = str(policy.get("effect") or "deny").lower()
    decision = str(decision_override or effect).lower()

    # Normalize effect -> decision where needed.
    if effect in {"deny", "step_up", "redact", "quarantine", "fail_closed", "allow"}:
        decision = decision_override or effect

    owner_reason = str(policy.get("owner_reason") or "Policy matched during simulated review.")

    return {
        "scenario_id": scenario.get("scenario_id", "custom_scenario"),
        "label": scenario.get("label", "Custom policy simulation"),
        "decision": decision,
        "matched_policy_id": policy.get("policy_id", policy_id),
        "effect": effect,
        "enforcement_mode": "simulation_only",
        "receipt_type": policy.get("receipt_type", "policy_simulation_receipt"),
        "owner_reason": owner_reason,
        "soulaana_translation": _soulaana_translation(decision, policy_id, owner_reason),
        "simulated_only": True,
        "real_enforcement_executed": False,
        "input_summary": {
            "actor_type": scenario.get("actor_type"),
            "target_app": scenario.get("target_app"),
            "requested_action": scenario.get("requested_action"),
            "mode": scenario.get("mode"),
            "automation_level": scenario.get("automation_level"),
            "route": scenario.get("route"),
            "resource_type": scenario.get("resource_type"),
            "data_classification": scenario.get("data_classification"),
            "dependency_name": scenario.get("dependency_name"),
        },
    }


def simulate_policy_decision(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a policy decision.

    The order is intentionally safety-first. It never performs real enforcement.
    """

    scenario = dict(scenario or {})

    # 1. No Tower clearance trying to open OB.
    if (
        scenario.get("target_app") in {"ob", "observatory", "the_observatory"}
        and scenario.get("requested_action") in {"open_app", "open_ob", "enter_app"}
        and scenario.get("tower_clearance") is False
    ):
        return _result_from_policy(scenario, "tower.no_clearance_no_ob")

    # 2. Public user requesting Live Automated.
    if (
        scenario.get("actor_type") in {"public", "public_user", "guest", "free_user"}
        and str(scenario.get("mode", "")).lower() == "live"
        and str(scenario.get("automation_level", "")).lower() == "automated"
    ):
        return _result_from_policy(scenario, "live.public_automated_locked")

    # 3. Sensitive export requiring step-up.
    if (
        scenario.get("requested_action") in {"export", "download", "release_export"}
        and scenario.get("data_classification") in {"sensitive", "restricted", "private", "secret"}
        and not scenario.get("step_up_completed", False)
    ):
        return _result_from_policy(scenario, "export.sensitive_step_up")

    # 4. Raw secret request denied.
    if (
        scenario.get("resource_type") in {"secret", "raw_secret", "broker_token", "api_key"}
        or scenario.get("requested_action") in {"read_raw_secret", "show_secret", "export_secret"}
    ):
        return _result_from_policy(scenario, "secrets.vault_boundary")

    # 5. Unknown route quarantined.
    if (
        scenario.get("requested_action") in {"open_route", "load_route", "access_route"}
        and scenario.get("route_known") is False
    ):
        return _result_from_policy(scenario, "route.unknown_route_quarantine")

    # 6. Object access without object permission denied.
    if (
        scenario.get("requested_action") in {"read_object", "write_object", "delete_object", "access_object"}
        and scenario.get("object_permission") is False
    ):
        return _result_from_policy(scenario, "object.least_privilege")

    # 7. Dependency failure fail-closed.
    if (
        scenario.get("requested_action") in {"use_dependency", "call_dependency", "dependency_check"}
        and scenario.get("dependency_ok") is False
    ):
        return _result_from_policy(scenario, "dependency.fail_closed")

    # 8. Privacy redaction case.
    if (
        scenario.get("requested_action") in {"view_private_data", "view_sensitive_data", "reveal_private_data"}
        and not scenario.get("reveal_approved", False)
    ):
        return _result_from_policy(scenario, "privacy.redact_by_default")

    # 9. Owner/admin action requiring receipt / step-up.
    if (
        scenario.get("actor_type") in {"owner", "admin"}
        and scenario.get("requested_action") in {"override", "admin_override", "policy_change", "route_replacement"}
        and not scenario.get("owner_receipt_present", False)
    ):
        return _result_from_policy(scenario, "admin.owner_receipt_required")

    # 10. Normal allowed / monitor-only case if explicitly allowed.
    if scenario.get("explicit_allow") is True:
        return {
            "scenario_id": scenario.get("scenario_id", "explicit_allow"),
            "label": scenario.get("label", "Explicitly allowed monitor-only simulation"),
            "decision": "allow",
            "matched_policy_id": "simulation.explicit_allow_monitor",
            "effect": "allow",
            "enforcement_mode": "simulation_only",
            "receipt_type": "policy_simulation_allow_monitor",
            "owner_reason": "The request was explicitly allowed for simulation review only.",
            "soulaana_translation": _soulaana_translation(
                "allow",
                "simulation.explicit_allow_monitor",
                "The request was explicitly allowed for simulation review only.",
            ),
            "simulated_only": True,
            "real_enforcement_executed": False,
            "input_summary": {
                "actor_type": scenario.get("actor_type"),
                "target_app": scenario.get("target_app"),
                "requested_action": scenario.get("requested_action"),
            },
        }

    # 11. Default deny fallback.
    return _result_from_policy(scenario, "tower.default_deny")


@lru_cache(maxsize=1)
def build_policy_simulation_mode_payload_cached() -> Dict[str, Any]:
    registry = load_pack_151_policy_status_cached()

    scenario_results = [
        simulate_policy_decision(scenario)
        for scenario in DEFAULT_SCENARIOS
    ]

    decision_counts: Dict[str, int] = {}
    for result in scenario_results:
        decision = str(result.get("decision") or "unknown")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    required_decisions = {"allow", "deny", "step_up", "redact", "quarantine", "fail_closed"}
    observed_decisions = set(decision_counts.keys())

    expected_policy_ids = {
        "tower.no_clearance_no_ob",
        "live.public_automated_locked",
        "export.sensitive_step_up",
        "secrets.vault_boundary",
        "route.unknown_route_quarantine",
        "object.least_privilege",
        "dependency.fail_closed",
        "simulation.explicit_allow_monitor",
    }

    matched_policy_ids = {
        str(row.get("matched_policy_id"))
        for row in scenario_results
        if row.get("matched_policy_id")
    }

    readiness_checks = {
        "simulated_only": all(row.get("simulated_only") is True for row in scenario_results),
        "no_real_enforcement": all(row.get("real_enforcement_executed") is False for row in scenario_results),
        "has_allow": "allow" in observed_decisions,
        "has_deny": "deny" in observed_decisions,
        "has_step_up": "step_up" in observed_decisions,
        "has_redact": "redact" in observed_decisions,
        "has_quarantine": "quarantine" in observed_decisions,
        "has_fail_closed": "fail_closed" in observed_decisions,
        "expected_policy_coverage": expected_policy_ids.issubset(matched_policy_ids),
        "pack_151_registry_loaded_or_fallback": registry.get("policy_count", 0) >= 10,
        "endpoint": SIMULATION_ENDPOINT,
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(bool(v) for v in readiness_checks.values() if not isinstance(v, str)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 152,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Simulation Mode foundation",
        "endpoint": SIMULATION_ENDPOINT,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "simulated_only": True,
        "real_enforcement_executed": False,
        "cached_non_recursive": True,
        "policy_registry": {
            "policy_count": registry.get("policy_count", 0),
            "enabled_policy_count": registry.get("enabled_policy_count", 0),
            "pack_151_status_available": registry.get("pack_151_status_available", False),
            "registry_source": registry.get("source_status", {}).get("registry_source", "pack_151_or_fallback"),
        },
        "summary": {
            "scenario_count": len(DEFAULT_SCENARIOS),
            "decision_counts": decision_counts,
            "matched_policy_count": len(matched_policy_ids),
            "required_decisions": sorted(required_decisions),
            "observed_decisions": sorted(observed_decisions),
            "readiness_score": readiness_score,
            "readiness_label": "Policy simulation mode ready" if readiness_score == 100 else "Policy simulation mode needs review",
        },
        "readiness_checks": readiness_checks,
        "scenarios": scenario_results,
        "quick_action": {
            "id": "policy_simulation_mode",
            "label": "Policy Simulation Mode",
            "href": SIMULATION_ENDPOINT,
            "description": "Practice policy decisions without enforcing them yet.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_simulation_mode",
            "title": "Policy Simulation Mode",
            "subtitle": "Simulated policy decisions before real enforcement.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": SIMULATION_ENDPOINT,
        },
    }


def build_policy_simulation_mode_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_simulation_mode_payload_cached.cache_clear()
        load_pack_151_policy_status_cached.cache_clear()
    return copy.deepcopy(build_policy_simulation_mode_payload_cached())


def get_policy_simulation_mode_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_simulation_mode_payload(force_refresh=force_refresh)


def build_policy_simulation_mode_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_simulation_mode_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 152,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", SIMULATION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy simulation mode ready"),
        "simulated_only": True,
        "real_enforcement_executed": False,
        "scenario_count": summary.get("scenario_count", 0),
        "decision_counts": summary.get("decision_counts", {}),
        "cached_non_recursive": True,
    }


def get_policy_simulation_mode_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_simulation_mode_status_bridge(force_refresh=force_refresh)


def build_policy_simulation_quick_action() -> Dict[str, Any]:
    bridge = build_policy_simulation_mode_status_bridge()
    return {
        "id": "policy_simulation_mode",
        "label": "Policy Simulation Mode",
        "title": "Policy Simulation Mode",
        "href": SIMULATION_ENDPOINT,
        "endpoint": SIMULATION_ENDPOINT,
        "description": "Practice Tower policy decisions without enforcing them yet.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 152",
        "category": "policy",
        "simulated_only": True,
    }


def build_policy_simulation_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_simulation_mode_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "simulation_readiness",
            "title": "Simulation readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy simulation mode ready"),
        },
        {
            "id": "scenario_count",
            "title": "Scenarios",
            "value": summary.get("scenario_count", 0),
            "label": "Hypothetical decisions tested",
        },
        {
            "id": "decision_coverage",
            "title": "Decision coverage",
            "value": len(summary.get("observed_decisions", [])),
            "label": ", ".join(summary.get("observed_decisions", [])),
        },
        {
            "id": "simulated_only",
            "title": "Simulated only",
            "value": "Yes" if checks.get("simulated_only") else "Review",
            "label": "No real enforcement executed",
        },
        {
            "id": "registry",
            "title": "Policy registry",
            "value": payload.get("policy_registry", {}).get("policy_count", 0),
            "label": "Pack 151 policies loaded or safely mirrored",
        },
        {
            "id": "endpoint",
            "title": "Guarded endpoint",
            "value": SIMULATION_ENDPOINT,
            "label": "Policy simulation JSON",
        },
    ]

    return {
        "section_id": "policy_simulation_mode",
        "title": "Policy Simulation Mode",
        "subtitle": "This lets The Tower practice policy decisions before real enforcement exists.",
        "status": payload.get("status", "ready"),
        "href": SIMULATION_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "cached_non_recursive": True,
    }


def build_policy_simulation_mode_html_section() -> str:
    section = build_policy_simulation_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-simulation-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-simulation-mode-section" id="policy-simulation-mode">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 152</p>
            <h2>{section.get('title', 'Policy Simulation Mode')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{SIMULATION_ENDPOINT}">Open simulation JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "SIMULATION_ENDPOINT",
    "DEFAULT_SCENARIOS",
    "simulate_policy_decision",
    "build_policy_simulation_mode_payload",
    "get_policy_simulation_mode_payload",
    "build_policy_simulation_mode_status_bridge",
    "get_policy_simulation_mode_status_bridge",
    "build_policy_simulation_quick_action",
    "build_policy_simulation_unified_owner_section",
    "build_policy_simulation_mode_html_section",
]
