
from engine.ledger_storage import compact_canonical_ledger, ledger_storage_health

print("BEFORE:", ledger_storage_health())
result = compact_canonical_ledger(snapshot_rows=750, archive_trigger_mb=25.0, force_archive=True)
print("COMPACT RESULT:", result)
print("AFTER:", ledger_storage_health())
