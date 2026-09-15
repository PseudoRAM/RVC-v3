"""Convert a clip locally, optionally timing repeated requests in one worker."""
import argparse
import json
from pathlib import Path
import shutil
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from service import VoiceService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--voice", default="CUSTOM")
    parser.add_argument("--model-url")
    parser.add_argument("--pitch", type=float, default=0)
    parser.add_argument("--use-index", action="store_true")
    parser.add_argument("--index-rate", type=float, default=0.5)
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()
    if args.runs < 1 or args.output.suffix not in (".wav", ".mp3"):
        parser.error("Use a positive run count and a .wav or .mp3 output")
    if args.input.resolve() == args.output.resolve():
        parser.error("Input and output must be different paths")
    if not 0 <= args.index_rate <= 1:
        parser.error("Index rate must be between 0 and 1")
    started = time.perf_counter()
    service = VoiceService()
    setup = time.perf_counter() - started
    durations = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for i in range(args.runs):
        started = time.perf_counter()
        output = service.convert(args.input, rvc_model=args.voice, custom_url=args.model_url,
                                 pitch_change=args.pitch, use_index=args.use_index,
                                 index_rate=args.index_rate, output_format=args.output.suffix[1:])
        durations.append(time.perf_counter() - started)
        try:
            if i == 0:
                shutil.copy2(output, args.output)
        finally:
            shutil.rmtree(output.parent)
    print(json.dumps({"output": str(args.output), "setup_seconds": setup,
                      "first_seconds": durations[0],
                      "warm_median_seconds": statistics.median(durations[1:]) if len(durations) > 1 else None,
                      "all_seconds": durations}, indent=2))


if __name__ == "__main__":
    main()
