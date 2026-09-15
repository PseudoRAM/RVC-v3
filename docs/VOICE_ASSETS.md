# Voice and audio asset research

Reviewed 2026-09-15; updated after finding and testing trained AISO v2 voices.
Weights remain separate downloads. Code licenses do not automatically license weights,
training recordings, or a person's voice. Existing benchmark reports are historical
measurements, not recommendations to redistribute their target voices.

## Test inputs available now

| Input | Reader | Duration | Source and attribution |
| --- | --- | --- | --- |
| Male | Garth Comira | 14.84 s | [librosa LibriSpeech excerpt](https://librosa.org/data/audio/5703-47212-0000.txt) |
| Female | Heather Barnett | 13.91 s | [librosa LibriSpeech excerpt](https://librosa.org/data/audio/198-209-0000.txt) |

Run `python scripts/download_examples.py`. Files land in `examples/audio/`.
[Full credits and download links](../examples/README.md) accompany these recordings.
[OpenSLR](https://www.openslr.org/12/) lists CC BY 4.0. Preserve attribution, link
the license, label conversions as modified audio, and do not imply endorsement.
The [CC license](https://creativecommons.org/licenses/by/4.0/) explicitly notes
that publicity, privacy and other rights may still apply. These are conversion
inputs, not a claim of permission to train and market clones of the narrators.

## Trained RVC v2 models found

### English-trained replacement pair

[Nekochu/RVC-VCTK_Voice-sample](https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample)
provides trained RVC voices from the English VCTK corpus, including **p226 (male)**
and **p231 (female)**. We selected the `rmvpe/` `.pth` variants and matching v2
indexes at revision `005c2f948ee9dafd7e3aa7f261b4c3a24beebeef`. The repository
also contains Beatrice models; those are a different architecture and are not used.

The model card declares Apache 2.0. The [original VCTK release](https://doi.org/10.7488/ds/2645)
is an English voice-cloning corpus under CC BY 4.0. Retain Nekochu's credit, the
Apache license and VCTK attribution to Junichi Yamagishi, Christophe Veaux and
Kirsten MacDonald, University of Edinburgh CSTR (2019, version 0.92). Local copies
of the published model card and licenses are in `examples/licenses/`.
This is documented dataset/model provenance, not independent verification of
individual speaker releases or a warranty about every downstream use. Do not
attempt to identify anonymous speakers or imply their endorsement.
Both checkpoints passed restricted weights-only inspection and twenty local GPU
conversions. Four retained [English examples](../examples/ENGLISH.md) are linked
from the README; SHA256-pinned downloads are available via
`scripts/download_english_voices.py`.

| Model | Terms and source | Status |
| --- | --- | --- |
| AISO HOWATTO and SITTORI, female | [Publisher](https://booth.pm/ja/items/4701666) explicitly states MIT for model files and permission from the ten contributing speakers for AI use; [public checkpoint mirror](https://huggingface.co/wok000/vcclient_model/tree/c46962577db8cf3fba2b3fc3526af98eb6611840/rvc_v2_chihaya_jinja) | Downloaded; restricted weights-only inspection confirms v2, 768 features, 40 kHz, no pitch guidance. Four examples generated successfully. |
| Matsukaze / Refreshing Young Man, male | [Publisher](https://booth.pm/ja/items/4768759) states speaker approval and CC BY 4.0 including model; credit 松風 required | Trained v2 ZIP listed, 512 MB; download redirects to BOOTH login. Not downloaded/tested. |
| Cool Woman, female | [Publisher](https://booth.pm/ja/items/4763870) declares CC0 including model, based on Common Voice, with a no-speaker-identification condition | Trained v2 ZIP listed, 224 MB; not downloaded or validated. We used AISO, which has a clearer explicit speaker-permission statement. |

These voices were trained on Japanese audio. English accent and quality need
listening review. [Examples and reproducible commands](../examples/README.md)
retain credits and the upstream AISO notice. Publisher provenance statements are
not independent verification of the speakers' releases. The CC BY and MIT terms
support commercial use/redistribution subject to their conditions.

## Optional English training sources (not used for the examples)

Train reproducible RVC checkpoints from CMU ARCTIC **BDL (US male)** and
**SLT (US female)**, after obtaining and retaining each release's COPYING file.
These are dataset choices, not downloaded RVC checkpoints; no training has run.
The [creators' release announcement](https://groups.google.com/g/comp.speech.research/c/JSwdwjrP38A)
identifies these speakers. Their [primary paper](https://www.cs.cmu.edu/~awb/papers/ssw5/arctic.pdf)
describes studio recordings made for speech synthesis and permits commercial and
non-commercial use. This offers stronger provenance than scraped celebrity clips.
The Festvox site returned errors during this review, so the exact release license
still needs to be retrieved before packaging a derived model.

For a production voice with explicit consent covering cloning, commercial API
hosting and redistribution of checkpoints, use recordings from yourself or a
commissioned speaker with those permissions recorded in writing. A dataset's
copyright license alone should not be represented as that release.

## Ready-made RVC candidates investigated

| Candidate | Finding | Public Replicate bundle decision |
| --- | --- | --- |
| [Lunar RVC](https://huggingface.co/IssacMosesD/Lunar-RVC-Model) | Female RVC v2; model card tags MIT, LJSpeech and VCTK, but access is gated and speaker/source permissions were not established | Not cleared; no download or acceptance of gated terms |
| [Tsukuyomi-chan sample](https://huggingface.co/wok000/vcclient_model/raw/main/rvc_v2_alpha/tsukuyomi-chan/terms_of_use.txt) | Japanese character voice with documented corpus; this distributed model is restricted to VCClient and has additional usage restrictions | Not suitable as a drop-in Replicate default under those terms |
| [Tokina Shigure sample](https://huggingface.co/wok000/vcclient_model/raw/main/rvc_v2_alpha/tokina_shigure/terms_of_use.txt) | Japanese boy-like character voice, documented performer/corpus; this sample is VCClient-only. Original model and corpus have separate conditions | Not cleared for this service |
| [Razer112 Public Models license](https://huggingface.co/Razer112/Public_Models/blob/9c322dca1a2bfac28788e89146324878045ecb71/LICENSE) | Allows some commercial use but explicitly prohibits redistribution without written permission | Do not bundle based on the repository's license tag |

The AISO/Matsukaze models are Japanese; the VCTK pair above is English-trained.
TTS voices and speaker
embeddings are not drop-in replacements for RVC `.pth` checkpoints.

## Publication safeguards

- Git ignores the entire local model directory except its README, including ZIPs.
- The source release packager excludes model binaries and audio.
- `.dockerignore` excludes voice directories; only HuBERT, RMVPE and the README
  are allowed by default. Those shared models retain their own upstream terms.
- Demo/benchmark commands require explicitly named voices; no celebrity defaults.
- Existing local weights are retained. Nothing here removes weights from older
  published repositories, Git history or existing Replicate versions.
- Before including a voice, retain the source URL/revision, checksum, license,
  training provenance, speaker permission evidence and required credits. Follow
  [publishing instructions](PUBLISHING.md) to allow that specific directory.

The Linux Cog image has not been built in this environment; inspect its actual
contents before publication. The two AISO replacement targets were tested locally;
the male Matsukaze target remains untested. No new model training was performed.
