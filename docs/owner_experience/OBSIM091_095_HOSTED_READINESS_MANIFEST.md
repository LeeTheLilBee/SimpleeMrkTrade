# OBSIM091–095 — Tower hosted rehearsal source-state manifest

## Problem this change addresses

The hosted runtime manifest already identified the WSGI entrypoint, source revision, critical routes and trading safety holds, but did not show whether the OBSIM056–090 owner rehearsal feature was merely **registered** or explicitly **enabled**, or whether its exact HTTPS origin was configured. A 404/503/302 anonymous response cannot independently answer those distinctions. An alternate Tower hostname can be ahead in source revision without being the owner's approved public entrance. This is a read-only diagnostic; it neither selects a hostname nor activates a feature.

## New redacted status in existing `/tower/runtime-manifest.json`

`owner_rehearsal` reports only booleans: `exact_source_routes_registered`, `explicit_feature_enabled`, `exact_https_origin_configured` and `source_runtime_activation_preconditions_met`. These are server-derived from the existing hosted route registration and private server-side adapter registration state. No configured hostname, environment value, token, owner ID, paths on disk, report bytes or client-supplied claim is returned.

Critically, `actual_owner_login_walkthrough_verified`, `durable_report_archive`, `restart_recovery`, `manual_live_clearance`, `broker_submission` and `capital_movement` remain **false even when the two feature flags are true**. Source flag/origin matches are necessary configuration diagnostics, not proof of an owner device walkthrough, durable storage or a real-money authorization. The original manifest's critical route and safety schema is additive/unchanged.

## How to interpret it

- Source routes present + feature OFF = code registered but owner experience **not activated**. Leave HOLD; do not call 503 a success.
- Feature ON + exact HTTPS origin configured = source runtime activation preconditions present, but **still no proof** that this public URL is the chosen owner site or that the owner successfully authenticated and exercised the service.
- A real release requires separately verified actual service ID, exact deployed revision, current Tower owner session, fresh step-up, operational OB receipt, authenticated real-device UI check, anonymous denial, expiry/logout/rotation negative tests and acknowledgement of volatile in-memory reports. Tests and a public manifest cannot perform a protected owner walkthrough.
- The historic `simpleemrktrade.onrender.com` main-tracking service had a separate missing-root-requirements/mismatched-start build configuration and is not a substitute for the owner-approved Tower URL. This change does not edit Render settings or deploy an unreviewed owner feature.

No paid resource, broker API, finance/capital access, provider authentication, Manual Live, Hybrid or Automated grant; no environment change and no new HTTP route. Source-only code in the existing hosted manifest, with exact default-OFF/partial/on spoof negative tests and source compatibility CI. The optional repository-wide Tower diagnostic must report its historical failures honestly and is not labelled a clean release gate.
