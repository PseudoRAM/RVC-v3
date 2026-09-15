from contextlib import nullcontext
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import service


class ServiceTests(unittest.TestCase):
    def test_shared_models_voice_switching_and_argument_forwarding(self):
        hubert, pitch = object(), object()
        config = SimpleNamespace(device="cpu", is_half=False)
        voice_loader = Mock(side_effect=lambda *args: ({"f0": 1}, "v2", object(), 48000, SimpleNamespace()))
        infer = Mock(side_effect=lambda *args: Path(args[3]).write_bytes(b"fake audio"))
        load_hubert = Mock(return_value=hubert)
        load_pitch = Mock(return_value=pitch)
        modules = {
            "torch": SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False), no_grad=nullcontext),
            "rvc": SimpleNamespace(Config=lambda *args: config, load_hubert=load_hubert,
                                   get_vc=voice_loader, rvc_infer=infer),
            "rmvpe": SimpleNamespace(RMVPE=load_pitch),
        }
        outputs = []
        try:
            with tempfile.TemporaryDirectory() as temp, patch.object(service, "ROOT", Path(temp)), patch.dict(sys.modules, modules), patch.dict("os.environ", {"RVC_VOICE_CACHE_SIZE": "1"}):
                for name in ("A", "B"):
                    folder = Path(temp) / "rvc_models" / name
                    folder.mkdir(parents=True)
                    (folder / "voice.pth").write_bytes(b"fake")
                    (folder / "voice.index").write_bytes(b"fake")
                runner = service.VoiceService()
                for name in ("A", "A", "B", "A"):
                    outputs.append(runner.convert("input.wav", rvc_model=name, crepe_hop_length=256))
                self.assertEqual(voice_loader.call_count, 3)
                self.assertEqual(load_hubert.call_count, 1)
                self.assertEqual(load_pitch.call_count, 1)
                self.assertEqual(len(set(outputs)), 4)
                args = infer.call_args.args
                self.assertTrue(args[0].endswith("voice.index"))
                self.assertEqual(args[1], 0.75)
                self.assertEqual(args[4], 4)
                self.assertEqual(args[13], 256)
                self.assertIs(args[14].model_rmvpe, pitch)
                self.assertIs(args[15], hubert)
                outputs.append(runner.convert("input.wav", rvc_model="A", use_index=False,
                                              pitch_change=0, index_rate=0.2))
                self.assertEqual(infer.call_args.args[0], "")
                self.assertEqual(infer.call_args.args[1], 0.2)
                self.assertEqual(infer.call_args.args[4], 0)
                (Path(temp) / "rvc_models" / "B" / "voice.index").unlink()
                outputs.append(runner.convert("input.wav", rvc_model="B"))
                self.assertEqual(infer.call_args.args[0], "")
                with self.assertRaises(ValueError):
                    runner.convert("input.wav", rvc_model="../escape")
        finally:
            for output in outputs:
                shutil.rmtree(output.parent)


if __name__ == "__main__":
    unittest.main()
