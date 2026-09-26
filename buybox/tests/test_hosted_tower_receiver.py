"""BBX011-015: synthetic signed Tower receiver and durable-host prerequisites."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet

from buybox.hosted_readiness import inspect_private_hosted_config
from buybox.tower_owner_receiver import (
    VerifiedOwnerHandoff,
    TowerBuyBoxHandoffError,
    consume_verified_handoff,
    verify_tower_buybox_owner_handoff,
)

SECRET = "synthetic-handshake-secret-0123456789ABCDEF"  # test-only
NOW = 2_000_000_000


def claims(**changes):
    obj = {
        "schema_version": "tower.buybox.owner.handoff.v1",
        "issuer": "tower",
        "audience": "buybox-owner",
        "purpose": "owner_entry",
        "handoff_id": "handoff_" + "a" * 32,
        "tower_session_ref": "tower_session_" + "b" * 32,
        "actor_ref": "actor_" + "c" * 32,
        "entity_ref": "entity_" + "d" * 32,
        "owner_entitlement_ref": "entitlement_" + "e" * 32,
        "issued_at_epoch": NOW,
        "expires_at_epoch": NOW + 60,
        "target_path": "/",
        "return_path": "/tower/access-home",
    }
    obj.update(changes)
    return obj


def encode(obj, secret=SECRET, *, raw=None):
    payload = raw if raw is not None else json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    segment = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    head = "tbh1." + segment
    mac = hmac.new(secret.encode(), head.encode(), hashlib.sha256).digest()
    return head + "." + base64.urlsafe_b64encode(mac).decode().rstrip("=")


class TowerReceiverTests(unittest.TestCase):
    def test_synthetic_exact_verified_and_durable_one_time_consumption(self):
        token = encode(claims())
        verified = verify_tower_buybox_owner_handoff(
            token, shared_secret=SECRET, now_epoch=NOW
        )
        self.assertIsInstance(verified, VerifiedOwnerHandoff)
        self.assertEqual(verified.claims["actor_ref"], claims()["actor_ref"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "private.sqlite3"
            with sqlite3.connect(path) as db:
                self.assertTrue(consume_verified_handoff(db, verified))
            with sqlite3.connect(path) as db:
                self.assertFalse(consume_verified_handoff(db, verified))
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM buybox_tower_consumed_handoffs").fetchone()[0], 1
                )

    def test_replay_does_not_depend_on_python_process_local_set(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ledger.sqlite3"
            verified = verify_tower_buybox_owner_handoff(
                encode(claims()), shared_secret=SECRET, now_epoch=NOW
            )
            a = sqlite3.connect(path)
            b = sqlite3.connect(path)
            try:
                self.assertTrue(consume_verified_handoff(a, verified))
                self.assertFalse(consume_verified_handoff(b, verified))
            finally:
                a.close()
                b.close()

    def test_requires_verified_wrapper_not_raw_claimed_dict(self):
        with sqlite3.connect(":memory:") as db:
            with self.assertRaises(TowerBuyBoxHandoffError):
                consume_verified_handoff(db, claims())

    def test_invalid_mac_secret_prefix_and_token_length(self):
        good = encode(claims())
        bad = [
            good[:-1] + ("A" if good[-1] != "A" else "B"),
            "tbh2." + good[5:],
            good + "X",
            "x" * 4097,
        ]
        for token in bad:
            with self.subTest(token_length=len(token)):
                with self.assertRaises(TowerBuyBoxHandoffError):
                    verify_tower_buybox_owner_handoff(
                        token, shared_secret=SECRET, now_epoch=NOW
                    )
        with self.assertRaises(TowerBuyBoxHandoffError):
            verify_tower_buybox_owner_handoff(good, shared_secret="incorrect", now_epoch=NOW)

    def test_other_issuer_audience_destination_and_unsupported_fields(self):
        for change in [
            {"issuer": "buybox"}, {"audience": "teller-persistence"},
            {"target_path": "//external.example"}, {"return_path": "https://bad.test"},
            {"purpose": "asset_purchase"}, {"entitled": True},
            {"handoff_id": "short"}, {"actor_ref": "bad/path"},
        ]:
            with self.subTest(change=change):
                with self.assertRaises(TowerBuyBoxHandoffError):
                    verify_tower_buybox_owner_handoff(
                        encode(claims(**change)), shared_secret=SECRET, now_epoch=NOW
                    )

    def test_time_expiry_long_ttl_future_and_bool_types(self):
        for change in [
            {"expires_at_epoch": NOW},
            {"expires_at_epoch": NOW + 61},
            {"issued_at_epoch": NOW + 6, "expires_at_epoch": NOW + 65},
            {"issued_at_epoch": True},
            {"expires_at_epoch": True},
            {"issued_at_epoch": NOW + 10, "expires_at_epoch": NOW + 10},
        ]:
            with self.subTest(change=change):
                with self.assertRaises(TowerBuyBoxHandoffError):
                    verify_tower_buybox_owner_handoff(
                        encode(claims(**change)), shared_secret=SECRET, now_epoch=NOW
                    )

    def test_duplicate_signed_json_keys_denied(self):
        base = json.dumps(claims(), sort_keys=True, separators=(",", ":"))
        self.assertIn('"issuer":"tower"', base)
        duplicate = base.replace('"issuer":"tower"', '"issuer":"tower","issuer":"tower"')
        with self.assertRaises(TowerBuyBoxHandoffError):
            verify_tower_buybox_owner_handoff(
                encode(None, raw=duplicate.encode()), shared_secret=SECRET, now_epoch=NOW
            )

    def test_weak_handoff_secret_denied(self):
        with self.assertRaises(TowerBuyBoxHandoffError):
            verify_tower_buybox_owner_handoff(
                encode(claims()), shared_secret="short", now_epoch=NOW
            )

    def test_no_token_in_exception_string(self):
        token = encode(claims(audience="wrong"))
        with self.assertRaises(TowerBuyBoxHandoffError) as caught:
            verify_tower_buybox_owner_handoff(token, shared_secret=SECRET, now_epoch=NOW)
        self.assertNotIn(token, str(caught.exception))
        self.assertNotIn(SECRET, str(caught.exception))


class HostedReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.mount = root / "durable"
        self.mount.mkdir(mode=0o700)
        self.dbdir = self.mount / "db"
        self.dbdir.mkdir(mode=0o700)
        self.docs = self.mount / "originals"
        self.docs.mkdir(mode=0o700)
        self.config = {
            "BUYBOX_AUTH_MODE": "tower",
            "BUYBOX_PUBLIC_ORIGIN": "https://buybox.example.test",
            "TOWER_PUBLIC_ORIGIN": "https://tower.example.test",
            "TOWER_BUYBOX_HANDOFF_SECRET": "separate-handoff-key-1234567890-abcdefgh",
            "BUYBOX_SECRET_KEY": "other-flask-key-1234567890-abcdefgh",
            "BUYBOX_DOCUMENT_KEY": Fernet.generate_key().decode("ascii"),
            "BUYBOX_DB_PATH": str(self.dbdir / "buybox.sqlite3"),
            "BUYBOX_DOCS_DIR": str(self.docs),
            "BUYBOX_DURABLE_MOUNT": str(self.mount),
            "BUYBOX_SECURE_COOKIE": "1",
        }

    def tearDown(self):
        self.temp.cleanup()

    def inspect(self, changes=None, mounted=True):
        config = deepcopy(self.config)
        config.update(changes or {})
        return inspect_private_hosted_config(
            config, is_mount=lambda _: mounted
        )

    def test_valid_source_configuration_never_claims_provider_or_backup_proof(self):
        report = self.inspect()
        self.assertEqual(report["status"], "SOURCE_CONFIGURATION_VALID")
        self.assertEqual(report["reason_codes"], [])
        self.assertFalse(report["provider_storage_proven"])
        self.assertFalse(report["backup_restore_proven"])
        self.assertFalse(report["tower_receiver_active"])
        self.assertFalse(report["may_serve_private_records"])
        self.assertFalse(report["secrets_exposed"])
        serialized = json.dumps(report)
        for key in (
            self.config["BUYBOX_SECRET_KEY"],
            self.config["TOWER_BUYBOX_HANDOFF_SECRET"],
            self.config["BUYBOX_DOCUMENT_KEY"],
            str(self.mount),
        ):
            self.assertNotIn(key, serialized)

    def test_missing_config_never_exposes_values(self):
        config = deepcopy(self.config)
        del config["BUYBOX_DURABLE_MOUNT"]
        report = inspect_private_hosted_config(config, is_mount=lambda _: True)
        self.assertIn("MISSING_BUYBOX_DURABLE_MOUNT", report["reason_codes"])
        self.assertFalse(report["may_serve_private_records"])

    def test_ephemeral_or_unmounted_path_denied(self):
        report = self.inspect(mounted=False)
        self.assertIn("REAL_MOUNT_NOT_VERIFIED", report["reason_codes"])
        self.assertEqual(report["status"], "BLOCKED")

    def test_local_password_mode_and_insecure_cookie_denied(self):
        report = self.inspect({
            "BUYBOX_AUTH_MODE": "local",
            "BUYBOX_PASSWORD_HASH": "synthetic-hash",
            "BUYBOX_SECURE_COOKIE": "0",
        })
        for code in (
            "TOWER_AUTH_MODE_REQUIRED", "HOSTED_LOCAL_PASSWORD_FORBIDDEN",
            "SECURE_SESSION_COOKIE_REQUIRED",
        ):
            self.assertIn(code, report["reason_codes"])

    def test_insecure_origin_and_reused_keys_denied(self):
        report = self.inspect({
            "BUYBOX_PUBLIC_ORIGIN": "http://localhost:8787",
            "TOWER_PUBLIC_ORIGIN": "http://tower.example.test",
            "BUYBOX_SECRET_KEY": self.config["TOWER_BUYBOX_HANDOFF_SECRET"],
        })
        self.assertIn("BUYBOX_PUBLIC_ORIGIN_INVALID", report["reason_codes"])
        self.assertIn("TOWER_PUBLIC_ORIGIN_INVALID", report["reason_codes"])
        self.assertIn("SECURITY_KEYS_MUST_BE_DISTINCT", report["reason_codes"])

    def test_documents_outside_actual_mount_denied(self):
        other = Path(self.temp.name) / "other"
        other.mkdir(mode=0o700)
        report = self.inspect({"BUYBOX_DOCS_DIR": str(other)})
        self.assertIn("DATABASE_AND_ORIGINALS_MUST_RESIDE_ON_MOUNT", report["reason_codes"])

    def test_private_directory_requirement(self):
        self.docs.chmod(0o755)
        report = self.inspect()
        self.assertIn("PRIVATE_DB_AND_DOCUMENT_DIRECTORIES_REQUIRED", report["reason_codes"])

    def test_not_independent_public_login_or_product_serving(self):
        import buybox.tower_owner_receiver as receiver
        import buybox.hosted_readiness as readiness
        for module in (receiver, readiness):
            source = Path(module.__file__).read_text(encoding="utf-8")
            self.assertNotIn("@app.route(", source)
            self.assertNotIn("requests.post(", source)
            self.assertNotIn("from observatory.", source)


if __name__ == "__main__":
    unittest.main()
