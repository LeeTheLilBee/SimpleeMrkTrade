"""GRD199–207: minimum append-only resident-access history in private Grounds.

This is an internal source record, not a provider/security SIEM, legal retention
decision, secret store or independent proof of identity. Only a validated
per-request Tower resident scope and current original lease may create/read it.
"""
from __future__ import annotations

from uuid import uuid4
from .access import AccessDenied,TowerScope
from .operations import GroundsConflict,GroundsOperations,_now
from .storage import GroundsStoreBase

_KINDS=frozenset((
    "workspace","my_home","rent","work_detail","work_thread",
    "move_concierge","privacy_history",
))


class GroundsResidentPrivacyLog:
    def __init__(self,store:GroundsStoreBase):
        self.ops=GroundsOperations(store)
        self.store=store

    def record_read(self,actor:TowerScope,*,property_ref:str,unit_ref:str,
                    resource_kind:str,resource_ref:str)->None:
        if resource_kind not in _KINDS:
            raise GroundsConflict("unsupported personal access kind")
        if not isinstance(resource_ref,str) or not resource_ref or len(resource_ref)>128:
            raise GroundsConflict("invalid private resource reference")
        actor=self.ops._scope(actor)
        with self.store.transaction(write=True) as db:
            # Re-evaluate actual lease membership within the auditing write,
            # not just from a previously rendered page or caller role claim.
            lease=self.ops._resident_lease(db,actor,property_ref,unit_ref)
            db.execute(
                """INSERT INTO resident_access_events
                   (access_ref,lease_ref,property_ref,unit_ref,actor_ref,
                    resource_kind,resource_ref,recorded_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (uuid4().hex,lease["lease_ref"],property_ref,unit_ref,
                 actor.subject_ref,resource_kind,resource_ref,_now()),
            )

    def my_history(self,actor:TowerScope,*,property_ref:str,unit_ref:str)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            lease=self.ops._resident_lease(db,actor,property_ref,unit_ref)
            count=db.execute(
                """SELECT COUNT(*) FROM resident_access_events
                   WHERE lease_ref=? AND property_ref=? AND unit_ref=? AND actor_ref=?""",
                (lease["lease_ref"],property_ref,unit_ref,actor.subject_ref),
            ).fetchone()[0]
            rows=[dict(r) for r in db.execute(
                """SELECT resource_kind,resource_ref,recorded_at
                   FROM resident_access_events
                   WHERE lease_ref=? AND property_ref=? AND unit_ref=? AND actor_ref=?
                   ORDER BY recorded_at DESC,access_ref DESC LIMIT 50""",
                (lease["lease_ref"],property_ref,unit_ref,actor.subject_ref),
            )]
        return {
            "source":"grounds","room":"resident_privacy_history",
            "property_ref":property_ref,"unit_ref":unit_ref,
            "lease_ref":lease["lease_ref"],"events":rows,
            "total_events_before_current_response":count,"visible_limit":50,
            "truncated":count>len(rows),
            "records_are_internal_ground_access_only":True,
            "session_tokens_included":False,"ip_addresses_included":False,
            "document_or_message_contents_included":False,
            "staff_access_log_complete":False,
            "approved_live_retention_policy_connected":False,
        }
