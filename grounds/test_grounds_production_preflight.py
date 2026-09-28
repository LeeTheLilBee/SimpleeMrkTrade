"""Grounds hosted composition sanitizes sensitive provider failures.

Entirely source/fiction-only: this never provisions a private DB, Tower
receiver, account, rent checkout or public server.
"""
from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from grounds.production_entry import (
    GroundsProductionUnavailable, create_wsgi_application,
)

ENV = {
    "TOWER_LOCAL_WALKTHROUGH_MODE": "0",
    "GROUNDS_PRIVATE_POSTGRES_URL":
        "postgresql://owner:do-not-print-this-private-password@db.invalid/grounds",
    "GROUNDS_CSRF_SECRET_HEX": bytes(range(32)).hex(),
}


def _certified_factories():
    return SimpleNamespace(
        create_certified_grounds_receiver=lambda: (lambda environ: None),
        create_certified_grounds_staff_directory=lambda: (lambda actor, prop: []),
        create_certified_grounds_staff_resolver=lambda: (lambda *args: None),
    )


class GroundsProductionErrorTests(unittest.TestCase):
    def test_store_constructor_failure_is_sanitized(self):
        with patch.dict(os.environ, ENV, clear=True), patch(
            "grounds.production_entry.import_module",
            return_value=_certified_factories(),
        ), patch(
            "grounds.production_entry.PostgresGroundsStore",
            side_effect=RuntimeError(ENV["GROUNDS_PRIVATE_POSTGRES_URL"]),
        ):
            with self.assertRaises(GroundsProductionUnavailable) as caught:
                create_wsgi_application()
        err = caught.exception
        self.assertEqual(
            str(err),
            "private Grounds database or authenticated runtime failed startup preflight",
        )
        self.assertNotIn("do-not-print-this-private-password", str(err))
        self.assertIsNone(err.__cause__)
        self.assertTrue(err.__suppress_context__)

    def test_web_schema_preflight_failure_is_sanitized(self):
        with patch.dict(os.environ, ENV, clear=True), patch(
            "grounds.production_entry.import_module",
            return_value=_certified_factories(),
        ), patch(
            "grounds.production_entry.PostgresGroundsStore",
            return_value=object(),
        ), patch(
            "grounds.production_entry.GroundsWebApp",
            side_effect=RuntimeError("private DB host and credential material"),
        ):
            with self.assertRaises(GroundsProductionUnavailable) as caught:
                create_wsgi_application()
        self.assertNotIn("credential", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_tower_receiver_factory_failure_is_sanitized(self):
        factories = _certified_factories()
        factories.create_certified_grounds_receiver = lambda: (_ for _ in ()).throw(
            RuntimeError("sensitive upstream integration diagnostic")
        )
        with patch.dict(os.environ, ENV, clear=True), patch(
            "grounds.production_entry.import_module", return_value=factories,
        ):
            with self.assertRaises(GroundsProductionUnavailable) as caught:
                create_wsgi_application()
        self.assertEqual(str(caught.exception), "certified Tower adapters failed initialization")
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_local_walkthrough_still_cannot_initialize_real_resident_runtime(self):
        with patch.dict(os.environ, {**ENV, "TOWER_LOCAL_WALKTHROUGH_MODE": "1"}, clear=True):
            with self.assertRaises(GroundsProductionUnavailable) as caught:
                create_wsgi_application()
        self.assertIn("local Tower walkthrough", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
