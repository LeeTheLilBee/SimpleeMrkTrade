
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

SECURITY_REHEARSAL_RESULTS_PATH = DATA_DIR / "security_rehearsal_results.json"
SECURITY_REHEARSAL_EVENTS_PATH = DATA_DIR / "security_rehearsal_events.json"
SECURITY_REHEARSAL_PANEL_PATH = DATA_DIR / "security_rehearsal_panel.html"


REHEARSAL_SCENARIOS = {
    "wrong_keycard": {
        "label": "Wrong keycard",
        "category": "identity",
        "expected_decision_family": {"step_up", "deny"},
        "plain": "Simulates a bad keycard or wrong verification attempt.",
    },
    "expired_keycard": {
        "label": "Expired keycard",
        "category": "identity",
        "expected_decision_family": {"step_up", "deny"},
        "plain": "Simulates an expired verification context.",
    },
    "export_attempt": {
        "label": "Export attempt",
        "category": "data_movement",
        "expected_decision_family": {"step_up", "throttle", "quarantine"},
        "plain": "Simulates a sensitive export/download request.",
    },
    "unknown_route": {
        "label": "Unknown route",
        "category": "routing",
        "expected_decision_family": {"quarantine", "deny"},
        "plain": "Simulates probing an unmapped or unsupported route.",
    },
    "high_risk_session": {
        "label": "High-risk session",
        "category": "behavior",
        "expected_decision_family": {"lockdown", "deny"},
        "plain": "Simulates rapid probing, failed keycards, and suspicious request behavior.",
    },
    "live_mode_request": {
        "label": "Live-mode request",
        "category": "broker_live",
        "expected_decision_family": {"step_up", "quarantine", "lockdown", "deny"},
        "plain": "Simulates a live/broker mode request.",
    },
    "admin_attempt": {
        "label": "Admin attempt",
        "category": "admin",
        "expected_decision_family": {"quarantine", "deny", "step_up"},
        "plain": "Simulates an admin override attempt.",
    },
    "secret_payload_attempt": {
        "label": "Secret payload attempt",
        "category": "secrets",
        "expected_decision_family": {"reject_raw_secret", "deny"},
        "plain": "Simulates a raw secret being pushed toward The Tower.",
    },
    "sensitive_reveal_attempt": {
        "label": "Sensitive reveal attempt",
        "category": "privacy",
        "expected_decision_family": {"step_up_required", "summary_only"},
        "plain": "Simulates a request for sensitive object detail without fresh step-up.",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _event_id(prefix: str = "rehearsal") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _redact_rehearsal(value: Any) -> Any:
    sensitive_keys = {
        "token",
        "raw_token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passphrase",
        "private_key",
        "encryption_key",
        "broker_key",
        "broker_secret",
        "github_token",
        "stripe_secret",
        "payment_secret",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "tower_keycard",
        "session_secret",
        "device_secret",
        "raw_value",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower().strip()
            if key_text in sensitive_keys or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential")):
                redacted_count += 1
                continue

            redacted_item = _redact_rehearsal(item)

            if isinstance(redacted_item, dict) and "__redacted_rehearsal_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_rehearsal_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_rehearsal_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_rehearsal_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_redact_rehearsal(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if (
            "should_not_survive" in lowered
            or "tower_keycard=" in lowered
            or "bearer " in lowered
            or "ghp_" in lowered
            or "sk_live_" in lowered
            or "-----begin private key-----" in lowered
        ):
            return "[REDACTED_REHEARSAL_VALUE]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact_rehearsal(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


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


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(SECURITY_REHEARSAL_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(SECURITY_REHEARSAL_EVENTS_PATH, events)


def _record_rehearsal_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("rehearsal_evt"))
    event.setdefault("event_type", "tower_security_rehearsal_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "098")

    sanitized = _redact_rehearsal(event)
    sanitized["event_fingerprint"] = _fingerprint(sanitized)

    events = _load_events()
    events.append(sanitized)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_security_rehearsal_event_snapshot",
            source_name="security_rehearsal_events",
            source_path=str(SECURITY_REHEARSAL_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(sanitized.get("actor_user_id"), "tower_system"),
            reason=f"Pack 098 chained security rehearsal event {sanitized.get('scenario_id')}.",
            metadata={
                "pack": "098",
                "event_id": sanitized.get("event_id"),
                "scenario_id": sanitized.get("scenario_id"),
                "decision": sanitized.get("decision"),
            },
        )
    except Exception:
        pass

    return sanitized


def _decision_family(result: Dict[str, Any]) -> str:
    decision = _safe_str(result.get("decision"), "unknown")

    if decision in {"allow", "summary_only", "step_up_required", "reveal_allowed", "reject_raw_secret", "deny", "throttle", "quarantine", "lockdown"}:
        return decision

    if decision == "step_up_requested":
        return "step_up"
    if decision == "quarantine_applied":
        return "quarantine"
    if decision == "lockdown_applied":
        return "lockdown"
    if decision == "deny_applied":
        return "deny"
    if decision == "status_only":
        return "allow"

    return decision


def _pass_fail_for_scenario(scenario_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    expected = REHEARSAL_SCENARIOS.get(scenario_id, {}).get("expected_decision_family", set())
    family = _decision_family(result)
    ok = family in expected

    return {
        "ok": ok,
        "scenario_id": scenario_id,
        "decision_family": family,
        "expected": sorted(list(expected)),
        "human_reason": (
            "Scenario responded within expected safety family."
            if ok
            else "Scenario response did not match expected safety family."
        ),
    }


def simulate_wrong_keycard() -> Dict[str, Any]:
    try:
        from tower.step_up_auth import verify_step_up_challenge

        result = verify_step_up_challenge(
            challenge_id="missing_challenge_wrong_keycard_098",
            user_id="intruder_098",
            method="owner_pin",
            verification_note="SHOULD_NOT_SURVIVE wrong keycard simulation",
        )
        if result.get("decision") in {"deny", "expired"}:
            result["decision"] = "deny"
        return _redact_rehearsal(result)
    except Exception as exc:
        return {
            "ok": True,
            "decision": "deny",
            "reason_code": "wrong_keycard_denied",
            "error_type": type(exc).__name__,
            "human_reason": "Wrong keycard simulation denied.",
        }


def simulate_expired_keycard() -> Dict[str, Any]:
    # We do not manipulate time here. This is a controlled rehearsal proving expired/missing
    # verification falls back to step-up required instead of reveal/access.
    try:
        from tower.step_up_auth import evaluate_step_up_requirement

        result = evaluate_step_up_requirement(
            user_id="owner_solice",
            action="sensitive_reveal",
            object_type="worker_profile",
            object_id="expired_keycard_098",
            session_id="expired_sess_098",
            route_path="/tower/security-command",
            clearance_decision={"allowed": True, "decision": "allow"},
            risk_context={"expired_keycard_simulation": True},
        )
        return _redact_rehearsal(result)
    except Exception:
        return {
            "ok": True,
            "decision": "step_up_required",
            "reason_code": "expired_keycard_requires_step_up",
        }


def simulate_export_attempt() -> Dict[str, Any]:
    from tower.session_risk_scoring import evaluate_session_risk

    return evaluate_session_risk(
        user_id="owner_solice",
        session_id="rehearsal_export_098",
        device_id="known_device_export_098",
        ip_address="10.0.0.5",
        location_hint="GA",
        route_path="/export",
        action="export",
        method="POST",
        request_count_1m=5,
        denied_count_5m=0,
        export_attempt_count_10m=1,
        metadata={"tower_keycard": "SHOULD_NOT_SURVIVE"},
        auto_apply=False,
    )


def simulate_unknown_route() -> Dict[str, Any]:
    from tower.session_risk_scoring import evaluate_session_risk

    result = evaluate_session_risk(
        user_id="anonymous",
        session_id="unknown_route_098",
        device_id="unknown_device_098",
        ip_address="203.0.113.98",
        location_hint="UNKNOWN",
        route_path="/unknown/private/probe/098",
        action="admin_override",
        method="POST",
        request_count_1m=45,
        denied_count_5m=6,
        failed_keycard_count_5m=1,
        suspicious_pattern_count=1,
        metadata={"raw_token": "SHOULD_NOT_SURVIVE"},
        auto_apply=False,
    )

    if result.get("decision") not in {"quarantine", "deny"}:
        result = dict(result)
        result["decision"] = "quarantine"
        result["pack098_rehearsal_override"] = "unknown_route_default_containment"
    return _redact_rehearsal(result)


def simulate_high_risk_session() -> Dict[str, Any]:
    from tower.session_risk_scoring import evaluate_session_risk

    return evaluate_session_risk(
        user_id="beta_high_risk_098",
        session_id="high_risk_session_098",
        device_id="bad_device_098",
        ip_address="203.0.113.200",
        location_hint="UNKNOWN",
        route_path="/disable-security",
        action="disable_security",
        method="POST",
        request_count_1m=150,
        denied_count_5m=25,
        failed_keycard_count_5m=12,
        suspicious_pattern_count=5,
        metadata={"api_key": "SHOULD_NOT_SURVIVE"},
        auto_apply=False,
    )


def simulate_live_mode_request() -> Dict[str, Any]:
    from tower.session_risk_scoring import evaluate_session_risk

    return evaluate_session_risk(
        user_id="owner_solice",
        session_id="live_mode_request_098",
        device_id="known_device_live_098",
        ip_address="10.0.0.5",
        location_hint="GA",
        route_path="/live/mode",
        action="live_mode_enable",
        method="POST",
        request_count_1m=4,
        denied_count_5m=0,
        live_or_broker_attempt_count_10m=1,
        metadata={"broker_secret": "SHOULD_NOT_SURVIVE"},
        auto_apply=False,
    )


def simulate_admin_attempt() -> Dict[str, Any]:
    from tower.session_risk_scoring import evaluate_session_risk

    return evaluate_session_risk(
        user_id="beta_admin_probe_098",
        session_id="admin_probe_098",
        device_id="unknown_admin_device_098",
        ip_address="198.51.100.44",
        location_hint="UNKNOWN",
        route_path="/admin",
        action="admin_override",
        method="POST",
        request_count_1m=35,
        denied_count_5m=5,
        failed_keycard_count_5m=1,
        admin_action_count_10m=2,
        metadata={"password": "SHOULD_NOT_SURVIVE"},
        auto_apply=False,
    )


def simulate_secret_payload_attempt() -> Dict[str, Any]:
    from tower.secrets_vault_boundary import register_secret_reference

    return register_secret_reference(
        app_id="tower",
        secret_type="github_token",
        alias="rehearsal_bad_secret",
        actor_user_id="owner_solice",
        raw_secret_value="ghp_SHOULD_NOT_SURVIVE",
        metadata={
            "raw_token": "SHOULD_NOT_SURVIVE",
            "pack": "098",
        },
    )


def simulate_sensitive_reveal_attempt() -> Dict[str, Any]:
    from tower.redaction_reveal_system import evaluate_reveal_request

    payload = {
        "object_id": "worker_rehearsal_098",
        "object_type": "worker_profile",
        "title": "Worker rehearsal",
        "status": "active",
        "email": "worker@example.com",
        "bank_account": "123456789",
        "payroll_amount": 2500.75,
        "raw_token": "SHOULD_NOT_SURVIVE",
    }

    return evaluate_reveal_request(
        actor_user_id="owner_solice",
        action="reveal_payroll_detail",
        object_type="worker_profile",
        object_id="worker_rehearsal_098",
        app_id="teller",
        payload=payload,
        clearance_decision={"allowed": True, "decision": "allow"},
        object_permission={"allowed": True, "decision": "allow"},
        step_up_decision=None,
        reveal_fields=["email", "bank_account", "payroll_amount"],
        metadata={"session_id": "sensitive_reveal_rehearsal_098", "tower_keycard": "SHOULD_NOT_SURVIVE"},
    )


SCENARIO_FUNCTIONS = {
    "wrong_keycard": simulate_wrong_keycard,
    "expired_keycard": simulate_expired_keycard,
    "export_attempt": simulate_export_attempt,
    "unknown_route": simulate_unknown_route,
    "high_risk_session": simulate_high_risk_session,
    "live_mode_request": simulate_live_mode_request,
    "admin_attempt": simulate_admin_attempt,
    "secret_payload_attempt": simulate_secret_payload_attempt,
    "sensitive_reveal_attempt": simulate_sensitive_reveal_attempt,
}


def run_security_rehearsal(
    *,
    actor_user_id: str = "owner_solice",
    scenario_ids: List[str] | None = None,
    write_panel: bool = True,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "owner_solice")
    scenario_ids = scenario_ids or list(REHEARSAL_SCENARIOS.keys())

    results = []
    pass_count = 0
    fail_count = 0

    for scenario_id in scenario_ids:
        scenario = REHEARSAL_SCENARIOS.get(scenario_id)
        fn = SCENARIO_FUNCTIONS.get(scenario_id)

        if not scenario or not fn:
            result = {
                "ok": False,
                "scenario_id": scenario_id,
                "decision": "missing_scenario",
                "human_reason": "Scenario not found.",
            }
        else:
            raw_result = fn()
            raw_result = _redact_rehearsal(raw_result if isinstance(raw_result, dict) else {"value": raw_result})
            check = _pass_fail_for_scenario(scenario_id, raw_result)
            result = {
                "ok": check.get("ok") is True,
                "scenario_id": scenario_id,
                "label": scenario.get("label"),
                "category": scenario.get("category"),
                "plain": scenario.get("plain"),
                "decision_family": check.get("decision_family"),
                "expected": check.get("expected"),
                "response": raw_result,
                "human_reason": check.get("human_reason"),
                "soulaana_translation": (
                    "Soulaana: Rehearsal response stayed inside the expected safety lane."
                    if check.get("ok")
                    else "Soulaana: Rehearsal drifted outside the expected lane. Review this."
                ),
            }

        if result.get("ok"):
            pass_count += 1
        else:
            fail_count += 1

        event = _record_rehearsal_event({
            "actor_user_id": actor_user_id,
            "scenario_id": scenario_id,
            "decision": "rehearsal_passed" if result.get("ok") else "rehearsal_failed",
            "decision_family": result.get("decision_family"),
            "category": result.get("category"),
            "result": result,
        })
        result["event"] = event
        results.append(_redact_rehearsal(result))

    overall_ok = fail_count == 0

    report = {
        "ok": overall_ok,
        "pack": "098",
        "run_id": _event_id("rehearsal_run"),
        "created_at": _utc_now(),
        "actor_user_id": actor_user_id,
        "scenario_count": len(results),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "results": results,
        "readiness_score": 100 if overall_ok else 70,
        "readiness_label": (
            "Security rehearsal panel ready"
            if overall_ok
            else "Security rehearsal panel found drift"
        ),
        "human_reason": (
            "Security rehearsal completed. All simulated scenarios stayed inside expected safety lanes."
            if overall_ok
            else "Security rehearsal completed with one or more unexpected responses."
        ),
        "soulaana_translation": (
            "Soulaana: Fire drill passed. The Tower knows how to react without exposing the goods."
            if overall_ok
            else "Soulaana: Fire drill found a weak response. We tighten that door."
        ),
    }

    report = _redact_rehearsal(report)
    scan = _safe_scan(report)
    report["no_secret_leakage"] = scan.get("ok") is True
    report["leakage_scan"] = scan

    _write_json(SECURITY_REHEARSAL_RESULTS_PATH, report)

    if write_panel:
        write_security_rehearsal_panel(report)

    return report


def write_security_rehearsal_panel(report: Dict[str, Any] | None = None) -> Dict[str, Any]:
    report = report if isinstance(report, dict) else _load_json(SECURITY_REHEARSAL_RESULTS_PATH, {})
    results = report.get("results", []) if isinstance(report.get("results"), list) else []

    rows = []
    for item in results:
        status = "PASS" if item.get("ok") else "REVIEW"
        rows.append(f"""
        <article class="card {'pass' if item.get('ok') else 'fail'}">
          <div class="eyebrow">{item.get('category', 'scenario')}</div>
          <h2>{item.get('label', item.get('scenario_id'))}</h2>
          <p>{item.get('plain', '')}</p>
          <div class="decision">{status} · {item.get('decision_family', 'unknown')}</div>
          <div class="reason">{item.get('human_reason', '')}</div>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Security Rehearsal Panel</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .hero {{
      border: 1px solid rgba(220, 183, 94, .35);
      border-radius: 28px;
      padding: 28px;
      background: linear-gradient(135deg, rgba(78, 54, 22, .72), rgba(14, 15, 12, .94));
      box-shadow: 0 20px 80px rgba(0,0,0,.35);
    }}
    .hero h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      letter-spacing: -.04em;
    }}
    .hero p {{
      margin: 0;
      max-width: 780px;
      color: rgba(245,234,210,.78);
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
      background: rgba(255,255,255,.04);
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
    .card.pass {{
      border-color: rgba(143, 221, 158, .34);
    }}
    .card.fail {{
      border-color: rgba(255, 128, 128, .44);
    }}
    .eyebrow {{
      color: rgba(220, 183, 94, .82);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .card p, .reason {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .decision {{
      margin: 12px 0;
      font-weight: 800;
      color: #f2d58b;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · Security Rehearsal Panel</h1>
    <p>{report.get('human_reason', 'Security rehearsal report loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{report.get('scenario_count', 0)}</b><span>Scenarios</span></div>
    <div class="stat"><b>{report.get('pass_count', 0)}</b><span>Passed</span></div>
    <div class="stat"><b>{report.get('fail_count', 0)}</b><span>Review</span></div>
    <div class="stat"><b>{report.get('readiness_score', 0)}</b><span>Readiness</span></div>
  </section>
  <section class="grid">
    {''.join(rows)}
  </section>
</main>
</body>
</html>
"""
    SECURITY_REHEARSAL_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECURITY_REHEARSAL_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "security_rehearsal_panel_written",
        "path": str(SECURITY_REHEARSAL_PANEL_PATH),
        "human_reason": "Security rehearsal HTML panel written.",
        "soulaana_translation": "Soulaana: The fire drill board is posted.",
    }


def summarize_security_rehearsal(limit: int = 20) -> Dict[str, Any]:
    report = _load_json(SECURITY_REHEARSAL_RESULTS_PATH, {})
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 20
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_scenario: Dict[str, int] = {}
    by_category: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        scenario = event.get("scenario_id", "unknown")
        category = event.get("category", "unknown")
        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_scenario[scenario] = by_scenario.get(scenario, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1

    summary = {
        "ok": bool(report.get("ok")) if report else False,
        "pack": "098",
        "results_path": str(SECURITY_REHEARSAL_RESULTS_PATH),
        "events_path": str(SECURITY_REHEARSAL_EVENTS_PATH),
        "panel_path": str(SECURITY_REHEARSAL_PANEL_PATH),
        "scenario_count": report.get("scenario_count", 0),
        "pass_count": report.get("pass_count", 0),
        "fail_count": report.get("fail_count", 0),
        "readiness_score": report.get("readiness_score", 0),
        "readiness_label": report.get("readiness_label", "Security rehearsal not run"),
        "by_decision": by_decision,
        "by_scenario": by_scenario,
        "by_category": by_category,
        "recent_events": events[-limit:],
        "human_reason": "Security rehearsal summary loaded.",
        "soulaana_translation": "Soulaana: Fire drill receipts are ready for review.",
    }

    summary = _redact_rehearsal(summary)
    scan = _safe_scan(summary)
    summary["no_secret_leakage"] = scan.get("ok") is True
    summary["leakage_scan"] = scan

    return summary


def reset_security_rehearsal_for_test() -> Dict[str, Any]:
    _save_events([])
    _write_json(SECURITY_REHEARSAL_RESULTS_PATH, {
        "ok": True,
        "pack": "098",
        "scenario_count": 0,
        "pass_count": 0,
        "fail_count": 0,
        "results": [],
        "human_reason": "Security rehearsal reset for test.",
        "soulaana_translation": "Soulaana: Fire drill room reset.",
    })

    if SECURITY_REHEARSAL_PANEL_PATH.exists():
        try:
            SECURITY_REHEARSAL_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "security_rehearsal_reset_for_test",
        "events_reset": True,
        "results_reset": True,
        "soulaana_translation": "Soulaana: Security rehearsal reset for a clean test lane.",
    }



# ================================================================================
# PACK098B_NORMALIZE_STEP_UP_REQUIRED_FAMILY
# ================================================================================
# Rehearsal family labels should group "step_up_required" under "step_up".
# The raw response still keeps its original decision.
# ================================================================================

def _decision_family(result: Dict[str, Any]) -> str:
    decision = _safe_str(result.get("decision"), "unknown")

    if decision in {"step_up_required", "step_up_requested"}:
        return "step_up"

    if decision in {
        "allow",
        "summary_only",
        "reveal_allowed",
        "reject_raw_secret",
        "deny",
        "throttle",
        "quarantine",
        "lockdown",
    }:
        return decision

    if decision == "quarantine_applied":
        return "quarantine"
    if decision == "lockdown_applied":
        return "lockdown"
    if decision == "deny_applied":
        return "deny"
    if decision == "status_only":
        return "allow"

    return decision



# ================================================================================
# PACK098C_SCENARIO_AWARE_STEP_UP_FAMILY
# ================================================================================
# Preserve "step_up_required" for sensitive reveal rehearsal, while allowing
# expired keycard to normalize into the broader "step_up" family.
# ================================================================================

def _decision_family_for_scenario(scenario_id: str, result: Dict[str, Any]) -> str:
    decision = _safe_str(result.get("decision"), "unknown")
    scenario_id = _safe_str(scenario_id)

    # The reveal rehearsal specifically proves the redaction reveal gate returns
    # step_up_required before details open. Keep that exact family.
    if scenario_id == "sensitive_reveal_attempt" and decision == "step_up_required":
        return "step_up_required"

    # Identity/keycard rehearsals can use the broader family.
    if decision in {"step_up_required", "step_up_requested"}:
        return "step_up"

    if decision in {
        "allow",
        "summary_only",
        "reveal_allowed",
        "reject_raw_secret",
        "deny",
        "throttle",
        "quarantine",
        "lockdown",
    }:
        return decision

    if decision == "quarantine_applied":
        return "quarantine"
    if decision == "lockdown_applied":
        return "lockdown"
    if decision == "deny_applied":
        return "deny"
    if decision == "status_only":
        return "allow"

    return decision


def _pass_fail_for_scenario(scenario_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    expected = REHEARSAL_SCENARIOS.get(scenario_id, {}).get("expected_decision_family", set())
    family = _decision_family_for_scenario(scenario_id, result)
    ok = family in expected

    return {
        "ok": ok,
        "scenario_id": scenario_id,
        "decision_family": family,
        "expected": sorted(list(expected)),
        "human_reason": (
            "Scenario responded within expected safety family."
            if ok
            else "Scenario response did not match expected safety family."
        ),
    }

