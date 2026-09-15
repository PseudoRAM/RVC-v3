# Human speech test inputs

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

Audio is downloaded on demand and excluded from the source repository. Retain
this attribution if redistributing these clips or derived conversions, and label
converted recordings as modified audio. Voice checkpoints have separate terms.

For female voices, start with the female input at zero pitch shift. For conversion
from a lower-pitched speaker, compare several shifts instead of assuming zero or
a fixed octave works for every source/target. Pitch is only one factor: the voice
model's training quality, range, accent and retrieval index also affect results.
Sandy is a character checkpoint and should not be used to establish natural-female
voice quality in general.
