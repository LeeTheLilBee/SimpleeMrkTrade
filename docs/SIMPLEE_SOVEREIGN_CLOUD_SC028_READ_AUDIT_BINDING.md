# SIMPLEE SOVEREIGN CLOUD — SC028 EXACT READ AUDIT BINDING

Date: September 28, 2026. Based on verified merged `vault-dev` source `517f0ac2f1a8626ab40ae44e6fb35527cbeb2688` after SC027. Source-only; **production NO_GO**.

## Gap

SC027 correctly requires a durable acknowledged primary before any signed encrypted read can reach the provider. The operational journal still recorded only generic `read_intent` / `read_verified` events keyed by opaque request tag and namespace. Those events did not themselves bind the read request to the exact immutable object ref and ciphertext SHA. A later audit could prove that "a read happened" but not, from the Cloud journal alone, which acknowledged ciphertext the request was tied to.

## Change

SC028 adds an append-only `read_intents` table. Every journaled read first reserves an exact tuple:

- opaque read request tag derived from entity namespace + logical read ID;
- opaque namespace digest;
- exact Cloud object ref;
- exact ciphertext SHA-256;
- creation timestamp.

The entire row is committed into a `READ_RESERVED` audit-chain event using the same reservation hash discipline as primary and backup intents. Reservation runs in a `BEGIN IMMEDIATE` transaction and transactionally rechecks that the exact primary ref/hash is currently `WRITE_ACKNOWLEDGED` or `RECONCILE_PRESENT`. A raw provider object, later ACK, wrong entity, wrong ref/hash or primary integrity HOLD cannot create a read reservation or reach provider GET.

Existing `read_intent` and `read_verified` audit events now use a separate read-tag namespace and require the exact durable read reservation to exist. `read_verified` additionally requires a preceding `read_intent`. Read-integrity and primary-read backend incidents must also correspond to an existing reserved read request. Same logical read ID may be retried only against the same exact object/hash; a different object/hash with the same logical read ID is an idempotency conflict. Different read IDs may independently read the same acknowledged ciphertext.

Historical verification now rejects:
- a bound read with no exact primary journal source;
- a read reserved before the primary was acknowledged, even if ACK appears later;
- generic `read_intent` / `read_verified` events with no durable exact read reservation;
- mutated read reservation metadata;
- a verified read event with no earlier intent.

## Limits

This is local source audit provenance, not proof of live Tower signer identity, mTLS, Vault retention/receipt policy, provider access logs, external SIEM, employee/user attribution, legal audit certification or independent immutable custody. The journal still stores no plaintext, raw entity name, document body or reusable Tower credential. A successful source read remains encrypted VLT1 bytes only.

No HTTP route, provider, paid resource, production secret, user document, deployment or owner release is added. Real service identity and canonical Vault read authorization remain owning-workstream gates in [issue #99](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/99).
