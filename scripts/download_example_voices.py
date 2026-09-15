"""Fetch two pinned MIT-licensed AISO RVC v2 speech checkpoints."""
import hashlib
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = "c46962577db8cf3fba2b3fc3526af98eb6611840"
BASE = f"https://huggingface.co/wok000/vcclient_model/resolve/{REVISION}/rvc_v2_chihaya_jinja/"
VOICES = {
    "AisoHowatto": ("V2-AISO-HOWATTO.pth", "8fc32652b8ec472615af3f6661a50a195dd54990e0f517bd0dbd66db59813146"),
    "AisoSittori": ("V2-AISO-SITTORI.pth", "7696d020ced92d9d5502ca40943ee7d35120988a92b70909fa099fc4e24a8477"),
}


def main():
    for voice, (name, checksum) in VOICES.items():
        folder = ROOT / "rvc_models" / voice
        folder.mkdir(parents=True, exist_ok=True)
        for filename, expected in ((name, checksum), ("description.txt", "7d84b5e3c30a47589c57d68c49ed79e86c6ca2469dd119887ddfc3f851f06b1c")):
            target = folder / filename
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
                continue
            with urllib.request.urlopen(BASE + filename, timeout=60) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"Checksum mismatch: {filename}")
            target.write_bytes(data)
        print(f"Verified {voice}; creator/terms: examples/AISO-LICENSE.txt")


if __name__ == "__main__":
    main()
