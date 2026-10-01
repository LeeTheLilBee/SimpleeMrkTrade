# BBX136–155 — Owner Experience & Hardening

This pack improves speed, clarity, accessibility, provenance and owner acceptance without changing BuyBox's acquisition-authority boundaries.

## Included

- Persistent **Acquisition Pulse**: active opportunities, deals needing owner attention, external-proof blockers and changes since the owner last marked the pulse read.
- **Owner Opening View**: explicit Focus-marked deals, due/overdue work and recent material activity; shows an all-clear state when nothing needs attention.
- **Universal Owner Command / Search** across saved opportunity content, location, sources, evidence and owner notes.
- **Calm / Standard / Deep Dive** persistent density modes.
- **Bounded pagination** on Discover plus supporting database indexes.
- **Bulk owner triage**: Focus, Watch, Parked, Archive Candidate. Triage is workflow metadata, not lifecycle/evidence/authorization.
- **Why am I seeing this? Provenance** view for rules, evidence, metrics and accepted external-proof records.
- **Deal Change Diff** between the latest two preserved opportunity revisions.
- **Soulaana Context Rail** with grounded overview/evidence/change/next-action links.
- **Mobile Field Mode** for fast owner observations.
- Field observations may be turned into **owner follow-up tasks only**; they are never silently promoted to evidence or source truth.
- **Release / Integration Cockpit** for Tower, Teller, Vault and receiving-system proof presence.
- **Owner Acceptance Mode** with a release-walkthrough defect ledger separate from opportunity evidence.
- **Keyboard search shortcut** and reduced-motion/accessibility refinements.
- **Human-readable fail-closed error states** for invalid, unauthorized and missing records.
- Repairs two template-structure defects that had left Intelligence Studio sections and an opportunity integration link outside the rendered block.

## Performance / scaling

- Discover uses a bounded page size (24; helper hard cap 60).
- Universal search results are hard bounded.
- Latest owner-triage state is fetched in one batched query rather than one query per opportunity.
- Integration cockpit evaluates each opportunity once and reuses the result across system rows.
- Indexes added for event chronology, opportunity vertical/name, triage history and acceptance defects.

## Truth and authority boundaries

Nothing in BBX136–155:

- creates external market/listing facts,
- converts owner observations into evidence,
- grants Tower/Teller/Vault/Grounds/SimpleeOnTheGo authority,
- reads OB balances,
- sends offers,
- signs contracts,
- moves money,
- closes an acquisition,
- marks a deal operational,
- provisions hosting or paid resources.

Owner triage, acceptance defects, density preferences and field notes are internal owner-workflow records only. External readiness remains dependent on authenticated current proof from the owning system.

## Acceptance target

The exact feature head must pass the existing full BuyBox regression family, including hosted Tower boundary, Tower action outbox, Teller readiness and original-integrity cross-contract checks, plus the new owner-experience unit and authenticated web tests.
