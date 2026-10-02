# TWR176–TWR180 — Hosted Tower Identity + Observatory Product Doorway

Parent: `780014d06244d3a787f62a4a0e2daf8e9ceea041`.

- TWR176: canonical `web.hosted_tower:app` identity, manifest and response headers.
- TWR177: authoritative `deploy/hosted_tower/` startup/dependencies. Old paths delegate only. Current registry and owner-console identity uses hosted naming.
- TWR178: preserve the existing secured launch, one-time handoff, receiving edge, session and step-up checks. Validate the unique real dashboard registration at hosted startup.
- TWR179: remove the obsolete dashboard response replacement; restrict all three walkthrough UI injectors to their proof namespace. Preserve the existing OB dashboard route, template and assets. Reject a successful response that substitutes a different surface.
- TWR180: product rendering, stale response substitution, default-deny, session, step-up, handoff, runtime identity, closed actions and historical-readiness regression checks.

## Verified source findings

`web/app.py` already registers `/ob/dashboard` as `ob_dashboard_v16`, rendering `dashboard.html`. Its obsolete after-request callback replaced the template output. Tower's walkthrough blueprint also had application-wide response injectors capable of adding guided controls to product rooms. These source defects are repaired; the exact deployed revision and the user's browser session were not inspected.

## Validation

176 selected product, identity, parity, handoff, owner-session, step-up, release-readiness and prerequisite-certification tests passed. Twelve deployment/compatibility tests passed separately. Full repository testing was not performed. Tests requiring legacy runtime names were updated to the new canonical contract; historical evidence was not rewritten.

## Remaining migration and audit limits

This is a source build, not a deployment or a claim that every repository occurrence of staging is gone. The audit records 100 matching tracked files and 601 matching lines after the source edits. It identifies compatibility paths, historical evidence, receipt/safety schemas, Vault workflow uses, and other references requiring scope review. Signed historical receipt and certificate schemas remain intact. In particular, legacy `staging_ready` and `staging_ready_changed` security fields are not relabeled to invalidate existing receipts. The former beta readiness panel is explicitly historical and cannot certify the current host.

The hosting provider's actual service name, URL, environment settings and startup command were not changed or verified. A later separately authorized host migration must use:

Build: `pip install -r deploy/hosted_tower/requirements.txt`

Start: `bash deploy/hosted_tower/start.sh`

After deployment, verify the exact revision header, anonymous denial, real authenticated Tower handoff, dashboard assets, all six rooms and Tower return. Do not treat the source test result as live verification or as completed host migration.

## Authority

No commit, push, deployment, promotion, release execution, broker submission, capital movement, Manual Live or Live Auto is authorized by this pack. The Colab cell applies the build and runs tests, then stops for review. Historical evidence remains evidence.
