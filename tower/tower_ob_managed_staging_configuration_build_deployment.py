"""Managed staging configuration, build, and deployment boundary.

This layer converts the repository-side staging shell into a real Render-backed
staging deployment while preserving Tower as the only browser front door.

Provider authentication and runtime secret values are accepted only at execution
time. They are never returned by state builders, written to evidence, committed
to Git, or included in operator worksheets.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

SCHEMA_VERSION = "simplee.tower_ob.managed_staging_configuration_build_deployment.v1"
SERVICE_NAME = "simplee-tower-ob-staging"
PROVIDER_SLUG = "render"
REPOSITORY_URL = "https://github.com/LeeTheLilBee/SimpleeMrkTrade.git"
SOURCE_BRANCH = "tower-ob-integration-dev"
RUNTIME_TARGET = "web.managed_staging:app"
BUILD_COMMAND = "pip install -r deploy/managed_staging/requirements.txt"
START_COMMAND = "deploy/managed_staging/start.sh"
HEALTH_PATH = "/tower/healthz"
DEFAULT_REGION = "virginia"
DEFAULT_PLAN = "free"
PYTHON_VERSION = "3.12.13"
SOURCE_COMMIT_BINDING = "explicit_render_deploy_endpoint_runtime_commit"
DEPLOY_APPROVAL_PHRASE = "DEPLOY SIMPLEE TOWER OB STAGING"
RENDER_API_BASE = "https://api.render.com/v1"
FINAL_DECISION_HOLD = "STAGING_CONFIGURATION_READY_HOLD_PROVIDER_CREDENTIALS_OR_DEPLOYMENT"
FINAL_DECISION_DEPLOYED = "MANAGED_STAGING_DEPLOYED_READY_FOR_OWNER_WALKTHROUGH"
NEXT_BOUNDARY = "managed_staging_verification_and_owner_walkthrough"

ALLOWED_REGIONS = frozenset({"frankfurt", "oregon", "ohio", "singapore", "virginia"})
ALLOWED_PLANS = frozenset({
    "free", "starter", "starter_plus", "standard", "standard_plus",
    "pro", "pro_plus", "pro_max", "pro_ultra",
})
TERMINAL_DEPLOY_STATUSES = frozenset({
    "live", "deactivated", "build_failed", "update_failed", "canceled",
    "pre_deploy_failed",
})
FAILED_DEPLOY_STATUSES = frozenset({
    "deactivated", "build_failed", "update_failed", "canceled",
    "pre_deploy_failed",
})
REQUIRED_OPERATOR_INPUT_NAMES = (
    "RENDER_API_KEY",
    "SIMPLEE_STAGING_DEPLOY_APPROVAL",
    "TOWER_OWNER_USERNAME",
    "TOWER_OWNER_PASSWORD_HASH",
    "TOWER_OWNER_ID",
)
OPTIONAL_OPERATOR_INPUT_NAMES = (
    "RENDER_OWNER_ID",
    "SIMPLEE_STAGING_REGION",
    "SIMPLEE_STAGING_PLAN",
)
SECRET_ENVIRONMENT_NAMES = frozenset({
    "RENDER_API_KEY",
    "GITHUB_TOKEN",
    "TOWER_SESSION_SECRET",
    "TOWER_OWNER_PASSWORD_HASH",
})
RUNTIME_ENVIRONMENT_NAMES = (
    "SIMPLEE_DEPLOYMENT_ENVIRONMENT",
    "TOWER_HOSTED_MODE",
    "SIMPLEE_MANAGED_HOST_PROVIDER",
    "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM",
    "SIMPLEE_STAGING_DEPLOYMENT_REGION",
    "SIMPLEE_PROVIDER_OWNER_APPROVAL",
    "TOWER_SESSION_SECRET",
    "TOWER_OWNER_USERNAME",
    "TOWER_OWNER_PASSWORD_HASH",
    "TOWER_OWNER_ID",
    "PYTHON_VERSION",
)
PREVIOUS_CHECKPOINT_RELATIVE = (
    "integration_checkpoints/20260717T002435Z_"
    "tower_ob_managed_staging_service_creation/resume_checkpoint.json"
)
DEPLOY_ROOT_RELATIVE = "deploy/managed_staging"

_RUNTIME_EXCLUDED_PARTS = frozenset({
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "tests", "tools", "integration_checkpoints",
})
_MANDATORY_REQUIREMENTS = {
    "Flask": "Flask>=3.1,<4",
    "Werkzeug": "Werkzeug>=3.1,<4",
    "gunicorn": "gunicorn>=23,<24",
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def payload_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def fingerprint(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _is_runtime_python_file(root: Path, path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    if any(part in _RUNTIME_EXCLUDED_PARTS for part in relative.parts):
        return False
    name = relative.name
    if name.startswith("test_") or name.endswith("_test.py"):
        return False
    return path.suffix == ".py"


def _local_top_level_names(root: Path) -> set[str]:
    names: set[str] = set()
    for child in root.iterdir():
        if child.name.startswith("."):
            continue
        if child.is_dir() and (child / "__init__.py").is_file():
            names.add(child.name)
        elif child.is_file() and child.suffix == ".py":
            names.add(child.stem)
    return names


def discover_top_level_imports(repository_root: str | Path) -> set[str]:
    root = Path(repository_root).resolve()
    found: set[str] = set()
    for path in root.rglob("*.py"):
        if not _is_runtime_python_file(root, path):
            continue
        try:
            parsed = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except (OSError, SyntaxError, UnicodeError):
            continue
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".", 1)[0])
    return found


def discover_requirement_lines(
    repository_root: str | Path,
    *,
    package_map: Mapping[str, Sequence[str]] | None = None,
    versions: Mapping[str, str] | None = None,
    stdlib_names: Iterable[str] | None = None,
) -> list[str]:
    root = Path(repository_root).resolve()
    imports = discover_top_level_imports(root)
    local_names = _local_top_level_names(root)
    stdlib = set(sys.stdlib_module_names if stdlib_names is None else stdlib_names)
    mapping = (
        importlib.metadata.packages_distributions()
        if package_map is None
        else {str(key): list(value) for key, value in package_map.items()}
    )
    resolved_versions = dict(versions or {})
    distributions: set[str] = set()

    for name in imports:
        if name in stdlib or name in local_names:
            continue
        for distribution in mapping.get(name, ()):
            distributions.add(distribution)

    distributions.update(_MANDATORY_REQUIREMENTS)

    lines: list[str] = []
    for distribution in sorted(distributions, key=str.lower):
        if distribution in _MANDATORY_REQUIREMENTS and distribution not in resolved_versions:
            try:
                resolved_versions[distribution] = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                lines.append(_MANDATORY_REQUIREMENTS[distribution])
                continue
        version = resolved_versions.get(distribution)
        if version is None:
            try:
                version = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                continue
        lines.append(f"{distribution}=={version}")

    # Deduplicate case-insensitively while preserving deterministic order.
    deduplicated: dict[str, str] = {}
    for line in lines:
        name = re.split(r"[<>=!~]", line, maxsplit=1)[0].strip().lower()
        deduplicated[name] = line
    return [deduplicated[key] for key in sorted(deduplicated)]


def requirements_text(lines: Sequence[str]) -> str:
    clean = [str(line).strip() for line in lines if str(line).strip()]
    return (
        "# Generated by Steps 151-160 from runtime imports and installed distributions.\n"
        "# Staging only. No credentials or environment values are stored here.\n"
        + "\n".join(clean)
        + "\n"
    )


def render_blueprint_text() -> str:
    return """# Tower-OB managed staging service. Staging only.
