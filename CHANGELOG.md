# Changelog

## Unreleased

- Adopt the accepted Rogan listening preset as shared service, CLI and Cog API
  defaults: pitch +4 semitones, retrieval enabled when available, index rate 0.75.
- Add `--no-use-index` for explicit retrieval opt-out; per-request pitch and
  retrieval overrides remain supported. Existing deployments need rebuilding
  to adopt the new defaults.
- Keep historical example and legacy comparison scripts on explicit recorded settings.

## 0.1.0 — RVC v3 service candidate

- Retain HuBERT/RMVPE across requests and bound cached voice models.
- Cache custom voice downloads with expiry, refresh and archive limits.
- Support WAV/MP3 output, CREPE hop selection and optional retrieval.
- Add local conversion/benchmark commands and attributed human-speech examples.
- Add source packaging, shared-model checksum downloads and cross-platform unit CI.

`v3` is the service release name; checkpoint support remains RVC v1/v2.
Linux container/T4 validation and production hardening remain pending.
