"""Benchmark supplied audio; optionally compare an explicitly provided legacy checkout."""
import argparse
import faulthandler
import json
import os
from pathlib import Path
import shutil
import statistics
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["legacy", "v3"], default="v3")
parser.add_argument("--audio", type=Path, required=True)
parser.add_argument("--legacy-root", type=Path)
parser.add_argument("--output-dir", type=Path)
parser.add_argument("--runs", type=int, default=7)
parser.add_argument("--voices", nargs="+", required=True)
args = parser.parse_args()
faulthandler.enable()
faulthandler.dump_traceback_later(120, repeat=True)
if args.runs < 2:
    parser.error("At least two runs required")
if args.mode == "legacy" and args.legacy_root is None:
    parser.error("Legacy mode requires --legacy-root pointing to the v2 source checkout")
root = Path(__file__).resolve().parents[1]
demo = args.output_dir or root / "benchmarks" / "comparison"
demo.mkdir(parents=True, exist_ok=True)
audio_path = args.audio.resolve()
started = time.perf_counter()
sys.path.insert(0, str((args.legacy_root if args.mode == "legacy" else root) / "src"))
import torch
import soundfile as sf
import numpy as np

if not torch.cuda.is_available():
    raise RuntimeError("GPU demo requires CUDA; refusing to silently benchmark CPU")

if args.mode == "legacy":
    import main as legacy
    legacy.rvc_models_dir = str(root / "rvc_models")
    legacy.output_dir = str(demo / "legacy-temp")
    convert = lambda voice: Path(legacy.voice_conversion(str(audio_path), voice))
else:
    from service import VoiceService
    runner = VoiceService()
    convert = lambda voice: runner.convert(audio_path, rvc_model=voice)

import rvc
original_infer = rvc.rvc_infer


def seeded_infer(*values, **options):
    # Seed after model initialization so caching does not change the RNG position.
    torch.manual_seed(1234)
    torch.cuda.manual_seed_all(1234)
    np.random.seed(1234)
    return original_infer(*values, **options)


rvc.rvc_infer = seeded_infer
if args.mode == "legacy":
    legacy.rvc_infer = seeded_infer

torch.cuda.synchronize()
startup = time.perf_counter() - started
source_info = sf.info(audio_path)
report = {"mode": args.mode, "gpu": torch.cuda.get_device_name(0),
          "python": sys.version, "torch": torch.__version__, "cuda": torch.version.cuda,
          "startup_including_imports_seconds": startup,
          "source": audio_path.name, "source_duration_seconds": source_info.duration,
          "source_sample_rate": source_info.samplerate,
          "settings": {"seed_before_inference": 1234, "pitch_change": 0, "f0_method": "rmvpe", "use_index": False,
                       "rms_mix_rate": 0.25, "protect": 0.33, "output_format": "wav"},
          "voices": []}
for voice in args.voices:
    rows = []
    for run in range(args.runs):
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        before = time.perf_counter()
        output = convert(voice)
        torch.cuda.synchronize()
        duration = time.perf_counter() - before
        rows.append({"seconds": duration,
                     "peak_allocated_mib": torch.cuda.max_memory_allocated() / 1024**2,
                     "peak_reserved_mib": torch.cuda.max_memory_reserved() / 1024**2})
        if run == 0:
            saved = demo / f"{args.mode}-{voice}.wav"
            shutil.copy2(output, saved)
        if args.mode == "v3":
            shutil.rmtree(output.parent)
        else:
            output.unlink()
    signal, sr = sf.read(saved)
    warm = statistics.median(row["seconds"] for row in rows[1:])
    report["voices"].append({"voice": voice, "output": saved.name,
                             "first_seconds": rows[0]["seconds"], "warm_median_seconds": warm,
                             "warm_min_seconds": min(row["seconds"] for row in rows[1:]),
                             "warm_max_seconds": max(row["seconds"] for row in rows[1:]),
                             "real_time_factor": warm / source_info.duration,
                             "output_sample_rate": sr, "output_duration_seconds": len(signal) / sr,
                             "output_peak": float(np.max(np.abs(signal))),
                             "output_rms": float(np.sqrt(np.mean(signal**2))),
                             "output_finite": bool(np.isfinite(signal).all()), "runs": rows})
    (demo / f"{args.mode}-results.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report["voices"][-1]), flush=True)
faulthandler.cancel_dump_traceback_later()
