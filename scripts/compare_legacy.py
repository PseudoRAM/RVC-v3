"""Compare local v2/v3 inference using identical assets and controlled random seeds.

Run each engine in a separate process to avoid Python module-name collisions.
Requires the normal GPU inference environment and a local legacy source checkout.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['v2', 'v3'], required=True)
    parser.add_argument('--legacy-root', type=Path, required=True)
    parser.add_argument('--voice', default='DavidGoggins')
    parser.add_argument('--output-dir', type=Path,
                        help='Separate comparison directory, e.g. demo/rogan-comparison')
    parser.add_argument('--seed', type=int, default=20260916)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = args.legacy_root.resolve() if args.engine == 'v2' else root
    sys.path.insert(0, str(source / 'src'))
    import numpy as np
    import soundfile as sf
    import torch
    from rvc import Config, get_vc, load_hubert, rvc_infer
    from rmvpe import RMVPE

    destination = args.output_dir.resolve() if args.output_dir else root / 'demo' / 'similarity-audit'
    destination.mkdir(parents=True, exist_ok=True)
    voice = root / 'rvc_models' / args.voice
    checkpoint, = voice.glob('*.pth')
    index, = voice.glob('*.index')
    input_path = root / 'examples/audio/male.wav'
    if args.engine == 'v2':
        config = Config('cuda:0', True)
        hubert = load_hubert(config.device, config.is_half, str(root / 'rvc_models/hubert_base.pt'))
        cpt, version, net_g, sr, pipeline = get_vc(config.device, config.is_half, config, str(checkpoint))
        # Preload pitch before seeding: model construction otherwise consumes RNG
        # on the first v2 call but during setup in v3.
        pipeline.model_rmvpe = RMVPE(str(root / 'rvc_models/rmvpe.pt'), config.is_half, config.device)
    else:
        from service import VoiceService
        service = VoiceService()
        # Prime the voice cache before seeding for the same reason.
        warmup = service.convert(input_path, rvc_model=args.voice)
        shutil.rmtree(warmup.parent)
        pipeline = next(iter(service.voices.items.values()))[-1]

    cases = [('no-index', 0, 0), ('index50', .5, 0), ('index75', .75, 0),
             ('index100', 1, 0), ('index75-pitch3', .75, 3), ('index75-pitch6', .75, 6)]
    if args.engine == 'v2':
        cases = cases[:2]
    else:
        cases.append(('index50-repeat', .5, 0))
    results = []
    for name, rate, pitch in cases:
        torch.manual_seed(args.seed)
        torch.cuda.manual_seed_all(args.seed)
        np.random.seed(args.seed)
        target = destination / f'{args.engine}-{name}.wav'
        if args.engine == 'v2':
            rvc_infer(str(index) if rate else '', rate, str(input_path), str(target), pitch,
                      'rmvpe', cpt, version, net_g, 3, sr, .25, .33, 160, pipeline, hubert)
        else:
            output = service.convert(input_path, rvc_model=args.voice, use_index=bool(rate),
                                     index_rate=rate, pitch_change=pitch)
            shutil.copy2(output, target)
            shutil.rmtree(output.parent)
        samples, sample_rate = sf.read(target)
        results.append(dict(file=target.name, index_rate=rate, pitch=pitch,
                            duration=len(samples)/sample_rate, sample_rate=sample_rate,
                            finite=bool(np.isfinite(samples).all()),
                            peak=float(np.max(np.abs(samples))),
                            rms=float(np.sqrt(np.mean(samples**2)))))
    from my_utils import load_audio
    f0 = pipeline.model_rmvpe.infer_from_audio(load_audio(str(input_path), 16000), thred=.03)
    metadata = dict(engine=args.engine, voice=args.voice, source=str(source), seed=args.seed, cases=results,
                    source_voiced_pitch_median=float(np.median(f0[f0 > 0])))
    (destination / f'{args.engine}-results.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2))
    if args.engine == 'v3':
        comparisons = []
        for left, right in [('v2-no-index', 'v3-no-index'), ('v2-index50', 'v3-index50'),
                            ('v3-index50', 'v3-index50-repeat')]:
            legacy_file = destination / (left + '.wav')
            if not legacy_file.exists():
                raise FileNotFoundError('Run the v2 comparison first: ' + str(legacy_file))
            x, rate_x = sf.read(legacy_file)
            y, rate_y = sf.read(destination / (right + '.wav'))
            assert rate_x == rate_y and x.shape == y.shape, 'Audio shape mismatch'
            error_power = float(np.sum((x - y) ** 2))
            snr = float(10 * np.log10(np.sum(x*x) / error_power)) if error_power else None
            correlation = float(np.corrcoef(x, y)[0, 1])
            comparisons.append(dict(left=left, right=right, correlation=correlation,
                                    snr_db=snr, identical=error_power == 0,
                                    passed=correlation > .9999 and (snr is None or snr > 40)))
        (destination / 'parity.json').write_text(json.dumps(comparisons, indent=2))
        print(json.dumps(comparisons, indent=2))
        if not all(row['passed'] for row in comparisons):
            raise SystemExit('Audio parity failed; inspect parity.json. This is not a speaker-similarity score.')


if __name__ == '__main__':
    main()
