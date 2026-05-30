
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

POLICY_AS_CODE_REGISTRY_PATH = DATA_DIR / "policy_as_code_registry.json"
POLICY_AS_CODE_STATUS_PATH = DATA_DIR / "policy_as_code_engine_status.json"
POLICY_AS_CODE_PANEL_PATH = DATA_DIR / "policy_as_code_engine_panel.html"

ALLOWED_POLICY_EFFECTS = {
    "allow",
    "deny",
    "step_up",
    "log",
    "redact",
    "quarantine",
    "lockdown",
    "route",
    "fail_closed",
}

ALLOWED_POLICY_DOMAINS = {
    "tower",
    "ob",
    "archive",
    "simpleepay",
    "broker",
    "secrets",
    "admin",
    "export",
    "privacy",
    "live_trading",
    "identity",
    "route",
    "object",
}

DEFAULT_TOWER_POLICIES: List[Dict[str, Any]] = [
    {
        "policy_id": "tower.default_deny",
        "title": "Tower Default Deny",
        "domain": "tower",
        "scope": {"applies_to": ["route", "object", "action", "mode"], "zone": "all"},
        "condition": "no explicit allow policy is matched",
        "effect": "deny",
        "priority": 1000,
        "enforcement": {"mode": "hard_block", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "policy_deny"},
        "owner_reason": "The Tower denies access unless a policy explicitly allows it.",
        "soulaana_translation": "Soulaana: No clearance means no passage.",
        "enabled": True,
    },
    {
        "policy_id": "tower.no_clearance_no_ob",
        "title": "No Tower Clearance = No Observatory",
        "domain": "ob",
        "scope": {"applies_to": ["ob_app", "survey", "paper", "signals", "analysis_vault"], "zone": "ob"},
        "condition": "tower_clearance is missing or invalid",
        "effect": "deny",
        "priority": 990,
        "enforcement": {"mode": "hard_block", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "ob_clearance_denied"},
        "owner_reason": "The Observatory must not load without Tower clearance.",
        "soulaana_translation": "Soulaana: The Observatory stays dark until the Tower clears the user.",
        "enabled": True,
    },
    {
        "policy_id": "live.public_automated_locked",
        "title": "Public Live Automated Trading Locked",
        "domain": "live_trading",
        "scope": {"applies_to": ["live_automated", "public_user", "broker_action"], "zone": "broker"},
        "condition": "public user requests live automated trading before legal/compliance approval",
        "effect": "deny",
        "priority": 980,
        "enforcement": {"mode": "hard_block", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "live_automation_block"},
        "owner_reason": "Public Live Automated trading remains locked until legal, licensing, broker, and Control Tower gates are ready.",
        "soulaana_translation": "Soulaana: Automated Live stays locked for public users.",
        "enabled": True,
    },
    {
        "policy_id": "secrets.vault_boundary",
        "title": "Secrets Vault Boundary",
        "domain": "secrets",
        "scope": {"applies_to": ["api_key", "broker_key", "github_token", "payment_secret"], "zone": "secrets"},
        "condition": "raw secret is requested by Tower app code",
        "effect": "deny",
        "priority": 970,
        "enforcement": {"mode": "hard_block", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "secret_boundary_denied"},
        "owner_reason": "The Tower must not store or expose raw broker keys, API keys, GitHub tokens, payment secrets, or encryption keys.",
        "soulaana_translation": "Soulaana: Secrets stay sealed in the vault.",
        "enabled": True,
    },
    {
        "policy_id": "export.sensitive_step_up",
        "title": "Sensitive Export Requires Step-Up",
        "domain": "export",
        "scope": {"applies_to": ["archive_export", "evidence_bundle", "sensitive_report"], "zone": "export"},
        "condition": "sensitive export is requested",
        "effect": "step_up",
        "priority": 940,
        "enforcement": {"mode": "step_up_required", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "export_step_up"},
        "owner_reason": "Sensitive exports require step-up verification and audit evidence.",
        "soulaana_translation": "Soulaana: Sensitive exports need owner confirmation.",
        "enabled": True,
    },
    {
        "policy_id": "privacy.redact_by_default",
        "title": "Redact Sensitive Details by Default",
        "domain": "privacy",
        "scope": {"applies_to": ["pii", "secret", "sensitive_detail", "owner_private_data"], "zone": "privacy"},
        "condition": "viewer lacks reveal clearance or step-up",
        "effect": "redact",
        "priority": 930,
        "enforcement": {"mode": "redact_first", "requires_receipt": True, "fail_behavior": "redact"},
        "evidence": {"audit_required": True, "receipt_type": "redaction_applied"},
        "owner_reason": "Sensitive details should show as summaries until reveal clearance is proven.",
        "soulaana_translation": "Soulaana: I show the shape, not the secret, until clearance is proven.",
        "enabled": True,
    },
    {
        "policy_id": "admin.owner_receipt_required",
        "title": "Owner/Admin Actions Require Receipts",
        "domain": "admin",
        "scope": {"applies_to": ["resolve", "override", "grant", "lockdown_disable", "route_policy_change"], "zone": "admin"},
        "condition": "owner or admin changes protected Tower state",
        "effect": "log",
        "priority": 920,
        "enforcement": {"mode": "receipt_required", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "owner_admin_action"},
        "owner_reason": "Protected owner/admin actions must leave receipts.",
        "soulaana_translation": "Soulaana: Owner/admin moves leave a trail.",
        "enabled": True,
    },
    {
        "policy_id": "route.unknown_route_quarantine",
        "title": "Unknown Route Quarantine",
        "domain": "route",
        "scope": {"applies_to": ["unknown_route", "probing", "legacy_unmapped"], "zone": "route"},
        "condition": "route is unknown, unmapped, or suspiciously probed",
        "effect": "quarantine",
        "priority": 900,
        "enforcement": {"mode": "quarantine_or_redirect", "requires_receipt": True, "fail_behavior": "quarantine"},
        "evidence": {"audit_required": True, "receipt_type": "route_quarantine"},
        "owner_reason": "Unknown or suspicious routes should be noisy and contained.",
        "soulaana_translation": "Soulaana: Strange doors go to holding, not deeper inside.",
        "enabled": True,
    },
    {
        "policy_id": "object.least_privilege",
        "title": "Object Least Privilege",
        "domain": "object",
        "scope": {"applies_to": ["object_detail", "record", "user_data", "archive_item"], "zone": "object"},
        "condition": "actor lacks object-level permission",
        "effect": "deny",
        "priority": 890,
        "enforcement": {"mode": "object_guard", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "object_access_denied"},
        "owner_reason": "Users and systems must only see objects explicitly permitted to them.",
        "soulaana_translation": "Soulaana: Clearance to the room is not clearance to every drawer.",
        "enabled": True,
    },
    {
        "policy_id": "dependency.fail_closed",
        "title": "Critical Dependency Failure Fails Closed",
        "domain": "tower",
        "scope": {"applies_to": ["broker", "archive", "secrets", "payment", "email", "policy_engine"], "zone": "dependency"},
        "condition": "critical dependency unavailable or untrusted",
        "effect": "fail_closed",
        "priority": 880,
        "enforcement": {"mode": "fail_closed", "requires_receipt": True, "fail_behavior": "deny"},
        "evidence": {"audit_required": True, "receipt_type": "dependency_fail_closed"},
        "owner_reason": "Critical systems should fail closed instead of silently allowing unsafe access.",
        "soulaana_translation": "Soulaana: If a critical system goes quiet, the doors do not open.",
        "enabled": True,
    },
]


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


