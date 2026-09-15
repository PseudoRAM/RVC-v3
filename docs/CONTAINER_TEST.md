# Linux container validation

Tested on 2026-09-16 using Cog 0.22.0, Docker through WSL, and an NVIDIA RTX 4090.
The image uses Python 3.10, Torch 2.0.1+cu118, CUDA 11.8 and Fairseq 0.12.2.
The first section records local GPU measurements; hosted T4 checks are below.

The actual built image passed SHA256 checks for HuBERT, RMVPE, VCTK226,
VCTK231 and both retrieval indexes. Its model directory contained only those
assets, the README and voice provenance JSON. The Apache 2.0 notice, VCTK
attribution/license and model card were present. No other local voice weights
were included.

## Inference smoke test

The source code and models came from the built image. Only the two test inputs
and a directory for test outputs were mounted from the host. Each voice ran three
times in one service process, with RMVPE, zero pitch shift and retrieval at 0.5.

| Case | First conversion | Two repeated conversions | Output duration |
| --- | --- | --- | --- |
| Male input → VCTK226 | 1.503 s | 0.382 s, 0.285 s | 14.82 s |
| Female input → VCTK231 | 0.717 s | 0.340 s, 0.270 s | 13.90 s |

Shared-model setup inside the process took 2.811 seconds. This excludes container
startup and image transfer. Both WAVs were 40 kHz, finite and non-silent, with zero
clipped samples. An additional female-to-VCTK231 MP3 conversion passed. This small
smoke test demonstrates functionality; use longer runs for performance comparisons
and listen to the outputs before judging conversion quality.

## Reproduce the Cog API check

Both Cog API checks passed: male input with the default voice and WAV output,
and female input with VCTK231, retrieval enabled and MP3 output. The custom URL
input is explicitly optional so the generated Cog 0.22 schema requires only audio.

```sh
python scripts/download_models.py
python scripts/download_english_voices.py
cog build
cog predict r8.im/pseudoram/rvc-v3 -i input_audio=@examples/audio/male.wav -o male-output.wav
cog predict r8.im/pseudoram/rvc-v3 -i input_audio=@examples/audio/female.wav -i rvc_model=VCTK231 -i use_index=true -i output_format=mp3 -o female-output.mp3
```

## Hosted Replicate T4 smoke tests

Successfully pushed to [pseudoram/rvc-v3](https://replicate.com/pseudoram/rvc-v3),
configured as a private model on an NVIDIA T4. Version:
`c8b070a3bd63f4f25383d92e7c9b75e27c4d2f24b0432c339788df3abb73b230`.

| Input / target | Retrieval | Voice cache hit | Service total | Replicate reported prediction time |
| --- | --- | --- | --- | --- |
| Male → VCTK226, first | off | no | 3.902 s | 4.4 s |
| Male → VCTK226, another worker boot | off | no | 3.896 s | 4.4 s |
| Female → VCTK231, voice switch | 0.5 | no | 1.737 s | 2.3 s |
| Female → VCTK231, immediate repeat | 0.5 | yes | 0.922 s | 1.4 s |

All four hosted requests succeeded and returned playable WAVs: 14.82 seconds for
the male input and 13.90 seconds for the female input. Inputs are the attributed
recordings in `examples/audio/`; pitch shift was zero. The repeated female request
logged a 0.000476-second cache lookup/load and 0.922-second conversion.

The first two requests included a separate cloud boot wait. The prediction times
above exclude that wait and must not be described as end-to-end cold-start times.
This is a four-request functionality check, not a latency distribution or a
controlled comparison against v2. Cloud cold-start benchmarking, long recordings
and production soak behavior still need separate validation.
