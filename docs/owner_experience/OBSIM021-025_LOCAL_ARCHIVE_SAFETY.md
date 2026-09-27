# OBSIM021–025 — zero-cost local report atomicity and privacy

This is a source-only follow-up to OBSIM016–020 in [PR #50](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/50). It does not add a production timer, owner login, broker interface, paid service or unattended reporting.

The previous local single-writer archive used a check-then-\`os.replace\` publication: a race could overwrite another same-name report. This pack uses same-directory temporary JSON with file fsync, then an atomic no-clobber hard-link publication, removes the temporary name and fsyncs the directory on POSIX. It denies symlinked final archive/session directories and refuses to silently weaken or change private directory permissions. The archive's owner-selected root/session directory must be 0700-like (no group/other permission). Source tests exercise duplicates, a simulated competing writer, symlink redirection, unsafe root permissions and previous simulation replay regressions.

Remaining owner UI, explicit 30-second caller, authentic market data source, local storage acceptance, complete provenance and Tower session authorization are still outstanding. Report-only recovery cannot restore live harness/positions. Simulation cannot unlock Manual Live, issue broker orders, or choose winners. Keep PR #50 draft until these distinct release checks are fulfilled.
