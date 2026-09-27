"""Owner-started local terminal for synthetic/historical three-lane rehearsal.

No Tower login, server, data vendor, clock daemon, auto-input, broker or money.
Only an active person may submit a private, explicit JSON input when due.
Run from repository root: python -m scripts.ob_local_owner_rehearsal --archive PATH
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
from typing import Callable

from web.ob_explicit_owner_rehearsal_input import LocalOwnerRehearsalDesk
from web.ob_multi_simulation_harness import create_multi_simulation_harness
from web.ob_on_demand_simulation_session import (
    LocalSimulationReportStore, SourceKind, start_session,
)

MAX_INPUT_BYTES = 65536
REHEARSAL_ACCOUNT = "PROOF-DEMO"
SIMULATED_UNITS = 10000.0
HELP = "Commands: status | tick <private-json-file> | pause | resume | stop | exit | help"


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key in explicit rehearsal input")
        result[key] = value
    return result


def _bad_constant(_: str) -> object:
    raise ValueError("invalid nonfinite rehearsal JSON")


def read_private_rehearsal_input(path: Path) -> dict[str, object]:
    """Read an owner-chosen local fixture, never credentials or public data."""
    path = Path(path)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("symlinked rehearsal input forbidden")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        if path.is_symlink():
            raise ValueError("symlinked rehearsal input forbidden") from exc
        raise
    with os.fdopen(fd, "rb") as file:
        mode = os.fstat(file.fileno()).st_mode
        if not stat.S_ISREG(mode) or stat.S_IMODE(mode) & 0o077:
            raise ValueError("rehearsal input must be private regular file")
        raw = file.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("rehearsal input exceeds bounded local size")
    payload = json.loads(
        raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
        parse_constant=_bad_constant,
    )
    if type(payload) is not dict:
        raise ValueError("explicit rehearsal input must be JSON object")
    return payload


def run_local_owner_rehearsal(
    argv: list[str] | None = None, *,
    input_fn: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> int:
    parser = argparse.ArgumentParser(
        description="Private local OBSIM historical/synthetic owner rehearsal; no live trading."
    )
    parser.add_argument("--archive", type=Path, required=True, help="Owner-chosen private local report folder")
    parser.add_argument("--session-id", default="LOCAL-OWNER-REHEARSAL", help="New single-session ID")
    parser.add_argument(
        "--source-kind", choices=("SYNTHETIC", "HISTORICAL"), default="SYNTHETIC",
        help="Declared rehearsal source, not institution authentication",
    )
    args = parser.parse_args(argv)
    # PROOF-DEMO only, with clearly synthetic units. No option can bind real
    # mission accounts, financial resources or a production owner identity.
    harness = create_multi_simulation_harness(
        harness_id="OBSIM_LOCAL_OWNER_REHEARSAL",
        account_key=REHEARSAL_ACCOUNT,
        starting_capital=SIMULATED_UNITS,
        control_ref="CONTROL-FROZEN",
        integrated_ref="INTEGRATED-ACCEPTED",
        experimental_ref="EXPERIMENTAL-ISOLATED",
    )
    session = start_session(
        session_id=args.session_id, initial_harness=harness,
        source_kind=SourceKind(args.source_kind), now=clock(),
    )
    desk = LocalOwnerRehearsalDesk(session, LocalSimulationReportStore(args.archive))
    output(
        "The Observatory · LOCAL PRIVATE REHEARSAL | PROOF-DEMO only | "
        "10,000 simulated units | Tower owner identity NOT authenticated here | "
        "no real Manual Live or broker activity."
    )
    output(HELP)
    while True:
        try:
            command = input_fn("OB rehearsal > ").strip()
        except (EOFError, StopIteration):
            output("Local process ended; unfinalized reports remain INCOMPLETE_REPORT_ONLY.")
            return 0
        if command == "help":
            output(HELP)
        elif command == "status":
            state = desk.view(now=clock())
            due = state["due"]
            output(
                f'{state["state"]}; {state["accepted_ticks"]} accepted tick(s); '
                f'due={due["state"]}; seconds_remaining={due["due_in_seconds"]}; '
                "historical/synthetic source unverified; no broker or Manual Live."
            )
        elif command.startswith("tick "):
            try:
                payload = read_private_rehearsal_input(Path(command[5:].strip()))
                state = desk.submit_explicit_input(payload, now=clock())
            except (ValueError, OSError, UnicodeError, json.JSONDecodeError):
                output("Input rejected. No new report was accepted by this command.")
                continue
            output(
                f'Accepted simulated tick {state["accepted_ticks"]}; '
                f'report hash={state["last_report_hash"]}; no live authority.'
            )
        elif command == "pause":
            try:
                desk.pause()
                output("Paused. No due reports are backfilled.")
            except ValueError:
                output("Pause rejected; session remains unchanged.")
        elif command == "resume":
            try:
                desk.resume(now=clock())
                output("Resumed. A fresh 30-second interval is required.")
            except ValueError:
                output("Resume rejected; session remains unchanged.")
        elif command == "stop":
            try:
                archive = desk.stop(now=clock())
                output(
                    f'Closed: {archive["status"]}; {archive["tick_count"]} '
                    "source-labelled simulated reports; no session restored."
                )
            except (ValueError, OSError):
                output("Stop receipt not accepted; inspect the private archive before retry.")
                continue
            return 0
        elif command == "exit":
            output("Local process ended; if not stopped, archive is report-only/incomplete.")
            return 0
        else:
            output(HELP)


if __name__ == "__main__":
    raise SystemExit(run_local_owner_rehearsal())
