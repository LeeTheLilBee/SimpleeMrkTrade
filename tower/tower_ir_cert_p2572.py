"""
Tower IR Cert Pack 2572: Merge and deploy readiness cert
"""

from __future__ import annotations

from tower.tower_owner_beta_route_gate import owner_beta_route_gate_cert


def tower_ir_cert_p2572():
    return owner_beta_route_gate_cert(2572)
