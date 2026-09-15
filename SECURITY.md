# Runtime trust boundary

This release retains a legacy Torch/Fairseq stack for compatibility. It has not
been audited or hardened for hostile checkpoint uploads. PyTorch checkpoint
deserialization can execute code; use trusted voice sources only. Archive path
handling and size limits do not make checkpoint contents safe.

Custom URL fetching also needs host/network restrictions when exposed publicly:
this implementation accepts HTTP(S) URLs and follows redirects. It does not
implement an SSRF allowlist or isolate model loading. Restrict permitted sources
and isolate ingestion before operating an unrestricted public upload service.

Do not place tokens, credentials or private checkpoints in source releases or
public container builds. The source package builder excludes weights and data,
but the Cog image intentionally includes provisioned model assets.

Report security issues privately to the repository owner's security reporting
channel when it is configured. Avoid posting secrets or exploit payloads in
public issues.
