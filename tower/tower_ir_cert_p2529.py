"""
Pack 2529 — Deployment / Activation Hold Panel.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_owner_console_v1 import (
    build_owner_console_cert,
)


PACK_ID = "2529"
ENDPOINT = "/tower/ir-cert-v2529.json"


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    payload = build_owner_console_cert(2529)
    payload["endpoint"] = ENDPOINT
    return payload


def build_ir_cert_p2529_preview():
    return deepcopy(_build_cached())
