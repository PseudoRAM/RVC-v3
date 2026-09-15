# Human speech validation — 2026-09-15

## Inputs

The earlier synthetic clip was unsuitable for judging output voice quality.
This test uses two human audiobook excerpts from LibriSpeech distributed as
librosa examples. See [source attribution and download instructions](../examples/README.md).

- Female: Heather Barnett reading *Sense and Sensibility*, utterance `198-209-0000`,
  13.910 seconds, 16 kHz mono. RMVPE median voiced pitch: 212.37 Hz.
- Male: Garth Comira reading *The Ashiel Mystery*, utterance `5703-47212-0000`,
  14.840 seconds, 16 kHz mono. RMVPE median voiced pitch: 76.89 Hz.

These pitch statistics describe these recordings; they are not target voice
ranges and do not prove that any particular semitone shift is optimal.

## Run configuration and results

RTX 4090, Windows, Python 3.9.13, Torch 2.0.1+cu118. Shared model setup took
2.596 seconds (excluding import time). RMVPE was also used to analyze
sources before conversions, so the first conversion is not a cold-start benchmark.

Five requests per case, retaining the first output and reporting the median of
four repeats. RMVPE, protect 0.33, RMS mix 0.25, index rate 0.5 where enabled.
The same worker is used across cases. The 25 conversions completed successfully.

| Case / output stem | Target checkpoint label | Semitone shift | Retrieval | Warm median |
| --- | --- | ---: | --- | ---: |
| female-zero-no-index | Sandy | +0 | off | 0.215 s |
| female-zero-index | Sandy | +0 | on | 0.315 s |
| female-plus3-index | Sandy | +3 | on | 0.315 s |
| male-to-female-plus8-index | Sandy | +8 | on | 0.321 s |
| male-zero-index | Rogan | +0 | on | 0.470 s |

Sandy uses `SandyCheeks.pth`; Rogan uses `JoeRogan-48k_e325_s10400.pth`.
These are local, separately provided RVC v2 checkpoints. They are not in the source
release. The tested Sandy model is a character voice, not a natural female baseline.

All outputs were finite, non-silent and had zero full-scale clipped samples.
Female-source outputs are 13.9 seconds; male-source outputs are 14.82 seconds.
This only verifies execution and simple signal properties. It does not establish
naturalness, speaker similarity, or that the user's quality concern is resolved.
Listen to the female-source zero-shift pair before assessing retrieval and compare
+3 only as a controlled variant. The male-to-female +8 case is exploratory, not a
recommended universal pitch adjustment.

## Reproduce and listen

```sh
python scripts/download_examples.py
python scripts/speech_demo.py --female-voice Sandy --male-voice Rogan --runs 5
```

Provision the target voices first. Audio appears under `benchmarks/speech/`.
The source recordings are under `examples/audio/`. Generated conversions are
modified versions of the attributed recordings. Audio is intentionally omitted
from the public source archive; the commands reproduce the comparison with the
same supplied models.

[Raw measurements](benchmarks/human-speech-2026-09-15.json).

This is a local demo, not a Linux/Cog build test or a Replicate T4 benchmark.
The four-repeat medians do not characterize production tail latency. Retrieval
currently reloads/reconstructs the FAISS index per request and therefore has a
visible cost; index caching is a future optimization.
