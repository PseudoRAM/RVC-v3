"""Run repeated predictions in one process; output JSON timings and clean files."""
import argparse
import json
from pathlib import Path
import shutil
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from service import VoiceService

parser = argparse.ArgumentParser()
parser.add_argument("audio", type=Path)
parser.add_argument("--voice", required=True, help="Authorized local voice directory")
parser.add_argument("--runs", type=int, default=10)
args = parser.parse_args()
if args.runs < 2:
    parser.error("Use at least two runs to separate first and warm predictions")
start = time.perf_counter()
service = VoiceService()
setup_seconds = time.perf_counter() - start
durations = []
for _ in range(args.runs):
    start = time.perf_counter()
    output = service.convert(args.audio, rvc_model=args.voice)
    durations.append(time.perf_counter() - start)
    shutil.rmtree(output.parent)
print(json.dumps({"setup_seconds": setup_seconds, "first_prediction_seconds": durations[0],
                  "warm_median_seconds": statistics.median(durations[1:]),
                  "all_prediction_seconds": durations}, indent=2))
