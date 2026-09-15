"""Check that omitted settings and explicit overrides reach the service."""
import ast
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EntryPointDefaultsTests(unittest.TestCase):
    def test_cog_schema_defaults_are_literals_matching_service(self):
        defaults = load_module('shared_defaults', ROOT / 'src/defaults.py')
        expected = {'pitch_change': defaults.PITCH_CHANGE,
                    'index_rate': defaults.INDEX_RATE, 'use_index': defaults.USE_INDEX}
        tree = ast.parse((ROOT / 'predict.py').read_text())
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef) and node.name == 'predict')
        for arg, value in zip(method.args.args[-len(method.args.defaults):], method.args.defaults):
            if arg.arg in expected:
                literal = next(item.value for item in value.keywords if item.arg == 'default')
                self.assertIsInstance(literal, ast.Constant, arg.arg)
                self.assertEqual(literal.value, expected.pop(arg.arg))
        self.assertFalse(expected)

    def test_cli_defaults_and_explicit_legacy_override(self):
        cli = load_module('convert_cli', ROOT / 'scripts/convert.py')
        for options, expected in [([], (4, .75, True)),
                                  (['--pitch', '0', '--index-rate', '0.5', '--no-use-index'],
                                   (0, .5, False))]:
            with self.subTest(options=options), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                result = folder / 'generated' / 'output.wav'
                result.parent.mkdir()
                result.write_bytes(b'converted audio')
                runner = SimpleNamespace(convert=Mock(return_value=result))
                target = folder / 'saved.wav'
                argv = ['convert.py', str(folder / 'input.wav'), str(target), '--voice', 'Rogan'] + options
                with patch.object(cli, 'VoiceService', return_value=runner), patch.object(sys, 'argv', argv):
                    cli.main()
                kwargs = runner.convert.call_args.kwargs
                self.assertEqual((kwargs['pitch_change'], kwargs['index_rate'], kwargs['use_index']), expected)
                self.assertEqual(target.read_bytes(), b'converted audio')

    def test_cog_defaults_and_explicit_legacy_override(self):
        cog = SimpleNamespace(BasePredictor=object, Path=Path, Input=lambda default=None, **kw: default)
        with patch.dict(sys.modules, {'cog': cog}):
            api = load_module('predict_default_test', ROOT / 'predict.py')
        predictor = api.Predictor()
        predictor.service = SimpleNamespace(convert=Mock(return_value=Path('output.wav')))
        for options, expected in [({}, (4, .75, True)),
                                  ({'pitch_change': 0, 'index_rate': .5, 'use_index': False},
                                   (0, .5, False))]:
            with self.subTest(options=options):
                predictor.predict(Path('input.wav'), rvc_model='Rogan', **options)
                values = predictor.service.convert.call_args.args
                self.assertEqual((values[4], values[5], values[12]), expected)


if __name__ == '__main__':
    unittest.main()
