"""Local durable nonce callback acceptance using actual OB source export/receiver."""
from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest

from web.ob_tower_account_identity_export import create_ob_account_identity_export
from tower.obml_account_namespace_source import (
    NamespaceSourceRefused, verify_ob_account_namespace_source,
)
from tower.obml_local_source_nonce_ledger import (
    LocalSQLiteSourceNonceLedger, local_nonce_ledger_contract, SCHEMA_VERSION,
)

KEY = b"synthetic-only-local-nonce-callback-key-0123456789-abcdef"
WRONG = b"synthetic-only-other-nonce-callback-key-0123456789abcdef"
NOW = 2_000_000_000


def token(account="trust"):
    return create_ob_account_identity_export(
        account, now_epoch=NOW, signing_secret=KEY,
    )


def verify(value, ledger, *, key=KEY, now=NOW):
    return verify_ob_account_namespace_source(
        value, now_epoch=now, verification_key=key,
        consume_once=ledger.consume_once,
    )


def test_actual_source_token_first_consumption_and_restart_replay_denial(tmp_path):
    path = tmp_path / "tower-source-nonces.sqlite"
    t = token()
    first = LocalSQLiteSourceNonceLedger(path)
    result = verify(t, first)
    assert result.one_time_nonce_consumed_by_caller_store
    assert result.manual_live_granted is False
    assert result.tower_permission_verified is False
    assert result.broker_account_verified is False
    assert result.real_capital_verified is False
    assert path.is_file()
    # A newly constructed adapter simulates process restart on the same file.
    reopened = LocalSQLiteSourceNonceLedger(path)
    with pytest.raises(NamespaceSourceRefused):
        verify(t, reopened)
    with sqlite3.connect(path) as conn:
        digest, expiry = conn.execute(
            "SELECT nonce_digest, expires_at_epoch FROM tower_obml_source_nonce_v1"
        ).fetchone()
        assert len(digest) == 64 and expiry == NOW + 60
        assert conn.execute("SELECT COUNT(*) FROM tower_obml_source_nonce_v1").fetchone()[0] == 1
        assert "trust" not in digest


def test_two_distinct_real_tokens_same_account_each_consume_once(tmp_path):
    ledger = LocalSQLiteSourceNonceLedger(tmp_path / "nonce.sqlite")
    t1, t2 = token(), token()
    assert t1 != t2
    assert verify(t1, ledger).manual_live_granted is False
    assert verify(t2, ledger).manual_live_granted is False
    with sqlite3.connect(tmp_path / "nonce.sqlite") as conn:
        assert conn.execute("SELECT COUNT(*) FROM tower_obml_source_nonce_v1").fetchone()[0] == 2


def test_concurrent_separate_connections_cannot_both_claim_same_nonce(tmp_path):
    path = tmp_path / "shared-local.sqlite"
    t = token()
    def attempt(_):
        try:
            verify(t, LocalSQLiteSourceNonceLedger(path))
            return True
        except NamespaceSourceRefused:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        accepted = list(pool.map(attempt, range(2)))
    assert sorted(accepted) == [False, True]
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM tower_obml_source_nonce_v1").fetchone()[0] == 1


def test_invalid_config_is_never_reinterpreted_as_ephemeral_store(tmp_path):
    for path in (":memory:", "relative.db", str(tmp_path / "missing" / "nonce.db"),
                 "", None):
        with pytest.raises(ValueError):
            LocalSQLiteSourceNonceLedger(path)
    original = tmp_path / "original.sqlite"
    original.write_text("not a database")
    alias = tmp_path / "link.sqlite"
    alias.symlink_to(original)
    with pytest.raises(ValueError):
        LocalSQLiteSourceNonceLedger(alias)


def test_wrong_key_and_expired_source_do_not_touch_ledger(tmp_path):
    path = tmp_path / "no-false-consume.sqlite"
    ledger = LocalSQLiteSourceNonceLedger(path)
    t = token()
    with pytest.raises(NamespaceSourceRefused):
        verify(t, ledger, key=WRONG)
    with pytest.raises(NamespaceSourceRefused):
        verify(t, ledger, now=NOW+60)
    assert not path.exists()
    assert verify(t, ledger).manual_live_granted is False


def test_sqlite_corruption_schema_or_locked_transaction_denies_without_promotion(tmp_path):
    path = tmp_path / "bad-schema.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE tower_obml_source_nonce_v1 (nonce_digest TEXT PRIMARY KEY, invalid TEXT)")
    ledger = LocalSQLiteSourceNonceLedger(path)
    with pytest.raises(NamespaceSourceRefused):
        verify(token(), ledger)
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM tower_obml_source_nonce_v1").fetchone()[0] == 0


def test_callback_direct_bad_inputs_and_contract_remain_fail_closed(tmp_path):
    ledger = LocalSQLiteSourceNonceLedger(tmp_path / "nonce.sqlite")
    for account, nonce, expiry in (
        ("trust ", "a"*32, NOW+60), ("proof_demo", "BAD", NOW+60),
        ("trust", "short", NOW+60), ("trust", "a"*32, True),
        ("trust", "a"*32, 0), (None, "a"*32, NOW+60),
    ):
        assert ledger.consume_once(account, nonce, expiry) is False
    c = local_nonce_ledger_contract()
    assert c["authority"] == SCHEMA_VERSION
    assert c["atomic_sqlite_unique_nonce_digest"] is True
    assert c["explicit_local_path_required"] is True
    assert c["multi_host_shared_storage_certified"] is False
    assert c["ephemeral_container_disk_is_production_durable"] is False
    assert c["persists_raw_nonce_or_account"] is False
    for flag in (
        "default_path_configured", "production_key_configured",
        "owner_authentication", "tower_session_or_step_up_verification",
        "manual_live_clearance", "broker_order_api", "capital_movement",
        "paid_service_provisioned",
    ):
        assert c[flag] is False