def _load_registry() -> List[Dict[str, Any]]:
    data = _load_json(POLICY_AS_CODE_REGISTRY_PATH, [])
    if isinstance(data, list) and data:
        return [item for item in data if isinstance(item, dict)]

    _write_json(POLICY_AS_CODE_REGISTRY_PATH, DEFAULT_TOWER_POLICIES)
    return list(DEFAULT_TOWER_POLICIES)


def _validate_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    missing = []

    for key in [
        "policy_id",
        "title",
        "domain",
        "scope",
        "condition",
        "effect",
        "priority",
        "enforcement",
        "evidence",
        "owner_reason",
        "soulaana_translation",
        "enabled",
    ]:
        if key not in policy:
            missing.append(key)

    policy_id = str(policy.get("policy_id", "") or "").strip()
    domain = str(policy.get("domain", "") or "").strip()
    effect = str(policy.get("effect", "") or "").strip()

    scope = policy.get("scope", {})
    enforcement = policy.get("enforcement", {})
    evidence = policy.get("evidence", {})

    problems = []

    if not policy_id:
        problems.append("missing_policy_id")

    if domain not in ALLOWED_POLICY_DOMAINS:
        problems.append("invalid_domain")

    if effect not in ALLOWED_POLICY_EFFECTS:
        problems.append("invalid_effect")

    if not isinstance(scope, dict) or not scope.get("applies_to"):
        problems.append("invalid_scope")

    if not isinstance(enforcement, dict):
        problems.append("invalid_enforcement")
    else:
        if "mode" not in enforcement:
            problems.append("missing_enforcement_mode")
        if "fail_behavior" not in enforcement:
            problems.append("missing_fail_behavior")

    if not isinstance(evidence, dict):
        problems.append("invalid_evidence")
    else:
        if evidence.get("audit_required") is not True:
            problems.append("audit_not_required")
        if not evidence.get("receipt_type"):
            problems.append("missing_receipt_type")

    if not isinstance(policy.get("enabled"), bool):
        problems.append("enabled_not_bool")

    return {
        "policy_id": policy_id,
        "ok": not missing and not problems,
        "missing_fields": missing,
        "problems": problems,
        "domain": domain,
        "effect": effect,
        "enabled": policy.get("enabled") is True,
        "priority": _num(policy.get("priority"), 0),
    }


