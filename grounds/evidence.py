"""GRD018 — append-only references to *verified* Vault work-order evidence.

A Vault/Tower-certified verifier must authenticate proof authenticity and the
work-order binding before this code records a reference. No raw file URLs, file
content, upload service, direct Vault access or public records are created.
"""
from __future__ import annotations

import sqlite3
from typing import Callable, Mapping
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsOperations, GroundsConflict, _required, _now
from .storage import GroundsStore

PROOF_KINDS = frozenset(("intake","before","after","completion","inspection"))
ROLE_KINDS = {
    "resident": frozenset(("intake",)),
    "maintenance_technician": frozenset(("before","after","completion")),
    "owner": PROOF_KINDS,
    "property_manager": PROOF_KINDS,
    "maintenance_supervisor": PROOF_KINDS,
}


class GroundsWorkProof:
    def __init__(self, store: GroundsStore):
        if not isinstance(store, GroundsStore):
            raise TypeError("GroundsStore required")
        self.store = store
        self.operations = GroundsOperations(store)

    def record(
        self, actor: TowerScope, *, work_ref: str, kind: str, signed_proof: object,
        proof_verifier: Callable[[object], Mapping],
    ) -> dict:
        actor = self.operations._scope(actor)
        if kind not in ROLE_KINDS.get(actor.role, ()):
            raise AccessDenied("proof type unavailable")
        if not callable(proof_verifier):
            raise AccessDenied("certified Vault/Tower proof verifier required")
        try:
            proof = proof_verifier(signed_proof)
        except Exception as exc:
            raise AccessDenied("work evidence rejected") from exc
        if (not isinstance(proof, Mapping) or proof.get("status") != "verified_sealed"
            or proof.get("work_ref") != work_ref):
            raise AccessDenied("work evidence rejected")
        proof_ref = _required(proof.get("proof_ref"), "proof_ref", max_length=128)
        evidence_ref = uuid4().hex
        with self.store.transaction(write=True) as db:
            self.operations._visible_order(db,actor,work_ref)
            try:
                db.execute(
                    """INSERT INTO work_evidence_refs
                       (evidence_ref,work_ref,kind,vault_proof_ref,actor_ref,recorded_at)
                       VALUES(?,?,?,?,?,?)""",
                    (evidence_ref,work_ref,kind,proof_ref,actor.subject_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("duplicate or invalid sealed proof reference") from exc
        return {"evidence_ref":evidence_ref,"work_ref":work_ref,"kind":kind,
                "vault_proof_ref":proof_ref,"content_url":None}

    def list_refs(self, actor: TowerScope, *, work_ref: str) -> list[dict]:
        actor = self.operations._scope(actor)
        with self.store.transaction() as db:
            self.operations._visible_order(db,actor,work_ref)
            return [dict(x) for x in db.execute(
                """SELECT evidence_ref,kind,vault_proof_ref,recorded_at
                   FROM work_evidence_refs WHERE work_ref=? ORDER BY recorded_at""", (work_ref,),
            )]
