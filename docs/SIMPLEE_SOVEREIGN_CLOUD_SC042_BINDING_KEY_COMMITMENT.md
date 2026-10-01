# SIMPLEE SOVEREIGN CLOUD — SC042 DURABLE NAMESPACE BINDING-KEY COMMITMENT

Date: October 1, 2026. Based on verified `vault-dev` commit `6882f8141315f005bfa9bd0cb679843830fe74a2` after SC041. Source-only; production remains **NO_GO**.

## Gap closed

SC038 made entity→opaque-namespace bindings durable, append-only and fail-closed for namespace drift. SC041 reconciled resolver-used namespaces against that durable registry. One subtle gap remained: the ledger itself could be reopened with a DIFFERENT 32-byte binding key and still pass structural event-chain verification. Entity lookups would later fail, but an inventory-only owner check could still describe the namespace registry as structurally valid.

SC042 creates a single append-only `ledger_metadata` row on a fresh empty source ledger containing a domain-separated SHA-256 commitment to the exact 32-byte namespace binding key. Every transaction, inventory, checkpoint-prefix read, explicit binding lookup and owner verification now first requires the supplied in-memory key to match that registered commitment.

A populated old source ledger with no commitment is NOT silently adopted. It fails at open with a reviewed-migration hold. Restart with the wrong key fails at ledger construction, before provider I/O or owner status can be generated. Metadata update/delete, duplicate metadata rows and partial legacy states fail closed.

The owner evidence desk exposes only `binding_key_matches_registered_commitment=True` when a supplied ledger passes this check. It does not expose the commitment value, raw binding key, entity tags, entity names or namespace values.

## What this proves — and what it does not

This proves only that the CURRENT source process holds the same high-entropy 32-byte secret that initialized that local ledger metadata. It does **not** prove:
- external KMS/HSM custody;
- secure operator access;
- approved key rotation or recovery;
- offsite immutability of the key commitment;
- that a malicious administrator who can rewrite the entire local DB and all external evidence cannot substitute both metadata and key;
- actual Tower/Vault registry authority;
- production readiness.

The existing SC039 control checkpoint still binds the namespace binding EVENT chain, not this new key-commitment metadata. Therefore `binding_key_commitment_external_anchor_certified=False` remains explicit. A later source hardening step may bind the commitment into the external control checkpoint format, but no existing checkpoint is reinterpreted retroactively.

The commitment is safe only under the existing requirement that the binding key is a uniformly random 256-bit secret. It is not a password verifier and must not be used with human-memorable or low-entropy material.

No paid infrastructure, provider account, production secret, hosted route, real document or release authority is introduced.
