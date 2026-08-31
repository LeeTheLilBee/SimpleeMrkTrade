# THE TOWER — TWR121–TWR125
## Authoritative Tower Truth Contract

Parent:

`2167d225236983f9cd7f9a1593d04b6e2512013d`

TWR121–TWR125 establishes the canonical truth contract that all later Tower
product surfaces must obey.

## TWR121 — Source truth

Tower now distinguishes:

- AUTHORITATIVE
- DERIVED
- CACHED
- HISTORICAL
- EVIDENCE_ONLY
- TEST_ONLY
- UNAVAILABLE

TEST_ONLY and EVIDENCE_ONLY material may continue to exist for acceptance,
audit, and historical proof, but they may not masquerade as primary product
truth.

## TWR122 — Provenance + freshness

Tower truth can now carry:

- value
- source ID
- source class
- verification state
- observed-at time
- freshness window
- reason

A stale value is not current verified truth.

## TWR123 — No plausible defaults

Missing state does not silently become:

- 0
- False
- Ready
- Healthy
- Clean
- Available
- empty collection

A genuinely present empty collection may truthfully produce zero.

Unknown means UNKNOWN.

Unavailable means UNAVAILABLE.

Not configured means NOT_CONFIGURED.

## TWR124 — Capability truth

Tower now treats these as independent dimensions:

REGISTERED → CONFIGURED → PUBLISHED → ENTITLED → AUTHORIZED → AVAILABLE → ENABLED → LOCKED

No dimension automatically grants the next.

A future app may be registered without being published or available.

The Observatory may be registered/published while current runtime availability,
current entitlement, and current authorization still require their own
authoritative providers.

Safety locks remain real truth.

## TWR125 — Truth-debt inventory

Product surfaces audited:

- tower/app_registry.py
- tower/owner_people_registry.py
- tower/owner_dashboard_service.py
- tower/access_home_owner_launches.py
- tower/owner_dashboard_web.py
- tower/hosted_owner_release_walkthrough_web.py
- tower/tower_human_login_ob_launch.py

Current machine-detected findings:

`66`

The existence of findings is intentional at this checkpoint.

This pack does NOT bless the findings.

It makes them explicit so TWR126–TWR130 can retire them deliberately.

## Next

**TWR126–TWR130 — Practice Surface Retirement**

Primary targets:

- walkthrough / practice product navigation
- preview / simulate / rehearsal controls
- placeholder people
- staged/future identities shown as real people state
- invite drafts presented like operational access management
- unsupported Ready / Healthy / Available claims
- future-app cards that imply usability
- proof/evidence surfaces in normal product navigation

Execution boundaries remain unchanged.

Observatory remains untouched.

This build does not stage, commit, or push.
