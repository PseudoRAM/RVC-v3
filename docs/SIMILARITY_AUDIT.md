# Voice similarity audit — 2026-09-16

The David Goggins example was reported as a weak voice match. Execution speed,
finite samples, and absence of clipping do not validate speaker similarity.

## Findings

Compared the local original checkout at commit `1d01d51` with RVCV3 at
`63cbddd`, using the same DavidGoggins v2 checkpoint, source WAV, HuBERT,
RMVPE, CUDA environment, half precision, and controlled random seed.
HuBERT and RMVPE file hashes match across the two checkouts. Synthesizer and
RMVPE source files are unchanged. The RMVPE conversion path differs in cache
lifetime and CUDA allocator handling, not feature extraction or synthesis.

The original local `main.voice_conversion` always passes an empty retrieval
index path, even when index_rate is nonzero. At the time of this audit, RVCV3 defaulted to retrieval off
too, but the published Goggins demo explicitly enabled it at 0.5. That demo
therefore did not use the original local wrapper's settings.

The comparison script calls the original inference functions with the original
wrapper's parameters; it also tests V2 with an explicitly supplied index.
Models are loaded before resetting RNG to avoid measuring randomness consumed
by first-time model construction as an engine difference.

| Controlled WAV comparison | Correlation | Signal / difference (dB) |
| --- | ---: | ---: |
| V2 vs V3, retrieval off | 0.99999818 | 54.39 |
| V2 vs V3, retrieval 0.5 | 0.99999878 | 56.12 |
| V3 vs cached repeat after other settings | 0.99999924 | 58.16 |

These results do not show a material waveform regression for this local clip.
They are not speaker-identity scores, perceptual listening results, or proof
about every input, hardware configuration, or deployed Replicate version.
The exact previously preferred hosted version and output remain unverified.

Source median voiced pitch is 76.89 Hz. RVC keeps source pitch at zero shift;
it does not infer a target pitch distribution from the checkpoint. A source
range mismatch is a candidate explanation, not a demonstrated cause. The
target's training-pitch distribution was not available.

## Changes and listening candidates

Added a reproducible local parity check, including cached-request stability.
Added CLI controls for pitch method, CREPE hop, consonant protection, and RMS
envelope mixing, previously available only through the service/API. Defaults
and inference math remain unchanged pending evidence and listening feedback.

Generated retrieval blends 0.75 and 1.0, plus +3/+6-semitone variants at 0.75.
Published them with the V2/V3 baselines on the existing owner-private audio page.
No variant is claimed to improve identity until listening review selects it.
Do not choose a global pitch shift based on this single input.

### Listening feedback and Rogan comparison

The user preferred Goggins samples 5 and 6 (retrieval 0.75, pitch +3/+6),
but said similarity still needed improvement. This is a preference for this
source/model pair, not a globally accepted preset.

Repeated the comparison using the existing `JoeRogan-48k_e325_s10400.pth`
checkpoint and its matching index. V2/V3 correlation was 0.99999792 with
retrieval off and 0.99999904 at retrieval 0.5. Cached-repeat correlation was
0.99999867. All parity checks passed. Generated six Rogan variants: retrieval
off/0.5/0.75/1.0 at zero shift, and retrieval 0.75 at +3/+6 semitones.
All WAVs were 14.82 s, 48 kHz, finite, non-silent, with no full-scale clipping.
The delivered MP3s decoded successfully with peaks below full scale.
The private page includes these six variants and two V2 baselines.

The user also preferred Rogan samples 5 and 6 (+3/+6 at retrieval 0.75).
The next listening round preserves those exact clips as A/D and adds +4/+5
at retrieval 0.75 (B/C), plus +4/+5 at retrieval 0.90 (E/F). Other controls,
source audio, model and random seed remain fixed. Four new 14.82-second,
48 kHz WAVs and their MP3 encodings passed finite/non-silent signal checks;
decoded MP3 peaks stayed below full scale. No new global default was selected.

After this refinement the user accepted all six candidates and requested a
system default. Selected candidate B: +4 semitones, retrieval enabled when an
index is present, rate 0.75. These defaults are shared across service, CLI and
Cog API, with explicit per-request overrides. The choice is an accepted starting
point, not proof of optimal similarity for other inputs or models. Previous
statements about unchanged defaults describe the earlier investigation.

To retain separate outputs for another voice, use `--voice Rogan
--output-dir demo/rogan-comparison` with both comparison commands below.

## Reproduce

In the inference environment, from the RVCV3 checkout:

```powershell
$env:NUMBA_CACHE_DIR = (Resolve-Path .cache/numba).Path
python scripts/compare_legacy.py --engine v2 --legacy-root ..
python scripts/compare_legacy.py --engine v3 --legacy-root ..
```

Outputs and `parity.json` are in `demo/similarity-audit/`. The comparison exits
unsuccessfully if correlation is <=0.9999 or signal/difference is <=40 dB.
This tolerance allows small GPU floating-point differences and is a regression
check, not an audio-quality acceptance threshold. The downloaded voice and
shared models must already be provisioned. Unit suite: 7 tests passed. A real
conversion with the newly exposed CLI controls also passed.
