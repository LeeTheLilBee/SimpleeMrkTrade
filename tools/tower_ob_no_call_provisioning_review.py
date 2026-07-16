#!/usr/bin/env python3
"""Offline utility for Tower/Observatory no-call provisioning review worksheets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tower.tower_ob_managed_staging_no_call_provisioning_review import (
    build_current_no_call_provisioning_review_state,
    write_no_call_review_worksheets,
)


def _load_json(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or inspect non-secret Tower/Observatory no-call "
            "provider-provisioning review worksheets."
        )
    )
    parser.add_argument(
        "--repository-root",
        default=str(ROOT),
        help="Repository root. Defaults to the parent of tools/.",
    )
    parser.add_argument(
        "--write-worksheets",
        help="Output directory for blank offline review worksheets.",
    )
    parser.add_argument("--provider-inputs")
    parser.add_argument("--owner-decision")
    parser.add_argument("--review-inputs")
    parser.add_argument(
        "--print-state",
        action="store_true",
        help="Print the current fail-closed review state.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository_root = Path(args.repository_root).resolve()
    provider_inputs = _load_json(args.provider_inputs)
    owner_decision = _load_json(args.owner_decision)
    review_inputs = _load_json(args.review_inputs)

    emitted = False
    if args.write_worksheets:
        result = write_no_call_review_worksheets(
            args.write_worksheets,
            repository_root=repository_root,
            provider_inputs=provider_inputs,
            owner_decision=owner_decision,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        emitted = True

    if args.print_state:
        state = build_current_no_call_provisioning_review_state(
            repository_root,
            provider_inputs,
            owner_decision,
            review_inputs,
        )
        print(json.dumps(state, indent=2, sort_keys=True))
        emitted = True

    if not emitted:
        raise SystemExit(
            "Choose --write-worksheets or --print-state."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
