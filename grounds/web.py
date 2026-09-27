"""GRD089–093 — real-data, authenticated WSGI-facing Grounds web composition.

No demo fixtures, local role switcher, caller-supplied auth/verification callbacks,
or independent password login are exposed. This application REQUIRES an actual
server-owned Tower authentication adapter on EVERY request and an independent
secret for session-bound anti-CSRF. It is not a public deployment/entrypoint;
existing GroundsStore is only disposable local SQLite, and certified live Tower
receiver plus private durable tenant database are still mandatory deployment
dependencies. No live deployment, signature protocol, or credential is invented.

A GET of this WSGI application has no meaning without a valid externally
authenticated TowerScope. The UI fetches real domain views only.
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import re
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs
from uuid import UUID, uuid4

from .access import AccessDenied, TowerScope
from .communications import GroundsCommunications
from .maintenance import MaintenanceIntake
from .operations import GroundsConflict, GroundsOperations
from .postgres import PostgresGroundsStore
from .safety import GroundsSafety
from .storage import GroundsStore, GroundsStoreBase
from .workspaces import build_workspace

_UI=Path(__file__).parent/"ui"
_NO_CACHE=[("Cache-Control","no-store, private, max-age=0"),
           ("Pragma","no-cache"),("X-Content-Type-Options","nosniff"),
           ("X-Frame-Options","DENY"),("Referrer-Policy","no-referrer"),
           ("Cross-Origin-Resource-Policy","same-origin"),
           ("Content-Security-Policy",
            "default-src 'none'; base-uri 'none'; form-action 'self'; "
            "frame-ancestors 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self'; font-src 'self'")]
_ROUTES={
    ("GET","/grounds"),
    ("GET","/grounds/app.css"),
    ("GET","/grounds/app.js"),
    ("GET","/grounds/api/me"),
    ("GET","/grounds/api/workspace"),
    ("GET","/grounds/api/work"),
    ("GET","/grounds/api/appointment"),
    ("GET","/grounds/api/appointments"),
    ("GET","/grounds/api/entry-preference"),
    ("POST","/grounds/api/work"),
    ("POST","/grounds/api/notice-read"),
    ("POST","/grounds/api/appointment/request"),
    ("POST","/grounds/api/appointment/propose"),
    ("POST","/grounds/api/appointment/accept"),
    ("POST","/grounds/api/appointment/cancel"),
    ("POST","/grounds/api/urgency/review"),
    ("POST","/grounds/api/work/transition"),
    ("POST","/grounds/api/work/entry-preference"),
}
_REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")

class GroundsWebConfigurationError(ValueError):
    pass

class GroundsBadRequest(ValueError):
    pass

def _ref(value, key):
    if not isinstance(value,str) or _REF.fullmatch(value) is None:
        raise GroundsBadRequest("Invalid "+key)
    return value

def _exact(body:dict,required:set,optional:set=frozenset()):
    if not isinstance(body,dict) or not required.issubset(body) or set(body)-(required|optional):
        raise GroundsBadRequest("Invalid request fields")

def _revision(value):
    if type(value) is not int or not 0<=value<=2147483647:
        raise GroundsBadRequest("Invalid revision")
    return value

def _bounded_text(value,key,max_length):
    if (not isinstance(value,str) or not value.strip() or len(value.strip())>max_length
        or "\x00" in value):
        raise GroundsBadRequest("Invalid "+key)
    return value.strip()

def _no_duplicate_json(items):
    result={}
    for key,val in items:
        if key in result:
            raise GroundsBadRequest("Duplicate JSON key")
        result[key]=val
    return result

def _body(environ):
    content_type=environ.get("CONTENT_TYPE","").split(";",1)[0].strip().lower()
    if content_type!="application/json":
        raise GroundsBadRequest("JSON required")
    try:
        size=int(environ.get("CONTENT_LENGTH",""))
    except (TypeError,ValueError) as exc:
        raise GroundsBadRequest("Content length required") from exc
    if size<2 or size>8192:
        raise GroundsBadRequest("JSON body outside limit")
    raw=environ["wsgi.input"].read(size)
    if len(raw)!=size:
        raise GroundsBadRequest("Truncated body")
    try:
        value=json.loads(raw.decode("utf-8"),object_pairs_hook=_no_duplicate_json,
                         parse_constant=lambda _: (_ for _ in ()).throw(GroundsBadRequest("Invalid JSON constant")))
    except (ValueError,UnicodeDecodeError) as exc:
        raise GroundsBadRequest("Invalid JSON") from exc
    if not isinstance(value,dict):
        raise GroundsBadRequest("JSON object required")
    return value

def _query(environ,required:set,optional:set=frozenset()):
    try:
        values=parse_qs(environ.get("QUERY_STRING",""),keep_blank_values=True,strict_parsing=True,
                        max_num_fields=8)
    except ValueError as exc:
        raise GroundsBadRequest("Invalid query") from exc
    if not required.issubset(values) or set(values)-(required|optional) or any(len(v)!=1 for v in values.values()):
        raise GroundsBadRequest("Invalid query")
    return {key:value[0] for key,value in values.items()}

class SessionCSRF:
    """Independent anti-CSRF only; never substitutes for Tower authentication."""
    def __init__(self,secret:bytes):
        if not isinstance(secret,bytes) or len(secret)<32 or len(set(secret))<8:
            raise GroundsWebConfigurationError("independent high-entropy CSRF secret required")
        self._secret=secret

    def token(self,scope:TowerScope)->str:
        scope.assert_active()
        # The short-lived Tower handoff expiry may rotate while the verified
        # *session* stays active. Tie CSRF to that session, not a ticket TTL.
        # This is not an authorization grant: receiver + assert_active run on
        # every request, and revocation must be enforced by Tower.
        payload="grounds-csrf-v2\x1f"+scope.session_ref+"\x1f"+scope.subject_ref+"\x1f"+scope.role
        return hmac.new(self._secret,payload.encode("utf-8"),hashlib.sha256).hexdigest()

    def verify(self,scope:TowerScope,token:str)->bool:
        return (isinstance(token,str) and len(token)==64
                and hmac.compare_digest(self.token(scope),token))

def _idempotency_key(environ):
    """Require a browser-created UUIDv4 for create actions, no silent fallback."""
    value=environ.get("HTTP_X_GROUNDS_IDEMPOTENCY_KEY")
    if not isinstance(value,str) or len(value)!=36:
        raise GroundsBadRequest("Idempotency key required")
    try:
        token=UUID(value)
    except (ValueError,AttributeError) as exc:
        raise GroundsBadRequest("Invalid idempotency key") from exc
    if token.version!=4 or str(token)!=value:
        raise GroundsBadRequest("Invalid idempotency key")
    return value


class GroundsWebApp:
    """Mount ONLY behind verified Tower request middleware and private datastore.

    The receiver is a trusted SERVER-INJECTED callable returning TowerScope
    after Tower has independently checked signed session, audience, replay,
    current grants and revocation. No HTTP body/header can choose this callable.
    SQLite is accepted only in explicit fixture mode; private PostgreSQL must
    pass a real read-only schema preflight. Neither condition authenticates a
    Tower sender: production composition MUST supply its separately certified
    receiver and must not install a fixture callback on a public ingress.
    """
    def __init__(self,store:GroundsStoreBase,*,tower_receiver:Callable,
                 csrf_secret:bytes,local_fixture_only:bool=False):
        if not callable(tower_receiver):
            raise GroundsWebConfigurationError("server-owned Tower receiver required")
        if type(store) is GroundsStore:
            if local_fixture_only is not True:
                raise GroundsWebConfigurationError(
                    "SQLite is disposable fiction only, never private production storage"
                )
        elif type(store) is PostgresGroundsStore:
            if local_fixture_only:
                raise GroundsWebConfigurationError(
                    "PostgreSQL must not be silently demoted into fictional local mode"
                )
            store.assert_schema_ready()
        else:
            raise GroundsWebConfigurationError("supported transaction-backed Grounds store required")
        self.store=store
        self.receiver=tower_receiver
        self.csrf=SessionCSRF(csrf_secret)
        self.ops=GroundsOperations(store)
        self.communications=GroundsCommunications(store)
        self.safety=GroundsSafety(store)

    def _resource_ref(self,actor,kind,key,*refs):
        """Opaque stable identifier; session/subject/target bound, never guessable."""
        actor.assert_active()
        message=json.dumps(
            ["grounds-create-v1",actor.session_ref,actor.subject_ref,actor.role,
             kind,key,*refs],ensure_ascii=False,separators=(",",":"),
        ).encode("utf-8")
        digest=hmac.new(self.csrf._secret,message,hashlib.sha256).hexdigest()[:40]
        return ("work_" if kind=="work" else "appt_")+digest

    def _response(self,start_response,status,payload,content_type="application/json; charset=utf-8"):
        raw=(json.dumps(payload,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf-8")
             if content_type.startswith("application/json") else payload)
        start_response(status,_NO_CACHE+[("Content-Type",content_type),
                                         ("Content-Length",str(len(raw)))])
        return [raw]

    def __call__(self,environ,start_response):
        method=environ.get("REQUEST_METHOD","")
        path=environ.get("PATH_INFO","")
        if (method,path) not in _ROUTES:
            return self._response(start_response,"404 Not Found",{"error":"not_found"})
        # No API or UI is ever served to an unverified requester. Test adapters
        # must never be installed on a public route.
        try:
            actor=self.receiver(environ)
            if not isinstance(actor,TowerScope):
                raise AccessDenied("not verified")
            actor.assert_active()
        except Exception:
            return self._response(start_response,"401 Unauthorized",{"error":"authentication_required"})
        try:
            if method=="POST":
                if not self.csrf.verify(actor,environ.get("HTTP_X_GROUNDS_CSRF","")):
                    return self._response(start_response,"403 Forbidden",{"error":"csrf_required"})
                body=_body(environ)
            else:
                body=None
            result=self.dispatch(method,path,actor,environ,body)
            if path=="/grounds":
                raw=(_UI/"app.html").read_text(encoding="utf-8")
                raw=raw.replace("__GROUNDS_CSRF__",html.escape(self.csrf.token(actor),quote=True))
                return self._response(start_response,"200 OK",raw.encode("utf-8"),
                                      "text/html; charset=utf-8")
            if path in ("/grounds/app.css","/grounds/app.js"):
                filename="app.css" if path.endswith(".css") else "app.js"
                media="text/css; charset=utf-8" if filename.endswith("css") else "text/javascript; charset=utf-8"
                return self._response(start_response,"200 OK",(_UI/filename).read_bytes(),media)
            return self._response(start_response,"200 OK" if method=="GET" else "201 Created",result)
        except AccessDenied:
            return self._response(start_response,"404 Not Found",{"error":"resource_unavailable"})
        except (GroundsBadRequest,GroundsConflict,ValueError) as exc:
            if isinstance(exc,GroundsBadRequest):
                return self._response(start_response,"400 Bad Request",{"error":"invalid_request"})
            return self._response(start_response,"409 Conflict",{"error":"state_or_input_conflict"})
        except Exception:
            # No user data, file path, secret, traceback or other tenant IDs in errors.
            return self._response(start_response,"503 Service Unavailable",{"error":"service_unavailable"})

    def dispatch(self,method,path,actor,environ,body):
        if path in ("/grounds","/grounds/app.css","/grounds/app.js"):
            return None
        if method=="GET":
            if path=="/grounds/api/me":
                return {"role":actor.role,"property_refs":sorted(actor.property_refs),
                        "unit_refs":sorted(actor.unit_refs) if actor.role=="resident" else [],
                        "session_authenticated":True,"expires_at":actor.expires_at,
                        "payment_connected":False,"notification_delivery_connected":False}
            if path=="/grounds/api/workspace":
                q=_query(environ,{"property_ref"},{"unit_ref"})
                return build_workspace(
                    actor,self.ops,property_ref=_ref(q["property_ref"],"property_ref"),
                    unit_ref=_ref(q["unit_ref"],"unit_ref") if "unit_ref" in q else None)
            if path=="/grounds/api/work":
                q=_query(environ,{"work_ref"})
                return self.ops.get_work_order(actor,work_ref=_ref(q["work_ref"],"work_ref"))
            if path=="/grounds/api/appointment":
                q=_query(environ,{"appointment_ref"})
                return self.communications.appointment(actor,appointment_ref=_ref(q["appointment_ref"],"appointment_ref"))
            if path=="/grounds/api/appointments":
                q=_query(environ,{"work_ref"})
                work_ref=_ref(q["work_ref"],"work_ref")
                return {"work_ref":work_ref,"appointments":self.communications.appointments_for_work(actor,work_ref=work_ref),
                        "entry_consent_granted":False,"external_dispatch_confirmed":False}
            if path=="/grounds/api/entry-preference":
                q=_query(environ,{"work_ref"})
                return self.safety.entry_preference(actor,work_ref=_ref(q["work_ref"],"work_ref"))
        if path=="/grounds/api/work":
            _exact(body,{"property_ref","unit_ref","category","description","emergency_flag","entry_permission"})
            if type(body["emergency_flag"]) is not bool:
                raise GroundsBadRequest("Invalid urgency")
            intake=MaintenanceIntake(
                _ref(body["property_ref"],"property_ref"),
                _ref(body["unit_ref"],"unit_ref"),
                _bounded_text(body["category"],"category",80),
                _bounded_text(body["description"],"description",2000),
                body["emergency_flag"],
                _bounded_text(body["entry_permission"],"entry_permission",32),
            )
            work_ref=self._resource_ref(
                actor,"work",_idempotency_key(environ),intake.property_ref,intake.unit_ref,
            )
            try:
                return self.ops.submit_maintenance(actor,work_ref=work_ref,intake=intake)
            except GroundsConflict:
                # Unique resource ref makes uncertain-network retries safe after
                # first commit; no stale/other-lease data is returned.
                existing=self.ops.get_work_order(actor,work_ref=work_ref)
                expected={
                    "property_ref":intake.property_ref,"unit_ref":intake.unit_ref,
                    "created_by":actor.subject_ref,"category":intake.category,
                    "description":intake.description,
                    "emergency_flag":int(intake.emergency_flag),
                    "entry_permission":intake.entry_permission,
                }
                if any(existing.get(key)!=value for key,value in expected.items()):
                    raise GroundsConflict("idempotency key reused with different request")
                return {"work_ref":work_ref,"state":existing["state"],
                        "emergency_flag":bool(existing["emergency_flag"]),
                        "emergency_dispatch_confirmed":False,"notification_sent":False,
                        "replayed":True}
        if path=="/grounds/api/notice-read":
            _exact(body,{"property_ref","unit_ref","notice_ref"})
            return self.communications.mark_notice_read(
                actor,property_ref=_ref(body["property_ref"],"property_ref"),
                unit_ref=_ref(body["unit_ref"],"unit_ref"),
                notice_ref=_ref(body["notice_ref"],"notice_ref"))
        if path=="/grounds/api/appointment/request":
            _exact(body,{"work_ref","start_at","end_at"})
            from .communications import _slot
            work_ref=_ref(body["work_ref"],"work_ref")
            start_at=_bounded_text(body["start_at"],"start_at",64)
            end_at=_bounded_text(body["end_at"],"end_at",64)
            appointment_ref=self._resource_ref(
                actor,"appointment",_idempotency_key(environ),work_ref,
            )
            try:
                return self.communications.request_appointment(
                    actor,work_ref=work_ref,appointment_ref=appointment_ref,
                    start_at=start_at,end_at=end_at)
            except GroundsConflict:
                existing=self.communications.appointment(
                    actor,appointment_ref=appointment_ref,
                )
                normalized=_slot(start_at,end_at)
                if (existing["work_ref"]!=work_ref or
                    (existing["start_at"],existing["end_at"])!=normalized):
                    raise GroundsConflict("idempotency key reused with different appointment")
                return {"appointment_ref":appointment_ref,"state":existing["state"],
                        "revision":existing["revision"],"dispatch_confirmed":False,
                        "entry_consent_granted":False,"replayed":True}
        if path=="/grounds/api/appointment/propose":
            _exact(body,{"appointment_ref","start_at","end_at","expected_revision"})
            return self.communications.propose_appointment(
                actor,appointment_ref=_ref(body["appointment_ref"],"appointment_ref"),
                start_at=_bounded_text(body["start_at"],"start_at",64),
                end_at=_bounded_text(body["end_at"],"end_at",64),
                expected_revision=_revision(body["expected_revision"]))
        if path=="/grounds/api/appointment/accept":
            _exact(body,{"appointment_ref","expected_revision"})
            return self.communications.accept_appointment(
                actor,appointment_ref=_ref(body["appointment_ref"],"appointment_ref"),
                expected_revision=_revision(body["expected_revision"]))
        if path=="/grounds/api/appointment/cancel":
            _exact(body,{"appointment_ref","expected_revision"})
            return self.communications.cancel_appointment(
                actor,appointment_ref=_ref(body["appointment_ref"],"appointment_ref"),
                expected_revision=_revision(body["expected_revision"]))
        if path=="/grounds/api/urgency/review":
            _exact(body,{"work_ref","assessed_urgency"})
            return self.safety.acknowledge_urgency(
                actor,work_ref=_ref(body["work_ref"],"work_ref"),
                assessed_urgency=_bounded_text(body["assessed_urgency"],"assessed_urgency",24))
        if path=="/grounds/api/work/transition":
            _exact(body,{"work_ref","next_state","expected_revision"})
            return self.ops.advance_work_order(
                actor,work_ref=_ref(body["work_ref"],"work_ref"),
                next_state=_bounded_text(body["next_state"],"next_state",32),
                expected_revision=_revision(body["expected_revision"]))
        if path=="/grounds/api/work/entry-preference":
            _exact(body,{"work_ref","preference","expected_revision"})
            return self.safety.record_entry_preference(
                actor,work_ref=_ref(body["work_ref"],"work_ref"),
                preference=_bounded_text(body["preference"],"preference",32),
                expected_revision=_revision(body["expected_revision"]))
        raise GroundsBadRequest("Unknown request")