services:
  - type: web
    name: simplee-tower-ob-staging
    runtime: python
    plan: free
    region: virginia
    branch: tower-ob-integration-dev
    autoDeploy: false
    buildCommand: pip install -r deploy/managed_staging/requirements.txt
    startCommand: deploy/managed_staging/start.sh
    healthCheckPath: /tower/healthz
    envVars:
      - key: SIMPLEE_DEPLOYMENT_ENVIRONMENT
        value: staging
      - key: TOWER_HOSTED_MODE
        value: "true"
      - key: SIMPLEE_MANAGED_HOST_PROVIDER
        value: render
      - key: SIMPLEE_STAGING_DEPLOYMENT_REGION
        value: virginia
      - key: SIMPLEE_PROVIDER_OWNER_APPROVAL
        value: APPROVED
      - key: TOWER_SESSION_SECRET
        sync: false
      - key: TOWER_OWNER_USERNAME
        sync: false
      - key: TOWER_OWNER_PASSWORD_HASH
        sync: false
      - key: TOWER_OWNER_ID
        sync: false
"""


def render_api_contract() -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "provider": PROVIDER_SLUG,
        "api_base": RENDER_API_BASE,
        "service_create": {"method": "POST", "path": "/services"},
        "service_list": {"method": "GET", "path": "/services"},
        "service_update": {"method": "PATCH", "path": "/services/{service_id}"},
        "environment_variable_update": {
            "method": "PUT",
            "path": "/services/{service_id}/env-vars/{key}",
        },
        "deploy_trigger": {
            "method": "POST",
            "path": "/services/{service_id}/deploys",
        },
        "deploy_list": {
            "method": "GET",
            "path": "/services/{service_id}/deploys",
        },
        "service_health": {
            "method": "GET",
            "path": HEALTH_PATH,
        },
        "authentication": "bearer_token_runtime_only",
        "token_in_arguments": False,
        "token_in_git": False,
        "token_in_evidence": False,
        "database_endpoint_used": False,
        "object_storage_endpoint_used": False,
        "dns_endpoint_used": False,
    }
    payload["contract_hash"] = payload_hash(payload)
    return payload


def deployment_contract(
    source_commit: str,
    requirements_sha256: str,
    *,
    region: str = DEFAULT_REGION,
    plan: str = DEFAULT_PLAN,
) -> dict[str, Any]:
    region = _safe_text(region).lower() or DEFAULT_REGION
    plan = _safe_text(plan).lower() or DEFAULT_PLAN
    payload = {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "provider": PROVIDER_SLUG,
        "repository_url": REPOSITORY_URL,
        "source_branch": SOURCE_BRANCH,
        "source_commit": _safe_text(source_commit),
        "runtime": "python",
        "python_version": PYTHON_VERSION,
        "plan": plan,
        "region": region,
        "auto_deploy": False,
        "build_command": BUILD_COMMAND,
        "start_command": START_COMMAND,
        "runtime_target": RUNTIME_TARGET,
        "health_check_path": HEALTH_PATH,
        "requirements_sha256": _safe_text(requirements_sha256),
        "service_count": 1,
        "database_creation_allowed": False,
        "object_storage_creation_allowed": False,
        "dns_change_allowed": False,
        "production_deployment_allowed": False,
        "manual_live_allowed": False,
        "broker_submission_allowed": False,
        "real_capital_movement_allowed": False,
        "live_auto_locked": True,
    }
    payload["contract_hash"] = payload_hash(payload)
    return payload


def expected_static_file_payloads(source_commit: str, requirements_sha256: str) -> dict[str, str]:
    # The repository cannot embed the hash of the commit that contains this file
    # without creating a circular hash dependency. The exact source commit is
    # therefore bound at the explicit Render deploy request and recorded in the
    # provider deployment receipt.
    contract = deployment_contract(SOURCE_COMMIT_BINDING, requirements_sha256)
    contract["runtime_source_commit_required"] = True
    contract["runtime_source_commit_reference"] = SOURCE_COMMIT_BINDING
    contract["contract_hash"] = payload_hash({k: v for k, v in contract.items() if k != "contract_hash"})
    readme = (
        "# Managed Staging Configuration, Build, and Deployment\n\n"
        "Steps 151–160 configure and deploy one Render-backed Tower-fronted staging "
        "web service from `tower-ob-integration-dev`. Runtime secrets are supplied "
        "only through the provider secret store. Production, DNS, database, object "
        "storage, broker submission, real capital movement, and Live Auto remain "
        "locked. The deployment is manual and pinned to a specific source commit.\n"
    )
    return {
        "render.yaml": render_blueprint_text(),
        f"{DEPLOY_ROOT_RELATIVE}/deployment_contract.json": (
            json.dumps(contract, indent=2, sort_keys=True) + "\n"
        ),
        f"{DEPLOY_ROOT_RELATIVE}/render_api_contract.json": (
            json.dumps(render_api_contract(), indent=2, sort_keys=True) + "\n"
        ),
        f"{DEPLOY_ROOT_RELATIVE}/DEPLOYMENT.md": readme,
    }


def validate_operator_inputs(values: Mapping[str, Any]) -> dict[str, Any]:
    presence = {
        name: bool(_safe_text(values.get(name)))
        for name in (*REQUIRED_OPERATOR_INPUT_NAMES, *OPTIONAL_OPERATOR_INPUT_NAMES)
    }
    region = _safe_text(values.get("SIMPLEE_STAGING_REGION")).lower() or DEFAULT_REGION
    plan = _safe_text(values.get("SIMPLEE_STAGING_PLAN")).lower() or DEFAULT_PLAN
    checks = {
        "render_api_key_present": presence["RENDER_API_KEY"],
        "deployment_approval_exact": (
            _safe_text(values.get("SIMPLEE_STAGING_DEPLOY_APPROVAL"))
            == DEPLOY_APPROVAL_PHRASE
        ),
        "tower_owner_username_present": presence["TOWER_OWNER_USERNAME"],
        "tower_owner_password_hash_present": presence["TOWER_OWNER_PASSWORD_HASH"],
        "tower_owner_password_appears_hashed": (
            ":" in _safe_text(values.get("TOWER_OWNER_PASSWORD_HASH"))
            and len(_safe_text(values.get("TOWER_OWNER_PASSWORD_HASH"))) >= 20
        ),
        "tower_owner_id_present": presence["TOWER_OWNER_ID"],
        "region_allowed": region in ALLOWED_REGIONS,
        "plan_allowed": plan in ALLOWED_PLANS,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    report = {
        "schema_version": SCHEMA_VERSION,
        "valid": not blockers,
        "checks": checks,
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "region": region,
        "plan": plan,
        "render_owner_id_present": presence["RENDER_OWNER_ID"],
        "secret_values_returned": False,
        "api_key_fingerprint": fingerprint(values.get("RENDER_API_KEY")),
        "owner_username_fingerprint": fingerprint(values.get("TOWER_OWNER_USERNAME")),
        "owner_password_hash_fingerprint": fingerprint(values.get("TOWER_OWNER_PASSWORD_HASH")),
        "owner_id_fingerprint": fingerprint(values.get("TOWER_OWNER_ID")),
    }
    report["report_hash"] = payload_hash(report)
    return report


def runtime_env_vars(
    owner_id: str,
    values: Mapping[str, Any],
    *,
    region: str = DEFAULT_REGION,
) -> list[dict[str, Any]]:
    return [
        {"key": "SIMPLEE_DEPLOYMENT_ENVIRONMENT", "value": "staging"},
        {"key": "TOWER_HOSTED_MODE", "value": "true"},
        {"key": "SIMPLEE_MANAGED_HOST_PROVIDER", "value": PROVIDER_SLUG},
        {"key": "SIMPLEE_MANAGED_HOST_ACCOUNT_OR_TEAM", "value": owner_id},
        {"key": "SIMPLEE_STAGING_DEPLOYMENT_REGION", "value": region},
        {"key": "SIMPLEE_PROVIDER_OWNER_APPROVAL", "value": "APPROVED"},
        {"key": "TOWER_SESSION_SECRET", "generateValue": True},
        {"key": "TOWER_OWNER_USERNAME", "value": _safe_text(values.get("TOWER_OWNER_USERNAME"))},
        {"key": "TOWER_OWNER_PASSWORD_HASH", "value": _safe_text(values.get("TOWER_OWNER_PASSWORD_HASH"))},
        {"key": "TOWER_OWNER_ID", "value": _safe_text(values.get("TOWER_OWNER_ID"))},
        {"key": "PYTHON_VERSION", "value": PYTHON_VERSION},
    ]


def build_render_service_payload(
    owner_id: str,
    source_commit: str,
    values: Mapping[str, Any],
    *,
    region: str = DEFAULT_REGION,
    plan: str = DEFAULT_PLAN,
) -> dict[str, Any]:
    payload = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": REPOSITORY_URL,
        "autoDeploy": "no",
        "branch": SOURCE_BRANCH,
        "envVars": runtime_env_vars(owner_id, values, region=region),
        "serviceDetails": {
            "runtime": "python",
            "plan": plan,
            "region": region,
            "numInstances": 1,
            "healthCheckPath": HEALTH_PATH,
            "envSpecificDetails": {
                "buildCommand": BUILD_COMMAND,
                "startCommand": START_COMMAND,
            },
        },
    }
    # Render's create-service payload does not accept commitId. The exact commit
    # is supplied to the explicit deploy endpoint after service configuration.
    payload["_sourceCommitForExplicitDeploy"] = source_commit
    return payload


def build_render_service_patch(
    *,
    region: str = DEFAULT_REGION,
    plan: str = DEFAULT_PLAN,
) -> dict[str, Any]:
    return {
        "autoDeploy": "no",
        "repo": REPOSITORY_URL,
        "branch": SOURCE_BRANCH,
        "name": SERVICE_NAME,
        "serviceDetails": {
            "runtime": "python",
            "plan": plan,
            "healthCheckPath": HEALTH_PATH,
            "envSpecificDetails": {
                "buildCommand": BUILD_COMMAND,
                "startCommand": START_COMMAND,
            },
        },
    }


def sanitize_provider_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(token in lowered for token in (
                "token", "password", "secret", "cookie", "authorization",
                "api_key", "apikey",
            )):
                result[str(key)] = "<redacted>"
            elif lowered == "envvars" and isinstance(item, Sequence):
                result[str(key)] = [
                    {
                        "key": _safe_text(entry.get("key")) if isinstance(entry, Mapping) else "",
                        "value": "<redacted>" if isinstance(entry, Mapping) and "value" in entry else None,
                        "generateValue": bool(entry.get("generateValue")) if isinstance(entry, Mapping) and "generateValue" in entry else None,
                    }
                    for entry in item
                ]
            else:
                result[str(key)] = sanitize_provider_payload(item)
        return result
    if isinstance(value, list):
        return [sanitize_provider_payload(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_provider_payload(item) for item in value]
    text = str(value) if isinstance(value, str) else value
    if isinstance(text, str):
        text = re.sub(r"\b(?:rnd|ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_-]{16,}\b", "<redacted>", text)
        text = re.sub(r"Bearer\s+\S+", "Bearer <redacted>", text, flags=re.I)
    return text


class RenderAPIError(RuntimeError):
    def __init__(self, status: int, message: str, payload: Any = None):
        super().__init__(f"Render API request failed ({status}): {message}")
        self.status = int(status)
        self.payload = sanitize_provider_payload(payload)


Transport = Callable[[str, str, Any | None], tuple[int, Any]]


class RenderAPIClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = RENDER_API_BASE,
        timeout: float = 30.0,
        transport: Transport | None = None,
    ):
        if not _safe_text(api_key):
            raise ValueError("Render API key is required.")
        self._api_key = str(api_key)
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.transport = transport

    def request_json(
        self,
        method: str,
        path: str,
        payload: Any | None = None,
    ) -> Any:
        if self.transport is not None:
            status, response = self.transport(method.upper(), path, payload)
            if not 200 <= int(status) < 300:
                raise RenderAPIError(int(status), "transport error", response)
            return response

        url = self.base_url + (path if path.startswith("/") else "/" + path)
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method.upper(),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Simplee-Tower-OB-Staging/151-160",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                if not body:
                    return None
                return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"message": raw[:1000]}
            message = (
                parsed.get("message")
                if isinstance(parsed, Mapping)
                else "HTTP error"
            )
            raise RenderAPIError(exc.code, _safe_text(message) or "HTTP error", parsed) from None
        except urllib.error.URLError as exc:
            raise RenderAPIError(0, f"network error: {exc.reason}") from None

    def list_workspaces(self) -> list[dict[str, Any]]:
        response = self.request_json("GET", "/owners?limit=100") or []
        records: list[dict[str, Any]] = []
        for item in response if isinstance(response, list) else []:
            owner = item.get("owner", item) if isinstance(item, Mapping) else {}
            if isinstance(owner, Mapping):
                records.append(dict(owner))
        return records

    def list_named_services(self, owner_id: str) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode([
            ("ownerId", owner_id),
            ("name", SERVICE_NAME),
            ("type", "web_service"),
            ("includePreviews", "false"),
            ("limit", "100"),
        ])
        response = self.request_json("GET", f"/services?{query}") or []
        records: list[dict[str, Any]] = []
        for item in response if isinstance(response, list) else []:
            service = item.get("service", item) if isinstance(item, Mapping) else {}
            if isinstance(service, Mapping):
                records.append(dict(service))
        return records

    def create_service(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        clean = dict(payload)
        clean.pop("_sourceCommitForExplicitDeploy", None)
        response = self.request_json("POST", "/services", clean)
        service = response.get("service", response) if isinstance(response, Mapping) else {}
        if not isinstance(service, Mapping):
            raise RenderAPIError(500, "create service response did not contain a service")
        return dict(service)

    def update_service(self, service_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        response = self.request_json("PATCH", f"/services/{service_id}", dict(payload))
        service = response.get("service", response) if isinstance(response, Mapping) else {}
        return dict(service) if isinstance(service, Mapping) else {}

    def update_env_var(self, service_id: str, entry: Mapping[str, Any]) -> Any:
        key = urllib.parse.quote(_safe_text(entry.get("key")), safe="")
        body = (
            {"generateValue": True}
            if bool(entry.get("generateValue"))
            else {"value": _safe_text(entry.get("value"))}
        )
        return self.request_json(
            "PUT",
            f"/services/{service_id}/env-vars/{key}",
            body,
        )

    def trigger_deploy(self, service_id: str, source_commit: str) -> dict[str, Any]:
        response = self.request_json(
            "POST",
            f"/services/{service_id}/deploys",
            {
                "clearCache": "do_not_clear",
                "commitId": source_commit,
            },
        )
        deploy = response.get("deploy", response) if isinstance(response, Mapping) else {}
        if not isinstance(deploy, Mapping):
            raise RenderAPIError(500, "deploy response did not contain a deploy")
        return dict(deploy)

    def list_deploys(self, service_id: str) -> list[dict[str, Any]]:
        response = self.request_json(
            "GET",
            f"/services/{service_id}/deploys?limit=100",
        ) or []
        records: list[dict[str, Any]] = []
        for item in response if isinstance(response, list) else []:
            deploy = item.get("deploy", item) if isinstance(item, Mapping) else {}
            if isinstance(deploy, Mapping):
                records.append(dict(deploy))
        return records


def choose_workspace(
    workspaces: Sequence[Mapping[str, Any]],
    explicit_owner_id: str = "",
) -> dict[str, Any]:
    explicit = _safe_text(explicit_owner_id)
    if explicit:
        matches = [item for item in workspaces if _safe_text(item.get("id")) == explicit]
        if len(matches) != 1:
            raise RuntimeError("Configured RENDER_OWNER_ID is not uniquely accessible.")
        return dict(matches[0])
    if len(workspaces) != 1:
        raise RuntimeError(
            "RENDER_OWNER_ID is required when the API key can access "
            f"{len(workspaces)} workspaces."
        )
    return dict(workspaces[0])


def validate_existing_service(service: Mapping[str, Any], owner_id: str) -> dict[str, Any]:
    details = service.get("serviceDetails", {}) if isinstance(service.get("serviceDetails"), Mapping) else {}
    owner = service.get("owner", {}) if isinstance(service.get("owner"), Mapping) else {}
    checks = {
        "name_matches": _safe_text(service.get("name")) == SERVICE_NAME,
        "owner_matches": (
            _safe_text(owner.get("id") or service.get("ownerId")) == owner_id
        ),
        "type_is_web_service": _safe_text(service.get("type")) in {"web_service", "web"},
        "repo_matches": _safe_text(service.get("repo")) in {"", REPOSITORY_URL},
        "branch_matches": _safe_text(service.get("branch")) in {"", SOURCE_BRANCH},
        "runtime_matches": _safe_text(details.get("runtime")) in {"", "python"},
    }
    report = {
        "valid": all(checks.values()),
        "checks": checks,
        "service_id": _safe_text(service.get("id")),
        "service_url": _safe_text(details.get("url") or service.get("url")),
    }
    report["report_hash"] = payload_hash(report)
    return report


def poll_deploy(
    client: RenderAPIClient,
    service_id: str,
    deploy_id: str,
    *,
    timeout_seconds: float = 1200.0,
    interval_seconds: float = 10.0,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    deadline = monotonic() + timeout_seconds
    last: dict[str, Any] = {}
    while monotonic() <= deadline:
        deployments = client.list_deploys(service_id)
        match = next(
            (item for item in deployments if _safe_text(item.get("id")) == deploy_id),
            None,
        )
        if match is not None:
            last = dict(match)
            status = _safe_text(last.get("status"))
            if status in TERMINAL_DEPLOY_STATUSES:
                return last
        sleep(interval_seconds)
    raise TimeoutError(
        "Timed out waiting for Render deploy to reach a terminal status. "
        f"Last status: {_safe_text(last.get('status')) or 'unknown'}"
    )


def health_check(
    service_url: str,
    *,
    timeout: float = 20.0,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    base = _safe_text(service_url).rstrip("/")
    if not base.startswith("https://"):
        raise ValueError("Staging service URL must use HTTPS.")
    url = base + HEALTH_PATH
    open_url = urllib.request.urlopen if opener is None else opener
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "Simplee-Tower-OB-Health/151-160"},
    )
    with open_url(request, timeout=timeout) as response:
        status = int(getattr(response, "status", 200))
        payload = json.loads(response.read().decode("utf-8"))
    ok = status == 200 and payload.get("ok") is True
    result = {
        "ok": ok,
        "status_code": status,
        "health_url": url,
        "raw_body_returned": False,
    }
    result["receipt_hash"] = payload_hash(result)
    return result


def provider_binding_record(
    *,
    workspace: Mapping[str, Any],
    service: Mapping[str, Any],
    deploy: Mapping[str, Any],
    source_commit: str,
    region: str,
    plan: str,
    health: Mapping[str, Any],
) -> dict[str, Any]:
    details = service.get("serviceDetails", {}) if isinstance(service.get("serviceDetails"), Mapping) else {}
    service_id = _safe_text(service.get("id"))
    service_url = _safe_text(details.get("url") or service.get("url"))
    deploy_id = _safe_text(deploy.get("id"))
    status = _safe_text(deploy.get("status"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "provider": PROVIDER_SLUG,
        "service_name": SERVICE_NAME,
        "workspace_id_ref": _safe_text(workspace.get("id")),
        "workspace_name": _safe_text(workspace.get("name")),
        "service_id_ref": service_id,
        "service_url_ref": service_url,
        "deploy_id_ref": deploy_id,
        "deploy_status": status,
        "source_commit": source_commit,
        "source_branch": SOURCE_BRANCH,
        "region": region,
        "plan": plan,
        "runtime_target": RUNTIME_TARGET,
        "health_check": dict(health),
        "workspace_id_fingerprint": fingerprint(workspace.get("id")),
        "service_id_fingerprint": fingerprint(service_id),
        "deploy_id_fingerprint": fingerprint(deploy_id),
        "api_key_included": False,
        "secret_values_included": False,
        "database_created": False,
        "object_storage_created": False,
        "dns_changed": False,
        "production_resource_created": False,
    }
    payload["record_hash"] = payload_hash(payload)
    return payload


def build_configuration_deployment_state(
    repository_root: str | Path,
    *,
    source_commit: str,
    requirements_sha256: str,
    provider_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    previous_path = root / PREVIOUS_CHECKPOINT_RELATIVE
    previous_ready = False
    if previous_path.is_file():
        try:
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
        previous_ready = (
            previous.get("closed_through_step") == 150
            and previous.get("service_shell_created") is True
        )
    files = expected_static_file_payloads(source_commit, requirements_sha256)
    checks = {
        relative: (root / relative).is_file()
        and (root / relative).read_text(encoding="utf-8") == content
        for relative, content in files.items()
    }
    requirements_path = root / DEPLOY_ROOT_RELATIVE / "requirements.txt"
    requirements_ready = (
        requirements_path.is_file()
        and hashlib.sha256(requirements_path.read_bytes()).hexdigest() == requirements_sha256
    )
    provider = dict(provider_record or {})
    deployed = (
        _safe_text(provider.get("deploy_status")) == "live"
        and bool((provider.get("health_check") or {}).get("ok"))
        and _safe_text(provider.get("source_commit")) == source_commit
    )
    blockers: list[str] = []
    if not previous_ready:
        blockers.append("step150_service_shell_handoff")
    if not all(checks.values()):
        blockers.append("deployment_configuration_files")
    if not requirements_ready:
        blockers.append("staging_requirements_manifest")
    if not deployed:
        blockers.append("render_deployment_and_health")
    state = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONFIGURATION_BUILD_AND_DEPLOYMENT",
        "closed_through_step": 160,
        "next_boundary": NEXT_BOUNDARY,
        "service_name": SERVICE_NAME,
        "runtime_target": RUNTIME_TARGET,
        "runtime_topology": "single_tower_fronted_managed_python_web_service",
        "step150_handoff_ready": previous_ready,
        "configuration_files_ready": all(checks.values()),
        "requirements_ready": requirements_ready,
        "local_build_validation_performed": True,
        "provider_binding_complete": deployed,
        "provider_resource_created_or_reused": deployed,
        "provider_calls_performed": deployed,
        "build_performed": deployed,
        "deployment_performed": deployed,
        "health_check_passed": deployed,
        "database_created": False,
        "object_storage_created": False,
        "dns_changed": False,
        "production_resource_created": False,
        "official_walkthrough_performed": False,
        "blocking_requirements": blockers,
        "blocking_requirement_count": len(blockers),
        "final_decision": (
            FINAL_DECISION_DEPLOYED if deployed else FINAL_DECISION_HOLD
        ),
        "provider_record": provider if deployed else {},
        "secret_values_included": False,
    }
    state["state_hash"] = payload_hash(state)
    return state


def build_step_evidence(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    names = {
        151: "step150_handoff_and_render_provider_binding",
        152: "staging_dependency_manifest_and_python_runtime",
        153: "render_blueprint_and_api_contract",
        154: "local_build_and_runtime_import_validation",
        155: "deployment_configuration_commit_and_push",
        156: "render_workspace_and_duplicate_service_preflight",
        157: "one_tower_fronted_service_create_or_reuse",
        158: "runtime_environment_secret_registration",
        159: "commit_pinned_build_deploy_and_health_check",
        160: "managed_staging_deployment_closeout",
    }
    records: list[dict[str, Any]] = []
    previous_hash = ""
    for step in range(151, 161):
        record = {
            "schema_version": SCHEMA_VERSION,
            "step_number": step,
            "step_name": names[step],
            "previous_receipt_hash": previous_hash,
            "service_name": SERVICE_NAME,
            "runtime_target": RUNTIME_TARGET,
            "provider": PROVIDER_SLUG,
            "deployment_performed": bool(state.get("deployment_performed")) if step >= 159 else False,
            "provider_calls_performed": bool(state.get("provider_calls_performed")) if step >= 156 else False,
            "database_created": False,
            "object_storage_created": False,
            "dns_changed": False,
            "production_resource_created": False,
            "secret_values_included": False,
            "final_decision": state.get("final_decision") if step == 160 else None,
        }
        record["receipt_hash"] = payload_hash(record)
        previous_hash = record["receipt_hash"]
        records.append(record)
    return records
