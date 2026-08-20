# Tower Person Owner Decision Workflow / TWR061–TWR065

The owner can review pending person-control events and record one append-only decision:

- APPROVED
- REJECTED
- HOLD
- RETURN_FOR_CHANGES

Approved events become effectively READY_FOR_VAULT.

The source event is never rewritten.

The owner decision is a new append-only event with its own receipt.

Vault delivery remains disabled in this layer.
