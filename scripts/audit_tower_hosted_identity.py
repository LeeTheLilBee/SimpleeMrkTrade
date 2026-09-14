"""Audit active Tower host surfaces for retired environment identity."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


AUTHORITATIVE_FILES = (
    "web/hosted_tower.py",
    "deploy/hosted_tower/requirements.txt",
    "deploy/hosted_tower/start.sh",
    "tower/hosted_migration_contract.py",
    "tower/hosted_runtime_parity.py",
    "tower/ob_product_landing.py",
    "tower/tower_human_login_ob_launch.py",
    "scripts/verify_tower_hosted_live.py",
)


def retired_word() -> str:
    return "stag" + "ing"


def retired_token() -> str:
    return (
        "managed_"
        + retired_word()
    )


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )

    return [
        x
        for x in result.stdout.split("\0")
        if x
    ]


def audit() -> dict[str, object]:
    failures = []

    forbidden = (
        retired_token(),
        "web." + retired_token(),
        "deploy/" + retired_token(),
        "simplee-tower-ob-" + retired_word(),
    )

    for relative in AUTHORITATIVE_FILES:
        path = ROOT / relative

        if not path.is_file():
            failures.append(
                {
                    "path": relative,
                    "reason": "missing",
                }
            )
            continue

        text = path.read_text(
            encoding="utf-8"
        ).lower()

        hits = [
            fragment
            for fragment in forbidden
            if fragment.lower() in text
        ]

        if retired_word() in text:
            hits.append(
                retired_word()
            )

        if hits:
            failures.append(
                {
                    "path": relative,
                    "reason": "retired_identity",
                    "hits": sorted(
                        set(hits)
                    ),
                }
            )

    old_runtime = (
        ROOT
        / "web"
        / (
            retired_token()
            + ".py"
        )
    )

    old_deploy = (
        ROOT
        / "deploy"
        / retired_token()
    )

    if old_runtime.exists():
        failures.append(
            {
                "path": str(
                    old_runtime.relative_to(ROOT)
                ),
                "reason": "retired_runtime_exists",
            }
        )

    if old_deploy.exists():
        failures.append(
            {
                "path": str(
                    old_deploy.relative_to(ROOT)
                ),
                "reason": "retired_deploy_exists",
            }
        )

    return {
        "ok": not failures,
        "active_failures": failures,
    }


if __name__ == "__main__":
    result = audit()

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )

    if not result["ok"]:
        raise SystemExit(1)
