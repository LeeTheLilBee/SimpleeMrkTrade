# Tower Person Existing Vault Handoff Adapter / TWR066–TWR070

This layer does NOT create a second Vault transport.

It maps an approved TOWER_PERSON_CHANGE_PROOF packet into an existing Vault handoff callable.

Delivery gates:

1. Person event exists.
2. Owner decision exists.
3. Owner decision is APPROVED.
4. Packet is READY_FOR_VAULT.
5. Existing handoff callable resolves.
6. Existing handoff executes.
7. Only explicit acceptance/sealing marks VAULT_SEALED.

Unresolved or ambiguous handoff results fail closed.

The browser never calls Vault directly.
