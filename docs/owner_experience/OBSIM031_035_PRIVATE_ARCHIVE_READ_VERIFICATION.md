# OBSIM031–035 — private archive read-back and final chain verification

Stacked on the refreshed owner-session draft [PR #50](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/50), brought forward to accepted `main@2b0c29eaa00a1587bf1386d5c22bd57829479edc` through the review branch's non-deploying reconciliation commit `7133f18d792ae7562487c83bcd4af6b34b96bd2e`. The ten existing PR #50 paths were absent from main and overlaid unchanged. There is no Tower or production route mutation.

## Problem and boundary

The local archive previously refused unsafe writes but read `[0-9][0-9][0-9][0-9].json` through ordinary `Path.open` without checking private directory/file permissions or refusing symlinked final files. It validated tick hashes and sequence but did not read/validate `_final.json` against the tick chain. A local report reader could therefore follow an unexpected report symlink or treat a tampered terminal summary as a valid closed session.

## Changes

- Local single-host private read checks root and session directory: no direct symlink and no group/other mode bits; missing archive is not an empty success. Opens report files with `O_NOFOLLOW` where supported and requires private regular files.
- Strict JSON parser refuses duplicate keys and non-finite constants; tick reports require contiguous sequence, checksum, simulation-only, no broker/capital/mode authority.
- `load_final` validates its hash, session, tick count, last tick receipt hash, final lane snapshot, and no broker/capital grants. `inspect_archive` distinguishes **INCOMPLETE_REPORT_ONLY** from **FINALIZED_REPORT_ONLY**; it never reconstructs a live session, Tower identity or external market proof.
- Existing OBSIM006–030 replay, OBTIME/CAPSIM policy, local no-clobber publication and 30-second cadence remain unchanged. This does not establish a multi-tenant adversarial filesystem or network-proof security boundary; owner-selected local storage is single-host best-effort.

## Acceptance / remaining

`tests/test_obsim031_035_private_archive_read_verification.py` verifies normal closed/partial archives, symlink and permission refusal, duplicate JSON keys, missing sequence, tampered final metadata even when rehashed, and forbidden authority flags even when rehashed. Run focused upstream OBSIM tests and full repository tests at exact branch head.

PR #50 remains draft until a real owner-facing locally active UI, explicit canonical source/decision input adapter, actual storage/owner walkthrough and Tower session/hosted review are separately demonstrated. Existing archive recovery is **report-only**; no live state, source authenticity, broker placement, capital transfer, real Manual Live, Hybrid or Auto. No paid infrastructure, production key, external data source or unattended scheduling.
