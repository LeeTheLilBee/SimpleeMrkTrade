"""BuyBox owner workspace: real, persistent manual acquisition intake.

Run: BUYBOX_PASSWORD_HASH='<werkzeug scrypt hash>' BUYBOX_SECRET_KEY='<random>'
     BUYBOX_DB_PATH='/private/path/buybox.sqlite3' python -m buybox.app

Local-only by default. Production public exposure requires Tower integration,
TLS, encrypted protected file storage and deployment hardening.
"""
from __future__ import annotations
import os
import secrets
import stat
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timezone, timedelta
from functools import wraps
from contextlib import contextmanager
from pathlib import Path

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for, send_file)
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

from .core import (new_opportunity, add_evidence, evaluate, soulaana_brief,
                   scenario_calculation, money, LIFECYCLE)
from .discovery import filter_opportunities, duplicate_candidates
from .registry import VERTICALS, get_vertical
from .store import connect, save, load, list_opportunities, activity, history
from .workflow import transition, gate_report, invalidate_on_change
from .documents import PrivateDocumentStore
from .dealroom import new_task, update_task, record_negotiation, current_tasks
from .workflow import add_decision_snapshot
from .soulaana import context as soulaana_context, INTENTS as SOULAANA_INTENTS
from .atm import register_machine
from .focus import build_focus
from .hosted_auth import (prepare_hosted_runtime, exact_receiver_origin,
    exact_tower_bootstrap_transport,
    require_verified_session, owner_session_claims, HostedAuthError)
from .tower_owner_receiver import (verify_tower_buybox_owner_handoff,
    consume_verified_handoff, TowerBuyBoxHandoffError)
from .tower_session_store import (create_owner_session,read_owner_session,
    revoke_owner_session)
from .tower_evidence import freeze_local_evidence_snapshot, HandoffPreparationError
from .saved_search import (normalize_filters, create_saved_search, saved_searches,
    get_saved_search, latest_check, run_saved_search, archive_saved_search)
from .claim_register import (record_source_claim, record_owner_document_review,
    integrity_report, active_claims, owner_reviewed_source)
from .diligence import diligence_snapshot, create_diligence_task
from .financing import record_financing_option, financing_snapshot, FINANCING_EVIDENCE_KIND
from .insurance import (INSURANCE_EVIDENCE_KIND, SOURCE_KINDS as INSURANCE_SOURCE_KINDS,
    DOCUMENT_KINDS as INSURANCE_DOCUMENT_KINDS, COVERAGE_CODES as INSURANCE_COVERAGES,
    record_insurance_document, insurance_snapshot, project_financing_with_insurance)
from .comparables import (COMPARABLE_EVIDENCE_KIND, record_comparable,
    market_evidence_report)
from .decision_desk import decision_dossier, record_owner_research_disposition
from .red_team import record_owner_financial_stress, red_team_report, model_financial_stress
from .closing_review import closing_review_snapshot, record_local_closing_review
from .offer_lab import offer_lab_snapshot, record_offer_scenario
from .external_proof_gate import integration_readiness
from .expansion_store import ensure_schema as ensure_expansion_schema, load_thesis, save_thesis, add_record as add_intelligence_record, records as intelligence_records
from .intelligence_studio import build_portfolio_studio, build_deal_studio, what_if
from .owner_experience import (
    ensure_ux_schema, preferences as ux_preferences, set_density, mark_pulse_seen,
    record_triage, latest_triage, triage_map, universal_search, paged_opportunities,
    pulse_snapshot, integration_cockpit, revision_diff, provenance, acceptance_steps,
    record_acceptance_defect, acceptance_defects, resolve_acceptance_defect,
)

