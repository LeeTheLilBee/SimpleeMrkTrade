#!/usr/bin/env python3
"""Offline operator worksheet generator for Tower-OB Steps 151-160.

This tool never calls Render, reads credentials, creates resources, builds, or
deploys. It writes only a non-secret operator-input template, a static
configuration preview, and a manifest outside the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tower.tower_ob_managed_staging_configuration_build_deployment import (
    BUILD_COMMAND,
    DEFAULT_PLAN,
    DEFAULT_REGION,
    DEPLOY_APPROVAL_PHRASE,
    FINAL_DECISION_HOLD,
    HEALTH_PATH,
    NEXT_BOUNDARY,
    PROVIDER_SLUG,
    RUNTIME_TARGET,
    SCHEMA_VERSION,
    SERVICE_NAME,
    SOURCE_BRANCH,
    START_COMMAND,
    canonical_json,
    payload_hash,
    render_api_contract,
)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=str(REPOSITORY_ROOT))
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--source-commit", default="")
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    output = Path(args.output_directory).resolve()
    if root == output or root in output.parents:
        raise SystemExit("Output directory must be outside the repository.")
    output.mkdir(parents=True, exist_ok=False)

    source_commit = str(args.source_commit).strip()
    operator_template = {
        "schema_version": SCHEMA_VERSION,
        "instructions": (
            "Store these values as private Colab secrets. Do not paste them into "
            "this JSON file or commit them to Git."
        ),
        "required_colab_secret_names": [
            "GITHUB_TOKEN",
            "RENDER_API_KEY",
            "SIMPLEE_STAGING_DEPLOY_APPROVAL",
            "TOWER_OWNER_USERNAME",
            "TOWER_OWNER_PASSWORD_HASH",
            "TOWER_OWNER_ID",
        ],
        "optional_colab_secret_names": [
            "RENDER_OWNER_ID",
            "SIMPLEE_STAGING_REGION",
            "SIMPLEE_STAGING_PLAN",
        ],
        "exact_deployment_approval_phrase": DEPLOY_APPROVAL_PHRASE,
        "default_region": DEFAULT_REGION,
        "default_plan": DEFAULT_PLAN,
        "secret_values_included": False,
    }
    preview = {
        "schema_version": SCHEMA_VERSION,
        "closed_layer": "MANAGED_STAGING_CONFIGURATION_BUILD_AND_DEPLOYMENT",
        "closed_through_step": 160,
        "next_boundary": NEXT_BOUNDARY,
        "final_decision": FINAL_DECISION_HOLD,
        "provider": PROVIDER_SLUG,
        "service_name": SERVICE_NAME,
        "source_branch": SOURCE_BRANCH,
        "source_commit": source_commit or None,
        "runtime_target": RUNTIME_TARGET,
        "build_command": BUILD_COMMAND,
        "start_command": START_COMMAND,
        "health_check_path": HEALTH_PATH,
        "provider_calls_performed": False,
        "provider_resource_created": False,
        "build_performed": False,
        "deployment_performed": False,
        "secret_values_included": False,
        "render_api_contract": render_api_contract(),
    }
    operator_path = output / "tower_ob_managed_staging_operator_inputs.template.json"
    preview_path = output / "tower_ob_managed_staging_configuration_deployment_preview.json"
    write_json(operator_path, operator_template)
    write_json(preview_path, preview)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "operator_input_template_path": str(operator_path),
        "configuration_deployment_preview_path": str(preview_path),
        "provider_calls_performed": False,
        "provider_resource_created": False,
        "build_performed": False,
        "deployment_performed": False,
        "secret_values_included": False,
    }
    manifest["manifest_hash"] = payload_hash(manifest)
    manifest_path = output / "worksheet_manifest.json"
    write_json(manifest_path, manifest)
    print(json.dumps({
        "operator_input_template_path": str(operator_path),
        "configuration_deployment_preview_path": str(preview_path),
        "manifest_path": str(manifest_path),
        "secret_values_included": False,
        "provider_calls_performed": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
