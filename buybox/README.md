# BuyBox — Simplee Universal Acquisition Intelligence

BuyBox is a dedicated package on its own feature branch in the accessible
SimpleeMrkTrade monorepo. Its full target is the comprehensive multi-asset
acquisition product, not an ATM-only release.

## Real owner workspace (BBX004)

The previous synthetic browser demonstration was deleted. The owner workspace
now uses authenticated, persistent server routes and begins **empty**. It accepts
real owner-entered opportunities across all seven categories, source URLs,
evidence references, owner-led stage-change requests, and retains immutable
historical revision copies and activity records. No sample seller, revenue,
bank balance, or fabricated opportunity is installed as live app content.

Run from the repository root with Python 3.12+:

```sh
python -m pip install -r buybox/requirements.txt
python -c "from werkzeug.security import generate_password_hash; import getpass; print(generate_password_hash(getpass.getpass('Set BuyBox owner password: ')))"
# Export the printed hash as BUYBOX_PASSWORD_HASH, a cryptographically random
# BUYBOX_SECRET_KEY, and BUYBOX_DB_PATH in a PRIVATE persistent directory.
python -m buybox.app
```

Default bind address is localhost (127.0.0.1), port 8787. Do not expose the
development server to the public internet. Protect the owner password, key and
database path; do not commit them. Set the secure-cookie option under an actual
TLS deployment with a production WSGI server.

## Authority and boundaries

- BuyBox owns opportunities, discovery, evidence registers, preliminary
  calculations, scenarios, stage logic, revision history and acquisition
  intelligence; it does not execute purchases or transfer money.
- Teller is the only BuyBox-facing source for capital deployment and
  people/management readiness. BuyBox does not read OB balances directly.
- Grounds is the existing real-property operations system and property handoff
  destination, not a second portfolio ledger in BuyBox.
- Tower authenticates and authorizes protected actions when integrated; there
  is NO live Tower adapter yet and the local app blocks protected transitions.
- Vault access is Tower-mediated; there is no direct BuyBox-Vault call.
- Soulaana's present deterministic briefing is grounded in stored findings,
  not a claim that live AI services or cross-app context are connected.

## Implemented foundation

Seven versioned vertical manifests: ATM, multifamily, commercial, laundromat,
land/farm, business and equipment. The universal opportunity core includes
distinct judgment and lifecycle states; evidence manifest and coverage;
decimal-safe preliminary scenario calculations; ATM machine ownership
screening; source normalization and conservative duplicate suggestions;
versioned SQLite persistence; conflict-safe local writes; owner login, CSRF,
limited upload body size, and responsive dark screens.

BBX003 adds source-located claim records, exact-byte digests for original-file
descriptors, conflict detection, stage-gate reports, and material-change
invalidation. The local app **does not accept document bytes for uploads yet**:
encrypted storage and access control must be integrated before exposing
sensitive acquisition files. It does record real evidence references.

## Tests

```sh
python -m unittest discover -s buybox/tests -v
```

Automated CI installs BuyBox dependencies and runs the isolated test suite.
Test fixture data in unit tests is deliberately artificial, solely to verify
behavior; no test fixtures populate the owner database or production product.
There are no fabricated live listings, performance, Teller readiness or
Tower approvals.

## Pending for full V1

Authenticated Tower/Teller/Grounds adapters; protected original-document
storage and extraction/review workflow; full metric/formula/policy registry and
vertical-specific calculations; actual licensed external listing connectors;
financing/portfolio and negotiation/diligence/closing room implementations;
live backend-connected Compare/Scenario interfaces; real Soulaana service
integration; operational handoff/outcome feeds; production infrastructure,
security review, accessibility and end-to-end deployment certification.

This branch and draft PR are **not** a finished or deployed production release.
No legacy Tower/OB runtime is modified or merged by this branch.