def create_app(config=None):
    app=Flask(__name__, template_folder="ui/templates", static_folder="ui/static",
              static_url_path="/buybox/static")
    app.config.update(
        SECRET_KEY=os.environ.get("BUYBOX_SECRET_KEY"),
        BUYBOX_SECRET_KEY=os.environ.get("BUYBOX_SECRET_KEY"),
        BUYBOX_AUTH_MODE=os.environ.get("BUYBOX_AUTH_MODE","local"),
        BUYBOX_PUBLIC_ORIGIN=os.environ.get("BUYBOX_PUBLIC_ORIGIN"),
        TOWER_PUBLIC_ORIGIN=os.environ.get("TOWER_PUBLIC_ORIGIN"),
        TOWER_BUYBOX_HANDOFF_SECRET=os.environ.get("TOWER_BUYBOX_HANDOFF_SECRET"),
        BUYBOX_DURABLE_MOUNT=os.environ.get("BUYBOX_DURABLE_MOUNT"),
        BUYBOX_SECURE_COOKIE=os.environ.get("BUYBOX_SECURE_COOKIE","0"),
        BUYBOX_PASSWORD_HASH=os.environ.get("BUYBOX_PASSWORD_HASH"),
        BUYBOX_DB_PATH=os.environ.get("BUYBOX_DB_PATH"),
        BUYBOX_DOCS_DIR=os.environ.get("BUYBOX_DOCS_DIR"),
        BUYBOX_DOCUMENT_KEY=os.environ.get("BUYBOX_DOCUMENT_KEY"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=os.environ.get("BUYBOX_SECURE_COOKIE","0")=="1",
        MAX_CONTENT_LENGTH=26*1024*1024,
    )
    if config:
        app.config.update(config)
    auth_mode=app.config.get("BUYBOX_AUTH_MODE")
    if auth_mode not in ("local","tower"):
        raise RuntimeError("Unsupported BuyBox authentication mode.")
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set BUYBOX_SECRET_KEY before starting BuyBox.")
    if auth_mode=="local" and not app.config.get("BUYBOX_PASSWORD_HASH"):
        raise RuntimeError("Set BUYBOX_PASSWORD_HASH for private development mode.")
    if auth_mode=="tower":
        if app.config.get("SESSION_COOKIE_SECURE") is not True:
            raise RuntimeError("Hosted session must use Secure cookies.")
        # This cannot be satisfied by environment variables alone: real trusted
        # storage/restore and live Tower session verifier adapters are required.
        try:
            prepare_hosted_runtime(app.config)
        except HostedAuthError as exc:
            raise RuntimeError(str(exc)) from exc
        app.permanent_session_lifetime=timedelta(minutes=15)
    if not app.config.get("BUYBOX_DB_PATH"):
        raise RuntimeError("Set BUYBOX_DB_PATH to a protected persistent storage path.")
    db_path=Path(app.config["BUYBOX_DB_PATH"]).expanduser()
    if not db_path.parent.is_dir():
        raise RuntimeError("BUYBOX_DB_PATH parent must already exist and be access-controlled.")
    if db_path.exists() and db_path.is_symlink():
        raise RuntimeError("Refusing symlink database path.")
    if stat.S_IMODE(db_path.parent.stat().st_mode) & 0o077:
        raise RuntimeError("Database parent directory must be private (chmod 700).")
    if db_path.exists() and stat.S_IMODE(db_path.stat().st_mode) & 0o077:
        raise RuntimeError("Existing database must exclude group/other access (chmod 600).")
    os.umask(0o077)
    app.config["BUYBOX_DB_PATH"]=str(db_path)
    if not app.config.get("BUYBOX_DOCS_DIR") or not app.config.get("BUYBOX_DOCUMENT_KEY"):
        raise RuntimeError("Set BUYBOX_DOCS_DIR and BUYBOX_DOCUMENT_KEY for protected document intake.")
    docstore=PrivateDocumentStore(app.config["BUYBOX_DOCS_DIR"],
                                  app.config["BUYBOX_DOCUMENT_KEY"])
    db=connect(str(db_path));ensure_expansion_schema(db);ensure_ux_schema(db);db.close()

    @app.after_request
    def no_cache(response):
        response.headers["Cache-Control"]="no-store"
        if auth_mode=="tower":
            response.headers["Strict-Transport-Security"]="max-age=31536000"
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["Content-Security-Policy"]=(
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'")
        return response

    @contextmanager
    def db():
        # sqlite3.Connection.__exit__ commits/rolls back but does NOT close a
        # connection. Close it explicitly on every route, including exceptions.
        connection = connect(app.config["BUYBOX_DB_PATH"])
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def owner_actor(conn):
        # Never let an HTTP form supply the actor of a stored search or check.
        if auth_mode != "tower":
            return "local_owner"
        claims=read_owner_session(conn,session.get("tower_session_handle"),
                                  now_epoch=int(datetime.now(timezone.utc).timestamp()))
        if claims is None:
            abort(403,"Tower owner session required")
        return claims["actor_ref"]

    def login_required(fn):
        @wraps(fn)
        def wrapped(*args,**kwargs):
            if session.get("buybox_owner") is not True:
                if auth_mode=="tower":
                    abort(403,"Tower owner session required")
                return redirect(url_for("login"))
            if auth_mode=="tower":
                now_epoch=int(datetime.now(timezone.utc).timestamp())
                with db() as conn:
                    claims=read_owner_session(conn,session.get("tower_session_handle"),
                                              now_epoch=now_epoch)
                if claims is None:
                    session.clear()
                    abort(403,"Tower owner session is unavailable or expired")
                try:
                    require_verified_session(app.config["TOWER_SESSION_VERIFIER"],
                                             claims,now_epoch=now_epoch)
                except HostedAuthError:
                    with db() as conn:
                        revoke_owner_session(conn,session.get("tower_session_handle"),
                                             now_epoch=now_epoch)
                    session.clear()
                    abort(403,"Tower owner session is unavailable or revoked")
            return fn(*args,**kwargs)
        return wrapped

    @app.context_processor
    def csrf_context():
        # The pre-auth Tower bootstrap must not create a BuyBox browser session.
        if request.endpoint=="tower_browser_bootstrap":
            return {"csrf_token":None, "verticals":VERTICALS,
                    "tower_governed":True,
                    "tower_return_url":app.config["TOWER_PUBLIC_ORIGIN"]+
                        "/tower/access-home"}
        if "csrf" not in session:
            session["csrf"]=secrets.token_hex(32)
        shell={"csrf_token": session["csrf"], "verticals": VERTICALS,
                "tower_governed": auth_mode=="tower",
                "tower_return_url": (app.config["TOWER_PUBLIC_ORIGIN"]+
                    "/tower/access-home" if auth_mode=="tower" else None),
                "owner_pulse":None,"density_mode":"STANDARD"}
        if session.get("buybox_owner") is True:
            with db() as conn:
                shell["owner_pulse"]=pulse_snapshot(conn)
                shell["density_mode"]=ux_preferences(conn)["density"]
        return shell

    @app.before_request
    def guard():
        if request.endpoint in ("tower_browser_bootstrap","tower_owner_exchange"):
            return
        if request.method not in ("GET","HEAD","OPTIONS"):
            value=request.form.get("csrf_token","")
            expected=session.get("csrf","")
            if not expected or not secrets.compare_digest(value,expected):
                abort(400,"Invalid CSRF token")

    @app.errorhandler(400)
    def owner_bad_request(error):
        return render_template("error.html",status=400,title="BuyBox could not use that request.",
            message=getattr(error,"description","The request was not valid."),
            guidance="Check the fields or return to the owner view. No deal state was advanced."),400

    @app.errorhandler(403)
    def owner_forbidden(error):
        return render_template("error.html",status=403,title="This BuyBox action is blocked.",
            message=getattr(error,"description","Current owner authority could not be verified."),
            guidance="Use the current Tower/BuyBox session or return to the previous owner workspace. A blocked action does not create approval."),403

    @app.errorhandler(404)
    def owner_not_found(error):
        return render_template("error.html",status=404,title="That BuyBox record or room was not found.",
            message="The requested record may not exist in the current workspace.",
            guidance="Search BuyBox by deal name, location, source, evidence, or note."),404

    @app.route("/login", methods=["GET","POST"])
    def login():
        if auth_mode=="tower":
            abort(404,"Standalone BuyBox login is disabled")
        if request.method=="POST":
            password=request.form.get("password","")
            if check_password_hash(app.config["BUYBOX_PASSWORD_HASH"],password):
                session.clear()
                session["buybox_owner"]=True
                session["csrf"]=secrets.token_hex(32)
                return redirect(url_for("index"))
            flash("Login failed. Check your credentials.","error")
        return render_template("login.html")

    @app.post("/logout")
    @login_required
    def logout():
        if auth_mode=="tower":
            with db() as conn:
                revoke_owner_session(conn,session.get("tower_session_handle"),
                    now_epoch=int(datetime.now(timezone.utc).timestamp()))
        session.clear()
        if auth_mode=="tower":
            return redirect(app.config["TOWER_PUBLIC_ORIGIN"]+"/tower/access-home",code=303)
        return redirect(url_for("login"))

    @app.post("/tower/bootstrap")
    def tower_browser_bootstrap():
        """Tower-origin bridge into the existing same-origin owner exchange.

        The signed bearer remains POST-body only. It is verified before being
        rendered into a no-store BuyBox-origin page, never placed in a URL,
        cookie, localStorage, or server log field by this route.
        """
        if auth_mode!="tower":
            abort(404)
        if request.content_length is None or not 0<request.content_length<=8192:
            abort(413,"Tower bootstrap payload size invalid")
        if (not exact_tower_bootstrap_transport(
                request,tower_origin=app.config["TOWER_PUBLIC_ORIGIN"],
                buybox_origin=app.config["BUYBOX_PUBLIC_ORIGIN"])
                or request.mimetype!="application/x-www-form-urlencoded"
                or set(request.form)!={"handoff"}
                or len(request.form.getlist("handoff"))!=1):
            abort(403,"Invalid Tower bootstrap transport")
        token=request.form.get("handoff","")
        try:
            verify_tower_buybox_owner_handoff(
                token,shared_secret=app.config["TOWER_BUYBOX_HANDOFF_SECRET"],
                now_epoch=int(datetime.now(timezone.utc).timestamp()))
        except TowerBuyBoxHandoffError:
            abort(403,"Tower bootstrap not verified")
        response=app.make_response(render_template(
            "tower_bootstrap.html",handoff=token))
        response.headers["Cache-Control"]="private, no-store, max-age=0"
        response.headers["Pragma"]="no-cache"
        return response

    @app.post("/tower/owner-exchange")
    def tower_owner_exchange():
        """A narrowly scoped pre-render exchange, not an independent login.

        This code is unreachable in production until certified, injected
        Tower session introspection and protected hosting are configured.
        The signed one-time token arrives only in an exact-origin POST body.
        """
        if auth_mode!="tower":
            abort(404)
        if request.content_length is None or not 0<request.content_length<=8192:
            abort(413,"Tower exchange payload size invalid")
        if (not exact_receiver_origin(request,app.config["BUYBOX_PUBLIC_ORIGIN"])
                or request.mimetype!="application/x-www-form-urlencoded"
                or set(request.form)!={"handoff"}
                or len(request.form.getlist("handoff"))!=1):
            abort(403,"Invalid Tower exchange transport")
        token=request.form.get("handoff","")
        now_epoch=int(datetime.now(timezone.utc).timestamp())
        try:
            verified=verify_tower_buybox_owner_handoff(token,
                shared_secret=app.config["TOWER_BUYBOX_HANDOFF_SECRET"],
                now_epoch=now_epoch)
            claims=owner_session_claims(verified)
            active=require_verified_session(app.config["TOWER_SESSION_VERIFIER"],
                claims,now_epoch=now_epoch)
        except (TowerBuyBoxHandoffError,HostedAuthError):
            abort(403,"Tower exchange not verified")
        with db() as conn:
            if not consume_verified_handoff(conn,verified):
                abort(403,"Tower exchange already consumed")
            handle=create_owner_session(conn,claims,now_epoch=now_epoch,
                                        expires_at_epoch=active["expires_at_epoch"])
        # Consumption and server-side owner session are persisted before a
        # browser cookie is issued. Never serialize Tower IDs into the cookie.
        session.clear()
        session.permanent=True
        session["buybox_owner"]=True
        session["tower_session_handle"]=handle
        session["csrf"]=secrets.token_hex(32)
        return redirect(url_for("index"),code=303)

    @app.get("/")
    @login_required
    def index():
        current_vertical=request.args.get("vertical","")
        if current_vertical and current_vertical not in VERTICALS:
            abort(400,"Unknown category")
        q=request.args.get("q","").strip()[:120]
        try: page=max(1,int(request.args.get("page","1")))
        except ValueError: abort(400,"Invalid page")
        with db() as conn:
            result=paged_opportunities(conn,vertical=current_vertical or None,
                                       query=q,page=page,page_size=24)
            triage=triage_map(conn,[op["id"] for op in result["items"]])
        panels=[{"record":op,"analysis":evaluate(op),"triage":triage.get(op["id"])}
                for op in result["items"]]
        return render_template("index.html",records=panels,total=result["total"],
            current_vertical=current_vertical,q=q,page=result["page"],pages=result["pages"])

    @app.get("/command")
    @login_required
    def command_center():
        q=request.args.get("q","").strip()[:160]
        with db() as conn:
            results=universal_search(conn,q,limit=50) if q else []
        return render_template("owner_command.html",q=q,results=results)

    @app.post("/owner-density")
    @login_required
    def owner_density():
        with db() as conn:
            try: set_density(conn,request.form.get("density"))
            except ValueError: abort(400,"Invalid density")
        return redirect(request.form.get("return_to") or url_for("focus"),code=303)

    @app.post("/pulse/seen")
    @login_required
    def pulse_seen():
        with db() as conn: mark_pulse_seen(conn)
        return redirect(request.form.get("return_to") or url_for("focus"),code=303)

    @app.post("/bulk-triage")
    @login_required
    def bulk_triage():
        ids=request.form.getlist("opportunity_id")
        if not 1<=len(ids)<=50 or len(set(ids))!=len(ids):
            abort(400,"Choose one to fifty distinct opportunities")
        state=request.form.get("state","")
        note=request.form.get("note","")
        with db() as conn:
            actor=owner_actor(conn)
            try:
                for oid in ids: record_triage(conn,oid,state,note,actor)
            except ValueError as exc:
                abort(400,str(exc))
        return redirect(request.form.get("return_to") or url_for("index"),code=303)

    @app.get("/integration-cockpit")
    @login_required
    def integration_cockpit_room():
        with db() as conn:
            ops=list_opportunities(conn)
        return render_template("integration_cockpit.html",
            systems=integration_cockpit(ops),opportunities=ops)

    @app.get("/opportunities/<oid>/provenance")
    @login_required
    def provenance_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            diff=revision_diff(conn,oid)
        analysis=evaluate(op)
        return render_template("provenance.html",op=op,analysis=analysis,
            rows=provenance(op,analysis),diff=diff)

    @app.route("/opportunities/<oid>/field",methods=["GET","POST"])
    @login_required
    def field_mode(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            if request.method=="POST":
                title=request.form.get("title","").strip()[:160]
                note=request.form.get("note","").strip()[:2000]
                if not title or not note: abort(400,"Field title and note required")
                add_intelligence_record(conn,oid,"QUICK_CAPTURE",
                    {"title":title,"note":note,"capture_mode":"FIELD"},
                    actor_ref=owner_actor(conn))
                return redirect(url_for("field_mode",oid=oid),code=303)
            captures=[r for r in intelligence_records(conn,opportunity_id=oid,kind="QUICK_CAPTURE")][:20]
        return render_template("field_mode.html",op=op,captures=captures)

    @app.post("/opportunities/<oid>/field/<record_id>/follow-up")
    @login_required
    def field_followup(oid,record_id):
        due=request.form.get("due_date","")
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            row=conn.execute("""SELECT payload_json FROM buybox_intelligence_records
                WHERE id=? AND opportunity_id=? AND kind='QUICK_CAPTURE'""",
                (record_id,oid)).fetchone()
            if row is None: abort(404)
            import json as _json
            payload=_json.loads(row["payload_json"])
            title=("Follow up: "+str(payload.get("title") or "field note"))[:180]
            try:
                revised,task=new_task(op,title=title,due_date=due,
                    owner=owner_actor(conn),source_reference="FIELD_CAPTURE:"+record_id,
                    notes=str(payload.get("note") or "")[:1000])
            except ValueError as exc: abort(400,str(exc))
            save(conn,revised,"FieldCapturePromotedToTask",
                {"capture_id":record_id,"task_id":task["id"],"evidence_promoted":False},
                expected_revision=op["version"])
        return redirect(url_for("deal_room",oid=oid),code=303)

    @app.get("/acceptance")
    @login_required
    def owner_acceptance():
        with db() as conn: defects=acceptance_defects(conn)
        return render_template("owner_acceptance.html",steps=acceptance_steps(),defects=defects)

    @app.post("/acceptance/defects")
    @login_required
    def add_acceptance_defect():
        with db() as conn:
            try:
                record_acceptance_defect(conn,area=request.form.get("area"),
                    severity=request.form.get("severity"),title=request.form.get("title"),
                    detail=request.form.get("detail"),actor_ref=owner_actor(conn))
            except ValueError as exc: abort(400,str(exc))
        return redirect(url_for("owner_acceptance"),code=303)

    @app.post("/acceptance/defects/<int:defect_id>/resolve")
    @login_required
    def resolve_defect(defect_id):
        with db() as conn:
            try: resolve_acceptance_defect(conn,defect_id,actor_ref=owner_actor(conn))
            except ValueError as exc: abort(400,str(exc))
        return redirect(url_for("owner_acceptance"),code=303)

    @app.get("/intelligence")
    @login_required
    def intelligence_home():
        with db() as conn:
            opportunities=list_opportunities(conn)
            thesis=load_thesis(conn)
            studio=build_portfolio_studio(
                opportunities,thesis,
                lambda oid:intelligence_records(conn,opportunity_id=oid))
            radar=[{"definition":saved,"latest":latest_check(conn,saved["id"])}
                   for saved in saved_searches(conn)]
        return render_template("intelligence_portfolio.html",
            opportunities=opportunities,thesis=thesis,studio=studio,radar=radar)

    @app.post("/intelligence/thesis")
    @login_required
    def save_intelligence_thesis():
        lines=lambda name:[x.strip() for x in request.form.get(name,"").splitlines() if x.strip()]
        with db() as conn:
            save_thesis(conn,priorities=lines("priorities"),
                preferred_regions=lines("preferred_regions"),avoid=lines("avoid"),
                sequence=lines("sequence"),notes=request.form.get("notes",""))
        return redirect(url_for("intelligence_home"),code=303)

    @app.post("/intelligence/inbox")
    @login_required
    def intelligence_inbox():
        vertical=request.form.get("vertical","")
        if vertical not in VERTICALS: abort(400,"Invalid category")
        title=request.form.get("title","").strip()[:160]
        note=request.form.get("note","").strip()[:4000]
        if not title or not note: abort(400,"Title and intake note required")
        url=request.form.get("source_url","").strip()[:500]
        if url:
            from .discovery import canonical_url
            if not canonical_url(url): abort(400,"Source must be HTTP(S)")
        op=new_opportunity(vertical,title,None,
            {"url":url,"type":"OWNER_INBOX"} if url else None,{})
        op["owner_notes"].append({"type":"OPPORTUNITY_INBOX","note":note,
                                  "recorded_at":datetime.now(timezone.utc).isoformat()})
        with db() as conn:
            existing=list_opportunities(conn)
            candidates=duplicate_candidates(op,existing)
            if candidates: op["duplicate_candidates"]=candidates
            op=save(conn,op,"OpportunityInboxCreated",
                    {"actor":owner_actor(conn),"source_url_present":bool(url)})
        return redirect(url_for("intelligence_deal",oid=op["id"]),code=303)

    @app.post("/intelligence/what-if")
    @login_required
    def intelligence_what_if():
        ids=request.form.getlist("opportunity_id")
        if not 1<=len(ids)<=8 or len(set(ids))!=len(ids):
            abort(400,"Choose one to eight distinct opportunities")
        with db() as conn:
            ops=[load(conn,x) for x in ids]
        if any(x is None for x in ops): abort(404)
        return render_template("intelligence_what_if.html",ops=ops,report=what_if(ops))

    @app.get("/opportunities/<oid>/intelligence")
    @login_required
    def intelligence_deal(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            opportunities=list_opportunities(conn)
            thesis=load_thesis(conn)
            records=intelligence_records(conn,opportunity_id=oid)
            events=activity(conn,oid)
        by_kind={kind:[] for kind in (
            "COUNTERPARTY","CAPEX_ITEM","MARKET_OBSERVATION","PERFORMANCE_ACTUAL",
            "AUTOPSY","QUICK_CAPTURE","TEAM_LANE","COMMUNITY_IMPACT")}
        for item in records: by_kind[item["kind"]].append(item)
        return render_template("intelligence_deal.html",op=op,
            studio=build_deal_studio(op,opportunities,thesis,records,events),
            records_by_kind=by_kind)

    @app.get("/opportunities/<oid>/decision-packet")
    @login_required
    def decision_packet_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            opportunities=list_opportunities(conn)
            thesis=load_thesis(conn)
            records=intelligence_records(conn,opportunity_id=oid)
            events=activity(conn,oid)
        packet=build_deal_studio(op,opportunities,thesis,records,events)["ic_packet"]
        return render_template("intelligence_packet.html",op=op,packet=packet)

    @app.post("/opportunities/<oid>/intelligence/<kind>")
    @login_required
    def intelligence_record(oid,kind):
        allowed={
          "COUNTERPARTY":("name","role","note"),
          "CAPEX_ITEM":("title","severity","estimated_cost","date","note"),
          "MARKET_OBSERVATION":("title","source","observed_on","note"),
          "PERFORMANCE_ACTUAL":("period","actual_net","note"),
          "AUTOPSY":("outcome","reason"),
          "QUICK_CAPTURE":("title","note"),
          "TEAM_LANE":("role","task","status"),
          "COMMUNITY_IMPACT":("dimension","note"),
        }
        if kind not in allowed: abort(400,"Unknown intelligence record")
        payload={key:request.form.get(key,"").strip()[:2000] for key in allowed[kind]}
        if not any(payload.values()): abort(400,"Record cannot be empty")
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            add_intelligence_record(conn,oid,kind,payload,actor_ref=owner_actor(conn))
        return redirect(url_for("intelligence_deal",oid=oid),code=303)

    @app.get("/focus")
    @login_required
    def focus():
        with db() as conn:
            opportunities=list_opportunities(conn)
            snapshot=build_focus(opportunities,lambda oid:activity(conn,oid))
            triage=triage_map(conn,[op["id"] for op in opportunities])
        focus_deals=[{"id":op["id"],"name":op["name"],"vertical":op["vertical"],
                      "location":op.get("location",{}),"triage":triage[op["id"]]}
                     for op in opportunities if triage.get(op["id"],{}).get("state")=="FOCUS"]
        return render_template("focus.html",snapshot=snapshot,focus_deals=focus_deals)

    @app.get("/saved-searches")
    @login_required
    def saved_search_home():
        with db() as conn:
            records=saved_searches(conn)
            entries=[{"definition":saved,"latest":latest_check(conn,saved["id"])}
                     for saved in records]
        selected=request.args.get("vertical","")
        if selected and selected not in VERTICALS:
            abort(400,"Unknown acquisition category")
        q=request.args.get("q","")[:120]
        return render_template("saved_searches.html",entries=entries,
                               selected_vertical=selected,q=q)

    @app.post("/saved-searches")
    @login_required
    def add_saved_search():
        with db() as conn:
            record=create_saved_search(
                conn,name=request.form.get("name",""),
                filters={"vertical":request.form.get("vertical") or None,
                         "query":request.form.get("query",""),
                         "max_price":request.form.get("max_price") or None},
                actor_reference=owner_actor(conn))
        return redirect(url_for("saved_search_detail",sid=record["id"]),code=303)

    @app.get("/saved-searches/<sid>")
    @login_required
    def saved_search_detail(sid):
        with db() as conn:
            definition=get_saved_search(conn,sid)
            if definition is None: abort(404)
            latest=latest_check(conn,sid)
            matched=[]
            if latest:
                for oid in latest["result"]["match_ids"]:
                    op=load(conn,oid)
                    matched.append({"id":oid,"current_name":op["name"] if op else "Record unavailable",
                                    "last_checked":latest["current_snapshot"].get(oid)})
        return render_template("saved_search_detail.html",
            definition=definition,latest=latest,matched=matched)

    @app.post("/saved-searches/<sid>/check")
    @login_required
    def check_saved_search(sid):
        with db() as conn:
            run_saved_search(conn,sid)
        return redirect(url_for("saved_search_detail",sid=sid),code=303)

    @app.post("/saved-searches/<sid>/archive")
    @login_required
    def archive_saved_search_route(sid):
        with db() as conn:
            archive_saved_search(conn,sid,actor_reference=owner_actor(conn))
        return redirect(url_for("saved_search_home"),code=303)

    @app.post("/opportunities")
    @login_required
    def create_opportunity():
        vertical=request.form.get("vertical","")
        if vertical not in VERTICALS: abort(400,"Invalid category")
        name=request.form.get("name","").strip()[:160]
        if not name: abort(400,"A name is required")
        asking=request.form.get("asking_price","").strip()
        if asking:
            val=money(asking)
            if val is None or val<0 or val>Decimal("100000000000000"):
                abort(400,"Invalid asking price")
        else:
            asking=None
        location={"city":request.form.get("city","").strip()[:90],
                  "region":request.form.get("region","").strip()[:90]}
        src=request.form.get("source_url","").strip()[:500]
        if src:
            from .discovery import canonical_url
            if not canonical_url(src): abort(400,"Source must be an HTTP(S) URL")
        op=new_opportunity(vertical,name,asking,{"url":src,"type":"OWNER_ENTERED"} if src else None,location)
        with db() as conn:
            existing=list_opportunities(conn)
            candidates=duplicate_candidates(op,existing)
            if candidates: op["duplicate_candidates"]=candidates
            op=save(conn,op,"OpportunityCreated",{"actor":"owner","intake":"manual"})
        return redirect(url_for("opportunity",oid=op["id"]))

    @app.get("/opportunities/<oid>")
    @login_required
    def opportunity(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            events=activity(conn,oid)
            revisions=history(conn,oid)
        analysis=evaluate(op)
        return render_template("opportunity.html",op=op,analysis=analysis,
                               brief=soulaana_brief(op,analysis),events=list(reversed(events)),
                               revisions=list(reversed(revisions)),
                               manifest=get_vertical(op["vertical"]),
                               gate_options=LIFECYCLE,gate_report=gate_report)

    @app.get("/opportunities/<oid>/soulaana")
    @login_required
    def soulaana_room(oid):
        intent=request.args.get("intent","overview")
        if intent not in SOULAANA_INTENTS:
            abort(400,"Unsupported Soulaana context")
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        return render_template("soulaana.html",op=op,
            context=soulaana_context(op,intent),intents=(
            ("overview","Overview"),("evidence","Evidence"),("diligence","Diligence"),
            ("financing","Financing"),("insurance","Insurance"),("valuation","Comparable Research"),("decision","Decision"),("offer","Offer Lab"),("closing","Closing"),("economics","Economics"),("changes","What changed"),
            ("red_team","Red Team"),("next_action","Next action")))

    @app.post("/compare")
    @login_required
    def compare():
        ids=request.form.getlist("opportunity_id")
        if not 2<=len(ids)<=4 or len(set(ids))!=len(ids):
            abort(400,"Choose two to four distinct opportunities")
        with db() as conn:
            opportunities=[load(conn,oid) for oid in ids]
        if any(op is None for op in opportunities):
            abort(404)
        panels=[{"record":op,"analysis":evaluate(op)} for op in opportunities]
        return render_template("compare.html",records=panels)

    @app.get("/opportunities/<oid>/scenario")
    @login_required
    def scenario(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        rev_raw=request.args.get("revenue_factor","1")
        exp_raw=request.args.get("expense_factor","1")
        revenue_factor=money(rev_raw)
        expense_factor=money(exp_raw)
        if (revenue_factor is None or expense_factor is None or
            not Decimal("0")<=revenue_factor<=Decimal("3") or
            not Decimal("0")<=expense_factor<=Decimal("3")):
            abort(400,"Scenario multipliers must be between 0 and 3")
        baseline=scenario_calculation(op)
        stressed=scenario_calculation(op,str(revenue_factor),str(expense_factor))
        return render_template("scenario.html",op=op,baseline=baseline,
            stressed=stressed,revenue_factor=revenue_factor,
            expense_factor=expense_factor)

    def assert_red_team_original_integrity(op, model):
        # Metadata alone cannot prove that a protected original is still
        # decryptable and digest-identical. Fail closed before saving stress.
        by_id={a["id"]:a for a in op.get("artifacts",[])}
        for source in model["source_metrics"]:
            descriptor=by_id.get(source["original_id"])
            if descriptor is None or descriptor.get("sha256")!=source["original_sha256"]:
                raise ValueError("STRESS_ORIGINAL_REFERENCE_CHANGED")
            docstore.read(descriptor)

    @app.get("/opportunities/<oid>/red-team")
    @login_required
    def red_team_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        try:
            baseline=model_financial_stress(op,revenue_factor="1",expense_factor="1")
            assert_red_team_original_integrity(op,baseline)
        except ValueError:
            baseline=None
        return render_template("red_team.html",op=op,
            report=red_team_report(op),baseline=baseline)

    @app.post("/opportunities/<oid>/red-team")
    @login_required
    def record_red_team(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            incoming_model=model_financial_stress(
                op,revenue_factor=request.form.get("revenue_factor",""),
                expense_factor=request.form.get("expense_factor",""))
            assert_red_team_original_integrity(op,incoming_model)
            revised,item=record_owner_financial_stress(
                conn,op,name=request.form.get("name",""),
                rationale=request.form.get("rationale",""),
                revenue_factor=request.form.get("revenue_factor",""),
                expense_factor=request.form.get("expense_factor",""),
                actor_ref=owner_actor(conn))
            save(conn,revised,"OwnerFinancialStressRecorded",{
                "scenario_id":item["id"],
                "source_revision":item["source_opportunity_revision"],
                "source_digest":item["source_snapshot_digest"],
                "record_type":item["record_type"],
                "authorizes_purchase":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("red_team_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/deal-room")
    @login_required
    def deal_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        return render_template("dealroom.html",op=op,tasks=current_tasks(op),
                               analysis=evaluate(op))

    @app.post("/opportunities/<oid>/tasks")
    @login_required
    def record_task(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,item=new_task(op,title=request.form.get("title",""),
                due_date=request.form.get("due_date",""),
                notes=request.form.get("notes",""))
            save(conn,revised,"DealTaskCreated",{"task_id":item["id"]},
                 expected_revision=int(request.form["revision"]))
        return redirect(url_for("deal_room",oid=oid))

    @app.post("/opportunities/<oid>/tasks/<task_id>/status")
    @login_required
    def task_status(oid,task_id):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,item=update_task(op,task_id=task_id,
                status=request.form.get("status",""),
                notes=request.form.get("notes",""))
            save(conn,revised,"DealTaskStatusChanged",
                {"task_id":item["id"],"status":item["status"],"supersedes":task_id},
                expected_revision=int(request.form["revision"]))
        return redirect(url_for("deal_room",oid=oid))

    @app.post("/opportunities/<oid>/negotiations")
    @login_required
    def negotiation(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,event=record_negotiation(op,
                kind=request.form.get("kind",""),
                description=request.form.get("description",""),
                source_reference=request.form.get("source_reference",""),
                amount=request.form.get("amount",""),
                occurred_on=request.form.get("occurred_on") or None)
            save(conn,revised,"NegotiationHistoryRecorded",
                {"event_id":event["id"],"kind":event["kind"],
                 "source_reference":event["source_reference"]},
                 expected_revision=int(request.form["revision"]))
        return redirect(url_for("deal_room",oid=oid))

    @app.post("/opportunities/<oid>/decision-note")
    @login_required
    def decision_note(oid):
        reason=request.form.get("reason","").strip()[:2000]
        if not reason: abort(400,"Owner decision note required")
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised=add_decision_snapshot(op,evaluate(op),
                      actor_reference="local_owner",reason=reason)
            save(conn,revised,"AnalyticalOwnerDecisionRecorded",
                {"kind":"ANALYTICAL_OWNER_NOTE","authorized_purchase":False},
                expected_revision=int(request.form["revision"]))
        return redirect(url_for("deal_room",oid=oid))

    @app.post("/opportunities/<oid>/atm/machines")
    @login_required
    def add_atm_machine(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            if op["vertical"]!="atm": abort(400,"ATM opportunity required")
            revised,machine=register_machine(op,
                serial_number=request.form.get("serial_number",""),
                model=request.form.get("model",""),
                location_name=request.form.get("location_name",""),
                ownership=request.form.get("ownership","UNKNOWN"),
                evidence_id=request.form.get("ownership_evidence_id") or None,
                source_reference=request.form.get("source_reference",""))
            save(conn,revised,"ATMMachineRecorded",{
                "machine_id":machine["record_id"],
                "serial_number":machine["serial_number"],
                "source_reference":machine["source_reference"]},
                expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.get("/opportunities/<oid>/decision-desk")
    @login_required
    def decision_desk_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        return render_template("decision_desk.html",op=op,
            report=decision_dossier(op),
            evidence_refs=[e for e in op.get("evidence",[]) if e.get("id")])

    @app.post("/opportunities/<oid>/decision-desk/notes")
    @login_required
    def research_disposition(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,record=record_owner_research_disposition(
                conn,op,choice=request.form.get("choice",""),
                rationale=request.form.get("rationale",""),
                actor_ref=owner_actor(conn),
                cited_evidence_ids=request.form.getlist("evidence_id"))
            save(conn,revised,"OwnerResearchDispositionRecorded",{
                "record_id":record["id"],"choice":record["choice"],
                "source_opportunity_revision":record["source_opportunity_revision"],
                "source_snapshot_digest":record["source_snapshot_digest"],
                "purchase_authorized":False,"external_action":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("decision_desk_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/offer-lab")
    @login_required
    def offer_lab_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        return render_template("offer_lab.html",op=op,report=offer_lab_snapshot(op))

    @app.post("/opportunities/<oid>/offer-lab/scenarios")
    @login_required
    def offer_lab_record(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,record=record_offer_scenario(
                conn,op,actor_ref=owner_actor(conn),
                name=request.form.get("name",""),
                proposed_purchase_price=request.form.get("proposed_purchase_price",""),
                earnest_money=request.form.get("earnest_money",""),
                requested_seller_credit=request.form.get("requested_seller_credit",""),
                due_diligence_days=request.form.get("due_diligence_days",""),
                financing_contingency=("financing_contingency" in request.form),
                planned_closing_date=request.form.get("planned_closing_date",""),
                financing_option_id=request.form.get("financing_option_id",""),
                insurance_record_id=request.form.get("insurance_record_id",""),
                rationale=request.form.get("rationale",""),
                terms_note=request.form.get("terms_note",""),
                supersedes=request.form.get("supersedes",""),
                correction_reason=request.form.get("correction_reason",""))
            save(conn,revised,"OwnerOfferScenarioRecorded",{
                "scenario_id":record["id"],
                "source_opportunity_revision":record["source_opportunity_revision"],
                "source_snapshot_digest":record["source_snapshot_digest"],
                "transmitted_to_seller":False,"loi_created":False,
                "tower_authorization":False,"teller_readiness":"UNKNOWN"},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("offer_lab_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/integration-readiness")
    @login_required
    def integration_readiness_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        return render_template("integration_readiness.html",op=op,
            report=integration_readiness(op))

    @app.get("/opportunities/<oid>/closing-review")
    @login_required
    def closing_review_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        report=closing_review_snapshot(op)
        return render_template("closing_review.html",op=op,report=report)

    @app.post("/opportunities/<oid>/closing-review")
    @login_required
    def closing_review_record(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,record=record_local_closing_review(
                conn,op,actor_ref=owner_actor(conn),
                rationale=request.form.get("rationale",""),
                financing_option_id=request.form.get("financing_option_id",""),
                insurance_record_id=request.form.get("insurance_record_id",""),
                planned_closing_date=request.form.get("planned_closing_date",""))
            save(conn,revised,"ClosingReviewRecorded",{
                "closing_review_id":record["id"],
                "source_opportunity_revision":record["source_opportunity_revision"],
                "source_snapshot_digest":record["source_snapshot_digest"],
                "selected_financing_option_id":record["selected_financing_option_id"],
                "selected_insurance_record_id":record["selected_insurance_record_id"],
                "authorizes_closing":False,"money_moved":False,
                "tower_authorization":False,"teller_readiness":"UNKNOWN"},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("closing_review_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/valuation")
    @login_required
    def valuation_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        documents=[e for e in op.get("evidence",[])
            if e.get("kind")==COMPARABLE_EVIDENCE_KIND
            and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED")
            and e.get("artifact_id")
            and any(a.get("id")==e["artifact_id"] for a in op.get("artifacts",[]))]
        from .comparables import BASIS_BY_VERTICAL, SOURCE_KINDS
        return render_template("valuation.html",op=op,
            report=market_evidence_report(op),documents=documents,
            bases=BASIS_BY_VERTICAL[op["vertical"]],
            kinds=sorted(SOURCE_KINDS),
            artifacts={a["id"]:a for a in op.get("artifacts",[])})

    @app.post("/opportunities/<oid>/valuation/comparables")
    @login_required
    def record_market_comparable(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            e=next((e for e in op.get("evidence",[])
                    if e.get("id")==request.form.get("evidence_id")),None)
            original=next((a for a in op.get("artifacts",[])
                           if e and a.get("id")==e.get("artifact_id")),None)
            if original is not None:
                try: docstore.read(original)
                except ValueError:
                    abort(409,"Comparable original missing or fails integrity checks")
            fields=("evidence_id","subject_id","market","source_kind","basis",
                    "price","denominator","event_date","locator","supersedes",
                    "correction_reason")
            kwargs={k:request.form.get(k,"") for k in fields}
            revised,item=record_comparable(op,actor_ref=owner_actor(conn),**kwargs)
            save(conn,revised,"ComparableSourceRecorded",{
                "record_id":item["id"],"source_sha256":item["source_sha256"],
                "source_artifact_id":item["source_artifact_id"],
                "source_kind":item["source_kind"],
                "basis":item["basis"],"supersedes":item["supersedes"],
                "independent_appraisal":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("valuation_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/insurance")
    @login_required
    def insurance_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        artifacts={a["id"]:a for a in op.get("artifacts",[])}
        originals=[e for e in op.get("evidence",[])
                   if e.get("kind") in INSURANCE_SOURCE_KINDS
                   and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED")
                   and e.get("artifact_id") in artifacts]
        report=insurance_snapshot(op)
        from .financing import current_options
        financing=current_options(op)
        for entry in report["records"]:
            entry["financing_overlays"]=(
                [project_financing_with_insurance(op,entry["record"],q)
                 for q in financing]
                if entry["record"]["annual_premium"] is not None else []
            )
        return render_template("insurance.html",op=op,report=report,
            originals=originals,artifacts=artifacts,
            document_kinds=sorted(INSURANCE_DOCUMENT_KINDS),
            coverage_codes=sorted(INSURANCE_COVERAGES),
            financing_labels={q["id"]:q["lender_label"]+" / "+q["program_label"]
                              for q in financing})

    @app.post("/opportunities/<oid>/insurance/records")
    @login_required
    def insurance_record(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            # Verify the encrypted original's authenticated bytes and digest
            # before allowing the source to support an owner transcription.
            evidence_id=request.form.get("evidence_id","")
            linked=next((e for e in op.get("evidence",[])
                         if e.get("id")==evidence_id),None)
            artifact=next((a for a in op.get("artifacts",[])
                           if linked and a.get("id")==linked.get("artifact_id")),None)
            if artifact is not None:
                try: docstore.read(artifact)
                except ValueError:
                    abort(409,"Original insurance document unavailable or integrity check failed")
            fields=("evidence_id","document_kind","carrier_label","broker_label",
                    "source_locator","source_date","quote_valid_until",
                    "effective_date","expiration_date","planned_closing_date",
                    "annual_premium","upfront_premium_due","limits_note",
                    "deductible_note","exclusion_note","supersedes","correction_reason")
            data={key:request.form.get(key,"") for key in fields}
            data["coverage_codes"]=request.form.getlist("coverage_codes")
            data["upfront_in_financing_costs"]="upfront_in_financing_costs" in request.form
            data["annual_in_operating_expenses"]="annual_in_operating_expenses" in request.form
            revised,item=record_insurance_document(op,actor_ref=owner_actor(conn),**data)
            save(conn,revised,"InsuranceDocumentRecorded",{
                "insurance_record_id":item["id"],
                "source_artifact_id":item["source_artifact_id"],
                "source_sha256":item["source_sha256"],
                "document_kind":item["document_kind"],
                "supersedes":item["supersedes"],
                "coverage_in_force":"UNKNOWN","insurer_contacted":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("insurance_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/financing")
    @login_required
    def financing_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        originals=[e for e in op.get("evidence",[])
            if e.get("kind")==FINANCING_EVIDENCE_KIND
            and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED")
            and e.get("artifact_id")
            and any(a.get("id")==e["artifact_id"] for a in op.get("artifacts",[]))]
        return render_template("financing.html",op=op,
            report=financing_snapshot(op),originals=originals,
            artifacts={a["id"]:a for a in op.get("artifacts",[])})

    @app.post("/opportunities/<oid>/financing/options")
    @login_required
    def financing_option(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            # Verify the real encrypted original still exists and matches its
            # stored digest before allowing its financing terms into the dossier.
            linked=next((e for e in op.get("evidence",[])
                         if e.get("id")==request.form.get("evidence_id")),None)
            original=next((a for a in op.get("artifacts",[])
                           if linked and a.get("id")==linked.get("artifact_id")),None)
            if original is not None:
                try:
                    docstore.read(original)
                except ValueError:
                    abort(409,"Original financing document is unavailable or fails integrity checks")
            keys=("evidence_id","lender_name","program_name","source_locator",
                  "source_date","expiration_date","purchase_price","principal",
                  "apr_percent","term_months","origination_fee","lender_fee",
                  "other_closing_cost","reserve_cash","vault_cash","supersedes",
                  "correction_reason")
            kwargs={key:request.form.get(key,"") for key in keys}
            revised,item=record_financing_option(
                op,actor_ref=owner_actor(conn),**kwargs)
            save(conn,revised,"FinancingOptionRecorded",{
                "option_id":item["id"],"source_artifact_id":item["source_artifact_id"],
                "source_sha256":item["source_sha256"],
                "supersedes":item["supersedes"],"approved":False,
                "teller_readiness":"UNKNOWN"},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("financing_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/diligence")
    @login_required
    def diligence_room(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        return render_template("diligence.html",op=op,
            checklist=diligence_snapshot(op))

    @app.post("/opportunities/<oid>/diligence/tasks")
    @login_required
    def create_evidence_task(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,task=create_diligence_task(
                op,evidence_kind=request.form.get("evidence_kind",""),
                due_date=request.form.get("due_date",""),
                owner_actor=owner_actor(conn),
                notes=request.form.get("notes",""),
            )
            save(conn,revised,"DiligenceEvidenceTaskCreated",{
                "task_id":task["id"],"kind":task["evidence_kind"],
                "due_date":task["due_date"],
                "registry_version":task["requirement_registry_version"],
                "source_revision":task["created_against_opportunity_revision"],
                "seller_contact_sent":False,
                "evidence_verified":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("diligence_room",oid=oid),code=303)

    @app.get("/opportunities/<oid>/integrity")
    @login_required
    def deal_integrity(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
        artifacts={a["id"]:a for a in op.get("artifacts",[])}
        available=[
            {"evidence":e,"artifact":artifacts[e["artifact_id"]]}
            for e in op.get("evidence",[])
            if e.get("artifact_id") in artifacts
            and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED","THIRD_PARTY_VERIFIED")
        ]
        current_claims=active_claims(op)
        return render_template("integrity.html",op=op,
            report=integrity_report(op),claims=current_claims,
            sources=available,artifacts=artifacts,
            reviewable_claim_ids={c["id"] for c in current_claims
                                  if owner_reviewed_source(op,c) is not None})

    @app.post("/opportunities/<oid>/claims")
    @login_required
    def record_claim(oid):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,record=record_source_claim(
                op,evidence_id=request.form.get("evidence_id",""),
                subject_id=request.form.get("subject_id",""),
                field=request.form.get("field",""),
                value=request.form.get("value",""),
                period_key=request.form.get("period_key",""),
                locator=request.form.get("locator",""),
                topic_key=request.form.get("topic_key") or None,
                supersedes_claim_id=request.form.get("supersedes_claim_id") or None,
                correction_reason=request.form.get("correction_reason") or None)
            save(conn,revised,"SourceClaimRecorded",{
                "claim_id":record["id"],"evidence_id":record["evidence_id"],
                "artifact_id":record["artifact_id"],"field":record["field"],
                "supersedes":record["supersedes"],
                "automatically_accepted":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("deal_integrity",oid=oid),code=303)

    @app.post("/opportunities/<oid>/claims/<claim_id>/review")
    @login_required
    def document_claim_review(oid,claim_id):
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            revised,record=record_owner_document_review(
                op,claim_id=claim_id,rationale=request.form.get("rationale",""))
            save(conn,revised,"SourceClaimDocumentReviewed",{
                "claim_id":record["id"],"supersedes":claim_id,
                "evidence_id":record["evidence_id"],
                "scope":"DOCUMENT_SUPPORT_ONLY","independently_verified":False},
                expected_revision=int(request.form.get("revision","")))
        return redirect(url_for("deal_integrity",oid=oid),code=303)

    @app.post("/opportunities/<oid>/source")
    @login_required
    def source(oid):
        from .discovery import canonical_url
        raw=request.form.get("url","").strip()[:500]
        url=canonical_url(raw)
        if not url: abort(400,"Valid HTTP(S) source required")
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
            if any(isinstance(s,dict) and canonical_url(s.get("url"))==url for s in op["sources"]):
                flash("This source is already attached.")
                return redirect(url_for("opportunity",oid=oid))
            op["sources"].append({"url":url,"type":"OWNER_ENTERED"})
            op=invalidate_on_change(op,changed_fields=["sources"],reason="New source attached",
                                    source_reference=url)
            save(conn,op,"SourceAttached",{"url":url},expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.post("/opportunities/<oid>/evidence")
    @login_required
    def evidence(oid):
        kind=request.form.get("kind","")
        reference=request.form.get("reference","").strip()[:500]
        source_party=request.form.get("source_party","").strip()[:160]
        if not reference or not source_party: abort(400,"Evidence source and reference required")
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
            if kind not in {e["kind"] for e in get_vertical(op["vertical"])["evidence"]}:
                abort(400,"Unregistered evidence category")
            item=add_evidence(op,kind,status="RECEIVED",reference=reference,
                              source=source_party,notes=request.form.get("notes","")[:1000])
            op=invalidate_on_change(op,changed_fields=["evidence",kind],
                                    reason="Evidence reference received",source_reference=item["id"])
            save(conn,op,"EvidenceReceived",{"kind":kind,"id":item["id"]},
                 expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.post("/opportunities/<oid>/upload")
    @login_required
    def upload_document(oid):
        file=request.files.get("document")
        kind=request.form.get("kind","")
        source_party=request.form.get("source_party","").strip()[:160]
        if not file or not file.filename or not source_party:
            abort(400,"Document and source party required")
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
            if kind not in ({e["kind"] for e in get_vertical(op["vertical"])["evidence"]} | {FINANCING_EVIDENCE_KIND, COMPARABLE_EVIDENCE_KIND, INSURANCE_EVIDENCE_KIND}):
                abort(400,"Unregistered evidence category")
            from werkzeug.utils import secure_filename
            filename=secure_filename(file.filename)
            if not filename: abort(400,"Invalid document name")
            try:
                descriptor=docstore.ingest(contents=file.read(),filename=filename,
                        mime=file.mimetype,source_party=source_party)
            except ValueError as exc:
                abort(400,str(exc))
            try:
                op.setdefault("artifacts",[]).append(descriptor)
                item=add_evidence(op,kind,status="RECEIVED",
                        reference=descriptor["id"],source=source_party,
                        notes="Original encrypted document received; not yet reviewed")
                item["artifact_id"]=descriptor["id"]
                op=invalidate_on_change(op,changed_fields=["evidence",kind],
                        reason="Original acquisition or financing document received",
                        source_reference=descriptor["id"])
                save(conn,op,"OriginalDocumentReceived",
                        {"kind":kind,"artifact_id":descriptor["id"],"sha256":descriptor["sha256"]},
                        expected_revision=int(request.form["revision"]))
            except BaseException:
                docstore.discard_uncommitted(descriptor)
                raise
        return redirect(url_for("opportunity",oid=oid))

    @app.get("/opportunities/<oid>/documents/<artifact_id>")
    @login_required
    def download_document(oid,artifact_id):
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
        descriptor=next((d for d in op.get("artifacts",[])
                         if d["id"]==artifact_id),None)
        if descriptor is None: abort(404)
        try: data=docstore.read(descriptor)
        except ValueError: abort(404,"Document unavailable or integrity check failed")
        from io import BytesIO
        return send_file(BytesIO(data),as_attachment=True,
             download_name=descriptor["name"],mimetype="application/octet-stream",
             max_age=0)

    @app.post("/opportunities/<oid>/evidence/<evidence_id>/freeze-proof")
    @login_required
    def freeze_local_proof(oid,evidence_id):
        # Local source-bound proof only. Does NOT invoke Tower or Vault.
        with db() as conn:
            op=load(conn,oid)
            if op is None: abort(404)
            e=next((item for item in op["evidence"]
                    if item["id"]==evidence_id),None)
            if not e or not e.get("artifact_id"):
                abort(400,"Uploaded original and matching evidence record required")
            try:
                revised,snapshot=freeze_local_evidence_snapshot(op,
                    evidence_id=e["id"],artifact_id=e["artifact_id"],
                    actor_reference="local_owner")
            except HandoffPreparationError as err:
                abort(400,str(err))
            save(conn,revised,"LocalEvidenceSnapshotFrozen",
                {"snapshot_id":snapshot["snapshot_id"],
                 "evidence_id":e["id"],
                 "source_document_id":e["artifact_id"],
                 "snapshot_sha256":snapshot["snapshot_sha256"],
                 "archive_state":"NOT_REQUESTED"},
                 expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.post("/opportunities/<oid>/evidence/<evidence_id>/review")
    @login_required
    def review_evidence(oid,evidence_id):
        # Human review of a real source reference; no AI or third-party
        # verification is claimed. Preserve the earlier evidence revision.
        rationale=request.form.get("rationale","").strip()[:1000]
        if not rationale: abort(400,"A review rationale is required")
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
            item=next((e for e in op["evidence"] if e["id"]==evidence_id),None)
            if not item: abort(404)
            if item["status"] not in ("RECEIVED","CLAIMED","STALE"):
                abort(400,"This evidence revision cannot be reviewed from its current state")
            if not item.get("reference") or not item.get("source"):
                abort(400,"Source evidence required")
            item["status"]="SUPERSEDED"
            from .core import now
            from uuid import uuid4
            reviewed=dict(item,id=str(uuid4()),status="DOCUMENT_SUPPORTED",
                          supersedes=evidence_id,observed_at=now(),
                          verification={"actor":"local_owner","rationale":rationale,"reviewed_at":now(),
                                  "verification_scope":"DOCUMENT_SUPPORT_ONLY"})
            op["evidence"].append(reviewed)
            op=invalidate_on_change(op,changed_fields=["evidence",reviewed["kind"]],
                    reason="Owner reviewed documented source",source_reference=reviewed["id"])
            save(conn,op,"EvidenceReviewed",{"kind":reviewed["kind"],
                "original_id":evidence_id,"reviewed_id":reviewed["id"]},
                expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.post("/opportunities/<oid>/metric")
    @login_required
    def record_metric(oid):
        # Owner can record a figure only against an already-reviewed document.
        # It is not promoted to third-party verification.
        metric_name=request.form.get("metric_name","")
        value=money(request.form.get("value",""))
        evidence_id=request.form.get("evidence_id","")
        period=request.form.get("period","").strip()[:100]
        if metric_name not in ("annual_revenue","annual_expenses","largest_location_share"):
            abort(400,"Unregistered financial input")
        if value is None or not period:
            abort(400,"Valid value and reporting period required")
        if metric_name in ("annual_revenue","annual_expenses"):
            try:
                start_raw,end_raw=period.split(" / ")
                start=date.fromisoformat(start_raw)
                end=date.fromisoformat(end_raw)
                if not 365 <= (end-start).days + 1 <= 366:
                    raise ValueError
            except (ValueError,TypeError):
                abort(400,"Annual metrics require a full 12-month YYYY-MM-DD / YYYY-MM-DD period")
        if metric_name=="largest_location_share" and not Decimal("0")<=value<=Decimal("1"):
            abort(400,"Location revenue share must be a fraction from 0 to 1")
        if metric_name!="largest_location_share" and value<0:
            abort(400,"Revenue and expenses cannot be negative in these gross fields")
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
            supporting=next((e for e in op["evidence"] if e["id"]==evidence_id and
                             e["status"]=="DOCUMENT_SUPPORTED"),None)
            if supporting is None: abort(400,"Select a documented, owner-reviewed evidence reference")
            if op["vertical"]=="atm":
                relevant={
                    "annual_revenue":{"processor_statements","settlement_records"},
                    "annual_expenses":{"expense_records"},
                    "largest_location_share":{"processor_statements"},
                }
                if supporting["kind"] not in relevant[metric_name]:
                    abort(400,"Evidence category does not support this financial input")
            from .core import now
            old=op["metrics"].get(metric_name)
            op["metrics"][metric_name]={
                "value":str(value),"state":"DOCUMENT_SUPPORTED",
                "source":supporting["reference"],"evidence_id":supporting["id"],
                "period":period,"recorded_at":now(),"recorded_by":"local_owner",
                "supersedes":old,
            }
            op=invalidate_on_change(op,changed_fields=["metrics",metric_name],
                reason="Document-linked financial figure revised",source_reference=supporting["id"])
            save(conn,op,"MetricRecorded",{"metric":metric_name,"evidence_id":supporting["id"]},
                expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.post("/opportunities/<oid>/stage")
    @login_required
    def stage(oid):
        with db() as conn:
            op=load(conn,oid)
            if not op: abort(404)
            revised=transition(op,request.form.get("target",""),
                               actor_reference="local_owner",reason=request.form.get("reason",""))
            save(conn,revised,"StageTransitioned",{"target":revised["lifecycle"]},
                 expected_revision=int(request.form["revision"]))
        return redirect(url_for("opportunity",oid=oid))

    @app.errorhandler(ValueError)
    def validation_error(error):
        return render_template("error.html",message=str(error)),409

    @app.errorhandler(400)
    @app.errorhandler(404)
    def bad_request(error):
        return render_template("error.html",message=str(error)),error.code
    return app

def main():
    app=create_app()
    app.run(host="127.0.0.1",port=int(os.environ.get("BUYBOX_PORT","8787")),debug=False)

if __name__=="__main__":
    main()
