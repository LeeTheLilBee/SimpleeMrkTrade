# OBSIM071–075 — passive original/secondary Tower host inventory

## Why this exists

The documented original owner-front-door candidate is **https://simplee-tower-ob.onrender.com**, on the staging-named free workspace with manual deployments. A different free workspace has **https://simplee-tower-ob-tunv.onrender.com**, which auto-deploys the dedicated Tower branch. Both are existing resources. A successful deploy at the second address cannot elect it as the owner's canonical entrance.

The passive existing `scripts/ob_hosted_anonymous_release_probe.py` is applied separately to each exact HTTPS origin with one **known exact** Tower revision (`7199a702a9ed9169c155ff24d4014a764a542ab4`, last verified LIVE on the secondary candidate during this inspection). The new `scripts/ob_anonymous_two_host_inventory.py` aggregates a small allowlist of route/health/revision/anonymous-denial statuses; no secrets, credentials, endpoint parameters, owner identity, trading data or Render API updates. Four fixed anonymous GET requests per host, redirects disabled. The CI workflow deliberately runs this as an **informational snapshot**, not a release gate: it may finish successfully even if one/both hosts are HOLD. Read the JSON `release_status`, which is always `HOLD_OWNER_SITE_AND_AUTHENTICATED_WALKTHROUGH`.

This snapshot does not prove service ownership by checking a hostname, user authorization, hosted feature activation, stored-report persistence, or an on-device owner walkthrough. It cannot turn on the feature, choose an official URL, add a paid resource, edit an environment variable, deploy code, or unlock Manual Live.

## Acceptance evidence

Tests deny substituted URL/query/port, bogus revision, accidental secret reflection and treating a successful secondary check as release authority; even both hosts passing remains HOLD. At current workflow head, tests and the read-only snapshot are run automatically.

**Next independently authorized phase**: owner confirms which existing URL they actually use, then verify its service ID and exact live revision, current owner login/step-up/operational OB receipt, exact deployed HTTPS Origin and explicit safe feature flag. The feature still uses volatile single-process Proof/Demo only; approving durable archive requires separate storage, not temporary Render filesystem. Real Manual Live, Hybrid and Auto HOLD.
