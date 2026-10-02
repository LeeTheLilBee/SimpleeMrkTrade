from __future__ import annotations

import hmac
import secrets

from flask import Blueprint, make_response, redirect, render_template, request, session

PATH = "/ob/settings"
SESSION_KEY = "ob_owner_settings_v1"
CSRF_KEY = "ob_owner_settings_csrf_v1"

DEFAULTS = {
    "soulaana_explain_company": True,
    "soulaana_translate_market": True,
    "soulaana_translate_macro": True,
    "soulaana_translate_catalysts": True,
    "soulaana_show_conflicts": True,
    "soulaana_show_missing": True,
    "soulaana_show_source_names": True,
    "show_company_background": True,
    "show_market_cap": True,
    "show_share_count": True,
    "show_website": True,
    "show_source_accounting": True,
    "show_evidence_drawer": True,
    "auto_refresh_symbol_research": True,
    "refresh_on_focus": True,
    "use_current_market_context": True,
    "use_public_options_data": True,
    "use_completed_session_history": True,
    "use_macro_context": True,
    "use_official_catalysts": True,
    "use_sec_filings": True,
    "compact_symbol_top": False,
    "show_technical_names": False,
    "refresh_seconds": 30,
}

BOOLEAN_KEYS = {k for k, v in DEFAULTS.items() if isinstance(v, bool)}
REFRESH_ALLOWED = {15, 30, 60, 120}

CONTROL_COPY = (
    ("soulaana_explain_company", "Explain the company", "Soulaana uses company/industry background when she explains why outside conditions matter."),
    ("soulaana_translate_market", "Translate market movement", "Soulaana explains what current and recent price behavior means instead of only showing numbers."),
    ("soulaana_translate_macro", "Translate the economy", "Soulaana connects inflation, jobs, GDP and rates to the company when there is a reasonable link."),
    ("soulaana_translate_catalysts", "Translate outside events", "Soulaana explains relevant government, energy, futures and other catalyst information without pretending unrelated events matter."),
    ("soulaana_show_conflicts", "Show disagreements", "Keep conflicting evidence visible instead of smoothing everything into one neat story."),
    ("soulaana_show_missing", "Tell me what is missing", "Soulaana says what she still cannot verify so blank spots do not look like certainty."),
    ("soulaana_show_source_names", "Show where the information came from", "Keep provider/source names visible beside explanations."),
    ("show_company_background", "Show company background", "Show company name, industry, exchange, country, IPO and other available profile facts."),
    ("show_market_cap", "Show market cap", "Show the company's approximate market value when a reviewed source provides it."),
    ("show_share_count", "Show shares outstanding", "Show approximate shares outstanding when available."),
    ("show_website", "Show company website", "Show the company website from the reviewed profile source."),
    ("show_source_accounting", "Show source status", "Show which research sources were used, held, unavailable or not relevant."),
    ("show_evidence_drawer", "Keep the evidence drawer", "Let you open the source-level evidence underneath Soulaana's combined read."),
    ("auto_refresh_symbol_research", "Refresh research automatically", "Re-check the Symbol Page research on a timer while the page is open."),
    ("refresh_on_focus", "Refresh when I come back to the tab", "When you return to the browser tab, refresh research instead of waiting for the timer."),
    ("use_current_market_context", "Use current market context", "Allow current quote/minute-bar sources to feed the Symbol Page when they are available."),
    ("use_public_options_data", "Use Public options data", "Let OB and Soulaana use your approved Public options market data for the current symbol. Turning this off stops option-chain research without disconnecting Public or changing your actual Public permissions."),
    ("use_completed_session_history", "Use recent daily history", "Use completed daily sessions to compare what the stock has been doing recently."),
    ("use_macro_context", "Use economy and rates context", "Allow BLS, BEA and Treasury information to affect Soulaana's background read when relevant."),
    ("use_official_catalysts", "Use official catalyst information", "Allow reviewed Federal Register, CFTC, EIA, World Bank and NWS context when it actually matters."),
    ("use_sec_filings", "Use SEC filings and company facts", "Allow issuer filings, financial facts and company events to feed the Symbol Page."),
    ("compact_symbol_top", "Compact the top of Symbol Page", "Use tighter top cards so more company information fits above the fold."),
    ("show_technical_names", "Show technical labels", "Show backend terms like SOURCE_BOUND and AI-use review. Leave this off for normal language."),
)


def _csrf():
    token = session.get(CSRF_KEY)
    if not isinstance(token, str) or len(token) < 32:
        token = secrets.token_urlsafe(32)
        session[CSRF_KEY] = token
    return token


def get_owner_settings():
    stored = session.get(SESSION_KEY)
    settings = dict(DEFAULTS)
    if isinstance(stored, dict):
        for key in DEFAULTS:
            if key in stored and isinstance(stored[key], type(DEFAULTS[key])):
                settings[key] = stored[key]
    return settings


def register_ob_settings_control_room(app):
    if app.extensions.get("ob_settings_control_room_v1"):
        return app

    bp = Blueprint("ob_settings_control_room", __name__)

    @bp.route(PATH + ".json", methods=["GET"])
    def settings_json():
        response = make_response({
            "schema": "OB_OWNER_SETTINGS_V1",
            "settings": get_owner_settings(),
            "owner_changeable": sorted(DEFAULTS.keys()),
            "rights_flags_are_not_user_toggles": True,
        })
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    @bp.route(PATH, methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            supplied = request.form.get("csrf", "")
            expected = _csrf()
            if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
                return make_response("Settings request held.", 403)

            next_settings = dict(DEFAULTS)
            for key in BOOLEAN_KEYS:
                next_settings[key] = request.form.get(key) == "on"

            try:
                refresh = int(request.form.get("refresh_seconds", DEFAULTS["refresh_seconds"]))
            except (TypeError, ValueError):
                refresh = DEFAULTS["refresh_seconds"]
            next_settings["refresh_seconds"] = refresh if refresh in REFRESH_ALLOWED else DEFAULTS["refresh_seconds"]

            session[SESSION_KEY] = next_settings
            session["ob_settings_notice"] = "Settings saved for this owner session."
            return redirect(PATH, code=303)

        response = make_response(render_template(
            "ob_settings.html",
            settings=get_owner_settings(),
            controls=CONTROL_COPY,
            csrf=_csrf(),
            notice=session.pop("ob_settings_notice", ""),
            refresh_choices=sorted(REFRESH_ALLOWED),
        ))
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    app.register_blueprint(bp)
    app.extensions["ob_settings_reader_v1"] = get_owner_settings
    app.extensions["ob_settings_control_room_v1"] = {
        "path": PATH,
        "owner_changeable": tuple(DEFAULTS.keys()),
        "rights_flags_are_not_user_toggles": True,
        "broker_execution_authority": False,
        "capital_authority": False,
    }
    return app
