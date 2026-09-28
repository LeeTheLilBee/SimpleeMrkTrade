# BuyBox source-only readiness stored-proof integrity — 2026-09-28

The protected Integration Readiness projection previously counted any persisted object with a matching `deal_fingerprint` as a present external proof. Now it requires the exact verifier-produced local receipt-record fields, digest integrity, linked deal identity and prior revision, expected safe flags, valid timestamp and properly formatted receipt/issuer/source digests. Malformed, scalar, injected, unhashable or modified records are treated as **missing** rather than crashing or displaying a receipt as present. Genuine records from the trusted adapter remain current across proof-only saves; a material deal change still invalidates them.

The record SHA-256 is an **unkeyed local integrity check**, not proof of an external issuer and not a substitute for a separately authenticated server adapter. The source-only `record_verified_external_proof` boundary still requires independent verifier injection; no browser may mint a genuine readiness receipt. Even a complete matrix does not authorize purchase, close, capital or property/ATM operational transfer.

No direct OB access, fabricated Tower/Teller/Vault/Grounds acceptance, live deployment or paid Render resources. Parent BuyBox PR #26 remains draft.
