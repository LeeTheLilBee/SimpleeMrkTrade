"""
Pack 2534 — Door Card Metadata Model.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_app_registry_v2 import (
    build_app_registry_cert,
)


PACK_ID = "2534"
ENDPOINT = "/tower/ir-cert-v2534.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_app_registry_cert(2534)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2534_preview():
    return deepcopy(_build_cached())
