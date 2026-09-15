# Publish the source and a Replicate candidate

## GitHub

The prepared repository contains code, documentation and dependency-free tests.
Model weights, input/output audio, caches, environments and private credentials
are ignored. `python scripts/package_source.py` creates `dist/rvc-v3-source.zip`
using an allowlist, suitable for a new repository or source release.

Create an empty GitHub repository, for example `PseudoRAM/RVC-v3`. Then, from the
prepared local repository after reviewing your commit:

```sh
git branch -M main
git remote add origin https://github.com/PseudoRAM/RVC-v3.git
git push -u origin main
```

The name above is a suggested destination, not an existing/published repository.
The included GitHub Actions workflow runs unit tests and syntax checks on Linux
and Windows. It does not claim GPU, audio-quality, or container validation.

## Replicate

1. Install Docker, NVIDIA GPU support and [Cog](https://github.com/replicate/cog).
2. Run `python scripts/download_models.py` and provision authorized voice weights.
3. Run `python scripts/download_examples.py` for the human speech test clips.
4. Build and test on Linux, including the intended Replicate GPU:

```sh
cog build
cog predict -i input_audio=@examples/audio/female.wav -i rvc_model=MyVoice -i output_format=wav
```

5. Review the built image's voice assets: Git ignores do not control the container.
   The working folder may contain private/local voices that must not be included in
   a public image. Build from a clean source extraction with only intended assets.
6. Create a separate candidate model in your Replicate account, for example
   `pseudoram/rvc-v3`, then publish from that clean build directory:

```sh
cog login
cog push r8.im/pseudoram/rvc-v3
```

Neither destination is configured in the source, and no publish workflow runs
automatically. The existing `pseudoram/rvc-v2` deployment is unaffected.

The Python 3.10/CUDA 11.8 container configuration is a candidate. Native Windows
inference has been tested; a Linux Cog build and T4 inference still need validation.
The requirements pin direct dependencies, not a full Linux transitive lock.

Before switching clients, compare human speech and singing, short/long clips,
female/male sources, pitch methods, retrieval, failures and resource growth.
Measure true container cold startup separately from warm inference. Keep the old
version ID for rollback. Review [SECURITY.md](../SECURITY.md) before accepting
arbitrary model URLs on a public service.

Reference: [Replicate custom model deployment](https://replicate.com/docs/get-started/deploy-a-custom-model).
