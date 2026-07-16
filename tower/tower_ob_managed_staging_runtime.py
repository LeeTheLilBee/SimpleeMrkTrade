"""Fail-closed managed-staging runtime boundary for Tower and Observatory.

The initial managed-host topology is intentionally one Tower-fronted Flask
service. Observatory routes remain co-resident in ``web.app`` and are guarded
at the HTTP path boundary. A separate Observatory service is not created by
this module.

This module never calls a hosting provider and never stores secret values.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote

SCHEMA_VERSION = "simplee.tower_ob.managed_staging_runtime.v1"

SOURCE_APPLICATION_TARGET = "web.app:app"
MANAGED_WSGI_TARGET = "web.managed_staging:app"
MANAGED_START_COMMAND = (
    "gunicorn --bind 0.0.0.0:$PORT web.managed_staging:app"
)

DEPLOYMENT_ENVIRONMENT_ENV = "SIMPLEE_DEPLOYMENT_ENVIRONMENT"
HOSTED_MODE_ENV = "TOWER_HOSTED_MODE"
MANAGED_HOST_PROVIDER_ENV = "SIMPLEE_MANAGED_HOST_PROVIDER"
MANAGED_HOST_ACCOUNT_OR_TEAM_ENV = (
    "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM"
)
STAGING_DEPLOYMENT_REGION_ENV = (
    "SIMPLEE_STAGING_DEPLOYMENT_REGION"
)
PROVIDER_OWNER_APPROVAL_ENV = (
    "SIMPLEE_PROVIDER_OWNER_APPROVAL"
)

TOWER_SESSION_SECRET_ENV = "TOWER_SESSION_SECRET"
TOWER_OWNER_USERNAME_ENV = "TOWER_OWNER_USERNAME"
TOWER_OWNER_PASSWORD_HASH_ENV = "TOWER_OWNER_PASSWORD_HASH"
TOWER_OWNER_ID_ENV = "TOWER_OWNER_ID"
TOWER_STEP_UP_MINUTES_ENV = "TOWER_STEP_UP_MINUTES"
TOWER_LOCAL_WALKTHROUGH_MODE_ENV = (
    "TOWER_LOCAL_WALKTHROUGH_MODE"
)
TOWER_LOCAL_OWNER_PASSWORD_ENV = (
    "TOWER_LOCAL_OWNER_PASSWORD"
)

REQUIRED_RUNTIME_REFERENCES = (
    DEPLOYMENT_ENVIRONMENT_ENV,
    HOSTED_MODE_ENV,
    TOWER_SESSION_SECRET_ENV,
    TOWER_OWNER_USERNAME_ENV,
    TOWER_OWNER_PASSWORD_HASH_ENV,
    TOWER_OWNER_ID_ENV,
)

REQUIRED_PROVIDER_REFERENCES = (
    MANAGED_HOST_PROVIDER_ENV,
    MANAGED_HOST_ACCOUNT_OR_TEAM_ENV,
    STAGING_DEPLOYMENT_REGION_ENV,
    PROVIDER_OWNER_APPROVAL_ENV,
)

PROHIBITED_HOSTED_REFERENCES = (
    TOWER_LOCAL_OWNER_PASSWORD_ENV,
)

PROTECTED_OB_EXACT_PATHS = frozenset({
    "/dashboard",
    "/market-map",
})

PROTECTED_OB_PREFIXES = (
    "/ob/",
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def payload_hash(value: Any) -> str:
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }


def _present(environ: Mapping[str, str], name: str) -> bool:
    return bool(str(environ.get(name, "") or "").strip())


def _fingerprint(value: str) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def environment_reference_contract() -> dict[str, Any]:
    """Return environment names and rules without reading or exposing values."""

    contract = {
        "schema_version": SCHEMA_VERSION,
        "runtime_required": list(REQUIRED_RUNTIME_REFERENCES),
        "provider_required_before_authorization_review": list(
            REQUIRED_PROVIDER_REFERENCES
        ),
        "optional": [
            "PORT",
            TOWER_STEP_UP_MINUTES_ENV,
            "TOWER_OB_WALKTHROUGH_DB",
            "TOWER_OB_WALKTHROUGH_BACKUP_DIR",
            "TOWER_OB_WALKTHROUGH_BACKUP_MAX_AGE_HOURS",
            "TOWER_OB_WALKTHROUGH_INCIDENT_DIR",
            "TOWER_OB_WALKTHROUGH_RETENTION_APPROVAL_DIR",
            "TOWER_OB_WALKTHROUGH_DEPLOYMENT_RECORD_DIR",
            "TOWER_OB_WALKTHROUGH_ACTIVATION_APPROVAL_DIR",
        ],
        "prohibited_in_hosted_staging": list(
            PROHIBITED_HOSTED_REFERENCES
        ),
        "rules": {
            "values_in_contract": False,
            "raw_secrets_in_git": False,
            "raw_secrets_in_evidence": False,
            "provider_secret_store_required": True,
            "production_secrets_reused_in_staging": False,
            "local_walkthrough_mode_allowed": False,
            "local_plaintext_owner_password_allowed": False,
        },
    }
    contract["contract_hash"] = payload_hash(contract)
    return contract


def evaluate_managed_staging_environment(
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Evaluate runtime and provider readiness without returning raw values."""

    source = os.environ if environ is None else environ

    session_secret = str(
        source.get(TOWER_SESSION_SECRET_ENV, "") or ""
    )
    password_hash = str(
        source.get(TOWER_OWNER_PASSWORD_HASH_ENV, "") or ""
    )

    reference_presence = {
        name: _present(source, name)
        for name in (
            *REQUIRED_RUNTIME_REFERENCES,
            *REQUIRED_PROVIDER_REFERENCES,
            TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
            TOWER_LOCAL_OWNER_PASSWORD_ENV,
            "PORT",
        )
    }

    runtime_checks = {
        "deployment_environment_is_staging": (
            str(
                source.get(
                    DEPLOYMENT_ENVIRONMENT_ENV,
                    "",
                )
                or ""
            )
            .strip()
            .lower()
            == "staging"
        ),
        "hosted_mode_enabled": _truthy(
            source.get(HOSTED_MODE_ENV)
        ),
        "session_secret_present": bool(
            session_secret.strip()
        ),
        "session_secret_minimum_length": (
            len(session_secret) >= 32
        ),
        "owner_username_present": _present(
            source,
            TOWER_OWNER_USERNAME_ENV,
        ),
        "owner_password_hash_present": bool(
            password_hash.strip()
        ),
        "owner_password_appears_hashed": (
            ":" in password_hash
            and len(password_hash) >= 20
        ),
        "owner_id_present": _present(
            source,
            TOWER_OWNER_ID_ENV,
        ),
        "local_walkthrough_mode_disabled": not _truthy(
            source.get(
                TOWER_LOCAL_WALKTHROUGH_MODE_ENV
            )
        ),
        "local_plaintext_password_absent": not _present(
            source,
            TOWER_LOCAL_OWNER_PASSWORD_ENV,
        ),
    }

    provider_checks = {
        "managed_host_provider_present": _present(
            source,
            MANAGED_HOST_PROVIDER_ENV,
        ),
        "managed_host_account_or_team_present": _present(
            source,
            MANAGED_HOST_ACCOUNT_OR_TEAM_ENV,
        ),
        "staging_deployment_region_present": _present(
            source,
            STAGING_DEPLOYMENT_REGION_ENV,
        ),
        "provider_owner_approval_recorded": (
            str(
                source.get(
                    PROVIDER_OWNER_APPROVAL_ENV,
                    "",
                )
                or ""
            )
            .strip()
            .upper()
            == "APPROVED"
        ),
    }

    runtime_ready = all(runtime_checks.values())
    provider_inputs_complete = all(
        provider_checks.values()
    )

    blockers: list[dict[str, str]] = []

    if not provider_checks[
        "managed_host_provider_present"
    ]:
        blockers.append({
            "requirement": "managed_host_provider",
            "status": "operator_input_required",
        })

    if not provider_checks[
        "managed_host_account_or_team_present"
    ]:
        blockers.append({
            "requirement": "managed_host_account_or_team",
            "status": "operator_input_required",
        })

    if not provider_checks[
        "staging_deployment_region_present"
    ]:
        blockers.append({
            "requirement": "deployment_region",
            "status": "operator_input_required",
        })

    if not provider_checks[
        "provider_owner_approval_recorded"
    ]:
        blockers.append({
            "requirement": "provider_owner_approval",
            "status": "owner_approval_required",
        })

    if not runtime_ready:
        blockers.append({
            "requirement": "managed_staging_runtime_environment",
            "status": "runtime_environment_references_required",
        })

    report = {
        "schema_version": SCHEMA_VERSION,
        "runtime_ready": runtime_ready,
        "provider_inputs_complete": provider_inputs_complete,
        "authorization_review_ready": (
            runtime_ready
            and provider_inputs_complete
        ),
        "runtime_checks": runtime_checks,
        "provider_checks": provider_checks,
        "reference_presence": reference_presence,
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "provider_fingerprints": {
            "managed_host_provider_sha256": _fingerprint(
                source.get(
                    MANAGED_HOST_PROVIDER_ENV,
                    "",
                )
            ),
            "managed_host_account_or_team_sha256": _fingerprint(
                source.get(
                    MANAGED_HOST_ACCOUNT_OR_TEAM_ENV,
                    "",
                )
            ),
            "staging_deployment_region_sha256": _fingerprint(
                source.get(
                    STAGING_DEPLOYMENT_REGION_ENV,
                    "",
                )
            ),
        },
        "raw_values_returned": False,
        "provider_calls_authorized": False,
        "deployment_authorized": False,
    }
    report["report_hash"] = payload_hash(report)
    return report


