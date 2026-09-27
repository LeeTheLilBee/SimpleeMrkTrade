"""GRD103 — production factory fails closed without real Tower or private DB."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from grounds.production_entry import (
    GroundsProductionUnavailable, create_wsgi_application,
)


class ProductionEntryTests(unittest.TestCase):
    def test_no_config_no_receiver_and_no_weak_secrets(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(GroundsProductionUnavailable):
                create_wsgi_application()
        with patch.dict(os.environ,{
            "TOWER_LOCAL_WALKTHROUGH_MODE":"true",
            "GROUNDS_PRIVATE_POSTGRES_URL":"postgresql://example/private",
            "GROUNDS_CSRF_SECRET_HEX":bytes(range(32)).hex(),
        },clear=True):
            with self.assertRaises(GroundsProductionUnavailable):
                create_wsgi_application()
        with patch.dict(os.environ,{
            "GROUNDS_PRIVATE_POSTGRES_URL":"postgresql://example/private",
            "GROUNDS_CSRF_SECRET_HEX":"badnothex",
        },clear=True):
            with self.assertRaises(GroundsProductionUnavailable):
                create_wsgi_application()
        with patch.dict(os.environ,{
            "GROUNDS_PRIVATE_POSTGRES_URL":"postgresql://example/private",
            "GROUNDS_CSRF_SECRET_HEX":bytes(range(32)).hex(),
        },clear=True):
            with patch("grounds.production_entry.import_module",
                       side_effect=ModuleNotFoundError("no certified Tower Grounds receiver")):
                with self.assertRaisesRegex(
                    GroundsProductionUnavailable,"real Tower Grounds receiver",
                ):
                    create_wsgi_application()

    def test_untrusted_factory_does_not_create_wsgi_application(self):
        with patch.dict(os.environ,{
            "GROUNDS_PRIVATE_POSTGRES_URL":"postgresql://example/private",
            "GROUNDS_CSRF_SECRET_HEX":bytes(range(32)).hex(),
        },clear=True):
            class UnsafeModule:
                create_certified_grounds_receiver="not a trusted callable"
            with patch("grounds.production_entry.import_module",
                       return_value=UnsafeModule()):
                with self.assertRaises(GroundsProductionUnavailable):
                    create_wsgi_application()

    def test_receiver_without_certified_staff_authority_stays_closed(self):
        with patch.dict(os.environ,{
            "GROUNDS_PRIVATE_POSTGRES_URL":"postgresql://example/private",
            "GROUNDS_CSRF_SECRET_HEX":bytes(range(32)).hex(),
        },clear=True):
            class IncompleteTower:
                @staticmethod
                def create_certified_grounds_receiver():
                    return lambda environ:None
            with patch("grounds.production_entry.import_module",
                       return_value=IncompleteTower()):
                with self.assertRaisesRegex(
                    GroundsProductionUnavailable,"staff authority",
                ):
                    create_wsgi_application()

    def test_preflight_database_failure_never_leaks_connection_string(self):
        dsn="postgresql://not-real-secret:private@example.invalid/test"
        with patch.dict(os.environ,{
            "GROUNDS_PRIVATE_POSTGRES_URL":dsn,
            "GROUNDS_CSRF_SECRET_HEX":bytes(range(32)).hex(),
        },clear=True):
            class FutureTower:
                @staticmethod
                def create_certified_grounds_receiver():
                    return lambda environ:None
                @staticmethod
                def create_certified_grounds_staff_directory():
                    return lambda actor,property_ref:[]
                @staticmethod
                def create_certified_grounds_staff_resolver():
                    return lambda actor,property_ref,work_ref,technician_ref:None
            with patch("grounds.production_entry.import_module",
                       return_value=FutureTower()):
                with patch("grounds.production_entry.GroundsWebApp",
                           side_effect=ValueError("provider internal details")):
                    try:
                        create_wsgi_application()
                    except GroundsProductionUnavailable as exc:
                        self.assertNotIn(dsn,str(exc))
                        self.assertNotIn("provider internal details",str(exc))
                    else:
                        self.fail("unsafe private runtime unexpectedly activated")


if __name__=="__main__":
    unittest.main()
