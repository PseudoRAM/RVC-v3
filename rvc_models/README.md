# Model assets (download separately)

Run `python scripts/download_models.py` to fetch HuBERT and RMVPE. Their SHA256
hashes are checked against the upstream file pages:

- [HuBERT](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/hubert_base.pt)
- [RMVPE](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/rmvpe.pt)

Place each trusted voice checkpoint in its own directory:

```text
rvc_models/
  hubert_base.pt
  rmvpe.pt
  MyVoice/
    voice.pth
    voice.index  # optional
```

Each voice must have exactly one `.pth` and at most one `.index`. The directory
name is the `rvc_model` API input / `--voice` CLI argument. Nested ZIP folders are
supported for custom downloads. Voice weights and indexes are not part of the
source release; supply models that you have permission to use. Local voice files
are excluded from Git. The container explicitly includes VCTK226 and VCTK231;
fetch those English voices with `python scripts/download_english_voices.py`.
Other voice directories are excluded from container builds. See
[voice asset research](../docs/VOICE_ASSETS.md) and the
[publishing guide](../docs/PUBLISHING.md) before explicitly including a voice.
