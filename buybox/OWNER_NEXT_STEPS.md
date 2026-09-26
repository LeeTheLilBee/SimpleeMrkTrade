# BuyBox — owner handoff and production prerequisites

## What has been done

This draft branch contains a functional, empty-by-default BuyBox owner workspace,
not a sample storefront. All seven acquisition categories share the opportunity
engine. Owner entries and encrypted uploads are saved to actual persistent paths.
Soulaana's contextual explanations, Focus Desk, Compare, Scenario Lab and Deal
Room consume saved records. Tests create temporary fixtures only; product data
starts empty. Tower/OB main has not been merged or deployed from this branch.

## Owner decisions needed (do not send any secrets over chat)

1. **Workspace confirmed (2026-09-26).** Owner selected Render `Simplee World`,
   workspace ID `tea-dag3rfu1egvs73a6s72g`. Existing service in it:
   `simplee-tower-ob` (`srv-dag3sv2jnfac73bjqj8g`). Owner correction:
   BuyBox belongs behind Tower's front door and launches with Tower's
   identity/permission model, not via a permanent standalone BuyBox login.
   Its deployment topology (same service versus an isolated backend behind
   Tower) remains for coordinated Tower/hosting review. Do not change the
   existing Tower runtime or independently expose BuyBox without that review. Read-only workspace inspection found no Postgres
   instance. **Still needed:** owner approval of a durable, protected storage
   arrangement (persistent disk/volume for private SQLite and encrypted
   originals, or an explicit database/object-storage migration), along with
   a Tower-governed owner-only exposure plan. Do not run the current storage
   on an ephemeral filesystem or create a standalone public BuyBox entrance.
   Deployment requires Tower identity/launch integration, production serving,
   TLS, secrets, protected original-document handling and review.
2. **Confirm the actual source repositories and authorized integration endpoints.**
   Tower owns identity, permission, step-up and Vault mediation. Teller owns
   money and management-capacity readiness. Grounds owns real-property context.
   The applications need authenticated, versioned contracts and appropriate
   test credentials issued via the hosting secret manager; a reference-shaped
   response is not proof.
3. **Approve numerical acquisition policies.** Evidence freshness, financing
   coverage, concentration and reserve thresholds, plus ATM acquisition-set
   rules, should be owner-approved configuration. Do not invent protected OB
   floors or have BuyBox independently compute spendable OB capital.
4. **Supply an actual acquisition listing/package when ready.** A source link,
   listing/purchase terms and whatever documents are available can be entered
   directly into BuyBox after secure hosting. Unknown stays unknown. No external
   listing feed can go live without an authenticated provider and permitted
   data access.

## Security and launch gate

- Use a private owner password with a one-way hash, random Flask signing key
  and a separately saved document encryption key. Put these ONLY in a secret
  manager or protected environment, never in the repository, commit, or chat.
- The current locally bound Flask dev server is NOT a production service.
- Back up both the database and encrypted files consistently, along with the
  separately protected encryption key. Test recovery before accepting sensitive
  originals.
- Add malware scanning, retention controls and Tower-mediated Vault transfers.
  Original evidence in local BuyBox intake is not permanent Vault proof.
- Run all automated tests, authenticated integration tests, manual owner UI
  walkthrough and a deployment/security review before changing the draft PR
  into a release candidate.
- Do not merge this branch into active OB/Tower merely to expose the BuyBox UI.

## Acceptance of a first real owner session

A fresh account starts empty. The owner enters a real opportunity and source;
uploads a protected original; records documentary review; enters metrics tied to
that proof; sees missing information and unavailable external readiness truthfully;
inspects source-grounded Soulaana context; creates a real task; tests an assumption
in Scenario Lab; and compares actual saved opportunities. No funding, contracts
or closing state are executed absent authenticated Tower and Teller integrations.
