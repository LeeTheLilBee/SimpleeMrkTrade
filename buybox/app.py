"""BuyBox owner workspace: real, persistent manual acquisition intake.

Run: BUYBOX_PASSWORD_HASH='<werkzeug scrypt hash>' BUYBOX_SECRET_KEY='<random>'
     BUYBOX_DB_PATH='/private/path/buybox.sqlite3' python -m buybox.app

Local-only by default. Production public exposure requires Tower integration,
TLS, encrypted protected file storage and deployment hardening.
"""
from __future__ import annotations
import os
import secrets
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

from .core import (new_opportunity, add_evidence, evaluate, soulaana_brief,
                   money, LIFECYCLE)
from .discovery import filter_opportunities, duplicate_candidates
from .registry import VERTICALS, get_vertical
from .store import connect, save, load, list_opportunities, activity, history
from .workflow import transition, gate_report, invalidate_on_change

def create_app(config=None):
    app=Flask(__name__, template_folder="ui/templates", static_folder="ui/static",
              static_url_path="/buybox/static")
    app.config.update(
        SECRET_KEY=os.environ.get("BUYBOX_SECRET_KEY"),
        BUYBOX_PASSWORD_HASH=os.environ.get("BUYBOX_PASSWORD_HASH"),
        BUYBOX_DB_PATH=os.environ.get("BUYBOX_DB_PATH"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=os.environ.get("BUYBOX_SECURE_COOKIE","0")=="1",
        MAX_CONTENT_LENGTH=1024*1024,
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
    app.config["BUYBOX_DB_PATH"]=str(db_path)
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
