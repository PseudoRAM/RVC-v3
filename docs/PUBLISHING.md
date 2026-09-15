# Publish the source and a Replicate candidate

## GitHub

The prepared repository contains code, documentation and dependency-free tests.
Model weights, scratch generated audio, caches, environments and private credentials
are ignored. Two attributed input WAVs in `examples/audio/` and four selected AISO
outputs in `examples/converted/`, plus four English-trained VCTK outputs in
`examples/english/`, are available for Git.
`python scripts/package_source.py` creates `dist/rvc-v3-source.zip`
using an allowlist, suitable for a new repository or source release.

GitHub destination: `PseudoRAM/RVC-v3`. From the
prepared local repository after reviewing your commit:

```sh
git branch -M main
git remote add origin https://github.com/PseudoRAM/RVC-v3.git
git push -u origin main
```

The commands above describe the initial remote setup; skip adding it if already configured.
The included GitHub Actions workflow runs unit tests and syntax checks on Linux
and Windows. It does not claim GPU, audio-quality, or container validation.

## Replicate

1. Install Docker, NVIDIA GPU support and [Cog](https://github.com/replicate/cog).
2. Run `python scripts/download_models.py` and
   `python scripts/download_english_voices.py`. The image explicitly includes
   VCTK226 (male, API default) and VCTK231 (female), with their indexes. Their
   license and attribution notices are included from `examples/licenses/`.
   Other voice directories are excluded. For an additional voice whose
   model, source and speaker permissions cover your deployment, append these exact
   exceptions to `.dockerignore` (replace `MyVoice` with its directory name):

   ```text
   !rvc_models/MyVoice/
   !rvc_models/MyVoice/**
   ```

   Keep its license, attribution and provenance with the weights. Do not remove
   the catch-all exclusion. A trusted custom model URL can instead supply a voice
   at runtime. See [voice asset research](VOICE_ASSETS.md).
3. Run `python scripts/download_examples.py` for the human speech test clips.
4. Build and test on Linux, including the intended Replicate GPU:

```sh
cog build
cog predict -i input_audio=@examples/audio/male.wav -o male-output.wav
cog predict -i input_audio=@examples/audio/female.wav -i rvc_model=VCTK231 -i use_index=true -o female-output.wav
```

5. Review the built image's voice assets: Git ignores do not control the container.
   The working folder may contain private/local voices that must not be included in
   a public image. Build from a clean source extraction with only intended assets.
6. Publish to the separate candidate `pseudoram/rvc-v3` from the reviewed build
   directory. This destination is configured in `cog.yaml`:

```sh
cog login
cog push r8.im/pseudoram/rvc-v3
```

No publish workflow runs automatically. The existing `pseudoram/rvc-v2`
deployment is unaffected.

The Python 3.10/CUDA 11.8 container configuration is a candidate. Native Windows
inference and a [Linux Cog build with GPU smoke tests](CONTAINER_TEST.md) have
passed locally on an RTX 4090. The image was also pushed successfully to
`pseudoram/rvc-v3`, and four hosted T4 smoke requests passed, including confirmed
voice-cache reuse. See the validation report for the exact version and timings.
The requirements pin direct dependencies, not a full Linux transitive lock.

Before switching clients, compare human speech and singing, short/long clips,
female/male sources, pitch methods, retrieval, failures and resource growth.
Measure true container cold startup separately from warm inference. Keep the old
version ID for rollback. Review [SECURITY.md](../SECURITY.md) before accepting
arbitrary model URLs on a public service.

Reference: [Replicate custom model deployment](https://replicate.com/docs/get-started/deploy-a-custom-model).
