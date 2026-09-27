# OBSIM041–045 — active local terminal owner rehearsal (zero paid resources)

Stacked on [PR #50](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/50), after OBSIM031–035 and OBSIM036–040. **This is a local Python terminal surface, not a hosted Tower/OB beta route or an authenticated live account.**

The owner can explicitly start a local Proof/Demo-only historical/synthetic rehearsal, inspect due status, submit a *private pre-authored* JSON input once the next 30-second interval is due, pause, resume, stop and validate a local report-only archive. There is no daemon, hidden timer, provider polling, inferred decision, real balance, broker order, permission grant or paid resource. The terminal's 30-second rule is checked against the process clock only while the process is running and the human chooses `tick`; tab/process interruption is not backfilled. The existing canonical OBTIME/OBSIM/CAPSIM and single-writer 120-tick cap remain authoritative.

## Local trial

From the repository root in a local Python 3.11 environment with the existing dependencies:

```bash
mkdir -p "$HOME/ob-private"
chmod 700 "$HOME/ob-private"
cp examples/obsim_owner_synthetic_hold_example.json "$HOME/ob-private/owner-input.json"
chmod 600 "$HOME/ob-private/owner-input.json"
python -m scripts.ob_local_owner_rehearsal --archive "$HOME/ob-private/reports" --source-kind SYNTHETIC
```

The checked-in sample is an old **synthetic 2026-09-24 fixture** with owner-declared calendar and explicit HOLD decisions for Control, Integrated and Experimental. Its mark prices and 10,000 starting units are fictional; it is not a live price source or actual account balance. The sample file must be copied to an owner-private 0600 file because ordinary repository checkouts are generally readable by others. At the terminal prompt use `status`, wait for a due hint, then manually type `tick /path/to/owner-input.json`. `pause`, `resume`, `stop` and `exit` are explicit. `stop` stores a verified final report. `exit` without stop leaves any reports incomplete/report-only.

The local CLI intentionally accepts **only PROOF-DEMO**, and no argument can retarget a real mission account. It reads only a private regular input file with a bounded 64KiB JSON size, refuses a final-file symlink, duplicate keys and nonfinite JSON constants. The strict existing canonical envelope also refuses cross-account, unknown auth flags, unsafe time/price data, LIVE_OBSERVED, and Experimental OPEN/CLOSE without CAPSIM policy. Every successful tick is delegated to the accepted immutable source session, not a second simulation engine. Errors are reported without echoing private input.

## Gate still outstanding

This is runnable local **rehearsal**, not a deployed Observatory owner page. Before PR #50 can be accepted as a hosted owner-beta experience, a protected Tower→OB owner session, appropriate product UI integration, actual owner device/storage walkthrough and explicit source adapter acceptance must be tested at current runtime revision. A historical/synthetic self-declared fixture cannot prove broker/market provider data. Separate Manual Live/Tower/settlement/safety/Review Center/operator approvals remain HOLD. No Live, Hybrid, Automated, paywalled Render, permanent scheduler, broker API or capital movement is authorized.

Test: `tests/test_obsim041_045_local_terminal_owner_rehearsal.py` plus upstream source/time/archive suites and the full repository regression at exact PR head.
