# BuyBox — Simplee Universal Acquisition Intelligence

BuyBox is developed in a dedicated feature branch inside the currently connected
SimpleeMrkTrade repository. In the finished ecosystem, it is a **Tower-launched,
Tower-governed application**, not an independently accessed owner login. The local
password screen is temporary development-only access. Hosting placement within
Tower's runtime versus an isolated backend behind Tower remains a coordinated
implementation decision. The product target remains the **complete universal
acquisition system**, not an ATM-only application.

## Real owner workspace — BBX001–BBX009

The old synthetic UI preview was removed. The real, persistent workspace opens
with **no sample listings, invented earnings, or fabricated approval signals**.
It currently supports:
- Owner sign-in with a securely hashed password; CSRF and no-cache controls.
- Persistent owner-created opportunities in all seven registered acquisition classes.
- Source intake, cautious duplicate suggestions, responsive browse and search.
- Original PDF/image/text/CSV intake encrypted at rest with SHA-256 integrity
  checking and authenticated attachment-only retrieval.
- Received-versus-reviewed documentary evidence, preservation of original
  revisions and review rationale.
- Source-linked annual revenue/expense records with matching 12-month periods.
- Deterministic preliminary financial calculation, authenticated real-record
  comparison, and assumption-labeled mathematical scenario analysis.
- Local acquisition stage guards, event/revision history, and grounded textual
  Soulaana briefing (not yet a live AI service).
- A persistent Deal Room for real tasks, deadlines, sourced seller/negotiation
  events, changes in asking price and non-authorizing owner analytical records.
- Soulaana's read-only contextual room: actual documentary support and source
  references, fact versus calculation labels, material changes, Red Team data
  limitations, and sourced next actions. A live AI service is NOT connected yet.
- Individual ATM machine intake that distinguishes a seller ownership claim
  from source-linked owner-reviewed documentation; title/lien clearance remains
  explicitly unverified.
- Focus Desk that reads actual task due dates and material activity events only,
  without generating sample alerts.
- Per-request SQLite connections are closed and uncommitted encrypted upload
  blobs are discarded on rejected/stale opportunity revisions.
- Material-change invalidation: old assessments/readiness are not preserved as
  a fresh greenlight after material deal inputs change.

### Local private runbook

Install Python 3.12+ dependencies:
```sh
python -m pip install -r buybox/requirements.txt
```

Create **two private local directories**, excluding group/other access:
```sh
mkdir -p "$HOME/.local/share/simplee-buybox/documents"
chmod 700 "$HOME/.local/share/simplee-buybox" "$HOME/.local/share/simplee-buybox/documents"
```

Generate a hashed owner password and a document encryption key:
```sh
python -c "from werkzeug.security import generate_password_hash; import getpass; print(generate_password_hash(getpass.getpass('Owner password: ')))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_hex(32))"
```

Provide the resulting values securely as BUYBOX_PASSWORD_HASH,
BUYBOX_DOCUMENT_KEY and BUYBOX_SECRET_KEY. Also configure:
```sh
export BUYBOX_DB_PATH="$HOME/.local/share/simplee-buybox/buybox.sqlite3"
export BUYBOX_DOCS_DIR="$HOME/.local/share/simplee-buybox/documents"
python -m buybox.app
```

Default host: `127.0.0.1`, port `8787`. Do not expose the Flask development
server to the public internet. Protect all secrets and maintain secure backup
and key recovery procedures: losing BUYBOX_DOCUMENT_KEY prevents decryption of
previously uploaded evidence. Never commit sensitive values or financial files.

The local intake store is **not** the Archive Vault. Permanent proof transfer
must use Tower's authorized Vault corridor when the real integration exists.
Owner documentary review is not a claim of independent professional verification.

## Authority and integration limits

- BuyBox owns acquisition discovery, intelligence and records, not trades,
  payment execution or independent closing authorization.
- Teller is the BuyBox-facing source for money deployment, protected floors
  and management/expansion capacity. Until an authenticated connector exists,
  readiness is shown as UNKNOWN and cannot be forged with a serialized dict.
- Grounds supplies property-portfolio context and is the owned-property link
  and handoff destination. No live Grounds adapter is connected yet.
- Tower handles protected access and approvals. Contract-shaped receipts are
  not sufficient; protected transitions and handoff remain blocked until the
  authenticated adapter verifies the actual issuer, action, subject and snapshot.
- Soulaana's current deterministic explanation is grounded in stored evidence;
  the live Soulaana service and associated permissions are not wired yet.
- No external marketplace feeds, bank/broker data, or manufactured account
  balances are presented in the workspace.

## Tests and CI

```sh
python -m unittest discover -s buybox/tests -v
```

Engineering tests use isolated temporary databases and artificial test values
to prove correctness; these fixtures never populate the actual product.
GitHub CI installs dependencies and executes the suite.

See [OWNER_NEXT_STEPS.md](OWNER_NEXT_STEPS.md) for the owner handoff decisions and\nproduction readiness sequence.\n\n## Still required for the complete V1

Authenticated Tower/Teller/Grounds/Vault integration, document malware scanning
and formal retention controls, full per-vertical underwriting/policy registries,
licensed external feeds, advanced negotiation and diligence rooms, lender
comparison and true portfolio allocation, a fully integrated Soulaana service,
post-closing destination acknowledgments/feedback, operational deployment and
security/accessibility certification. The present branch is functional but NOT
the completed, publicly deployed V1. Do not merge into active Tower/OB without
integration review.
