"""
Pack 2533 — Ecosystem Door Registry Contract.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_app_registry_v2 import (
    build_app_registry_cert,
)


PACK_ID = "2533"
ENDPOINT = "/tower/ir-cert-v2533.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_app_registry_cert(2533)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2533_preview():
    return deepcopy(_build_cached())
