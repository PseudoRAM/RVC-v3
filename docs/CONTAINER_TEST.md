# Linux container validation

Tested on 2026-09-16 using Cog 0.22.0, Docker through WSL, and an NVIDIA RTX 4090.
The image uses Python 3.10, Torch 2.0.1+cu118, CUDA 11.8 and Fairseq 0.12.2.
These are local GPU measurements, not Replicate T4 or cloud cold-start results.

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

T4 latency, cloud cold starts, long recordings and production soak behavior still
need separate validation.
