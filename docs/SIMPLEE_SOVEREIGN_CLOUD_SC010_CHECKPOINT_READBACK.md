# SIMPLEE SOVEREIGN CLOUD — SC010 CHECKPOINT DELIVERY READ-BACK

Date: September 27, 2026. Based on merged SC009 `vault-dev` head `153bc2f9a4fe814b18bc6db4f2eae80d40f14832`. Production **NO_GO**.

## Gap

SC005 defines an independently signable hash-chain prefix checkpoint and a separately injected create-only sink. Its original `deliver_source_checkpoint` verified the signed checkpoint and called `sink.put_if_absent`, then returned the reference based on the sink's acknowledgement **without checking that the sink retained the same signed bytes**. An erroneous provider may return success after dropping, substituting or corrupting its copy. The protocol already exposed `CheckpointSink.get`, but delivery did not use it.

## Change

Delivery now requires BOTH create-only PUT and exact read-back capability. It verifies the checkpoint signature and local fully verified journal prefix first, invokes one put-if-absent, and reads back the exact reference. It then requires the result to be a `SignedCheckpoint` with byte-for-byte matching canonical payload and signature, re-verifies Ed25519 and journal prefix, and only then returns the internal reference.

A reported ACK with a missing, altered, non-checkpoint or temporarily inaccessible read-back is **not success**. If the sink accepted the put and lost read-back, the caller receives an ambiguous external state and must reconcile that SAME checkpoint/reference with separately authorized custody; it must never blindly repeat a put or create a substitute anchor. Read-back success still does **not** certify WORM, independent operator, genuine offsite jurisdiction, physical-server owner, immutable retention, independent signer custody or long-term rollback protection.

## Source acceptance

New synthetic fakes cover correct exact bytes; fake ACK then drop; altered signature/payload; wrong return type; missing GET contract; independently inaccessible read-back after accepted put; no automatic re-PUT; and default-disabled live delivery. The full Cloud regression suite and independent Vault/Cloud corridor source workflow remain in CI.

## Release boundary

No real external checkpoint store, live signer/private key, provider, Tower/Vault authorization, production route, physical backup/site failover, paid resource or real document is added. Real ownership/custody, durable signed external checkpoints and operational reconciliation are still owner and external-team gates in issues #66 and #99.
