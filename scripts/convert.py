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
from defaults import PITCH_CHANGE, INDEX_RATE, USE_INDEX


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--voice", default="CUSTOM")
    parser.add_argument("--model-url")
    parser.add_argument("--pitch", type=float, default=PITCH_CHANGE,
                        help="Pitch shift in semitones (default: +4); use 0 to preserve source pitch")
    parser.add_argument("--use-index", action=argparse.BooleanOptionalAction, default=USE_INDEX,
                        help="Use the model's index when available (default: enabled); --no-use-index disables it")
    parser.add_argument("--index-rate", type=float, default=INDEX_RATE,
                        help="Retrieval blend (default: 0.75)")
    parser.add_argument("--f0-method", choices=("rmvpe", "mangio-crepe"), default="rmvpe")
    parser.add_argument("--crepe-hop-length", type=int, default=160)
    parser.add_argument("--protect", type=float, default=0.33,
                        help="Unvoiced consonant protection; 0.5 disables protection")
    parser.add_argument("--rms-mix-rate", type=float, default=0.25,
                        help="Loudness envelope blend; 0 uses the input envelope, 1 the converted envelope")
    parser.add_argument("--runs", type=int, default=1)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.runs < 1 or args.output.suffix not in (".wav", ".mp3"):
        parser.error("Use a positive run count and a .wav or .mp3 output")
    if args.input.resolve() == args.output.resolve():
        parser.error("Input and output must be different paths")
    if not 0 <= args.index_rate <= 1:
        parser.error("Index rate must be between 0 and 1")
    if not 0 <= args.protect <= 0.5 or not 0 <= args.rms_mix_rate <= 1:
        parser.error("Protect must be between 0 and 0.5; RMS mix rate between 0 and 1")
    if args.crepe_hop_length < 1:
        parser.error("CREPE hop length must be positive")
    started = time.perf_counter()
    service = VoiceService()
    setup = time.perf_counter() - started
    durations = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for i in range(args.runs):
        started = time.perf_counter()
        output = service.convert(args.input, rvc_model=args.voice, custom_url=args.model_url,
                                 pitch_change=args.pitch, use_index=args.use_index,
                                 index_rate=args.index_rate, f0_method=args.f0_method,
                                 crepe_hop_length=args.crepe_hop_length, protect=args.protect,
                                 rms_mix_rate=args.rms_mix_rate, output_format=args.output.suffix[1:])
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
