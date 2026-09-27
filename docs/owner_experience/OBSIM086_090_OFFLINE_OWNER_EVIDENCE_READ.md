# OBSIM086–090 — downloaded synthetic report reader hardening

## Scope
The owner already has a working source-only, read-only offline integrity check:
`python -m scripts.ob_verify_owner_evidence --file /path/to/downloaded.json`.
Its existing envelope/sequence/hash checks deliberately demonstrate only **local
content integrity**, not authenticated provider data, Tower permission, a
signature or any live order/fill.

This pack hardens the path-to-file reader. The previous sequence
`Path.is_file(); Path.is_symlink(); Path.stat(); Path.open()` could admit a
symlink substituted between check and open, and file size could change during
read. The new implementation:

- rejects missing, empty, oversized, symlinked, directory and nonregular paths;
- uses an atomic `O_NOFOLLOW` open (fails closed on platforms lacking it),
  nonblocking mode to refuse special files, and fstat inode/device comparison
  against the original lstat;
- caps **actual bytes read** to 16 MiB + 1, rather than trusting only initial
  metadata; rejects invalid UTF-8, duplicate JSON keys and nonfinite values;
- passes parsed content to the unchanged original
  `verify_downloaded_owner_evidence_packet` for exact synthetic source,
  report chain, final receipt and packet hash validation;
- emits no failed packet contents, owner session token or claim of live grant.

The downloaded file is a device copy, not a guaranteed durable server archive.
Even a successful hash-only result is not an independent digital signature;
a malicious actor who could replace the whole file and recompute all unkeyed
hashes is not authenticated by this check. Real Manual Live, broker orders,
capital movement and hosted owner acceptance remain separate HOLD gates.
No Render configuration or deployment change.
