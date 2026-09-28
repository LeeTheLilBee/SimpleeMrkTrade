# SIMPLEE SOVEREIGN CLOUD — SC026 OWNER-SAFE ATOMIC LOCAL JOURNAL SNAPSHOT

Date: September 28, 2026. Stacked on merged SC025 `vault-dev` at `80d72d0d234435a7a454929b629cb0c2b9b8f5e0`. Source-only; **production NO_GO**.

## Why this matters

SC022 introduced useful acknowledged-primary/backup-match counts. The owner snapshot previously called `journal.health()` and `journal.source_backup_coverage()` separately, each opening and verifying the same local SQLite database at potentially different commit positions. If a different request committed between those two calls, the resulting owner card could show a primary-write count from one moment and a backup-coverage count from another.

SC026 adds `SQLiteOperationalJournal.source_owner_metrics()`, which explicitly begins one local SQLite read transaction, verifies the complete event/intent/backup/incident chain, derives both existing source health and exact backup coverage using that same connection/snapshot, and closes the transaction before returning. The original independent health and coverage methods remain available, with their health aggregation extracted into one shared helper to prevent divergent formulas. `owner_safe_source_snapshot()` and the SC021 evidence desk use this consistent combined result. The report displays safe aggregate numbers only, without entity, request, object, provider exception or document content. It remains non-authorizing.

The local source report carries `local_storage_point_in_time_consistent=True`; importantly `cross_ledger_point_in_time_certified=False`. Tower-shaped grant replay state is a DIFFERENT SQLite ledger, and local snapshots from two distinct DBs are not a real globally atomic Tower/Vault/Cloud decision. The SC020 signed storage/replay checkpoint is separately verifiable and the real external/latest independent custody remains an open release gate. An empty healthy local journal never means live provider health or production GO.

## Regression evidence

Tests check consistent acknowledged-primary and matching-backup counts, ensure owner reporting cannot revert to independently timed `health()` and `source_backup_coverage()` calls, attempt a second write during the owner report's health-to-coverage calculation and prove the first report retains one historical point-in-time snapshot while a subsequent report sees the new committed write, and reject a corrupted journal before any reassuring owner display.

No new workflow is added; the existing consolidated Vault/Cloud source suite tests the exact PR head. This is not hosted status polling, live provider monitoring, a cross-service database transaction, independent audit anchoring, owner alert delivery, a real Tower issuer/Vault authenticated receiver, paid deployment or production release.
