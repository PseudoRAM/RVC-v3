# README comparison players

These videos present the published WAV examples in sequence: original narration,
conversion to male VCTK p226, then conversion to female VCTK p231. On-screen labels
identify the current segment and pitch setting. `chapters.json` lists the source
files and approximate segment start times; video frame rounding can shift a
boundary by a fraction of a second.

- [Male narration comparison](male-comparison.mp4)
- [Female narration comparison](female-comparison.mp4)

The original WAVs remain unchanged. The previews resample audio to 48 kHz and
encode it as mono AAC at 160 kb/s, with an H.264 title card for browser playback.
They do not apply additional voice conversion, pitch changes or normalization.

## Rebuild

Install FFmpeg with `libx264`, AAC and `drawtext`, then run from the repository root:

```sh
python scripts/build_readme_previews.py
# If no system font is found:
python scripts/build_readme_previews.py --font /path/to/font.ttf
```

For inline GitHub README players, upload the MP4s through a GitHub Markdown
editor's attachment control and place each resulting `github.com/user-attachments/assets/`
URL in its own paragraph in the main README. Keep the repository copies as
downloadable fallbacks. A plain HTML `<audio>` tag is not a GitHub README player.

## Credits

Original recordings: LibriSpeech excerpts read by Garth Comira and Heather Barnett,
distributed by librosa under CC BY 4.0. The converted segments are modified audio.
See [full input attribution](../README.md) and [model attribution and settings](../ENGLISH.md).
Target checkpoints: Nekochu's English-trained VCTK p226 and p231 RVC v2 models.
Audio retains its separate license; the repository code's MIT license does not
replace it. No endorsement by the readers or model creators is implied.
