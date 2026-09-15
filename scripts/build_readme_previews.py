"""Build labelled README video players from the published WAV examples.

Requires FFmpeg/ffprobe with libx264, AAC and drawtext. Audio is resampled to
48 kHz and encoded as AAC for browser playback; the original WAVs are unchanged.
"""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.check_output(args, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, help="Path to a TrueType font")
    args = parser.parse_args()
    fonts = [args.font] if args.font else [
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    font = next((p for p in fonts if p and p.is_file()), None)
    if font is None:
        parser.error("Pass --font with the path to a TrueType font")
    escaped_font = font.as_posix().replace(":", "\\:")
    destination = ROOT / "examples" / "previews"
    destination.mkdir(exist_ok=True)
    manifest = {}
    for source, reader in [("male", "Garth Comira"), ("female", "Heather Barnett")]:
        clips = [
            (ROOT / "examples/audio" / (source + ".wav"), "Original recording", "LibriSpeech / " + reader),
            (ROOT / "examples/english" / (source + "-to-vctk226.wav"), "Converted / Male target p226", "Pitch " + ("0" if source == "male" else "-8") + " semitones / Retrieval 0.5"),
            (ROOT / "examples/english" / (source + "-to-vctk231.wav"), "Converted / Female target p231", "Pitch " + ("+8" if source == "male" else "0") + " semitones / Retrieval 0.5"),
        ]
        chapters = []
        elapsed = 0.0
        with tempfile.TemporaryDirectory() as scratch:
            temp = Path(scratch)
            for index, (audio, title, detail) in enumerate(clips):
                duration = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(audio)))
                chapters.append({"start_seconds": round(elapsed, 3), "title": title, "audio": audio.relative_to(ROOT).as_posix()})
                filters = [
                    "drawbox=x=0:y=0:w=iw:h=7:color=0x8fe3bc:t=fill",
                    "drawbox=x=48:y=295:w=864:h=2:color=0x334454:t=fill",
                ]
                for text, size, x, y, color in [
                    ("RVC-v3 / " + source.capitalize() + " narration", 24, 48, 42, "0x8fe3bc"),
                    (title, 40, 48, 120, "white"),
                    (detail, 23, 48, 184, "0xb9c6d2"),
                    (str(index + 1) + " / 3     Original  >  Male target  >  Female target", 21, 48, 241, "0xb9c6d2"),
                    ("Audio CC BY 4.0 / Models by Nekochu / Credits in README", 18, 48, 329, "0xb9c6d2"),
                ]:
                    filters.append("drawtext=fontfile='" + escaped_font + "':text='" + text + "':fontsize=" + str(size) + ":fontcolor=" + color + ":x=" + str(x) + ":y=" + str(y))
                subprocess.run([
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "color=c=0x101923:s=960x400:r=25",
                    "-i", str(audio), "-vf", ",".join(filters),
                    "-c:v", "libx264", "-tune", "stillimage", "-preset", "fast", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "1",
                    "-t", str(duration), str(temp / (str(index) + ".mp4")),
                ], check=True)
                elapsed += duration
            playlist = temp / "clips.txt"
            playlist.write_text("".join("file '" + str(i) + ".mp4'\n" for i in range(3)), encoding="utf-8")
            output = destination / (source + "-comparison.mp4")
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(playlist), "-c", "copy", "-movflags", "+faststart", str(output)], check=True)
            manifest[output.name] = chapters
            print(output)
    (destination / "chapters.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
