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
from functools import wraps
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

def create_app(config=None):
    app=Flask(__name__, template_folder="ui/templates", static_folder="ui/static",
              static_url_path="/buybox/static")
    app.config.update(
        SECRET_KEY=os.environ.get("BUYBOX_SECRET_KEY"),
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
    if not app.config.get("SECRET_KEY") or not app.config.get("BUYBOX_PASSWORD_HASH"):
        raise RuntimeError("Set BUYBOX_SECRET_KEY and BUYBOX_PASSWORD_HASH before starting BuyBox.")
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
    db=connect(str(db_path));db.close()

    @app.after_request
    def no_cache(response):
        response.headers["Cache-Control"]="no-store"
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["Content-Security-Policy"]=(
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'")
        return response

    def db():
        return connect(app.config["BUYBOX_DB_PATH"])

    def login_required(fn):
        @wraps(fn)
        def wrapped(*args,**kwargs):
            if session.get("buybox_owner") is not True:
                return redirect(url_for("login"))
            return fn(*args,**kwargs)
        return wrapped

    @app.context_processor
    def csrf_context():
        if "csrf" not in session:
            session["csrf"]=secrets.token_hex(32)
        return {"csrf_token": session["csrf"], "verticals": VERTICALS}

    @app.before_request
    def guard():
        if request.method not in ("GET","HEAD","OPTIONS"):
            value=request.form.get("csrf_token","")
            expected=session.get("csrf","")
            if not expected or not secrets.compare_digest(value,expected):
                abort(400,"Invalid CSRF token")

    @app.route("/login", methods=["GET","POST"])
    def login():
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
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    @login_required
    def index():
        with db() as conn:
            ops=list_opportunities(conn)
        current_vertical=request.args.get("vertical","")
        if current_vertical and current_vertical not in VERTICALS:
            abort(400,"Unknown category")
        q=request.args.get("q","").strip()[:120]
        selected=filter_opportunities(ops,vertical=current_vertical or None,query=q)
        panels=[{"record":op,"analysis":evaluate(op)} for op in selected]
        return render_template("index.html",records=panels,total=len(ops),
                               current_vertical=current_vertical,q=q)

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
            if kind not in {e["kind"] for e in get_vertical(op["vertical"])["evidence"]}:
                abort(400,"Unregistered evidence category")
            from werkzeug.utils import secure_filename
            filename=secure_filename(file.filename)
            if not filename: abort(400,"Invalid document name")
            try:
                descriptor=docstore.ingest(contents=file.read(),filename=filename,
                        mime=file.mimetype,source_party=source_party)
            except ValueError as exc:
                abort(400,str(exc))
            op.setdefault("artifacts",[]).append(descriptor)
            item=add_evidence(op,kind,status="RECEIVED",
                    reference=descriptor["id"],source=source_party,
                    notes="Original encrypted document received; not yet reviewed")
            item["artifact_id"]=descriptor["id"]
            op=invalidate_on_change(op,changed_fields=["evidence",kind],
                    reason="Original seller document received",
                    source_reference=descriptor["id"])
            save(conn,op,"OriginalDocumentReceived",
                    {"kind":kind,"artifact_id":descriptor["id"],"sha256":descriptor["sha256"]},
                    expected_revision=int(request.form["revision"]))
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
