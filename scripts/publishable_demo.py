"""Generate attributed speech examples with the downloaded AISO v2 voices."""
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main():
    import numpy as np
    import soundfile as sf
    import torch
    from service import VoiceService

    folder = ROOT / "examples" / "converted"
    folder.mkdir(exist_ok=True)
    service = VoiceService()
    report = {"gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
              "torch": torch.__version__, "cases": []}
    for voice in ("AisoHowatto", "AisoSittori"):
        checkpoint, = (ROOT / "rvc_models" / voice).glob("*.pth")
        metadata = torch.load(checkpoint, map_location="cpu", weights_only=True)
        assert metadata.get("version") == "v2" and metadata.get("f0") == 0
        del metadata
        for source in ("female", "male"):
            input_path = ROOT / "examples" / "audio" / f"{source}.wav"
            target = folder / f"{source}-to-{voice.lower()}.wav"
            times = []
            for run in range(5):
                torch.manual_seed(1234)
                np.random.seed(1234)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                start = time.perf_counter()
                output = service.convert(input_path, rvc_model=voice, use_index=False, pitch_change=0)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                times.append(time.perf_counter() - start)
                try:
                    if run == 0:
                        shutil.copy2(output, target)
                finally:
                    shutil.rmtree(output.parent)
            audio, sr = sf.read(target)
            assert np.isfinite(audio).all() and np.max(np.abs(audio)) > 0
            row = {"source": source, "voice": voice, "version": "v2", "f0": False,
                   "pitch_change": 0, "use_index": False, "output": target.relative_to(ROOT).as_posix(),
                   "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                   "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
                   "sample_rate": sr, "duration_seconds": len(audio) / sr,
                   "peak": float(np.max(np.abs(audio))), "clipped_samples": int(np.sum(np.abs(audio) >= 1)),
                   "all_seconds": times, "warm_median_seconds": statistics.median(times[1:])}
            report["cases"].append(row)
            (folder / "results.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
