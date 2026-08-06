"""
Pack 2536 — Door Permission Boundary Model.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_app_registry_v2 import (
    build_app_registry_cert,
)


PACK_ID = "2536"
ENDPOINT = "/tower/ir-cert-v2536.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_app_registry_cert(2536)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2536_preview():
    return deepcopy(_build_cached())
