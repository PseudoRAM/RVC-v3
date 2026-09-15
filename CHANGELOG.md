# Changelog

## 0.1.0 — RVC v3 service candidate

- Retain HuBERT/RMVPE across requests and bound cached voice models.
- Cache custom voice downloads with expiry, refresh and archive limits.
- Support WAV/MP3 output, CREPE hop selection and optional retrieval.
- Add local conversion/benchmark commands and attributed human-speech examples.
- Add source packaging, shared-model checksum downloads and cross-platform unit CI.

`v3` is the service release name; checkpoint support remains RVC v1/v2.
Linux container/T4 validation and production hardening remain pending.
