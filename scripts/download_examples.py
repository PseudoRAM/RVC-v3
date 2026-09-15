"""Fetch two attributed LibriSpeech examples and verify librosa's SHA256 hashes."""
import hashlib
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "male": ("5703-47212-0000.hq.ogg", "f09254a0daf4b14b292868d46dc2e3c8e158d19fafff739ad4c3931e2ce7b1b0"),
    "female": ("198-209-0000.hq.ogg", "6a8d2c16e56dcb27b7f5fe5aa99bfd26b4722a6dabca1968eff951b456936514"),
}


def main():
    folder = ROOT / "examples" / "audio"
    folder.mkdir(parents=True, exist_ok=True)
    for label, (filename, expected) in EXAMPLES.items():
        target = folder / filename
        if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            with urllib.request.urlopen("https://librosa.org/data/audio/" + filename, timeout=60) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"Checksum mismatch: {filename}")
            target.write_bytes(data)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(target),
                        "-ac", "1", "-c:a", "pcm_s16le", str(folder / f"{label}.wav")], check=True)
        print(f"Verified and decoded {label}: {folder / (label + '.wav')}")


if __name__ == "__main__":
    main()
