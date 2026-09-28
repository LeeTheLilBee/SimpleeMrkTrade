# BBX097–101 — External Proof Intake and Release Matrix

BuyBox now has one explicit boundary for externally authoritative facts. A browser form, local JSON object, locally typed READY value, or shaped receipt cannot become Tower/Teller/Vault/Grounds/ATM authority.

`record_verified_external_proof` accepts an opaque raw payload only through a separately injected trusted server-side verifier. The verifier must return authenticated claims bound to the exact persisted BuyBox opportunity ID, revision, and SHA-256 source digest. BuyBox stores only minimized receipt metadata and never credentials, balances, document bytes, title data, or payment instructions.

The release matrix expects Tower protected-action proof, Teller money+management proof, and Vault canonical archival proof. ATM and multifamily additionally require the receiving operations system's independent acceptance. Old proofs automatically stop counting after a saved opportunity revision changes.

Even when every external receipt is present, the matrix remains non-executing: owner release and hosted-runtime certification are still separate requirements. It cannot authorize purchase, closing, capital deployment, or operational takeover.

This is source-side completion only. It does not create external issuers, network routes, production secrets, paid hosting, direct OB access, or synthetic external approvals.
