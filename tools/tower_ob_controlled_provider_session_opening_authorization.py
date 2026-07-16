"""Offline worksheet CLI for Steps 101-110.

This utility writes non-secret controlled provider-session opening authorization
worksheets outside the repository. It never opens a provider session, logs in,
performs provider calls, creates resources, registers or reads secrets, builds,
or deploys the application.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_authorization import (
    blank_current_inputs,
    write_session_opening_authorization_worksheets,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--output-directory", required=True)
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    values = blank_current_inputs(root)
    result = write_session_opening_authorization_worksheets(
        Path(args.output_directory).resolve(),
        repository_root=root,
        provider_inputs=values[0],
        provider_review_owner_decision=values[1],
        review_inputs=values[2],
        provisioning_decision=values[3],
        execution_preparation_inputs=values[4],
        execution_authorization_decision=values[5],
        controlled_session_preparation_inputs=values[6],
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
