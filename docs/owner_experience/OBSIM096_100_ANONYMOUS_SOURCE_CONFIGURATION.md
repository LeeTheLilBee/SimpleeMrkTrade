# OBSIM096–100 — Anonymous release diagnostics include source activation, not an owner grant

The accepted hosted runtime manifest has source-only `owner_rehearsal` booleans for registered routes, explicit feature flag, exact HTTPS origin and source runtime preconditions. Previous anonymous probes and two-host inventory checked HTTP status/revision/denial but did **not** carry these safe activation diagnostics forward. A 302/403/503 with an exact published commit cannot distinguish "configured" from "default OFF."

The passive `scripts.ob_hosted_anonymous_release_probe` now includes precisely those **four tri-state booleans** in its redacted `observed.owner_rehearsal_source` map. A missing/non-boolean field is `null` ("unknown"), **not** silently `false` ("verified disabled"). Internal contradictions, or the public source manifest trying to declare owner walkthrough, archive durability, restart recovery, Manual Live, broker or capital clearance, explicitly produce HOLD. The ordinary higher-level `PASS_ANONYMOUS_PREFLIGHT_ONLY` remains a compatibility observation only, never release-ready.

`scripts.ob_anonymous_two_host_inventory` copies only those four exact true/false/null values per candidate, plus source HTTP status/revision already allowlisted. It discards any host, environment, token, owner ID, arbitrary string or secret accidentally supplied by a future probe implementation. It always keeps the candidate-host selection and actual owner/device acceptance at HOLD, even when the secondary host has a newer passing revision.

This pack does not use any credentials, test a real owner login, enable the feature, change Render/env/branch/host settings, request a paid resource, attest a provider/broker or approve actual Manual Live, Hybrid or Auto.

Regression `tests/test_obsim096_100_anonymous_source_config_diagnostics.py` drives the real parser with injected HTTP GET responses for default-OFF and all-configured cases, contradictory source flags, each forged external authority flag, unknown/malformed tri-state values and two-host redaction. Original OBSIM066, 071, 081 and the OBSIM091 hosted manifest tests remain acceptance dependencies.

Operational use after official owner URL selection and observed exact revision: run only the existing fixed-route anonymous probe, then **separately** perform the actual authenticated Tower session, fresh step-up and operational OB launch, private browser rehearsal and honest volatile-storage owner acceptance. No public probe is that owner acceptance.