def assert_managed_staging_environment(
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    report = evaluate_managed_staging_environment(
        environ
    )

    if not report["authorization_review_ready"]:
        names = [
            item["requirement"]
            for item in report[
                "blocking_requirements"
            ]
        ]
        raise RuntimeError(
            "Managed staging runtime failed closed. "
            "Unresolved requirements: "
            + ", ".join(names)
        )

    return report


def provider_capability_resolution() -> dict[str, Any]:
    resolution = {
        "schema_version": SCHEMA_VERSION,
        "topology": (
            "single_tower_fronted_managed_python_web_service"
        ),
        "provider_model": (
            "provider_neutral_composite_stack_allowed"
        ),
        "required_capabilities": [
            "managed Python web service",
            "provider supplied port binding",
            "HTTPS termination",
            "encrypted environment-secret store",
            "health checks",
            "deployment logs",
            "access logs",
            "manual deployment control",
            "rollback support",
            "managed PostgreSQL or compatible external PostgreSQL",
            "private S3-compatible object storage",
        ],
        "network_boundary": {
            "tower_is_only_browser_front_door": True,
            "observatory_separate_public_service": False,
            "observatory_separate_private_service_required_now": False,
            "observatory_routes_co_resident": True,
            "observatory_direct_anonymous_access_allowed": False,
            "future_service_split_allowed_without_boundary_change": True,
        },
        "selection_status": "operator_input_required",
        "provider_calls_authorized": False,
        "resources_created": False,
    }
    resolution["resolution_hash"] = payload_hash(
        resolution
    )
    return resolution


def dependency_graph() -> dict[str, Any]:
    graph = {
        "schema_version": SCHEMA_VERSION,
        "nodes": [
            {
                "id": "managed_wsgi",
                "path": "web/managed_staging.py",
                "role": "fail_closed_managed_wsgi_entrypoint",
            },
            {
                "id": "source_app",
                "path": "web/app.py",
                "role": "co_resident_tower_ob_flask_application",
            },
            {
                "id": "human_login",
                "path": "tower/tower_human_login_ob_launch.py",
                "role": "tower_identity_step_up_and_launch",
            },
            {
                "id": "native_gp046",
                "path": "tower/tower_ob_gp046_native_contract.py",
                "role": "native_protected_handoff_contract",
            },
            {
                "id": "walkthrough",
                "path": "tower/tower_observatory_walkthrough_web.py",
                "role": "protected_observatory_walkthrough_blueprint",
            },
        ],
        "edges": [
            {
                "from": "managed_wsgi",
                "to": "source_app",
                "relationship": "imports_after_environment_validation",
            },
            {
                "from": "source_app",
                "to": "human_login",
                "relationship": "registers_blueprint",
            },
            {
                "from": "source_app",
                "to": "walkthrough",
                "relationship": "registers_blueprint",
            },
            {
                "from": "human_login",
                "to": "native_gp046",
                "relationship": "builds_native_handoff",
            },
        ],
        "separate_observatory_process_discovered": False,
        "runtime_target": MANAGED_WSGI_TARGET,
    }
    graph["graph_hash"] = payload_hash(graph)
    return graph


def resolve_repository_runtime(
    repository_root: str | Path,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()

    paths = {
        "source_app": root / "web" / "app.py",
        "managed_wsgi": root / "web" / "managed_staging.py",
        "human_login": (
            root
            / "tower"
            / "tower_human_login_ob_launch.py"
        ),
        "native_gp046": (
            root
            / "tower"
            / "tower_ob_gp046_native_contract.py"
        ),
        "walkthrough": (
            root
            / "tower"
            / "tower_observatory_walkthrough_web.py"
        ),
    }

    text = {
        key: (
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
            if path.exists()
            else ""
        )
        for key, path in paths.items()
    }

    checks = {
        "source_app_exists": paths[
            "source_app"
        ].is_file(),
        "managed_wsgi_exists": paths[
            "managed_wsgi"
        ].is_file(),
        "human_login_exists": paths[
            "human_login"
        ].is_file(),
        "native_gp046_exists": paths[
            "native_gp046"
        ].is_file(),
        "walkthrough_exists": paths[
            "walkthrough"
        ].is_file(),
        "source_app_defines_flask_app": (
            "app = Flask(" in text["source_app"]
        ),
        "source_app_registers_human_login": (
            "register_tower_human_login(app)"
            in text["source_app"]
        ),
        "source_app_registers_walkthrough": (
            "tower_ob_walkthrough_bp"
            in text["source_app"]
            and "app.register_blueprint("
            in text["source_app"]
        ),
        "human_login_binds_native_gp046": (
            "build_native_gp046_handoff"
            in text["human_login"]
        ),
        "managed_wsgi_uses_runtime_factory": (
            "create_managed_staging_app"
            in text["managed_wsgi"]
        ),
        "managed_runtime_validates_before_source_import": (
            text["managed_wsgi"].find(
                "create_managed_staging_app"
            )
            >= 0
            and "from web.app import app"
            not in text["managed_wsgi"]
        ),
    }

    resolved = all(checks.values())

    contract = {
        "schema_version": SCHEMA_VERSION,
        "repository_root": str(root),
        "resolved": resolved,
        "checks": checks,
        "topology": (
            "single_tower_fronted_managed_python_web_service"
        ),
        "source_application_target": (
            SOURCE_APPLICATION_TARGET
        ),
        "managed_wsgi_target": MANAGED_WSGI_TARGET,
        "managed_start_command": (
            MANAGED_START_COMMAND
        ),
        "observatory_runtime_entrypoint": (
            MANAGED_WSGI_TARGET
        ),
        "observatory_runtime_mode": (
            "co_resident_behind_tower_boundary"
        ),
        "separate_observatory_service_required": False,
        "application_import_executed": False,
        "provider_calls_performed": False,
        "deployment_performed": False,
        "safety": {
            "tower_only_browser_front_door": True,
            "observatory_public_ingress_allowed": False,
            "broker_submission_enabled": False,
            "production_manual_live_authorized": False,
            "real_capital_movement_enabled": False,
            "direct_vault_upload_enabled": False,
            "live_auto_locked": True,
        },
    }
    contract["contract_hash"] = payload_hash(
        contract
    )
    return contract


def build_provider_authorization_packet(
    repository_root: str | Path,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    runtime = resolve_repository_runtime(
        repository_root
    )
    environment = (
        evaluate_managed_staging_environment(
            environ
        )
    )

    blockers = [
        item
        for item in environment[
            "blocking_requirements"
        ]
        if item["requirement"]
        != "managed_staging_runtime_environment"
    ]

    if not runtime["resolved"]:
        blockers.append({
            "requirement": "observatory_runtime_entrypoint",
            "status": "repository_resolution_required",
        })

    ready_for_review = (
        runtime["resolved"]
        and environment[
            "authorization_review_ready"
        ]
    )

    packet = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": (
            "managed_staging_provider_authorization_review"
        ),
        "runtime_contract_hash": (
            runtime["contract_hash"]
        ),
        "environment_report_hash": (
            environment["report_hash"]
        ),
        "runtime_resolved": runtime["resolved"],
        "managed_wsgi_target": (
            runtime["managed_wsgi_target"]
        ),
        "managed_start_command": (
            runtime["managed_start_command"]
        ),
        "provider_inputs_complete": (
            environment[
                "provider_inputs_complete"
            ]
        ),
        "runtime_environment_ready": (
            environment["runtime_ready"]
        ),
        "ready_for_separate_authorization_review": (
            ready_for_review
        ),
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(
            blockers
        ),
        "raw_provider_values_recorded": False,
        "raw_secrets_recorded": False,
        "provider_calls_authorized": False,
        "resource_creation_authorized": False,
        "deployment_authorized": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "deployment_performed": False,
        "final_decision": (
            "READY_FOR_SEPARATE_PROVIDER_PROVISIONING_AUTHORIZATION_REVIEW"
            if ready_for_review
            else "NO_GO_HOLD_PROVIDER_SELECTION_ACCOUNT_REGION_AND_OWNER_APPROVAL_REQUIRED"
        ),
    }
    packet["packet_hash"] = payload_hash(
        packet
    )
    return packet


def build_no_call_dry_run_plan(
    repository_root: str | Path,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    packet = build_provider_authorization_packet(
        repository_root,
        environ,
    )

    plan = {
        "schema_version": SCHEMA_VERSION,
        "plan_type": (
            "managed_staging_no_call_dry_run"
        ),
        "managed_wsgi_target": MANAGED_WSGI_TARGET,
        "command_template": MANAGED_START_COMMAND,
        "ordered_checks": [
            "verify provider capability match",
            "verify provider account or team ownership",
            "verify staging region",
            "verify environment references by presence only",
            "verify owner approval reference",
            "verify managed WSGI contract",
            "verify Tower-only ingress guard",
            "verify rollback and logs capability",
        ],
        "ordered_future_actions": [
            "create or select managed PostgreSQL",
            "create private object-storage namespace",
            "create provider secret references",
            "create one Tower-fronted staging web service",
            "bind database and storage references",
            "configure health checks and logs",
            "capture provider resource identifiers",
            "perform deployment verification without official walkthrough",
        ],
        "authorization_packet_hash": (
            packet["packet_hash"]
        ),
        "dry_run": True,
        "shell_invoked": False,
        "command_executed": False,
        "provider_api_invoked": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_created": False,
        "deployment_performed": False,
        "official_walkthrough_performed": False,
        "broker_submission_enabled": False,
        "production_manual_live_authorized": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }
    plan["plan_hash"] = payload_hash(plan)
    return plan


def configure_app_for_managed_staging(
    app: Any,
    environ: Mapping[str, str] | None = None,
) -> Any:
    source = os.environ if environ is None else environ
    report = assert_managed_staging_environment(
        source
    )

    app.secret_key = source[
        TOWER_SESSION_SECRET_ENV
    ]

    app.config.update({
        "ENV": "staging",
        "DEBUG": False,
        "TESTING": False,
        "PREFERRED_URL_SCHEME": "https",
        "SESSION_COOKIE_SECURE": True,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SIMPLEE_RUNTIME_TOPOLOGY": (
            "single_tower_fronted_service"
        ),
        "SIMPLEE_MANAGED_WSGI_TARGET": (
            MANAGED_WSGI_TARGET
        ),
        "SIMPLEE_RUNTIME_REPORT_HASH": (
            report["report_hash"]
        ),
    })

    return app


def install_tower_only_ingress_guard(
    app: Any,
) -> Any:
    """Guard co-resident Observatory paths in managed staging only."""

    extensions = getattr(app, "extensions", None)
    if extensions is None:
        extensions = {}
        app.extensions = extensions

    marker = "simplee_tower_only_ingress_guard"
    if extensions.get(marker):
        return app

    from flask import jsonify, redirect, request
    from tower.tower_human_login_ob_launch import (
        owner_session_active,
    )

    @app.before_request
    def _simplee_managed_staging_ob_ingress_guard():
        path = request.path or "/"

        protected = (
            path in PROTECTED_OB_EXACT_PATHS
            or any(
                path.startswith(prefix)
                for prefix in PROTECTED_OB_PREFIXES
            )
        )

        if not protected:
            return None

        if owner_session_active():
            return None

        if (
            path.endswith(".json")
            or request.accept_mimetypes.best
            == "application/json"
        ):
            return jsonify({
                "allowed": False,
                "reason_code": (
                    "tower_front_door_required"
                ),
                "tower_login": "/tower/login",
                "observatory_public_ingress": False,
            }), 403

        next_path = quote(
            request.full_path.rstrip("?"),
            safe="/?=&",
        )

        return redirect(
            f"/tower/login?next={next_path}"
        )

    extensions[marker] = True
    return app


def register_managed_health_route(
    app: Any,
) -> Any:
    extensions = getattr(app, "extensions", None)
    if extensions is None:
        extensions = {}
        app.extensions = extensions

    marker = "simplee_managed_health_route"
    if extensions.get(marker):
        return app

    from flask import jsonify

    existing_rules = {
        str(rule.rule)
        for rule in app.url_map.iter_rules()
    }

    if "/tower/healthz" not in existing_rules:
        def _simplee_managed_healthz():
            return jsonify({
                "ok": True,
                "service": "tower_ob_managed_staging",
                "topology": (
                    "single_tower_fronted_service"
                ),
                "observatory_public_ingress": False,
                "broker_submission_enabled": False,
                "production_manual_live_authorized": False,
                "live_auto_locked": True,
            })

        app.add_url_rule(
            "/tower/healthz",
            endpoint="simplee_managed_healthz",
            view_func=_simplee_managed_healthz,
            methods=["GET"],
        )

    extensions[marker] = True
    return app


def create_managed_staging_app(
    environ: Mapping[str, str] | None = None,
) -> Any:
    """Create the hosted WSGI application after fail-closed validation."""

    source = os.environ if environ is None else environ

    # This assertion intentionally occurs before importing the giant source app.
    assert_managed_staging_environment(
        source
    )

    from web.app import app as source_app

    configure_app_for_managed_staging(
        source_app,
        source,
    )
    install_tower_only_ingress_guard(
        source_app
    )
    register_managed_health_route(
        source_app
    )

    return source_app