def build_policy_as_code_engine_status(write_panel: bool = True) -> Dict[str, Any]:
    policies = _load_registry()
    validations = [_validate_policy(policy) for policy in policies]

    policy_ids = [str(policy.get("policy_id", "")) for policy in policies if isinstance(policy, dict)]
    duplicate_policy_ids = sorted([pid for pid in set(policy_ids) if policy_ids.count(pid) > 1])

    enabled_policies = [policy for policy in policies if policy.get("enabled") is True]
    enabled_validations = [item for item in validations if item.get("enabled") is True]

    failed_validations = [item for item in validations if item.get("ok") is not True]
    failed_enabled_validations = [item for item in enabled_validations if item.get("ok") is not True]

    by_domain: Dict[str, int] = {}
    by_effect: Dict[str, int] = {}

    for policy in policies:
        domain = str(policy.get("domain", "") or "unknown")
        effect = str(policy.get("effect", "") or "unknown")
        by_domain[domain] = by_domain.get(domain, 0) + 1
        by_effect[effect] = by_effect.get(effect, 0) + 1

    required_policy_ids = {
        "tower.default_deny",
        "tower.no_clearance_no_ob",
        "live.public_automated_locked",
        "secrets.vault_boundary",
        "export.sensitive_step_up",
        "privacy.redact_by_default",
        "object.least_privilege",
        "dependency.fail_closed",
    }

    present_policy_ids = set(policy_ids)

    checks = {
        "registry_loaded": len(policies) >= 8,
        "default_deny_present": "tower.default_deny" in present_policy_ids,
        "no_clearance_no_ob_present": "tower.no_clearance_no_ob" in present_policy_ids,
        "public_live_automated_locked_present": "live.public_automated_locked" in present_policy_ids,
        "secrets_vault_boundary_present": "secrets.vault_boundary" in present_policy_ids,
        "export_step_up_present": "export.sensitive_step_up" in present_policy_ids,
        "redact_by_default_present": "privacy.redact_by_default" in present_policy_ids,
        "object_least_privilege_present": "object.least_privilege" in present_policy_ids,
        "dependency_fail_closed_present": "dependency.fail_closed" in present_policy_ids,
        "all_required_policies_present": required_policy_ids.issubset(present_policy_ids),
        "no_duplicate_policy_ids": not duplicate_policy_ids,
        "all_enabled_policies_valid": not failed_enabled_validations,
        "deny_effect_present": by_effect.get("deny", 0) >= 3,
        "step_up_effect_present": by_effect.get("step_up", 0) >= 1,
        "redact_effect_present": by_effect.get("redact", 0) >= 1,
        "quarantine_effect_present": by_effect.get("quarantine", 0) >= 1,
        "fail_closed_effect_present": by_effect.get("fail_closed", 0) >= 1,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "151",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(POLICY_AS_CODE_STATUS_PATH),
        "panel_path": str(POLICY_AS_CODE_PANEL_PATH),
        "registry_path": str(POLICY_AS_CODE_REGISTRY_PATH),
        "policy_count": len(policies),
        "enabled_policy_count": len(enabled_policies),
        "validation_count": len(validations),
        "failed_validation_count": len(failed_validations),
        "failed_enabled_validation_count": len(failed_enabled_validations),
        "duplicate_policy_ids": duplicate_policy_ids,
        "required_policy_ids": sorted(required_policy_ids),
        "present_required_policy_count": len(required_policy_ids.intersection(present_policy_ids)),
        "by_domain": by_domain,
        "by_effect": by_effect,
        "checks": checks,
        "failed_checks": failed_checks,
        "policies": policies,
        "validations": validations,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 5)),
        "readiness_label": "Policy-as-Code foundation ready" if not failed_checks else "Policy-as-Code foundation needs review",
        "human_reason": "Policy-as-Code Engine foundation is ready with default deny, Tower clearance, Live automation lock, secrets boundary, export step-up, redaction, object least privilege, and fail-closed policies.",
        "soulaana_translation": "Soulaana: The Tower now has a written policy spine. Doors, secrets, exports, live trading, and objects have named rules.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(POLICY_AS_CODE_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_policy_as_code_foundation",
            source_name="policy_as_code_engine_status",
            source_path=str(POLICY_AS_CODE_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=len(policies),
            actor_user_id="tower_system",
            reason="Pack 151 Policy-as-Code Engine foundation generated.",
            metadata={
                "pack": "151",
                "status": status.get("status"),
                "policy_count": len(policies),
                "readiness_score": status.get("readiness_score"),
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_panel:
        write_policy_as_code_engine_panel(status)

    return status


def render_policy_as_code_engine_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_policy_as_code_engine_status(write_panel=False)
    policies = status.get("policies", []) if isinstance(status.get("policies"), list) else []

    policy_cards = []
    for policy in policies[:12]:
        if not isinstance(policy, dict):
            continue
        policy_cards.append(f"""
        <article class="policy-code-card">
          <div class="policy-code-card__eyebrow">{_html_escape(policy.get('domain', 'tower'))} · {_html_escape(policy.get('effect', 'deny'))}</div>
          <h3>{_html_escape(policy.get('title', 'Policy'))}</h3>
          <p>{_html_escape(policy.get('owner_reason', ''))}</p>
          <code>{_html_escape(policy.get('policy_id', ''))}</code>
        </article>
        """)

    html = f"""
<!-- PACK151_POLICY_AS_CODE_ENGINE_SECTION -->
<section class="policy-as-code-engine" data-pack="151">
  <style>
    .policy-as-code-engine {{
      margin: 24px 0;
      border: 1px solid rgba(168,175,255,.46);
      border-radius: 30px;
      padding: 24px;
      background:
        radial-gradient(circle at top left, rgba(168,175,255,.14), transparent 34%),
        radial-gradient(circle at bottom right, rgba(143,221,158,.11), transparent 36%),
        linear-gradient(135deg, rgba(22,20,48,.90), rgba(8,9,7,.96));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .policy-as-code-engine__eyebrow {{
      color: rgba(168,175,255,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .policy-as-code-engine h2 {{
      margin: 0;
      font-size: 28px;
      letter-spacing: -.04em;
    }}
    .policy-as-code-engine p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .policy-code-summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }}
    .policy-code-metric,
    .policy-code-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .policy-code-metric small,
    .policy-code-card__eyebrow {{
      display: block;
      color: rgba(168,175,255,.78);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .policy-code-metric b {{
      display: block;
      font-size: 20px;
      color: #f5ead2;
      word-break: break-word;
    }}
    .policy-code-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .policy-code-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
      color: #f5ead2;
    }}
    .policy-code-card p {{
      margin: 0;
      color: rgba(245,234,210,.64);
      font-size: 12px;
    }}
    .policy-code-card code {{
      display: block;
      margin-top: 10px;
      color: rgba(168,175,255,.92);
      font-size: 11px;
      word-break: break-word;
    }}
    @media (max-width: 1100px) {{
      .policy-code-summary,
      .policy-code-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="policy-as-code-engine__eyebrow">PACK 151 · POLICY-AS-CODE FOUNDATION</div>
  <h2>{_html_escape(status.get('readiness_label', 'Policy-as-Code Engine'))}</h2>
  <p>{_html_escape(status.get('human_reason', 'Policy-as-Code foundation loaded.'))}</p>

  <div class="policy-code-summary">
    <article class="policy-code-metric"><small>Policies</small><b>{_html_escape(status.get('policy_count', 0))}</b></article>
    <article class="policy-code-metric"><small>Enabled</small><b>{_html_escape(status.get('enabled_policy_count', 0))}</b></article>
    <article class="policy-code-metric"><small>Required</small><b>{_html_escape(status.get('present_required_policy_count', 0))}</b></article>
    <article class="policy-code-metric"><small>Failures</small><b>{_html_escape(status.get('failed_enabled_validation_count', 0))}</b></article>
    <article class="policy-code-metric"><small>Readiness</small><b>{_html_escape(status.get('readiness_score', 0))}%</b></article>
  </div>

  <div class="policy-code-grid">
    {''.join(policy_cards)}
  </div>
</section>
<!-- END PACK151_POLICY_AS_CODE_ENGINE_SECTION -->
"""
    return html


def write_policy_as_code_engine_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_policy_as_code_engine_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Policy-as-Code Engine</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1280px;margin:auto;">
{render_policy_as_code_engine_section(status)}
</main>
</body>
</html>
"""
    _write_text(POLICY_AS_CODE_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "151",
        "decision": "policy_as_code_engine_panel_written",
        "path": str(POLICY_AS_CODE_PANEL_PATH),
        "human_reason": "Policy-as-Code Engine panel written.",
        "soulaana_translation": "Soulaana: Policy-as-Code board posted.",
    }


def load_policy_as_code_engine_status() -> Dict[str, Any]:
    data = _load_json(POLICY_AS_CODE_STATUS_PATH, {})
    if not data:
        data = build_policy_as_code_engine_status(write_panel=True)
    return data if isinstance(data, dict) else {}


def policy_as_code_engine_status_card() -> Dict[str, Any]:
    status = load_policy_as_code_engine_status()

    return {
        "ok": status.get("ok") is True,
        "pack": "151",
        "title": "Policy-as-Code Engine",
        "readiness_score": status.get("readiness_score", 0),
        "policy_count": status.get("policy_count", 0),
        "enabled_policy_count": status.get("enabled_policy_count", 0),
        "failed_enabled_validation_count": status.get("failed_enabled_validation_count", 0),
        "present_required_policy_count": status.get("present_required_policy_count", 0),
        "default_deny_present": status.get("checks", {}).get("default_deny_present") is True if isinstance(status.get("checks"), dict) else False,
        "no_clearance_no_ob_present": status.get("checks", {}).get("no_clearance_no_ob_present") is True if isinstance(status.get("checks"), dict) else False,
        "public_live_automated_locked_present": status.get("checks", {}).get("public_live_automated_locked_present") is True if isinstance(status.get("checks"), dict) else False,
        "panel_path": status.get("panel_path", str(POLICY_AS_CODE_PANEL_PATH)),
        "status_path": status.get("status_path", str(POLICY_AS_CODE_STATUS_PATH)),
        "human_reason": "Policy-as-Code Engine status card loaded.",
        "soulaana_translation": "Soulaana: Policy-as-Code foundation is visible.",
    }


def reset_policy_as_code_engine_for_test() -> Dict[str, Any]:
    _write_json(POLICY_AS_CODE_REGISTRY_PATH, DEFAULT_TOWER_POLICIES)
    _write_json(POLICY_AS_CODE_STATUS_PATH, {
        "ok": True,
        "pack": "151",
        "reset_at": _utc_now(),
        "human_reason": "Policy-as-Code Engine reset for test.",
    })
    if POLICY_AS_CODE_PANEL_PATH.exists():
        try:
            POLICY_AS_CODE_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "policy_as_code_engine_reset_for_test",
        "soulaana_translation": "Soulaana: Policy-as-Code reset for a clean test lane.",
    }
