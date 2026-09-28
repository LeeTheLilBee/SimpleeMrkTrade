"""GRD163–171: source-backed role-specific home, daily and property health projections.

No money source, rent arithmetic, emergency dispatch, external provider, legal
lease determination, resident identity export or recommendation engine is added.
Every path rechecks an independently verified current TowerScope AND real
Grounds property/lease rows, independently of browser role flags.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from .access import AccessDenied, TowerScope
from .operations import GroundsOperations
from .storage import GroundsStoreBase

_LIMIT=50


def _utc(value: str):
    try:
        d=datetime.fromisoformat(value.replace("Z","+00:00"))
        if d.tzinfo is not None:
            return d.astimezone(timezone.utc)
    except (TypeError,ValueError,OverflowError):
        pass
    return None


class GroundsExperience:
    def __init__(self,store:GroundsStoreBase):
        self.ops=GroundsOperations(store)
        self.store=store

    def my_home(self,actor:TowerScope,*,property_ref:str,unit_ref:str)->dict:
        actor=self.ops._scope(actor)
        home=self.ops.resident_home(actor,property_ref=property_ref,unit_ref=unit_ref)
        lease=home["lease"]
        with self.store.transaction() as db:
            property_record=db.execute(
                "SELECT name FROM properties WHERE property_ref=?",(property_ref,),
            ).fetchone()
            if property_record is None:
                raise AccessDenied("property unavailable")
            # Only this active lease's original requester may see these
            # appointment metadata. Other residents' appointments never leak.
            upcoming=[dict(r) for r in db.execute(
                """SELECT a.appointment_ref,a.work_ref,a.state,a.start_at,a.end_at
                   FROM work_appointments a
                   JOIN work_orders w ON w.work_ref=a.work_ref
                   WHERE w.property_ref=? AND w.unit_ref=? AND w.lease_ref=?
                     AND w.created_by=? AND a.state!='cancelled'
                   ORDER BY a.start_at LIMIT 20""",
                (property_ref,unit_ref,lease["lease_ref"],actor.subject_ref),
            )]
        return {
            "source":"grounds","room":"my_home",
            "property_ref":property_ref,"unit_ref":unit_ref,
            "property_name":property_record["name"],"unit_label":home["unit_label"],
            "lease":{"lease_ref":lease["lease_ref"],
                     "start_on":lease["start_on"],"end_on":lease["end_on"]},
            "visible_notice_count":len(home["notices"]),
            "unread_in_app_count":sum(not bool(n["read_in_app"]) for n in home["notices"]),
            "my_request_count":len(home["maintenance"]),
            "open_my_request_count":sum(w["state"]!="closed" for w in home["maintenance"]),
            "next_appointments":upcoming,
            "rent":{"source":"teller","status":"unknown_without_separate_verified_read",
                    "amount_due_cents":None,"payment_enabled":False},
            "documents":{"source":"vault","private_retrieval_connected":False},
            "notice_delivery_proven":False,"legal_entry_authorized":False,
        }

    def daily(self,actor:TowerScope,*,property_ref:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","maintenance_supervisor")
        actor.require_property(property_ref)
        clock=datetime.now(timezone.utc)
        overdue=(clock-timedelta(days=3)).isoformat()
        through=(clock+timedelta(days=7)).isoformat()
        today=clock.date().isoformat()
        with self.store.transaction() as db:
            prop=db.execute(
                "SELECT name FROM properties WHERE property_ref=?",(property_ref,),
            ).fetchone()
            if prop is None: raise AccessDenied("property unavailable")
            urgent_count=db.execute(
                """SELECT COUNT(*) FROM work_orders w
                   LEFT JOIN emergency_reviews r ON r.work_ref=w.work_ref
                   WHERE w.property_ref=? AND w.emergency_flag=1
                     AND w.state!='closed' AND r.work_ref IS NULL""",
                (property_ref,),
            ).fetchone()[0]
            overdue_count=db.execute(
                """SELECT COUNT(*) FROM work_orders WHERE property_ref=?
                   AND state!='closed' AND created_at<?""",
                (property_ref,overdue),
            ).fetchone()[0]
            urgent=[dict(x) for x in db.execute(
                """SELECT w.work_ref,w.unit_ref,w.category,w.created_at
                   FROM work_orders w LEFT JOIN emergency_reviews r
                   ON r.work_ref=w.work_ref
                   WHERE w.property_ref=? AND w.emergency_flag=1 AND w.state!='closed'
                     AND r.work_ref IS NULL ORDER BY w.created_at LIMIT 20""",
                (property_ref,),
            )]
            pending_appointments=db.execute(
                """SELECT COUNT(*) FROM work_appointments
                   WHERE property_ref=? AND state IN ('requested','proposed')""",
                (property_ref,),
            ).fetchone()[0]
            appointments=[dict(x) for x in db.execute(
                """SELECT appointment_ref,unit_ref,state,start_at,end_at
                   FROM work_appointments WHERE property_ref=?
                     AND state IN ('proposed','accepted') AND start_at>=? AND start_at<=?
                   ORDER BY start_at LIMIT 20""",
                (property_ref,clock.isoformat(),through),
            )]
            due_preventive=db.execute(
                """SELECT COUNT(*) FROM preventive_plans WHERE property_ref=?
                   AND enabled=1 AND next_due_on<=?""",
                (property_ref,today),
            ).fetchone()[0]
            open_inspections=db.execute(
                """SELECT COUNT(*) FROM inspections WHERE property_ref=?
                   AND state!='closed'""",(property_ref,),
            ).fetchone()[0]
            open_turnovers=None
            if actor.role in ("owner","property_manager"):
                open_turnovers=db.execute(
                    """SELECT COUNT(*) FROM turnovers WHERE property_ref=?
                       AND state!='complete'""",(property_ref,),
                ).fetchone()[0]
            pending_intents=db.execute(
                "SELECT COUNT(*) FROM event_outbox WHERE property_ref=? AND status='pending'",
                (property_ref,),
            ).fetchone()[0]
        return {
            "source":"grounds","room":"daily_grounds","property_ref":property_ref,
            "property_name":prop["name"],"observed_at":clock.isoformat(),
            "counts":{"unreviewed_urgent":urgent_count,"open_older_than_three_days":overdue_count,
                      "pending_appointment_decisions":pending_appointments,
                      "due_preventive":due_preventive,"open_inspections":open_inspections,
                      "open_turnovers":open_turnovers,"pending_local_notification_intents":pending_intents},
            "urgent_work":urgent,"upcoming_appointments":appointments,
            "turnovers_authorized":actor.role in ("owner","property_manager"),
            "delivery_confirmed_by_this_view":False,"emergency_dispatch_confirmed":False,
            "work_age_threshold_days":3,
        }

    def property_health(self,actor:TowerScope,*,property_ref:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","regional_manager")
        actor.require_property(property_ref)
        pulse=self.ops.property_pulse(actor,property_ref=property_ref)
        clock=datetime.now(timezone.utc)
        current=(clock-timedelta(days=30)).isoformat()
        previous=(clock-timedelta(days=60)).isoformat()
        with self.store.transaction() as db:
            recent=db.execute(
                "SELECT COUNT(*) FROM work_orders WHERE property_ref=? AND created_at>=?",
                (property_ref,current),
            ).fetchone()[0]
            previous_count=db.execute(
                """SELECT COUNT(*) FROM work_orders WHERE property_ref=?
                   AND created_at>=? AND created_at<?""",
                (property_ref,previous,current),
            ).fetchone()[0]
            repeat=db.execute(
                """SELECT COUNT(*) FROM (
                     SELECT unit_ref,category FROM work_orders
                     WHERE property_ref=? AND created_at>=?
                     GROUP BY unit_ref,category HAVING COUNT(*)>=2
                   ) AS recurring""",(property_ref,current),
            ).fetchone()[0]
            # A bounded historical sample; never silently present it as a
            # complete SLA or statistical performance certification.
            rows=db.execute(
                """SELECT w.created_at,MIN(e.occurred_at) AS first_received
                   FROM work_orders w JOIN work_events e ON e.work_ref=w.work_ref
                   WHERE w.property_ref=? AND w.created_at>=? AND e.to_state='received'
                   GROUP BY w.work_ref,w.created_at ORDER BY w.created_at DESC LIMIT 200""",
                (property_ref,current),
            ).fetchall()
        durations=[]
        for row in rows:
            started,received=_utc(row["created_at"]),_utc(row["first_received"])
            if started and received and received>=started:
                durations.append(int((received-started).total_seconds()/60))
        return {
            "source":"grounds","room":"property_health","property_ref":property_ref,
            "observed_at":clock.isoformat(),
            "counts":{"units":pulse["units"],"occupied_units":pulse["occupied_units"],
                      "open_work":pulse["open_work_orders"],
                      "unreviewed_urgent":pulse["untriaged_urgent_work"],
                      "open_turnovers":pulse["open_turnovers"],
                      "unresolved_serious_inspection_findings":
                          pulse["unresolved_serious_inspection_findings"],
                      "new_requests_last_30_days":recent,
                      "new_requests_previous_30_days":previous_count,
                      "repeat_unit_category_groups_last_30_days":repeat},
            "first_received_elapsed_minutes_sample_mean":
                (round(sum(durations)/len(durations)) if durations else None),
            "response_sample_count":len(durations),
            "response_sample_row_limit":200,
            "response_sample_may_be_truncated":len(rows)==200,
            "sla_attested":False,"cause_of_repeat_issue_proven":False,
            "rent_collections":None,"available_capital":None,"financial_source":"teller",
            "resident_identity_included":False,"source_only":True,
        }

    def owner_portfolio(self,actor:TowerScope)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner")
        properties=sorted(actor.property_refs)
        if len(properties)>500:
            raise AccessDenied("property scope requires server-side pagination")
        # Do not enumerate ungranted properties, and never list resident identities.
        visible=properties[:_LIMIT]
        items=[self.property_health(actor,property_ref=p) for p in visible]
        return {"source":"grounds","room":"owner_portfolio","total_scope_count":len(properties),
                "visible_limit":_LIMIT,"truncated":len(properties)>_LIMIT,
                "properties":items,"financial_source":"teller",
                "money_fields_included":False,"provider_notification_sent":False}
