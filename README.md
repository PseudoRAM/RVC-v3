# RVC-v3 — Voice Conversion Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Convert a recording with an RVC voice model, locally or through a Cog container
on Replicate. This is a serving-focused successor to
[pseudoram/rvc-v2](https://replicate.com/pseudoram/rvc-v2), with persistent models
and bounded caches for repeated requests.

**“v3” names this service release. Voice checkpoints remain RVC v1/v2.**
This repository provides a CLI and API backend; it does not include the v2 Gradio UI.

## Listen: before and after

Each player runs through **original recording → male target p226 → female target
p231**, with the current voice and pitch setting shown on screen. These are the
actual English-trained RVC v2 conversions from the WAV examples below.

### Male narration

[Play the male comparison](examples/previews/male-comparison.mp4)

Original at **0:00**, male target at **0:15**, female target at **0:30**.

### Female narration

[Play the female comparison](examples/previews/female-comparison.mp4)

Original at **0:00**, male target at **0:14**, female target at **0:28**.

| Original recording | Male target p226 | Female target p231 |
| --- | --- | --- |
| [Male source WAV](examples/audio/male.wav) | [Converted WAV · 0 semitones](examples/english/male-to-vctk226.wav) | [Converted WAV · +8 semitones](examples/english/male-to-vctk231.wav) |
| [Female source WAV](examples/audio/female.wav) | [Converted WAV · −8 semitones](examples/english/female-to-vctk226.wav) | [Converted WAV · 0 semitones](examples/english/female-to-vctk231.wav) |

Inputs: LibriSpeech narration by **Garth Comira** and **Heather Barnett**, CC BY 4.0.
Converted segments are modified recordings using **Nekochu's VCTK p226/p231**
models, RMVPE and retrieval at 0.5. The players use AAC audio for browser playback;
the WAV links retain the original example files. See [source credits](examples/README.md),
[model credits and conversion settings](examples/ENGLISH.md), and
[preview reproduction](examples/previews/README.md).

## Features

- Load HuBERT and RMVPE once per worker.
- Reuse voice models with a bounded memory cache.
- Cache custom ZIP downloads with expiry, refresh, size limits and validation.
- Convert to WAV or MP3; adjust pitch and preserve unvoiced sounds.
- Choose RMVPE or Mangio-CREPE, with configurable CREPE hop length.
- Enable an optional FAISS retrieval index.
- Measure first and repeated requests with reproducible benchmark tools.

## Quick start

### 1. Prepare the environment

Use Python 3.10 and FFmpeg. The initial compatibility stack is Torch 2.0.1,
CUDA 11.8 and Fairseq 0.12.2. CUDA-enabled NVIDIA hardware is recommended.

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install pip==24.0 setuptools==69.5.1 wheel==0.43.0
python -m pip install -r requirements.txt
python -m pip install fairseq==0.12.2
```

Fairseq's legacy dependency metadata requires pip below 24.1. Direct dependencies
are pinned; this is not a complete transitive lock. Linux CPU/macOS installation
requires an appropriate Torch build rather than the CUDA requirements above.

### 2. Get shared models and a voice

```sh
python scripts/download_models.py
```

The script downloads HuBERT and RMVPE and verifies their SHA256 checksums.
Place your trusted voice checkpoint and optional index under `rvc_models/MyVoice/`:

```text
rvc_models/
  hubert_base.pt
  rmvpe.pt
  MyVoice/
    voice.pth
    voice.index
```

Voice checkpoints are supplied separately, not redistributed in this source
release. See [voice and audio licensing research](docs/VOICE_ASSETS.md),
[model setup](rvc_models/README.md) and [runtime trust limits](SECURITY.md).

### 3. Convert audio

```sh
python scripts/convert.py input.wav output.wav --voice MyVoice
python scripts/convert.py input.wav output.mp3 --voice MyVoice --pitch 3 --use-index
```

For a trusted custom model ZIP, provide `--model-url "https://.../voice.zip"`.
A ZIP must contain exactly one `.pth` and at most one `.index` file. Directory
nesting is supported. Use `--runs 7` to measure repeated requests in one process;
the first result is retained at the requested output path.

## Try real speech examples

The two input recordings are included in this repository:

| Source | Listen / download | Duration |
| --- | --- | --- |
| Male narration — Garth Comira | [Male input WAV](examples/audio/male.wav) | 14.84 s |
| Female narration — Heather Barnett | [Female input WAV](examples/audio/female.wav) | 13.91 s |

### English-trained RVC v2 targets

The **VCTK p226 male** and **VCTK p231 female** checkpoints from Nekochu are
trained on English speech. Both are RVC v2, 40 kHz, with pitch guidance.

| Source | Male target p226 | Female target p231 |
| --- | --- | --- |
| Male narration | [Listen / download](examples/english/male-to-vctk226.wav) | [Listen / download](examples/english/male-to-vctk231.wav) |
| Female narration | [Listen / download](examples/english/female-to-vctk226.wav) | [Listen / download](examples/english/female-to-vctk231.wav) |

Warm medians: **0.39–0.40 s** for these roughly 14-second clips on a local RTX 4090,
including retrieval at 0.5. Same-gender examples use zero pitch shift; cross-gender
examples use +8/-8 semitones as comparison settings, not universal recommendations.
See [English example credits, model links and reproduction](examples/ENGLISH.md).

### Japanese-trained comparison targets

Here are actual conversions with downloaded,
trained AISO RVC v2 female voices (model creator: 鶴乃; distributor: ちはや神社):

| Source | HOWATTO output | SITTORI output |
| --- | --- | --- |
| Female | [Listen / download](examples/converted/female-to-aisohowatto.wav) | [Listen / download](examples/converted/female-to-aisosittori.wav) |
| Male | [Listen / download](examples/converted/male-to-aisohowatto.wav) | [Listen / download](examples/converted/male-to-aisosittori.wav) |

Both targets are Japanese-trained female speech voices, 40 kHz, with no pitch
guidance or retrieval index. English quality needs listening review. Warm median
conversion times were 0.158–0.163 seconds on a local RTX 4090, five runs per case
with the first excluded; these are not Replicate/T4 or cold-start measurements.
See [credits, model terms and reproduction](examples/README.md).
The source-only ZIP omits audio; its users can fetch the same inputs below.

```sh
python scripts/download_examples.py
python scripts/convert.py examples/audio/female.wav female-output.wav --voice MyVoice --use-index
```

The examples are human audiobook recordings from LibriSpeech, also used by
librosa: a female narration by Heather Barnett and a male narration by Garth
Comira. The download script verifies source checksums. Attribution and the
CC BY 4.0 license are in [examples/README.md](examples/README.md).

Start with a source close to the target model's vocal range. For a female source
and female target, test zero shift first. For a lower-pitched source, compare pitch
shifts rather than assuming a universal value. An index can help match the target
timbre but adds processing. A character model is not a general test of natural
female-voice quality. Always listen to source and converted audio.

For a five-case pitch/index comparison, after provisioning both target voices:

```sh
python scripts/speech_demo.py --female-voice MyFemaleVoice --male-voice MyMaleVoice
```

Outputs and timing data are written to `benchmarks/speech/`, excluded from Git.

## Replicate / Cog

The container configuration includes the English VCTK226 male and VCTK231 female
voices. Download their pinned weights before building on a Linux NVIDIA Docker/Cog setup:

```sh
python scripts/download_models.py
python scripts/download_english_voices.py
cog build
cog predict -i input_audio=@examples/audio/male.wav -o male-output.wav
cog predict -i input_audio=@examples/audio/female.wav -i rvc_model=VCTK231 -o female-output.wav
cog login
cog push r8.im/pseudoram/rvc-v3
```

| Input | Default | Purpose |
| --- | --- | --- |
| `input_audio` | required | Source recording |
| `rvc_model` | `VCTK226` | `VCTK226` male, `VCTK231` female, or another provisioned voice directory |
| `custom_rvc_model_download_url` | none | Trusted voice ZIP URL, overrides directory selection |
| `pitch_change` | 0 | Semitone shift |
| `f0_method` | `rmvpe` | `rmvpe` or `mangio-crepe` |
| `crepe_hop_length` | 160 | Hop in samples at 16 kHz, for CREPE |
| `use_index` | false | Enable retrieval if an index is present |
| `index_rate` | 0.5 | Retrieval blend, used only when enabled |
| `protect` | 0.33 | Preserve breath/unvoiced consonants; 0.5 disables protection |
| `rms_mix_rate` | 0.25 | Input/output loudness blend |
| `filter_radius` | 3 | Legacy input; median filtering applies to harvest, not the exposed methods |
| `output_format` | `wav` | `wav` or `mp3` |
| `refresh_custom_model` | false | Redownload a cached custom model |

Weights are separate downloads and are excluded from Git. The image includes only
the shared models and the two explicitly allowed VCTK voices, with their notices
in `examples/licenses/`. The [publishing guide](docs/PUBLISHING.md) covers the
separate `pseudoram/rvc-v3` candidate.

## Performance and validation

The [human-speech test results](docs/HUMAN_SPEECH_TEST.md) cover female/male sources
and pitch/index variants on a local RTX 4090. These are measurements of execution,
not proof of perceptual quality or T4 performance.

An earlier 19.09-second synthetic-source test measured approximately 6x faster warm
requests than the original local v2 pipeline, but that source was unsuitable for
judging voice quality. Do not use that test as a female-voice quality demonstration.
The first process request can be slower because shared models are preloaded.

```sh
python scripts/benchmark.py input.wav --voice MyVoice --runs 10
python -m unittest discover -s tests -v
```

The unit tests run without ML dependencies; CI also checks Python syntax on Linux
and Windows. Native Windows GPU inference and the [Linux Cog image smoke test](docs/CONTAINER_TEST.md)
have run successfully on an RTX 4090. T4 timings, long-input behavior and production
soak tests remain unverified. Newer Torch/CUDA stacks and compilation are future benchmark work.

## Serving behavior

- One request at a time per worker; caches are local to that worker.
- `RVC_VOICE_CACHE_SIZE=1` retains one voice, in addition to HuBERT/RMVPE.
- Custom downloads retain up to four entries, expire after 24 hours and limit each
  archive/extracted model to 1 GiB. Signed URL changes can cause cache misses.
- `RVC_EMPTY_CACHE=1` restores frequent allocator clearing for comparison; default
  behavior retains reusable GPU allocations. Indexes are currently read per request.
- Successful service calls retain a temporary output directory until the caller
  consumes it. CLI tools clean it up. Verify Cog's output lifecycle during soak tests.
- Container exclusions allow HuBERT/RMVPE and the VCTK226/VCTK231 checkpoints and
  indexes. Other local voice directories are excluded.

## Credits and license

MIT for this repository's code; see [LICENSE](LICENSE). Based on PseudoRAM's
[RVC-v2-UI](https://github.com/PseudoRAM/RVC-v2-UI), derived from SociallyIneptWeeb's
AICoverGen, with RVC, HuBERT, RMVPE and the upstream projects acknowledged in the
source. Initial base commit: `1d01d5126f7e6ffbbf14e0090b6d150349ecfeef`.
Audio datasets and third-party model weights carry their own terms and attribution.
