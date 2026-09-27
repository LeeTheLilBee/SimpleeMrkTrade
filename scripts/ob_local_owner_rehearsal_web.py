"""Explicit standalone local owner browser rehearsal; never a hosted app entrypoint.

Run from repo root:
python -m scripts.ob_local_owner_rehearsal_web --archive "$HOME/ob-private/reports"
Open http://127.0.0.1:8765/ on the same device.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from web.ob_local_owner_rehearsal_ui import create_local_owner_rehearsal_app
from web.ob_on_demand_simulation_session import SourceKind


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Separate LOCAL Proof/Demo historical/synthetic UI only. No Tower/broker grant.",
    )
    parser.add_argument("--archive", type=Path, required=True, help="Private local report directory")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--session-id", default="LOCAL-OWNER-WEB-REHEARSAL")
    parser.add_argument(
        "--source-kind", choices=("SYNTHETIC", "HISTORICAL"), default="SYNTHETIC",
    )
    args = parser.parse_args(argv)
    app = create_local_owner_rehearsal_app(
        archive=args.archive, port=args.port, session_id=args.session_id,
        source_kind=SourceKind(args.source_kind),
    )
    print(
        f"Local only: http://127.0.0.1:{args.port}/ | Proof/Demo synthetic units | "
        "NOT Tower authenticated and NOT live brokerage.",
        flush=True,
    )
    app.run(host="127.0.0.1", port=args.port, threaded=False, debug=False, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
