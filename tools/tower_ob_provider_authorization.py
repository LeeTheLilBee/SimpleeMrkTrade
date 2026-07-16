#!/usr/bin/env python3
"""Offline operator utility for Tower/Observatory provider authorization.

The utility writes blank worksheets or evaluates completed local worksheets. It
never logs into a provider, calls a provider API, creates resources, reads
secrets, or deploys the application.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tower.tower_ob_managed_staging_provider_authorization import (  # noqa: E402
    build_current_provider_authorization_state,
    write_bound_owner_decision_worksheet,
    write_json,
    write_operator_worksheets,
)


def _read_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare or evaluate Tower/Observatory managed-staging provider "
            "authorization worksheets without provider calls."
        )
    )
    parser.add_argument(
        "--write-worksheets",
        type=Path,
        help="Directory in which blank non-secret worksheets are written.",
    )
    parser.add_argument(
        "--write-owner-decision",
        type=Path,
        help=(
            "Write a challenge-bound owner-decision worksheet. Requires "
            "--provider-inputs with a complete valid provider worksheet."
        ),
    )
    parser.add_argument(
        "--provider-inputs",
        type=Path,
        help="Completed provider-input JSON worksheet.",
    )
    parser.add_argument(
        "--owner-decision",
        type=Path,
        help="Completed owner-decision JSON worksheet.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for a sanitized evaluation report.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=ROOT,
        help="Repository root; defaults to the parent of tools/.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository_root = args.repository_root.resolve()

    if args.write_worksheets:
        manifest = write_operator_worksheets(
            args.write_worksheets.resolve(),
            repository_root=repository_root,
        )
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0

    provider_inputs = _read_json(args.provider_inputs)

    if args.write_owner_decision:
        if args.provider_inputs is None:
            raise ValueError(
                "--write-owner-decision requires --provider-inputs."
            )
        path = write_bound_owner_decision_worksheet(
            args.write_owner_decision.resolve(),
            repository_root=repository_root,
            provider_inputs=provider_inputs,
        )
        print(json.dumps({
            "owner_decision_path": str(path),
            "contains_secret_values": False,
            "provider_calls_performed": False,
        }, indent=2, sort_keys=True))
        return 0

    owner_decision = _read_json(args.owner_decision)
    state = build_current_provider_authorization_state(
        repository_root,
        provider_inputs,
        owner_decision,
    )

    if args.output:
        write_json(args.output, state)

    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
