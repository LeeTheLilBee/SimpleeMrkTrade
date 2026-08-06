"""
Pack 2541 — Registry Cert Routes.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_app_registry_v2 import (
    build_app_registry_cert,
)


PACK_ID = "2541"
ENDPOINT = "/tower/ir-cert-v2541.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_app_registry_cert(2541)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2541_preview():
    return deepcopy(_build_cached())
