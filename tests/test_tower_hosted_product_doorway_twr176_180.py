from pathlib import Path
import ast
import json

import pytest
from flask import Flask, render_template

from tower.ob_product_landing import register_ob_product_landing
from tower import ob_web_route_enforcement as enforcement

ROOT = Path(__file__).resolve().parents[1]


def make_app(monkeypatch, owner=True, elevated=True, receipt=True):
    app = Flask(__name__, template_folder=str(ROOT/'web/templates'),
                static_folder=str(ROOT/'web/static'), static_url_path='/static')
    app.secret_key = 'twr176-local-test-only'
    # Execute the actual sealed product route, not a lookalike renderer.
    tree = ast.parse((ROOT/'web/app.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == 'ob_dashboard_v16')
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'web/app.py', 'exec'),
         {'app': app, 'render_template': render_template})
    monkeypatch.setattr(enforcement, 'owner_session_active', lambda: owner)
    monkeypatch.setattr(enforcement, 'step_up_active', lambda: elevated)
    monkeypatch.setattr(enforcement, 'operational_ob_access_active', lambda: receipt)
    enforcement.register_ob_protected_route_enforcement(app)
    register_ob_product_landing(app)
    return app


def test_real_template_and_assets_survive(monkeypatch):
    app = make_app(monkeypatch)
    response = app.test_client().get('/ob/dashboard')
    assert response.status_code == 200
    assert response.headers['X-OB-Product-Surface'] == 'dashboard'
    assert b'ob_dashboard_soulaana_obux.css' in response.data
    assert b'dashboardMount' in response.data
    assert response.headers['Cache-Control'] == 'no-store'
    assert app.test_client().get('/static/ob/ob_dashboard.js').status_code == 200


@pytest.mark.parametrize('owner,elevated,receipt,destination', [
    (False, False, False, '/tower/login'),
    (True, False, False, '/tower/access-home'),
    (True, True, False, '/tower/launch/observatory'),
])
def test_existing_security_boundaries(monkeypatch, owner, elevated, receipt, destination):
    response = make_app(monkeypatch, owner, elevated, receipt).test_client().get('/ob/dashboard')
    assert response.status_code == 302
    assert response.headers['Location'] == destination


def test_unknown_room_still_denied(monkeypatch):
    assert make_app(monkeypatch).test_client().get('/ob/unknown').status_code == 403


@pytest.mark.parametrize('body', [
    '<h1>Observatory protected run-through</h1>',
    '<h1>Old dashboard replacement</h1>',
])
def test_response_substitution_fails_closed(monkeypatch, body):
    app = make_app(monkeypatch)
    @app.after_request
    def stale_renderer(response):
        response.set_data(body)
        return response
    response = app.test_client().get('/ob/dashboard')
    assert response.status_code == 503
    assert b'Return to Tower' in response.data


def test_duplicate_dashboard_rejected(monkeypatch):
    app = make_app(monkeypatch)
    app.extensions.pop('tower_ob_product_landing')
    app.add_url_rule('/ob/dashboard', endpoint='wrong', view_func=lambda: 'walkthrough')
    with pytest.raises(RuntimeError):
        register_ob_product_landing(app)


@pytest.mark.parametrize('name', [
    '_inject_real_surface_walkthrough_ui', '_inject_guided_run_controls',
    '_inject_guided_history_links',
])
@pytest.mark.parametrize('path', ['/ob/dashboard', '/tower', '/tower/access-home'])
def test_walkthrough_callbacks_cannot_touch_product(name, path):
    from tower import tower_observatory_walkthrough_web as proof
    app = Flask(__name__)
    with app.test_request_context(path):
        response = app.response_class('<html>product</html>', mimetype='text/html')
        result = getattr(proof, name)(response)
        assert result is response
        assert result.data == b'<html>product</html>'


def test_no_obsolete_response_rewriter():
    tree = ast.parse((ROOT/'web/app.py').read_text())
    assert not any(isinstance(n, ast.FunctionDef) and n.name ==
                   '_tower_obux006_010_dashboard_server_render_response' for n in tree.body)


def test_canonical_runtime_and_compatibility():
    import web.hosted_tower as runtime
    import web.managed_staging as legacy
    from tower.hosted_runtime_parity import EXPECTED_ENTRYPOINT
    assert legacy.app is runtime.app
    assert EXPECTED_ENTRYPOINT == 'web.hosted_tower:app'
    payload = runtime.hosted_tower_runtime_manifest()
    assert 'staging' not in json.dumps(payload).lower()
    for key in ('production_deployment', 'broker_submission', 'capital_movement',
                'manual_live_authorized', 'live_auto_authorized', 'hosted_ready'):
        assert payload[key] is False
    response = runtime.app.test_client().get('/tower/healthz')
    assert response.status_code == 200
    assert response.headers['X-Simplee-Entrypoint'] == EXPECTED_ENTRYPOINT
    assert response.json == {'ok': True}
    assert 'web.hosted_tower:app' in (ROOT/'deploy/hosted_tower/start.sh').read_text()
    assert 'web.managed_staging:app' not in (ROOT/'deploy/managed_staging/start.sh').read_text()


def test_hosted_runtime_action_flags_are_checked(monkeypatch):
    import web.hosted_tower as runtime
    from tower.hosted_owner_release_readiness import _managed_safety_closed
    assert _managed_safety_closed()
    monkeypatch.setattr(runtime, 'CAPITAL_MOVEMENT', True)
    assert not _managed_safety_closed()


def test_historical_beta_cannot_certify_current_host():
    from tower import tower_owner_beta_control_room as beta
    assert beta.CURRENT_STAGING_READY_DECISION == 'HISTORICAL_OWNER_BETA_EVIDENCE_ONLY'
    assert beta.STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH is False
    assert beta.hosted_staging_readiness_card().status == 'historical_evidence_only'


def test_current_app_and_console_identity():
    from tower.app_registry import TOWER_APP_REGISTRY
    from tower.tower_owner_console_v1 import deployment_hold_panel
    from tower.tower_app_registry_v2 import integration_readiness_summary
    ob = next(app for app in TOWER_APP_REGISTRY if app.app_id == 'observatory')
    assert ob.app_status == 'protected_hosted'
    for payload in (deployment_hold_panel(), integration_readiness_summary()):
        assert 'staging' not in json.dumps(payload).lower()
