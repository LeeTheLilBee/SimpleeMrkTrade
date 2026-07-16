"""Offline worksheet writer for Steps 091–100.

This utility writes non-secret controlled-session preparation worksheets outside
the repository. It does not authenticate to or call a provider.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_preparation import (
    blank_current_inputs,
    write_controlled_session_preparation_worksheets,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--repository-root", required=True)
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        _,
    ) = blank_current_inputs(root)
    result = write_controlled_session_preparation_worksheets(
        args.output_directory,
        repository_root=root,
        provider_inputs=provider,
        provider_review_owner_decision=review_owner,
        review_inputs=review,
        provisioning_decision=provisioning,
        execution_preparation_inputs=execution_preparation,
        execution_authorization_decision=execution_authorization,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
