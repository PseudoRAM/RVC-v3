# Human speech test inputs

For English-trained male and female RVC v2 targets, see the
[English before/after examples](ENGLISH.md). The AISO examples below remain for comparison.

## Listen to the inputs

- [Male input WAV — Garth Comira, 14.84 seconds](audio/male.wav)
- [Female input WAV — Heather Barnett, 13.91 seconds](audio/female.wav)

These two WAVs are included for the public repository. They are format-converted
from the attributed Ogg sources below, with no voice conversion applied.
The converted examples below use downloaded AISO v2 checkpoints. No CMU models
were trained or used.

Run `python scripts/download_examples.py` from the repository root. It fetches
two real audiobook recordings used by librosa, verifies the published SHA256
hashes and decodes them to mono PCM WAV with FFmpeg. It does not synthesize speech,
shift pitch, denoise or normalize the recording. The Ogg distribution is lossy;
decoding to WAV does not restore the original recording's lost information.

| Output | LibriSpeech utterance | Recording / reader |
| --- | --- | --- |
| `audio/male.wav` | `5703-47212-0000` (`libri1`) | The Ashiel Mystery, narrated by Garth Comira |
| `audio/female.wav` | `198-209-0000` (`libri3`) | Sense and Sensibility, chapter 18, narrated by Heather Barnett |

Source: [LibriSpeech / OpenSLR 12](https://www.openslr.org/12/), prepared by Vassil
Panayotov with assistance from Daniel Povey. License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Direct files and attribution:

- [Male recording](https://librosa.org/data/audio/5703-47212-0000.hq.ogg), [attribution](https://librosa.org/data/audio/5703-47212-0000.txt).
- [Female recording](https://librosa.org/data/audio/198-209-0000.hq.ogg), [attribution](https://librosa.org/data/audio/198-209-0000.txt).
- [librosa example index](https://github.com/librosa/librosa/blob/main/librosa/util/example_data/index.json).
- [librosa checksum registry](https://github.com/librosa/librosa/blob/main/librosa/util/example_data/registry.txt).

The two named input WAVs and selected `converted/` examples are available for Git;
downloaded Ogg files and `generated/` scratch outputs remain ignored.
The source-only ZIP omits audio. Retain
this attribution if redistributing these clips or derived conversions, and label
converted recordings as modified audio. Voice checkpoints have separate terms.

For female voices, start with the female input at zero pitch shift. For conversion
from a lower-pitched speaker, compare several shifts instead of assuming zero or
a fixed octave works for every source/target. Pitch is only one factor: the voice
model's training quality, range, accent and retrieval index also affect results.
Character checkpoints should not be used to establish natural-female voice quality
in general. These input licenses are not permission to train clones of the readers;
see [voice asset research](../docs/VOICE_ASSETS.md).

## Trained RVC v2 examples

Targets: **AISO HOWATTO** and **AISO SITTORI**, created by 鶴乃 and distributed by
ちはや神社. [Publisher](https://booth.pm/ja/items/4701666),
[checkpoint mirror](https://huggingface.co/wok000/vcclient_model/tree/c46962577db8cf3fba2b3fc3526af98eb6611840/rvc_v2_chihaya_jinja).
The publisher identifies the models as blends of ten consenting women's voices
and licenses the weights under MIT. Preserve the [upstream notice](AISO-LICENSE.txt).
This provenance statement comes from the publisher; individual releases were not
independently inspected. These are Japanese-trained speech models, not English
singing models; both have `version=v2`, `f0=0`, 768 input features and 40 kHz output.

| Input | HOWATTO | SITTORI |
| --- | --- | --- |
| Female narration | [Converted WAV](converted/female-to-aisohowatto.wav) | [Converted WAV](converted/female-to-aisosittori.wav) |
| Male narration | [Converted WAV](converted/male-to-aisohowatto.wav) | [Converted WAV](converted/male-to-aisosittori.wav) |

Outputs are modified LibriSpeech recordings: original readers Garth Comira and
Heather Barnett, with voice conversion applied. Retain the input CC BY 4.0 credits
above; these third-party audio assets are not covered by the repository code license.
No endorsement by the readers or voice creators is implied.

```sh
python scripts/download_models.py
python scripts/download_examples.py
python scripts/download_example_voices.py
python scripts/publishable_demo.py
```

[Actual results](converted/results.json) include checkpoint/input hashes and all
timings. Twenty conversions completed on RTX 4090 / Torch 2.0.1+cu118. All saved
outputs were finite, non-silent and had zero clipped samples. Warm medians range
from 0.158 to 0.163 seconds; quality has not been established by a listening panel.
Pitch shift and retrieval are disabled for these no-pitch-guidance models.

**Male target candidate:** [Matsukaze / Refreshing Young Man v2](https://booth.pm/ja/items/4768759).
The creator states the speaker approved publication; the model is CC BY 4.0 and
requires the credit 松風. The v2 ZIP is 512 MB and its download requires BOOTH login.
It has not been downloaded or tested here. Both targets in the table above are female.

## Other supplied target voices

Supply authorized RVC checkpoints under `rvc_models/`, then run:

```sh
python scripts/speech_demo.py --female-voice MyFemaleVoice --male-voice MyMaleVoice --output-dir examples/generated
```

This writes five conversions plus `results.json`, containing the actual voice
names, pitch/index settings, GPU, durations and measured timings. Listen to each
file and review target-voice terms before selecting public outputs. Generated
files remain ignored until deliberately selected for publication; never label
them as BDL/SLT results unless those are the checkpoints actually used.
