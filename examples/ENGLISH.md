# English-trained RVC v2 examples

## Models

| Target | Trained checkpoint | Local voice name |
| --- | --- | --- |
| Male p226 | [Mp226rmvpe.pth and index](https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample/tree/005c2f948ee9dafd7e3aa7f261b4c3a24beebeef/M/p226/rmvpe) | `VCTK226` |
| Female p231 | [Fp231rmvpe.pth and index](https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample/tree/005c2f948ee9dafd7e3aa7f261b4c3a24beebeef/F/p231/rmvpe) | `VCTK231` |

Creator: **Nekochu**. The [pinned model card](licenses/VCTK-model-card.md) identifies
VCTK training data, the Mangio RVC fork and 250 epochs. These are RVC `.pth`
checkpoints, not the Beatrice models also present in the upstream repository.
Restricted weights-only inspection confirms `version=v2`, `f0=1`, 768-dimensional
content features and 40 kHz output for both files.

## Before and after

| Source | Male p226 output | Female p231 output |
| --- | --- | --- |
| [Male input](audio/male.wav) | [Zero shift](english/male-to-vctk226.wav) | [+8 semitones](english/male-to-vctk231.wav) |
| [Female input](audio/female.wav) | [-8 semitones](english/female-to-vctk226.wav) | [Zero shift](english/female-to-vctk231.wav) |

RMVPE inference; retrieval enabled, index rate 0.5; remaining service settings
unchanged. Cross-gender pitch shifts are starting points, not calibrated optima.
Twenty conversions completed (five per case). Warm medians exclude the first
request of each case and range from 0.390 to 0.402 seconds on RTX 4090 with
Torch 2.0.1+cu118. All four retained WAVs are finite, non-silent, 40 kHz and have
zero full-scale clipped samples. These are local execution checks; they do not
establish perceptual quality, Replicate latency or container cold-start performance.
[Full timings, settings and file hashes](english/results.json).

## Reproduce

```sh
python scripts/download_models.py
python scripts/download_examples.py
python scripts/download_english_voices.py
python scripts/publishable_demo.py --collection vctk
```

Downloads are pinned to upstream revision
`005c2f948ee9dafd7e3aa7f261b4c3a24beebeef` and verified with SHA256 checksums.
Weights and indexes remain excluded from Git and default container builds.

## Credits and licenses

- **Models:** Nekochu, `RVC-VCTK_Voice-sample`; Apache 2.0 as declared in its model
  card. Preserve [Apache 2.0](licenses/APACHE-2.0.txt), the model card and attribution
  when redistributing. Checkpoints have not been modified.
- **Training corpus:** Junichi Yamagishi, Christophe Veaux and Kirsten MacDonald
  (2019), *CSTR VCTK Corpus: English Multi-speaker Corpus for CSTR Voice Cloning
  Toolkit, version 0.92*, University of Edinburgh CSTR.
  [Original source](https://doi.org/10.7488/ds/2645),
  [original CC BY 4.0 license](licenses/VCTK-CC-BY-4.0.txt).
- **Input recordings:** LibriSpeech excerpts read by Garth Comira (male) and
  Heather Barnett (female), distributed by librosa under CC BY 4.0.
  [Full source credits](README.md). These outputs are modified recordings with
  voice conversion and the pitch settings above applied; retain these credits.

The model license declaration and training provenance come from the model author.
Individual speaker releases were not independently reviewed. Dataset copyright
permission is not a guarantee concerning publicity/privacy rights for every use.
Do not identify anonymous corpus speakers or imply endorsement by them, Nekochu,
the input readers or the University of Edinburgh. Audio and model assets retain
their separate terms; the repository code's MIT license does not replace them.
