"""
Pack 2537 — Door Launch / Route Map.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_app_registry_v2 import (
    build_app_registry_cert,
)


PACK_ID = "2537"
ENDPOINT = "/tower/ir-cert-v2537.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_app_registry_cert(2537)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2537_preview():
    return deepcopy(_build_cached())
