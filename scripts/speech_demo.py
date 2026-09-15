"""Human-speech demo matrix; requires downloaded examples and supplied voices."""
import argparse
import json
from pathlib import Path
import shutil
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--female-voice", required=True, help="Authorized local female voice directory")
    parser.add_argument("--male-voice", required=True, help="Authorized local male voice directory")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "speech")
    args = parser.parse_args()
    if args.runs < 2:
        parser.error("At least two runs required")
    import numpy as np
    import soundfile as sf
    import torch
    from my_utils import load_audio
    from service import VoiceService

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    service = VoiceService()
    setup = time.perf_counter() - start
    def synchronize():
        if torch.cuda.is_available():
            torch.cuda.synchronize()
    source_stats = {}
    for label in ("male", "female"):
        path = ROOT / "examples" / "audio" / f"{label}.wav"
        audio, sr = sf.read(path)
        with torch.no_grad():
            f0 = service.pitch.infer_from_audio(load_audio(str(path), 16000))
        voiced = f0[f0 > 0]
        source_stats[label] = {"duration": len(audio)/sr, "sample_rate": sr,
                               "median_voiced_f0_hz": float(np.median(voiced)),
                               "peak": float(np.max(np.abs(audio)))}
    cases = [
        ("female-zero-no-index", "female", args.female_voice, 0, False),
        ("female-zero-index", "female", args.female_voice, 0, True),
        ("female-plus3-index", "female", args.female_voice, 3, True),
        ("male-to-female-plus8-index", "male", args.female_voice, 8, True),
        ("male-zero-index", "male", args.male_voice, 0, True),
    ]
    report = {"gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
              "torch": torch.__version__, "setup_seconds": setup,
              "source_stats": source_stats, "cases": []}
    for name, source, voice, pitch, indexed in cases:
        durations = []
        for i in range(args.runs):
            torch.manual_seed(1234)
            np.random.seed(1234)
            synchronize()
            start = time.perf_counter()
            path = service.convert(ROOT / "examples" / "audio" / f"{source}.wav",
                                   rvc_model=voice, pitch_change=pitch, use_index=indexed, index_rate=0.5)
            synchronize()
            durations.append(time.perf_counter() - start)
            try:
                if i == 0:
                    saved = output_dir / f"{name}.wav"
                    shutil.copy2(path, saved)
            finally:
                shutil.rmtree(path.parent)
        audio, sr = sf.read(saved)
        row = {"name": name, "source": source, "voice": voice, "pitch": pitch,
               "use_index": indexed, "warm_median_seconds": statistics.median(durations[1:]),
               "all_seconds": durations, "output_sample_rate": sr, "output_duration": len(audio)/sr,
               "finite": bool(np.isfinite(audio).all()), "rms": float(np.sqrt(np.mean(audio**2))),
               "clipped_samples": int(np.count_nonzero(np.abs(audio) >= 1))}
        report["cases"].append(row)
        (output_dir / "results.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
