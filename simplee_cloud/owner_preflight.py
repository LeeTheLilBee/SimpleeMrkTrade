"""SC006C owner-friendly, text-only Cloud release preflight renderer.

This has no external app access, role inference, provider verification, network
call, CI success assertion or release switch. It renders the SC006 static HOLD
gate inventory for local review and optional GitHub Actions job summary.
"""
from __future__ import annotations

import argparse
import json

from .readiness import source_preflight


def owner_preflight_markdown() -> str:
    report = source_preflight()
    lines = [
        "# Simplee Sovereign Cloud — Owner Release Preflight",
        "",
        "**SOURCE ONLY · NO GO · NO HOSTED RECEIVER**",
        "",
        "The Cloud and Vault source modules can be tested independently. A merged PR, "
        "green CI check or pasted evidence reference does not prove a working secure "
        "provider, real Tower issuer, Vault receipt or disaster recovery.",
        "",
        "## Live activation remains blocked",
        "",
        "| Release control | Current condition |",
        "| --- | --- |",
        "| Live Tower/Vault issuer and private service transport | Not independently certified |",
        "| Real provider and retained encrypted backup | Not independently certified |",
        "| Vault canonical archival/recovery receipt | Not independently certified |",
        "| Owner infrastructure and production approval | Not recorded here |",
        "",
        "## Required independent verification",
        "",
    ]
    for index, gate in enumerate(report["gates"], start=1):
        lines.extend([
            f"### {index:02d} · {gate['title']}",
            "",
            f"**Owner:** {gate['owner']}  ",
            f"**Evidence required:** {gate['required_proof']}  ",
            "**State:** Review pending; not independently certified.",
            "",
        ])
    lines.extend([
        "## What happens next",
        "",
        "Tower and Vault must independently accept and implement the handoff "
        "in issue #99. Cloud then needs actual authenticated cross-service "
        "proofs, owner-approved provider controls, offsite audit/backup "
        "custody, recovery drills and owner release verification.",
        "",
        "**This report cannot and does not authorize production access, "
        "funding, provider selection or a Vault archival commit.**",
        "",
    ])
    return "\n".join(lines)


def owner_preflight_json() -> str:
    # Only non-sensitive fixed fields are emitted; reference pointers are
    # deliberately not taken from CLI arguments or environment variables.
    return json.dumps(source_preflight(), indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render source-only Cloud owner release HOLD report",
    )
    parser.add_argument("--format", choices=("markdown", "json"),
                        default="markdown")
    args = parser.parse_args(argv)
    print(
        owner_preflight_json() if args.format == "json"
        else owner_preflight_markdown(), end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
